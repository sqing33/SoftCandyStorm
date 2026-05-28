import argparse
import importlib.util
import inspect
import json
import math
import random
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from python.gym_env import SoftCandyStormEnv
from python.train.train_behavior_clone import (
    load_behavior_clone_policy,
    load_trajectory_dataset,
    summarize_dataset,
)
from python.train.train_upgrade_choice import load_upgrade_choice_policy


REQUIRED_MODULES = ["gymnasium", "numpy", "stable_baselines3", "torch"]

BASE_DEMO_MAP_PRESETS = {
    "all-base-demo": [
        "frosting-grassland",
        "soda-creek",
        "cotton-cloud-pasture",
        "caramel-workshop",
        "jelly-platform",
        "cracked-star-jar",
    ],
    "high-pressure": [
        "soda-creek",
        "caramel-workshop",
        "cracked-star-jar",
    ],
    "stable-open": [
        "frosting-grassland",
        "cotton-cloud-pasture",
        "jelly-platform",
    ],
}
ANCHOR_SAMPLE_WEIGHTING_MODES = {
    "none",
    "time_bucket_balance",
    "map_time_bucket_balance",
}
ANCHOR_TIME_BUCKETS = [
    ("opening_lt_60", 0.0, 60.0),
    ("mid_60_to_180", 60.0, 180.0),
    ("late_180_to_300", 180.0, 300.0),
    ("post_300", 300.0, math.inf),
]
ANCHOR_TIME_BUCKET_LABELS = {label for label, _, _ in ANCHOR_TIME_BUCKETS}

GYM_ACTION_MOVEMENTS = {
    0: (0.0, 0.0),
    1: (0.0, 1.0),
    2: (math.sqrt(0.5), math.sqrt(0.5)),
    3: (1.0, 0.0),
    4: (math.sqrt(0.5), -math.sqrt(0.5)),
    5: (0.0, -1.0),
    6: (-math.sqrt(0.5), -math.sqrt(0.5)),
    7: (-1.0, 0.0),
    8: (-math.sqrt(0.5), math.sqrt(0.5)),
}
GYM_OBSERVATION_V2_NEAREST_HAZARD_START = 130
GYM_OBSERVATION_V2_BOSS_START = 137


def load_config(path):
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def dependency_status():
    return {
        module: importlib.util.find_spec(module) is not None for module in REQUIRED_MODULES
    }


def require_dependencies():
    status = dependency_status()
    missing = [module for module, available in status.items() if not available]
    if missing:
        raise RuntimeError(
            "missing Python dependencies: "
            + ", ".join(missing)
            + "; install python/train/requirements.txt before real training or evaluation"
        )
    return status


def algorithm_config(config, algorithm):
    try:
        selected = config["algorithms"][algorithm]
    except KeyError as exc:
        raise ValueError(f"unknown algorithm `{algorithm}`") from exc
    if not selected.get("enabled", False):
        raise ValueError(f"algorithm `{algorithm}` is disabled in config")
    return selected


def algorithm_overrides_from_args(args):
    overrides = {}
    if args.learning_rate is not None:
        if args.learning_rate <= 0.0:
            raise ValueError("--learning-rate must be greater than 0")
        overrides["learning_rate"] = args.learning_rate
    if args.ent_coef is not None:
        if args.algorithm != "ppo":
            raise ValueError("--ent-coef is only supported for --algorithm ppo")
        overrides["ent_coef"] = args.ent_coef
    return overrides


def merge_algorithm_parameters(base_parameters, overrides):
    merged = dict(base_parameters or {})
    merged.update(overrides or {})
    return merged


def algorithm_parameters_source_label(warm_start_metadata, warm_start_model, overrides):
    suffix = "_with_overrides" if overrides else ""
    if warm_start_metadata is not None:
        return f"warm_start_metadata{suffix}"
    if warm_start_model is not None:
        return f"config_fallback_missing_warm_start_metadata{suffix}"
    return f"config{suffix}"


def apply_loaded_model_overrides(model, overrides):
    for key, value in (overrides or {}).items():
        if not hasattr(model, key):
            raise ValueError(f"loaded model does not expose algorithm parameter `{key}`")
        setattr(model, key, value)
        if key == "learning_rate":
            setup_lr_schedule = getattr(model, "_setup_lr_schedule", None)
            if callable(setup_lr_schedule):
                setup_lr_schedule()


def validate_eval_random_seed(eval_random_seed, deterministic):
    if eval_random_seed is None:
        return None
    if eval_random_seed < 0:
        raise ValueError("--eval-random-seed must be non-negative")
    if deterministic:
        raise ValueError("--eval-random-seed requires --eval-stochastic")
    return eval_random_seed


def seed_stochastic_action_sampling(eval_random_seed, model=None):
    if eval_random_seed is None:
        return {
            "seed": None,
            "seeded_sources": [],
        }

    random.seed(eval_random_seed)
    seeded_sources = ["python_random"]

    try:
        import numpy as np

        np.random.seed(eval_random_seed)
        seeded_sources.append("numpy")
    except ImportError:
        pass

    try:
        import torch

        torch.manual_seed(eval_random_seed)
        seeded_sources.append("torch")
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(eval_random_seed)
            seeded_sources.append("torch_cuda")
    except ImportError:
        pass

    set_random_seed = getattr(model, "set_random_seed", None)
    if callable(set_random_seed):
        set_random_seed(eval_random_seed)
        seeded_sources.append("policy_model")

    return {
        "seed": eval_random_seed,
        "seeded_sources": seeded_sources,
    }


class StagedOpeningPolicy:
    policy_kind = "staged_sb3_opening"

    def __init__(
        self,
        opening_model,
        fallback_model,
        opening_seconds,
        opening_model_path,
        fallback_model_path,
    ):
        if opening_seconds <= 0.0:
            raise ValueError("opening_seconds must be greater than 0")
        self.opening_model = opening_model
        self.fallback_model = fallback_model
        self.opening_seconds = opening_seconds
        self.opening_model_path = str(opening_model_path)
        self.fallback_model_path = str(fallback_model_path)
        self._time_seconds = 0.0

    def reset(self):
        self._time_seconds = 0.0
        for model in (self.opening_model, self.fallback_model):
            reset = getattr(model, "reset", None)
            if callable(reset):
                reset()

    def set_map_id(self, map_id):
        for model in (self.opening_model, self.fallback_model):
            set_map_id = getattr(model, "set_map_id", None)
            if callable(set_map_id):
                set_map_id(map_id)

    def set_step_context(self, info):
        self._time_seconds = float(info.get("time_seconds", 0.0) or 0.0)
        for model in (self.opening_model, self.fallback_model):
            set_step_context = getattr(model, "set_step_context", None)
            if callable(set_step_context):
                set_step_context(info)

    def active_model(self):
        if self._time_seconds < self.opening_seconds:
            return self.opening_model
        return self.fallback_model

    def predict(self, observation, deterministic=True):
        return self.active_model().predict(observation, deterministic=deterministic)

    def set_random_seed(self, seed):
        for model in (self.opening_model, self.fallback_model):
            set_random_seed = getattr(model, "set_random_seed", None)
            if callable(set_random_seed):
                set_random_seed(seed)

    def action_scores(self, observation):
        return policy_action_scores(self.active_model(), observation)

    def opening_policy_report(self):
        return {
            "mode": "staged_sb3_opening",
            "opening_model_path": self.opening_model_path,
            "fallback_model_path": self.fallback_model_path,
            "opening_seconds": self.opening_seconds,
            "limitations": [
                "The opening model is used only during evaluation/comparison before opening_seconds.",
                "This wrapper does not train a new policy and is not policy acceptance evidence by itself.",
            ],
        }


class EdgeRecoveryFilterPolicy:
    policy_kind = "edge_recovery_filter"

    def __init__(self, policy, edge_distance=32.0):
        if edge_distance < 0.0:
            raise ValueError("edge_distance must be non-negative")
        self.policy = policy
        self.edge_distance = edge_distance
        self._step_context = {}
        self._last_recovery_decision = None

    def reset(self):
        reset = getattr(self.policy, "reset", None)
        if callable(reset):
            reset()

    def set_map_id(self, map_id):
        set_map_id = getattr(self.policy, "set_map_id", None)
        if callable(set_map_id):
            set_map_id(map_id)

    def set_step_context(self, info):
        self._step_context = info or {}
        set_step_context = getattr(self.policy, "set_step_context", None)
        if callable(set_step_context):
            set_step_context(info)

    def set_random_seed(self, seed):
        set_random_seed = getattr(self.policy, "set_random_seed", None)
        if callable(set_random_seed):
            set_random_seed(seed)

    def predict(self, observation, deterministic=True):
        self._last_recovery_decision = None
        action, state = self.policy.predict(observation, deterministic=deterministic)
        action_index = action_to_int(action)
        if deterministic and self.action_pushes_into_edge(action_index):
            action_scores = policy_action_scores(self.policy, observation)
            recovery_action = self.recovery_action(action_index, action_scores)
            if recovery_action != action_index:
                self._last_recovery_decision = self.build_recovery_decision(
                    action_index,
                    recovery_action,
                    action_scores,
                )
            action_index = recovery_action
            return action_index, state
        return action, state

    def action_scores(self, observation):
        return policy_action_scores(self.policy, observation)

    def action_pushes_into_edge(self, action_index):
        return action_pushes_into_edge(
            action_index,
            self._step_context.get("diagnostics", {}),
            self.edge_distance,
        )

    def recovery_action(self, blocked_action, action_scores):
        scores = action_scores.get("scores", []) if isinstance(action_scores, dict) else []
        ranked_actions = sorted(
            range(min(len(scores), len(GYM_ACTION_MOVEMENTS))),
            key=lambda index: float(scores[index]),
            reverse=True,
        )
        for action_index in ranked_actions:
            if not self.action_pushes_into_edge(action_index):
                return action_index
        return blocked_action

    def build_recovery_decision(self, blocked_action, recovery_action, action_scores):
        scores = action_scores.get("scores", []) if isinstance(action_scores, dict) else []
        ranked_actions = sorted(
            range(min(len(scores), len(GYM_ACTION_MOVEMENTS))),
            key=lambda index: float(scores[index]),
            reverse=True,
        )
        blocked_score = score_at(scores, blocked_action)
        recovery_score = score_at(scores, recovery_action)
        return {
            "mode": "edge_recovery_filter",
            "edge_distance": self.edge_distance,
            "original_action": int(blocked_action),
            "target_action": int(recovery_action),
            "score_kind": action_scores.get("kind") if isinstance(action_scores, dict) else None,
            "original_action_score": blocked_score,
            "target_action_score": recovery_score,
            "score_margin": (
                round(float(recovery_score) - float(blocked_score), 6)
                if blocked_score is not None and recovery_score is not None
                else None
            ),
            "target_rank": (
                ranked_actions.index(recovery_action) + 1
                if recovery_action in ranked_actions
                else None
            ),
        }

    def consume_recovery_decision(self):
        decision = self._last_recovery_decision
        self._last_recovery_decision = None
        return decision

    def opening_policy_report(self):
        return opening_policy_report(self.policy)

    def policy_adapter_report(self):
        return {
            "mode": "edge_recovery_filter",
            "edge_distance": self.edge_distance,
            "wrapped_policy_kind": getattr(self.policy, "policy_kind", "sb3"),
            "limitations": [
                "This deterministic wrapper is diagnostic repair evidence only.",
                "It is not a trained policy and cannot be used as RL policy acceptance evidence.",
            ],
        }


class LateRecoveryFilterPolicy:
    policy_kind = "late_recovery_filter"

    def __init__(
        self,
        policy,
        min_seconds=180.0,
        edge_distance=32.0,
        hazard_threshold=0.2,
        boss_threshold=0.05,
        enemy_threshold=0.05,
        low_health_threshold=0.25,
        toward_dot_threshold=0.15,
    ):
        if min_seconds < 0.0:
            raise ValueError("min_seconds must be non-negative")
        if edge_distance < 0.0:
            raise ValueError("edge_distance must be non-negative")
        self.policy = policy
        self.min_seconds = float(min_seconds)
        self.edge_distance = float(edge_distance)
        self.hazard_threshold = float(hazard_threshold)
        self.boss_threshold = float(boss_threshold)
        self.enemy_threshold = float(enemy_threshold)
        self.low_health_threshold = float(low_health_threshold)
        self.toward_dot_threshold = float(toward_dot_threshold)
        self._step_context = {}
        self._last_recovery_decision = None

    def reset(self):
        reset = getattr(self.policy, "reset", None)
        if callable(reset):
            reset()

    def set_map_id(self, map_id):
        set_map_id = getattr(self.policy, "set_map_id", None)
        if callable(set_map_id):
            set_map_id(map_id)

    def set_step_context(self, info):
        self._step_context = info or {}
        set_step_context = getattr(self.policy, "set_step_context", None)
        if callable(set_step_context):
            set_step_context(info)

    def set_random_seed(self, seed):
        set_random_seed = getattr(self.policy, "set_random_seed", None)
        if callable(set_random_seed):
            set_random_seed(seed)

    def predict(self, observation, deterministic=True):
        self._last_recovery_decision = None
        action, state = self.policy.predict(observation, deterministic=deterministic)
        action_index = action_to_int(action)
        if deterministic:
            action_scores = policy_action_scores(self.policy, observation)
            recovery_action, original_reasons, target_reasons = self.recovery_action(
                action_index,
                action_scores,
                observation,
            )
            if recovery_action != action_index:
                self._last_recovery_decision = self.build_recovery_decision(
                    action_index,
                    recovery_action,
                    action_scores,
                    original_reasons,
                    target_reasons,
                    observation,
                )
                action_index = recovery_action
                return action_index, state
        return action, state

    def action_scores(self, observation):
        return policy_action_scores(self.policy, observation)

    def recovery_action(self, blocked_action, action_scores, observation):
        original_reasons = self.action_risk_reasons(blocked_action, observation)
        if not original_reasons:
            return blocked_action, [], []

        scores = action_scores.get("scores", []) if isinstance(action_scores, dict) else []
        ranked_actions = sorted(
            range(min(max(len(scores), len(GYM_ACTION_MOVEMENTS)), len(GYM_ACTION_MOVEMENTS))),
            key=lambda index: score_at(scores, index) if score_at(scores, index) is not None else 0.0,
            reverse=True,
        )
        for action_index in ranked_actions:
            reasons = self.action_risk_reasons(action_index, observation)
            if not reasons:
                return action_index, original_reasons, []

        best_action = min(
            ranked_actions or range(len(GYM_ACTION_MOVEMENTS)),
            key=lambda index: (
                self.action_risk_score(index, observation),
                -(score_at(scores, index) or 0.0),
            ),
        )
        return best_action, original_reasons, self.action_risk_reasons(best_action, observation)

    def action_risk_reasons(self, action_index, observation):
        if self.current_time_seconds() < self.min_seconds:
            return []
        diagnostics = self._step_context.get("diagnostics", {}) or {}
        reasons = []
        if action_pushes_into_edge(action_index, diagnostics, self.edge_distance):
            reasons.append("wallward_edge")

        pressure = self.pressure_context(observation)
        if (
            int(action_index) == 0
            and pressure["combined_pressure"] > 0.0
            and (
                pressure["low_health_risk"] >= self.low_health_threshold
                or pressure["hazard_pressure_risk"] >= self.hazard_threshold
                or pressure["boss_pressure_risk"] >= self.boss_threshold
                or pressure["enemy_pressure_risk"] >= self.enemy_threshold
            )
        ):
            reasons.append("idle_under_late_pressure")
        if (
            pressure["hazard_pressure_risk"] >= self.hazard_threshold
            and action_moves_toward_vector(
                action_index,
                pressure["hazard_vector"],
                self.toward_dot_threshold,
            )
        ):
            reasons.append("toward_hazard")
        if (
            pressure["boss_pressure_risk"] >= self.boss_threshold
            and action_moves_toward_vector(
                action_index,
                pressure["boss_vector"],
                self.toward_dot_threshold,
            )
        ):
            reasons.append("toward_boss")
        if (
            pressure["enemy_pressure_risk"] >= self.enemy_threshold
            and action_moves_toward_vector(
                action_index,
                pressure["enemy_vector"],
                self.toward_dot_threshold,
            )
        ):
            reasons.append("toward_enemy_pressure")
        return reasons

    def action_risk_score(self, action_index, observation):
        diagnostics = self._step_context.get("diagnostics", {}) or {}
        pressure = self.pressure_context(observation)
        score = 0.0
        if action_pushes_into_edge(action_index, diagnostics, self.edge_distance):
            score += 1.0
        low_health_boost = 1.0 + pressure["low_health_risk"]
        score += pressure["hazard_pressure_risk"] * max(
            0.0,
            action_vector_alignment(action_index, pressure["hazard_vector"]),
        )
        score += pressure["boss_pressure_risk"] * max(
            0.0,
            action_vector_alignment(action_index, pressure["boss_vector"]),
        )
        score += pressure["enemy_pressure_risk"] * max(
            0.0,
            action_vector_alignment(action_index, pressure["enemy_vector"]),
        )
        if int(action_index) == 0 and pressure["combined_pressure"] > 0.0:
            score += 0.25 * pressure["combined_pressure"]
        return round(score * low_health_boost, 6)

    def pressure_context(self, observation):
        diagnostics = self._step_context.get("diagnostics", {}) or {}
        hazard_pressure = as_float(diagnostics.get("hazard_pressure_risk")) or 0.0
        boss_pressure = as_float(diagnostics.get("boss_pressure_risk")) or 0.0
        enemy_pressure = as_float(diagnostics.get("enemy_pressure_risk")) or 0.0
        low_health = as_float(diagnostics.get("low_health_risk")) or 0.0
        hazard_vector = observation_v2_nearest_hazard_vector(observation)
        boss_vector = observation_v2_boss_vector(observation)
        enemy_vector = diagnostics_enemy_vector(diagnostics)
        combined = max(hazard_pressure, boss_pressure, enemy_pressure)
        return {
            "hazard_pressure_risk": clamp_float(hazard_pressure, 0.0, 1.0),
            "boss_pressure_risk": clamp_float(boss_pressure, 0.0, 1.0),
            "enemy_pressure_risk": clamp_float(enemy_pressure, 0.0, 1.0),
            "low_health_risk": clamp_float(low_health, 0.0, 1.0),
            "combined_pressure": clamp_float(combined, 0.0, 1.0),
            "hazard_vector": hazard_vector,
            "boss_vector": boss_vector,
            "enemy_vector": enemy_vector,
        }

    def current_time_seconds(self):
        return float(self._step_context.get("time_seconds", 0.0) or 0.0)

    def build_recovery_decision(
        self,
        blocked_action,
        recovery_action,
        action_scores,
        original_reasons,
        target_reasons,
        observation,
    ):
        scores = action_scores.get("scores", []) if isinstance(action_scores, dict) else []
        ranked_actions = sorted(
            range(min(len(scores), len(GYM_ACTION_MOVEMENTS))),
            key=lambda index: float(scores[index]),
            reverse=True,
        )
        blocked_score = score_at(scores, blocked_action)
        recovery_score = score_at(scores, recovery_action)
        return {
            "mode": "late_recovery_filter",
            "min_seconds": self.min_seconds,
            "edge_distance": self.edge_distance,
            "thresholds": {
                "hazard": self.hazard_threshold,
                "boss": self.boss_threshold,
                "enemy": self.enemy_threshold,
                "low_health": self.low_health_threshold,
                "toward_dot": self.toward_dot_threshold,
            },
            "original_action": int(blocked_action),
            "target_action": int(recovery_action),
            "risk_reasons": list(original_reasons),
            "target_risk_reasons": list(target_reasons),
            "pressure_context": self.pressure_context(observation),
            "score_kind": action_scores.get("kind") if isinstance(action_scores, dict) else None,
            "original_action_score": blocked_score,
            "target_action_score": recovery_score,
            "score_margin": (
                round(float(recovery_score) - float(blocked_score), 6)
                if blocked_score is not None and recovery_score is not None
                else None
            ),
            "target_rank": (
                ranked_actions.index(recovery_action) + 1
                if recovery_action in ranked_actions
                else None
            ),
        }

    def consume_recovery_decision(self):
        decision = self._last_recovery_decision
        self._last_recovery_decision = None
        return decision

    def opening_policy_report(self):
        return opening_policy_report(self.policy)

    def policy_adapter_report(self):
        return {
            "mode": "late_recovery_filter",
            "min_seconds": self.min_seconds,
            "edge_distance": self.edge_distance,
            "hazard_threshold": self.hazard_threshold,
            "boss_threshold": self.boss_threshold,
            "enemy_threshold": self.enemy_threshold,
            "low_health_threshold": self.low_health_threshold,
            "toward_dot_threshold": self.toward_dot_threshold,
            "wrapped_policy_kind": getattr(self.policy, "policy_kind", "sb3"),
            "limitations": [
                "This deterministic wrapper is diagnostic repair evidence only.",
                "It produces late-window supervision samples and cannot be used as RL policy acceptance evidence.",
            ],
        }


def action_pushes_into_edge(action_index, diagnostics, edge_distance):
    movement = GYM_ACTION_MOVEMENTS.get(int(action_index), (0.0, 0.0))
    boundary = (diagnostics or {}).get("boundary") or {}
    left = as_float(boundary.get("left_distance"))
    right = as_float(boundary.get("right_distance"))
    bottom = as_float(boundary.get("bottom_distance"))
    top = as_float(boundary.get("top_distance"))
    dx, dy = movement
    return (
        (left is not None and left <= edge_distance and dx < 0.0)
        or (right is not None and right <= edge_distance and dx > 0.0)
        or (bottom is not None and bottom <= edge_distance and dy < 0.0)
        or (top is not None and top <= edge_distance and dy > 0.0)
    )


def score_at(scores, action_index):
    if not isinstance(scores, list):
        return None
    if 0 <= int(action_index) < len(scores):
        return round(float(scores[int(action_index)]), 6)
    return None


def as_float(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def clamp_float(value, minimum, maximum):
    return min(max(float(value), minimum), maximum)


def action_vector_alignment(action_index, vector):
    movement = GYM_ACTION_MOVEMENTS.get(int(action_index), (0.0, 0.0))
    vx, vy = vector or (0.0, 0.0)
    mx, my = movement
    movement_len = math.hypot(mx, my)
    vector_len = math.hypot(vx, vy)
    if movement_len <= 0.0 or vector_len <= 1e-6:
        return 0.0
    return (mx * vx + my * vy) / (movement_len * vector_len)


def action_moves_toward_vector(action_index, vector, threshold):
    return action_vector_alignment(action_index, vector) > float(threshold)


def observation_values_or_empty(observation):
    if observation is None:
        return []
    try:
        return observation_to_list(observation)
    except (TypeError, ValueError):
        return []


def observation_v2_nearest_hazard_vector(observation):
    values = observation_values_or_empty(observation)
    index = GYM_OBSERVATION_V2_NEAREST_HAZARD_START
    if len(values) <= index + 2:
        return (0.0, 0.0)
    if values[index + 2] <= 0.0:
        return (0.0, 0.0)
    return (float(values[index]), float(values[index + 1]))


def observation_v2_boss_vector(observation):
    values = observation_values_or_empty(observation)
    index = GYM_OBSERVATION_V2_BOSS_START
    if len(values) <= index + 2:
        return (0.0, 0.0)
    if values[index] <= 0.0:
        return (0.0, 0.0)
    return (float(values[index + 1]), float(values[index + 2]))


def diagnostics_enemy_vector(diagnostics):
    player = (diagnostics or {}).get("player_position") or {}
    enemy = ((diagnostics or {}).get("nearest_enemy") or {}).get("position") or {}
    player_x = as_float(player.get("x"))
    player_y = as_float(player.get("y"))
    enemy_x = as_float(enemy.get("x"))
    enemy_y = as_float(enemy.get("y"))
    if None in {player_x, player_y, enemy_x, enemy_y}:
        return (0.0, 0.0)
    return (enemy_x - player_x, enemy_y - player_y)


def wrap_edge_recovery_filter(policy, enabled=False, edge_distance=32.0):
    if not enabled:
        return policy
    return EdgeRecoveryFilterPolicy(policy, edge_distance=edge_distance)


def wrap_late_recovery_filter(
    policy,
    enabled=False,
    min_seconds=180.0,
    edge_distance=32.0,
    hazard_threshold=0.2,
    boss_threshold=0.05,
    enemy_threshold=0.05,
    low_health_threshold=0.25,
    toward_dot_threshold=0.15,
):
    if not enabled:
        return policy
    return LateRecoveryFilterPolicy(
        policy,
        min_seconds=min_seconds,
        edge_distance=edge_distance,
        hazard_threshold=hazard_threshold,
        boss_threshold=boss_threshold,
        enemy_threshold=enemy_threshold,
        low_health_threshold=low_health_threshold,
        toward_dot_threshold=toward_dot_threshold,
    )


def wrap_recovery_filter_for_eval(
    policy,
    *,
    edge_recovery_filter=False,
    edge_recovery_distance=32.0,
    late_recovery_filter=False,
    late_recovery_min_seconds=180.0,
    late_recovery_hazard_threshold=0.2,
    late_recovery_boss_threshold=0.05,
    late_recovery_enemy_threshold=0.05,
    late_recovery_low_health_threshold=0.25,
    late_recovery_toward_dot_threshold=0.15,
):
    if late_recovery_filter:
        return wrap_late_recovery_filter(
            policy,
            enabled=True,
            min_seconds=late_recovery_min_seconds,
            edge_distance=edge_recovery_distance,
            hazard_threshold=late_recovery_hazard_threshold,
            boss_threshold=late_recovery_boss_threshold,
            enemy_threshold=late_recovery_enemy_threshold,
            low_health_threshold=late_recovery_low_health_threshold,
            toward_dot_threshold=late_recovery_toward_dot_threshold,
        )
    return wrap_edge_recovery_filter(
        policy,
        enabled=edge_recovery_filter,
        edge_distance=edge_recovery_distance,
    )


def parse_map_list(value):
    if value is None:
        return None
    maps = [item.strip() for item in value.split(",") if item.strip()]
    if not maps:
        raise ValueError("map list must include at least one map id")
    return maps


def parse_seed_list(value):
    if value is None:
        return None
    seeds = []
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        try:
            seed = int(item)
        except ValueError as exc:
            raise ValueError(f"invalid seed `{item}`") from exc
        if seed < 0:
            raise ValueError("training seeds must be non-negative")
        seeds.append(seed)
    if not seeds:
        raise ValueError("seed list must include at least one seed")
    return seeds


def resolve_train_maps(train_maps, train_map_preset):
    parsed_maps = parse_map_list(train_maps)
    if parsed_maps is not None and train_map_preset is not None:
        raise ValueError("--train-maps and --train-map-preset cannot be used together")
    if train_map_preset is None:
        return parsed_maps, None
    try:
        return list(BASE_DEMO_MAP_PRESETS[train_map_preset]), train_map_preset
    except KeyError as exc:
        raise ValueError(f"unknown train map preset `{train_map_preset}`") from exc


def resolve_train_seed_values(train_seeds, train_seed_start, train_seed_count):
    parsed_seeds = parse_seed_list(train_seeds)
    has_range = train_seed_start is not None or train_seed_count is not None
    if parsed_seeds is not None and has_range:
        raise ValueError("--train-seeds cannot be combined with --train-seed-start/--train-seed-count")
    if parsed_seeds is not None:
        return parsed_seeds
    if not has_range:
        return None
    if train_seed_start is None or train_seed_count is None:
        raise ValueError("--train-seed-start and --train-seed-count must be used together")
    if train_seed_start < 0:
        raise ValueError("--train-seed-start must be non-negative")
    if train_seed_count <= 0:
        raise ValueError("--train-seed-count must be greater than 0")
    return [train_seed_start + offset for offset in range(train_seed_count)]


def validate_positive_seconds(value, flag_name):
    if value is None:
        return None
    if value <= 0.0:
        raise ValueError(f"{flag_name} must be greater than 0")
    return value


def validate_positive_int(value, flag_name):
    if value is None:
        return None
    if value <= 0:
        raise ValueError(f"{flag_name} must be greater than 0")
    return value


def validate_anchor_regularization_request(
    *,
    anchor_model=None,
    anchor_datasets=None,
    anchor_opening_seconds=60.0,
    anchor_regularization_weight=1.0,
    anchor_regularization_interval=2048,
    anchor_regularization_epochs=1,
    anchor_regularization_batch_size=256,
    anchor_regularization_learning_rate=None,
    anchor_limit_samples=None,
    anchor_sample_weighting="none",
    anchor_include_time_buckets=None,
    anchor_time_bucket_weights=None,
    anchor_validation_split=0.2,
):
    has_anchor_model = anchor_model is not None
    has_anchor_dataset = bool(anchor_datasets)
    if has_anchor_model != has_anchor_dataset:
        raise ValueError("--anchor-model and --anchor-dataset must be used together")
    if not has_anchor_model:
        return False
    validate_positive_seconds(anchor_opening_seconds, "--anchor-opening-seconds")
    validate_positive_int(
        anchor_regularization_interval,
        "--anchor-regularization-interval",
    )
    validate_positive_int(
        anchor_regularization_epochs,
        "--anchor-regularization-epochs",
    )
    validate_positive_int(
        anchor_regularization_batch_size,
        "--anchor-regularization-batch-size",
    )
    validate_positive_int(anchor_limit_samples, "--anchor-limit-samples")
    if anchor_regularization_weight <= 0.0:
        raise ValueError("--anchor-regularization-weight must be greater than 0")
    if (
        anchor_regularization_learning_rate is not None
        and anchor_regularization_learning_rate <= 0.0
    ):
        raise ValueError("--anchor-regularization-learning-rate must be greater than 0")
    if anchor_sample_weighting not in ANCHOR_SAMPLE_WEIGHTING_MODES:
        raise ValueError(
            "--anchor-sample-weighting must be one of "
            + ", ".join(sorted(ANCHOR_SAMPLE_WEIGHTING_MODES))
        )
    parse_anchor_time_bucket_list(anchor_include_time_buckets)
    parse_anchor_time_bucket_weights(anchor_time_bucket_weights)
    if not (0.0 < anchor_validation_split < 1.0):
        raise ValueError("--anchor-validation-split must be between 0 and 1")
    return True


def validate_anchor_validation_guard_thresholds(
    *,
    max_validation_kl=None,
    min_argmax_agreement=None,
):
    if max_validation_kl is not None and max_validation_kl < 0.0:
        raise ValueError("--anchor-guard-max-validation-kl must be non-negative")
    if min_argmax_agreement is not None and not (0.0 <= min_argmax_agreement <= 1.0):
        raise ValueError("--anchor-guard-min-argmax-agreement must be between 0 and 1")
    return max_validation_kl is not None or min_argmax_agreement is not None


def anchor_validation_guard_config(
    *,
    max_validation_kl=None,
    min_argmax_agreement=None,
):
    enabled = validate_anchor_validation_guard_thresholds(
        max_validation_kl=max_validation_kl,
        min_argmax_agreement=min_argmax_agreement,
    )
    return {
        "enabled": enabled,
        "max_validation_kl": max_validation_kl,
        "min_argmax_agreement": min_argmax_agreement,
        "limitations": [
            "This guard stops a PPO continuation when offline anchor validation drifts past the configured thresholds.",
            "It is an online anchor-drift guard only; it does not replace fixed-window no-regression reports or RL policy acceptance.",
        ],
    }


def evaluate_anchor_validation_guard(metrics, guard_config):
    if not guard_config.get("enabled"):
        return {
            "decision": "anchor_validation_guard_not_configured",
            "blockers": [],
            "metrics": metrics,
        }
    blockers = []
    max_kl = guard_config.get("max_validation_kl")
    mean_kl = metrics.get("mean_kl")
    if max_kl is not None and (mean_kl is None or mean_kl > max_kl):
        blockers.append(
            f"validation_mean_kl {mean_kl} exceeds max {max_kl}"
        )
    min_agreement = guard_config.get("min_argmax_agreement")
    argmax_agreement = metrics.get("argmax_agreement")
    if min_agreement is not None and (
        argmax_agreement is None or argmax_agreement < min_agreement
    ):
        blockers.append(
            f"validation_argmax_agreement {argmax_agreement} below min {min_agreement}"
        )
    return {
        "decision": (
            "anchor_validation_guard_failed"
            if blockers
            else "anchor_validation_guard_passed"
        ),
        "blockers": blockers,
        "metrics": metrics,
        "thresholds": {
            "max_validation_kl": max_kl,
            "min_argmax_agreement": min_agreement,
        },
    }


def build_env(
    config,
    seed=None,
    seconds=None,
    map_id=None,
    map_ids=None,
    map_selection="cycle",
    reward_profile="standard",
    upgrade_policy=None,
    seed_values=None,
    seed_selection="cycle",
):
    env_cfg = config["environment"]
    selected_map_id = map_id if map_id is not None else env_cfg.get("map_id", "frosting-grassland")
    return SoftCandyStormEnv(
        seed=seed if seed is not None else env_cfg["seed"],
        seconds=seconds if seconds is not None else env_cfg["seconds"],
        tick_rate=env_cfg["tick_rate"],
        map_id=selected_map_id,
        map_ids=map_ids,
        map_selection=map_selection,
        reward_profile=reward_profile,
        seed_values=seed_values,
        seed_selection=seed_selection,
        observation_version=env_cfg.get("observation_version", 2),
        content_dir=env_cfg["content_dir"],
        upgrade_policy=upgrade_policy,
    )


def dry_run(
    config,
    algorithm,
    steps,
    train_seconds=None,
    train_maps=None,
    train_map_selection="cycle",
    train_map_preset=None,
    reward_profile="standard",
    train_seed_values=None,
    train_seed_selection="cycle",
    upgrade_choice_model=None,
):
    requested_seconds = train_seconds or config["environment"]["seconds"]
    env = build_env(
        config,
        seconds=min(requested_seconds, 5.0),
        map_ids=train_maps,
        map_selection=train_map_selection,
        reward_profile=reward_profile,
        seed_values=train_seed_values,
        seed_selection=train_seed_selection,
    )
    total_reward = 0.0
    try:
        reset_seed = None if train_seed_values else config["environment"]["seed"]
        observation, info = env.reset(seed=reset_seed)
        assert len(observation) == config["environment"]["observation_len"]
        terminated = False
        truncated = False
        action = 3
        completed_steps = 0
        while not terminated and not truncated and completed_steps < steps:
            observation, reward, terminated, truncated, info = env.step(action)
            assert len(observation) == config["environment"]["observation_len"]
            total_reward += reward
            completed_steps += 1
        return {
            "status": "ok",
            "mode": "dry_run",
            "algorithm": algorithm,
            "steps": completed_steps,
            "terminated": terminated,
            "truncated": truncated,
            "seed": info["seed"],
            "map_id": info["map_id"],
            "time_seconds": info["time_seconds"],
            "observation_len": info["observation_len"],
            "action_count": info["action_count"],
            "requested_train_seconds": requested_seconds,
            "dry_run_seconds": env.seconds,
            "training_maps": train_maps
            or [config["environment"].get("map_id", "frosting-grassland")],
            "training_map_selection": train_map_selection if train_maps else "single",
            "training_map_preset": train_map_preset,
            "reward_profile": reward_profile,
            "upgrade_choice_model": str(upgrade_choice_model) if upgrade_choice_model else None,
            "training_seeds": train_seed_values,
            "training_seed_selection": train_seed_selection if train_seed_values else "single",
            "total_reward": round(total_reward, 4),
            "dependencies": dependency_status(),
        }
    finally:
        env.close()


def normalized_probability_scores(scores, action_count, np_module):
    if len(scores) < action_count:
        raise ValueError(
            f"anchor policy returned {len(scores)} scores for {action_count} actions"
        )
    probabilities = np_module.asarray(scores[:action_count], dtype=np_module.float32)
    probabilities = np_module.clip(probabilities, 0.0, 1.0)
    total = float(probabilities.sum())
    if total <= 0.0:
        raise ValueError("anchor policy returned an empty probability distribution")
    return probabilities / total


def collect_anchor_regularization_targets(dataset, anchor_policy, np_module):
    action_count = int(dataset["action_count"])
    observations = np_module.asarray(dataset["observations"], dtype=np_module.float32)
    targets = []
    anchor_argmax_actions = []
    dataset_argmax_matches = 0
    active_episode = None
    for observation, action, sample in zip(
        dataset["observations"],
        dataset["actions"],
        dataset["sample_metadata"],
    ):
        episode_key = (sample.get("path"), sample.get("seed"), sample.get("map_id"))
        if episode_key != active_episode:
            reset = getattr(anchor_policy, "reset", None)
            if callable(reset):
                reset()
            set_map_id = getattr(anchor_policy, "set_map_id", None)
            if callable(set_map_id):
                set_map_id(sample.get("map_id"))
            active_episode = episode_key
        set_step_context = getattr(anchor_policy, "set_step_context", None)
        if callable(set_step_context):
            set_step_context(
                {
                    "time_seconds": sample.get("time_seconds", 0.0),
                    "map_id": sample.get("map_id"),
                    "seed": sample.get("seed"),
                }
            )
        action_scores = policy_action_scores(anchor_policy, observation)
        if action_scores.get("kind") != "probability":
            raise ValueError("anchor policy must expose probability action_scores")
        probabilities = normalized_probability_scores(
            action_scores.get("scores", []),
            action_count,
            np_module,
        )
        targets.append(probabilities)
        anchor_action = int(probabilities.argmax())
        anchor_argmax_actions.append(anchor_action)
        if anchor_action == int(action):
            dataset_argmax_matches += 1

    return observations, np_module.asarray(targets, dtype=np_module.float32), {
        "anchor_argmax_agreement_with_dataset_actions": round(
            dataset_argmax_matches / max(1, len(dataset["actions"])),
            4,
        ),
        "anchor_argmax_distribution": {
            str(action): {
                "count": anchor_argmax_actions.count(action),
                "ratio": round(
                    anchor_argmax_actions.count(action)
                    / max(1, len(anchor_argmax_actions)),
                    4,
                ),
            }
            for action in range(action_count)
        },
    }


def anchor_time_bucket_label(time_seconds):
    value = float(time_seconds or 0.0)
    for label, start, end in ANCHOR_TIME_BUCKETS:
        if start <= value < end:
            return label
    return "unknown"


def parse_anchor_time_bucket_list(value):
    if value is None:
        return None
    if isinstance(value, str):
        labels = [item.strip() for item in value.split(",") if item.strip()]
    else:
        labels = [str(item).strip() for item in value if str(item).strip()]
    if not labels:
        raise ValueError("--anchor-include-time-buckets must include at least one bucket")
    unknown = sorted({label for label in labels if label not in ANCHOR_TIME_BUCKET_LABELS})
    if unknown:
        raise ValueError(
            "--anchor-include-time-buckets contains unknown bucket(s): "
            + ", ".join(unknown)
        )
    return list(dict.fromkeys(labels))


def parse_anchor_time_bucket_weights(value):
    if value is None or value == "":
        return {}
    if isinstance(value, dict):
        items = value.items()
    else:
        items = []
        for raw_item in str(value).split(","):
            item = raw_item.strip()
            if not item:
                continue
            if "=" not in item:
                raise ValueError(
                    "--anchor-time-bucket-weights entries must use bucket=weight"
                )
            label, raw_weight = item.split("=", 1)
            items.append((label.strip(), raw_weight.strip()))

    weights = {}
    for label, raw_weight in items:
        if label not in ANCHOR_TIME_BUCKET_LABELS:
            raise ValueError(
                f"--anchor-time-bucket-weights contains unknown bucket `{label}`"
            )
        try:
            weight = float(raw_weight)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"--anchor-time-bucket-weights has invalid weight for `{label}`"
            ) from exc
        if weight <= 0.0:
            raise ValueError(
                f"--anchor-time-bucket-weights for `{label}` must be greater than 0"
            )
        weights[label] = weight
    return weights


def time_bucket_counts(sample_metadata):
    counts = {label: 0 for label, _, _ in ANCHOR_TIME_BUCKETS}
    counts["unknown"] = 0
    for sample in sample_metadata:
        label = anchor_time_bucket_label(sample.get("time_seconds", 0.0))
        counts[label] = counts.get(label, 0) + 1
    return {label: count for label, count in counts.items() if count > 0}


def filter_anchor_dataset_by_time_buckets(dataset, include_time_buckets=None):
    labels = parse_anchor_time_bucket_list(include_time_buckets)
    sample_count = len(dataset["sample_metadata"])
    before_counts = time_bucket_counts(dataset["sample_metadata"])
    if labels is None:
        return dataset, {
            "mode": "all_samples",
            "include_time_buckets": None,
            "sample_count_before": int(sample_count),
            "sample_count_after": int(sample_count),
            "dropped_sample_count": 0,
            "bucket_counts_before": before_counts,
            "bucket_counts_after": before_counts,
        }

    keep_indices = [
        index
        for index, sample in enumerate(dataset["sample_metadata"])
        if anchor_time_bucket_label(sample.get("time_seconds", 0.0)) in labels
    ]
    filtered = dict(dataset)
    filtered["observations"] = [dataset["observations"][index] for index in keep_indices]
    filtered["actions"] = [dataset["actions"][index] for index in keep_indices]
    filtered["sample_metadata"] = [
        dataset["sample_metadata"][index] for index in keep_indices
    ]
    return filtered, {
        "mode": "include_time_buckets",
        "include_time_buckets": labels,
        "sample_count_before": int(sample_count),
        "sample_count_after": int(len(keep_indices)),
        "dropped_sample_count": int(sample_count - len(keep_indices)),
        "bucket_counts_before": before_counts,
        "bucket_counts_after": time_bucket_counts(filtered["sample_metadata"]),
    }


def apply_anchor_time_bucket_weight_multipliers(
    sample_metadata,
    np_module,
    weights,
    time_bucket_weights=None,
):
    parsed_weights = parse_anchor_time_bucket_weights(time_bucket_weights)
    if not parsed_weights:
        return weights, {
            "mode": "none",
            "weights": {},
            "matched_sample_counts": {},
        }
    matched_counts = {label: 0 for label in parsed_weights}
    multipliers = []
    for sample in sample_metadata:
        label = anchor_time_bucket_label(sample.get("time_seconds", 0.0))
        multiplier = parsed_weights.get(label, 1.0)
        if label in matched_counts:
            matched_counts[label] += 1
        multipliers.append(multiplier)
    adjusted = weights * np_module.asarray(multipliers, dtype=np_module.float32)
    return adjusted, {
        "mode": "custom_multipliers",
        "weights": {
            label: round(float(weight), 6)
            for label, weight in sorted(parsed_weights.items())
        },
        "matched_sample_counts": {
            label: int(count)
            for label, count in sorted(matched_counts.items())
        },
    }


def anchor_sample_weight_stats(weights):
    if len(weights) == 0:
        return {
            "min": None,
            "max": None,
            "mean": None,
        }
    return {
        "min": round(float(weights.min()), 6),
        "max": round(float(weights.max()), 6),
        "mean": round(float(weights.mean()), 6),
    }


def build_anchor_sample_weights(
    sample_metadata,
    np_module,
    mode="none",
    time_bucket_weights=None,
):
    if mode not in ANCHOR_SAMPLE_WEIGHTING_MODES:
        raise ValueError(
            "--anchor-sample-weighting must be one of "
            + ", ".join(sorted(ANCHOR_SAMPLE_WEIGHTING_MODES))
        )
    sample_count = len(sample_metadata)
    if sample_count == 0:
        weights = np_module.ones(0, dtype=np_module.float32)
        return weights, {
            "mode": mode,
            "sample_count": 0,
            "group_count": 0,
            "min": None,
            "max": None,
            "mean": None,
            "groups": {},
            "time_bucket_weights": {
                "mode": "none",
                "weights": {},
                "matched_sample_counts": {},
            },
        }
    if mode == "none":
        weights = np_module.ones(sample_count, dtype=np_module.float32)
        weights, time_bucket_weight_report = apply_anchor_time_bucket_weight_multipliers(
            sample_metadata,
            np_module,
            weights,
            time_bucket_weights,
        )
        stats = anchor_sample_weight_stats(weights)
        return weights, {
            "mode": "none",
            "sample_count": int(sample_count),
            "group_count": 0,
            **stats,
            "groups": {},
            "time_bucket_weights": time_bucket_weight_report,
        }

    keys = []
    counts = {}
    for sample in sample_metadata:
        bucket = anchor_time_bucket_label(sample.get("time_seconds", 0.0))
        if mode == "time_bucket_balance":
            key = bucket
        else:
            key = f"{sample.get('map_id') or 'unknown'}::{bucket}"
        keys.append(key)
        counts[key] = counts.get(key, 0) + 1

    group_count = max(1, len(counts))
    multipliers = {
        key: sample_count / (group_count * count)
        for key, count in counts.items()
    }
    weights = np_module.asarray(
        [multipliers[key] for key in keys],
        dtype=np_module.float32,
    )
    weights, time_bucket_weight_report = apply_anchor_time_bucket_weight_multipliers(
        sample_metadata,
        np_module,
        weights,
        time_bucket_weights,
    )
    stats = anchor_sample_weight_stats(weights)
    return weights, {
        "mode": mode,
        "sample_count": int(sample_count),
        "group_count": int(len(counts)),
        **stats,
        "groups": {
            key: {
                "sample_count": int(count),
                "sample_ratio": round(count / sample_count, 4),
                "weight_multiplier": round(float(multipliers[key]), 6),
            }
            for key, count in sorted(counts.items())
        },
        "time_bucket_weights": time_bucket_weight_report,
    }


def prepare_anchor_regularization(
    config,
    algorithm,
    *,
    anchor_model,
    anchor_datasets,
    anchor_opening_model=None,
    anchor_opening_seconds=60.0,
    anchor_regularization_weight=1.0,
    anchor_regularization_interval=2048,
    anchor_regularization_epochs=1,
    anchor_regularization_batch_size=256,
    anchor_regularization_learning_rate=None,
    anchor_limit_samples=None,
    anchor_sample_weighting="none",
    anchor_include_time_buckets=None,
    anchor_time_bucket_weights=None,
    anchor_validation_split=0.2,
    anchor_seed=12345,
    anchor_guard_max_validation_kl=None,
    anchor_guard_min_argmax_agreement=None,
):
    if not validate_anchor_regularization_request(
        anchor_model=anchor_model,
        anchor_datasets=anchor_datasets,
        anchor_opening_seconds=anchor_opening_seconds,
        anchor_regularization_weight=anchor_regularization_weight,
        anchor_regularization_interval=anchor_regularization_interval,
        anchor_regularization_epochs=anchor_regularization_epochs,
        anchor_regularization_batch_size=anchor_regularization_batch_size,
        anchor_regularization_learning_rate=anchor_regularization_learning_rate,
        anchor_limit_samples=anchor_limit_samples,
        anchor_sample_weighting=anchor_sample_weighting,
        anchor_include_time_buckets=anchor_include_time_buckets,
        anchor_time_bucket_weights=anchor_time_bucket_weights,
        anchor_validation_split=anchor_validation_split,
    ):
        return None
    if algorithm != "ppo":
        raise ValueError("anchor regularization is currently supported only for ppo")
    import numpy as np

    validation_guard = anchor_validation_guard_config(
        max_validation_kl=anchor_guard_max_validation_kl,
        min_argmax_agreement=anchor_guard_min_argmax_agreement,
    )
    dataset = load_trajectory_dataset(
        anchor_datasets,
        limit=anchor_limit_samples,
        include_anchor_drift_samples=True,
    )
    dataset, time_bucket_filter_report = filter_anchor_dataset_by_time_buckets(
        dataset,
        anchor_include_time_buckets,
    )
    if len(dataset["actions"]) < 2:
        raise ValueError("anchor regularization requires at least two samples")
    observations, targets, target_report = collect_anchor_regularization_targets(
        dataset,
        load_behavior_clone_policy_with_optional_opening(
            algorithm,
            Path(anchor_model),
            opening_model_path=(
                Path(anchor_opening_model) if anchor_opening_model else None
            ),
            opening_seconds=anchor_opening_seconds,
        ),
        np,
    )
    sample_weights, sample_weighting_report = build_anchor_sample_weights(
        dataset["sample_metadata"],
        np,
        anchor_sample_weighting,
        anchor_time_bucket_weights,
    )
    if observations.shape[1] != int(config["environment"]["observation_len"]):
        raise ValueError(
            "anchor dataset observation length does not match rl_training_config observation_len"
        )
    return {
        "observations": observations,
        "targets": targets,
        "sample_weights": sample_weights,
        "weight": float(anchor_regularization_weight),
        "interval_timesteps": int(anchor_regularization_interval),
        "epochs": int(anchor_regularization_epochs),
        "batch_size": int(anchor_regularization_batch_size),
        "learning_rate": anchor_regularization_learning_rate,
        "validation_split": float(anchor_validation_split),
        "seed": int(anchor_seed),
        "validation_guard": validation_guard,
        "report": {
            "mode": "behavior_clone_anchor_kl_regularization",
            "anchor_model": str(anchor_model),
            "anchor_opening_model": (
                str(anchor_opening_model) if anchor_opening_model else None
            ),
            "anchor_opening_seconds": (
                float(anchor_opening_seconds) if anchor_opening_model else None
            ),
            "datasets": [str(path) for path in anchor_datasets],
            "limit_samples": anchor_limit_samples,
            "dataset": summarize_dataset(dataset),
            "time_bucket_filter": time_bucket_filter_report,
            "target": target_report,
            "sample_weighting": sample_weighting_report,
            "regularization_weight": float(anchor_regularization_weight),
            "interval_timesteps": int(anchor_regularization_interval),
            "epochs_per_interval": int(anchor_regularization_epochs),
            "batch_size": int(anchor_regularization_batch_size),
            "learning_rate": anchor_regularization_learning_rate,
            "validation_split": float(anchor_validation_split),
            "seed": int(anchor_seed),
            "validation_guard": validation_guard,
            "limitations": [
                "Anchor regularization is repair training evidence only.",
                "It constrains closed-loop PPO drift on offline samples but does not replace high-pressure comparison, no-regression validation, or RL policy acceptance.",
            ],
        },
    }


def tensor_distribution_logits(model, observations, torch_module):
    distribution = model.policy.get_distribution(observations)
    torch_distribution = getattr(distribution, "distribution", None)
    logits = getattr(torch_distribution, "logits", None)
    if logits is None:
        probabilities = getattr(torch_distribution, "probs", None)
        if probabilities is None:
            raise ValueError("SB3 policy distribution does not expose logits or probs")
        logits = torch_module.log(probabilities.clamp_min(1e-8))
    return logits


def evaluate_anchor_regularization_batch(model, observations, targets, torch_module):
    model.policy.set_training_mode(False)
    with torch_module.no_grad():
        logits = tensor_distribution_logits(model, observations, torch_module)
        log_probs = torch_module.log_softmax(logits, dim=-1)
        probabilities = torch_module.softmax(logits, dim=-1)
        target_log_probs = torch_module.log(targets.clamp_min(1e-8))
        kl_loss = (targets * (target_log_probs - log_probs)).sum(dim=1).mean()
        cross_entropy = -(targets * log_probs).sum(dim=1).mean()
        argmax_agreement = (
            probabilities.argmax(dim=1) == targets.argmax(dim=1)
        ).float().mean()
        entropy = -(probabilities * log_probs).sum(dim=1).mean()
    model.policy.set_training_mode(True)
    return {
        "mean_kl": round(float(kl_loss.item()), 6),
        "cross_entropy": round(float(cross_entropy.item()), 6),
        "argmax_agreement": round(float(argmax_agreement.item()), 4),
        "policy_entropy_nats": round(float(entropy.item()), 6),
    }


def call_model_learn(model, total_timesteps, reset_num_timesteps=True):
    signature = inspect.signature(model.learn)
    if "reset_num_timesteps" in signature.parameters:
        return model.learn(
            total_timesteps=total_timesteps,
            reset_num_timesteps=reset_num_timesteps,
        )
    return model.learn(total_timesteps=total_timesteps)


def learn_model_with_anchor_regularization(model, total_timesteps, anchor_regularization):
    import numpy as np
    import torch
    from torch.utils.data import DataLoader, TensorDataset

    observations = anchor_regularization["observations"]
    targets = anchor_regularization["targets"]
    sample_weights = anchor_regularization.get("sample_weights")
    if sample_weights is None:
        sample_weights = np.ones(len(observations), dtype=np.float32)
    rng = np.random.default_rng(anchor_regularization["seed"])
    indices = np.arange(len(observations))
    rng.shuffle(indices)
    validation_count = int(round(len(indices) * anchor_regularization["validation_split"]))
    validation_count = min(max(validation_count, 1), max(1, len(indices) - 1))
    validation_indices = indices[:validation_count]
    train_indices = indices[validation_count:]
    train_dataset = TensorDataset(
        torch.from_numpy(observations[train_indices]),
        torch.from_numpy(targets[train_indices]),
        torch.from_numpy(sample_weights[train_indices]),
    )
    train_loader = DataLoader(
        train_dataset,
        batch_size=anchor_regularization["batch_size"],
        shuffle=True,
    )
    validation_x = torch.from_numpy(observations[validation_indices])
    validation_y = torch.from_numpy(targets[validation_indices])
    learning_rate = anchor_regularization["learning_rate"]
    if learning_rate is None:
        learning_rate = 0.0003
        lr_schedule = getattr(model, "lr_schedule", None)
        if callable(lr_schedule):
            try:
                learning_rate = float(lr_schedule(1.0))
            except (TypeError, ValueError):
                learning_rate = 0.0003
    optimizer = torch.optim.Adam(model.policy.parameters(), lr=float(learning_rate))

    remaining = int(total_timesteps)
    interval = int(anchor_regularization["interval_timesteps"])
    chunks = []
    reset_num_timesteps = True
    guard_failure = None
    validation_guard = anchor_regularization.get("validation_guard", {"enabled": False})
    while remaining > 0:
        chunk_timesteps = min(interval, remaining)
        call_model_learn(
            model,
            total_timesteps=chunk_timesteps,
            reset_num_timesteps=reset_num_timesteps,
        )
        reset_num_timesteps = False
        remaining -= chunk_timesteps
        interval_history = []
        for epoch in range(1, anchor_regularization["epochs"] + 1):
            model.policy.set_training_mode(True)
            total_loss = 0.0
            total_seen = 0
            total_correct = 0
            total_weighted_loss = 0.0
            for batch_x, batch_y, batch_weight in train_loader:
                logits = tensor_distribution_logits(model, batch_x, torch)
                log_probs = torch.log_softmax(logits, dim=-1)
                per_sample_kl = (
                    batch_y * (torch.log(batch_y.clamp_min(1e-8)) - log_probs)
                ).sum(dim=1)
                weighted_kl_loss = (per_sample_kl * batch_weight).mean()
                loss = weighted_kl_loss * anchor_regularization["weight"]
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                total_loss += float(per_sample_kl.sum().item())
                total_weighted_loss += float(weighted_kl_loss.item()) * len(batch_y)
                total_seen += len(batch_y)
                total_correct += int(
                    (logits.argmax(dim=1) == batch_y.argmax(dim=1)).sum().item()
                )
            validation_metrics = evaluate_anchor_regularization_batch(
                model,
                validation_x,
                validation_y,
                torch,
            )
            guard_report = evaluate_anchor_validation_guard(
                validation_metrics,
                validation_guard,
            )
            epoch_report = {
                "epoch": epoch,
                "train_mean_kl": round(total_loss / max(1, total_seen), 6),
                "weighted_train_mean_kl": round(
                    total_weighted_loss / max(1, total_seen),
                    6,
                ),
                "train_argmax_agreement": round(
                    total_correct / max(1, total_seen),
                    4,
                ),
                "validation_mean_kl": validation_metrics["mean_kl"],
                "validation_argmax_agreement": validation_metrics[
                    "argmax_agreement"
                ],
                "validation_policy_entropy_nats": validation_metrics[
                    "policy_entropy_nats"
                ],
                "validation_guard": guard_report,
            }
            interval_history.append(epoch_report)
            if guard_report["decision"] == "anchor_validation_guard_failed":
                guard_failure = {
                    **guard_report,
                    "chunk_timesteps": chunk_timesteps,
                    "epoch": epoch,
                    "remaining_timesteps": remaining,
                    "num_timesteps_after_chunk": int(
                        getattr(model, "num_timesteps", total_timesteps - remaining)
                    ),
                }
                break
        chunks.append(
            {
                "chunk_timesteps": chunk_timesteps,
                "remaining_timesteps": remaining,
                "num_timesteps_after_chunk": int(
                    getattr(model, "num_timesteps", total_timesteps - remaining)
                ),
                "regularization_epochs": interval_history,
            }
        )
        if guard_failure is not None:
            break

    final_metrics = evaluate_anchor_regularization_batch(
        model,
        validation_x,
        validation_y,
        torch,
    )
    final_guard = evaluate_anchor_validation_guard(final_metrics, validation_guard)
    return {
        **anchor_regularization["report"],
        "status": (
            "aborted_by_anchor_validation_guard"
            if guard_failure is not None
            else "applied"
        ),
        "guard_decision": (
            "anchor_validation_guard_failed"
            if guard_failure is not None
            else final_guard["decision"]
        ),
        "guard_failure": guard_failure,
        "train_samples": int(len(train_indices)),
        "validation_samples": int(len(validation_indices)),
        "effective_learning_rate": float(learning_rate),
        "chunks": chunks,
        "final_validation": final_metrics,
        "final_validation_guard": final_guard,
    }


def train(
    config,
    algorithm,
    total_timesteps=None,
    eval_episodes=None,
    eval_seconds=None,
    model_out=None,
    report_dir_out=None,
    train_seconds=None,
    train_maps=None,
    train_map_selection="cycle",
    train_map_preset=None,
    reward_profile="standard",
    train_seed_values=None,
    train_seed_selection="cycle",
    algorithm_overrides=None,
    eval_deterministic=True,
    eval_random_seed=None,
    eval_map_id=None,
    model_in=None,
    trace_dir=None,
    trace_failed_only=False,
    trace_sample_stride=30,
    trace_include_observation=False,
    edge_recovery_filter=False,
    edge_recovery_distance=32.0,
    edge_recovery_samples_out=None,
    late_recovery_filter=False,
    late_recovery_min_seconds=180.0,
    late_recovery_hazard_threshold=0.2,
    late_recovery_boss_threshold=0.05,
    late_recovery_enemy_threshold=0.05,
    late_recovery_low_health_threshold=0.25,
    late_recovery_toward_dot_threshold=0.15,
    upgrade_choice_model=None,
    anchor_model=None,
    anchor_datasets=None,
    anchor_opening_model=None,
    anchor_opening_seconds=60.0,
    anchor_regularization_weight=1.0,
    anchor_regularization_interval=2048,
    anchor_regularization_epochs=1,
    anchor_regularization_batch_size=256,
    anchor_regularization_learning_rate=None,
    anchor_limit_samples=None,
    anchor_sample_weighting="none",
    anchor_include_time_buckets=None,
    anchor_time_bucket_weights=None,
    anchor_validation_split=0.2,
    anchor_seed=12345,
    anchor_guard_max_validation_kl=None,
    anchor_guard_min_argmax_agreement=None,
):
    require_dependencies()
    # Imports stay inside the real training path so dry-run remains dependency-light.
    model_classes = stable_baselines_model_classes()

    selected = algorithm_config(config, algorithm)
    train_steps = total_timesteps or selected["total_timesteps"]
    effective_train_seconds = train_seconds or config["environment"]["seconds"]
    upgrade_policy = (
        load_upgrade_choice_policy(upgrade_choice_model) if upgrade_choice_model else None
    )
    env = build_env(
        config,
        seconds=effective_train_seconds,
        map_ids=train_maps,
        map_selection=train_map_selection,
        reward_profile=reward_profile,
        seed_values=train_seed_values,
        seed_selection=train_seed_selection,
        upgrade_policy=upgrade_policy,
    )
    model_dir = Path(config["outputs"]["model_dir"])
    report_dir = (
        Path(report_dir_out)
        if report_dir_out is not None
        else Path(config["outputs"]["report_dir"])
    )
    model_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    model_class = model_classes[algorithm]
    ignored_keys = {"enabled", "policy", "total_timesteps"}
    effective_config = {**selected, **(algorithm_overrides or {})}
    kwargs = {
        key: value for key, value in effective_config.items() if key not in ignored_keys
    }
    started_at = datetime.now(timezone.utc).isoformat()
    model_path = Path(model_out) if model_out is not None else default_model_path(config, algorithm)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    warm_start_model = Path(model_in) if model_in is not None else None
    if warm_start_model is not None and not warm_start_model.exists():
        raise ValueError(f"--model-in does not exist: {warm_start_model}")
    warm_start_metadata_path = None
    warm_start_metadata = None
    if warm_start_model is not None:
        warm_start_metadata_path, warm_start_metadata = load_model_metadata(warm_start_model)
    base_algorithm_parameters = (
        warm_start_metadata.get("algorithm_parameters", kwargs)
        if warm_start_metadata is not None
        else kwargs
    )
    algorithm_parameters = merge_algorithm_parameters(
        base_algorithm_parameters,
        algorithm_overrides,
    )
    algorithm_parameters_source = algorithm_parameters_source_label(
        warm_start_metadata,
        warm_start_model,
        algorithm_overrides,
    )
    anchor_regularization = prepare_anchor_regularization(
        config,
        algorithm,
        anchor_model=Path(anchor_model) if anchor_model is not None else None,
        anchor_datasets=anchor_datasets,
        anchor_opening_model=(
            Path(anchor_opening_model) if anchor_opening_model is not None else None
        ),
        anchor_opening_seconds=anchor_opening_seconds,
        anchor_regularization_weight=anchor_regularization_weight,
        anchor_regularization_interval=anchor_regularization_interval,
        anchor_regularization_epochs=anchor_regularization_epochs,
        anchor_regularization_batch_size=anchor_regularization_batch_size,
        anchor_regularization_learning_rate=anchor_regularization_learning_rate,
        anchor_limit_samples=anchor_limit_samples,
        anchor_sample_weighting=anchor_sample_weighting,
        anchor_include_time_buckets=anchor_include_time_buckets,
        anchor_time_bucket_weights=anchor_time_bucket_weights,
        anchor_validation_split=anchor_validation_split,
        anchor_seed=anchor_seed,
        anchor_guard_max_validation_kl=anchor_guard_max_validation_kl,
        anchor_guard_min_argmax_agreement=anchor_guard_min_argmax_agreement,
    )

    try:
        if warm_start_model is not None:
            model = model_class.load(warm_start_model, env=env)
            model.verbose = 1
            apply_loaded_model_overrides(model, algorithm_overrides)
        else:
            model = model_class(selected["policy"], env, verbose=1, **kwargs)
        if anchor_regularization is not None:
            anchor_regularization_report = learn_model_with_anchor_regularization(
                model,
                train_steps,
                anchor_regularization,
            )
        else:
            model.learn(total_timesteps=train_steps)
            anchor_regularization_report = None
        actual_timesteps = int(getattr(model, "num_timesteps", train_steps))
        completed_at = datetime.now(timezone.utc).isoformat()
        model.save(model_path)
    finally:
        env.close()

    evaluation_model = wrap_recovery_filter_for_eval(
        model,
        edge_recovery_filter=edge_recovery_filter,
        edge_recovery_distance=edge_recovery_distance,
        late_recovery_filter=late_recovery_filter,
        late_recovery_min_seconds=late_recovery_min_seconds,
        late_recovery_hazard_threshold=late_recovery_hazard_threshold,
        late_recovery_boss_threshold=late_recovery_boss_threshold,
        late_recovery_enemy_threshold=late_recovery_enemy_threshold,
        late_recovery_low_health_threshold=late_recovery_low_health_threshold,
        late_recovery_toward_dot_threshold=late_recovery_toward_dot_threshold,
    )
    evaluation = evaluate_model(
        evaluation_model,
        config,
        episodes=eval_episodes or config["evaluation"]["episodes"],
        seconds=eval_seconds or config["evaluation"]["seconds"],
        map_id=eval_map_id,
        deterministic=eval_deterministic,
        eval_random_seed=eval_random_seed,
        reward_profile=reward_profile,
        upgrade_policy=upgrade_policy,
        trace_dir=trace_dir,
        trace_failed_only=trace_failed_only,
        trace_sample_stride=trace_sample_stride,
        trace_include_observation=trace_include_observation,
        edge_recovery_samples_out=edge_recovery_samples_out,
    )
    known_exploit_notes = known_exploits_from_evaluation(evaluation)
    gate_decision = training_gate_decision(known_exploit_notes)
    if (
        anchor_regularization_report is not None
        and anchor_regularization_report.get("guard_decision")
        == "anchor_validation_guard_failed"
    ):
        gate_decision = "trained_anchor_validation_guard_failed_not_policy_gate"
    evaluation_path = report_dir / f"{algorithm}_evaluation_report.json"
    exploit_path = report_dir / f"{algorithm}_known_exploits.json"
    evaluation_path.write_text(
        json.dumps(evaluation, indent=2) + "\n", encoding="utf-8"
    )
    exploit_path.write_text(
        json.dumps(known_exploit_notes, indent=2) + "\n", encoding="utf-8"
    )

    metadata = {
        "model_version": 1,
        "algorithm": algorithm,
        "phase": config["phase"],
        "model_path": str(model_path),
        "config_file": "python/train/rl_training_config.json",
        "seed": config["environment"]["seed"],
        "content_dir": config["environment"]["content_dir"],
        "content_rules": "headless GameCore via game_harness gym-bridge",
        "reward_config": "prototype reward in game_harness gym_reward",
        "reward_profile": reward_profile,
        "upgrade_choice_model": str(upgrade_choice_model) if upgrade_choice_model else None,
        "warm_start_model": str(warm_start_model) if warm_start_model else None,
        "warm_start_metadata_path": (
            str(warm_start_metadata_path) if warm_start_metadata_path else None
        ),
        "observation_version": config["environment"].get("observation_version", 2),
        "observation_len": config["environment"]["observation_len"],
        "training_seconds": effective_train_seconds,
        "algorithm_parameters": algorithm_parameters,
        "algorithm_parameters_source": algorithm_parameters_source,
        "evaluation_policy": evaluation["action_selection"],
        "evaluation_action_random_seed": evaluation["action_random_seed"],
        "evaluation_map_id": evaluation["map_id"],
        "started_at": started_at,
        "completed_at": completed_at,
        "evaluation_path": str(evaluation_path),
        "known_exploits_path": str(exploit_path),
        "known_exploits": known_exploit_notes["known_exploits"],
        "training_maps": train_maps
        or [config["environment"].get("map_id", "frosting-grassland")],
        "training_map_selection": train_map_selection if train_maps else "single",
        "training_map_preset": train_map_preset,
        "training_seeds": train_seed_values,
        "training_seed_selection": train_seed_selection if train_seed_values else "single",
        "anchor_regularization": anchor_regularization_report,
    }
    metadata_path = metadata_path_for(config, algorithm, model_out=model_out)
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    report = {
        "status": "trained",
        "algorithm": algorithm,
        "model_path": str(model_path),
        "reward_profile": reward_profile,
        "metadata_path": str(metadata_path),
        "evaluation_path": str(evaluation_path),
        "known_exploits_path": str(exploit_path),
        "dependency_status": dependency_status(),
        "training": {
            "total_timesteps": actual_timesteps,
            "requested_timesteps": train_steps,
            "actual_timesteps": actual_timesteps,
            "seed": config["environment"]["seed"],
            "seconds": effective_train_seconds,
            "tick_rate": config["environment"]["tick_rate"],
            "content_dir": config["environment"]["content_dir"],
            "observation_version": config["environment"].get("observation_version", 2),
            "observation_len": config["environment"]["observation_len"],
            "maps": train_maps
            or [config["environment"].get("map_id", "frosting-grassland")],
            "map_selection": train_map_selection if train_maps else "single",
            "map_preset": train_map_preset,
            "reward_profile": reward_profile,
            "upgrade_choice_model": str(upgrade_choice_model) if upgrade_choice_model else None,
            "seeds": train_seed_values,
            "seed_selection": train_seed_selection if train_seed_values else "single",
            "started_at": started_at,
            "completed_at": completed_at,
            "algorithm_parameters": algorithm_parameters,
            "algorithm_parameters_source": algorithm_parameters_source,
            "warm_start_model": str(warm_start_model) if warm_start_model else None,
            "warm_start_metadata_path": (
                str(warm_start_metadata_path) if warm_start_metadata_path else None
            ),
            "evaluation_policy": evaluation["action_selection"],
            "evaluation_action_random_seed": evaluation["action_random_seed"],
            "evaluation_map_id": evaluation["map_id"],
            "anchor_regularization": anchor_regularization_report,
        },
        "evaluation": evaluation["summary"],
        "upgrade_policy": evaluation["upgrade_policy"],
        "anchor_regularization": anchor_regularization_report,
        "known_exploits": known_exploit_notes["known_exploits"],
        "limitations": known_exploit_notes["limitations"],
        "gate_decision": gate_decision,
    }
    report_path = report_dir / f"{algorithm}_training_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def stable_baselines_model_classes():
    require_dependencies()
    from stable_baselines3 import DQN, PPO

    return {"dqn": DQN, "ppo": PPO}


def default_model_path(config, algorithm):
    return Path(config["outputs"]["model_dir"]) / f"{algorithm}_phase1_movement_survival.zip"


def metadata_path_for(config, algorithm, model_out=None):
    if model_out is not None:
        model_path = Path(model_out)
        return model_path.with_name(f"{model_path.stem}_metadata.json")
    metadata_file = config["outputs"]["metadata_file"].format(algorithm=algorithm)
    return Path(config["outputs"]["model_dir"]) / metadata_file


def metadata_path_for_model(model_path):
    return model_path.with_name(f"{model_path.stem}_metadata.json")


def load_model_metadata(model_path):
    metadata_path = metadata_path_for_model(model_path)
    if not metadata_path.exists():
        return None, None
    return metadata_path, json.loads(metadata_path.read_text(encoding="utf-8"))


def evaluate_saved_policy(
    config,
    algorithm,
    model_path=None,
    opening_model_path=None,
    opening_seconds=60.0,
    eval_episodes=None,
    eval_seconds=None,
    seed_start=None,
    map_id=None,
    deterministic=True,
    eval_random_seed=None,
    reward_profile="standard",
    upgrade_choice_model=None,
    trace_dir=None,
    trace_failed_only=False,
    trace_sample_stride=30,
    trace_include_observation=False,
    edge_recovery_filter=False,
    edge_recovery_distance=32.0,
    edge_recovery_samples_out=None,
    late_recovery_filter=False,
    late_recovery_min_seconds=180.0,
    late_recovery_hazard_threshold=0.2,
    late_recovery_boss_threshold=0.05,
    late_recovery_enemy_threshold=0.05,
    late_recovery_low_health_threshold=0.25,
    late_recovery_toward_dot_threshold=0.15,
):
    model_class = stable_baselines_model_classes()[algorithm]
    fallback_model_path = model_path or default_model_path(config, algorithm)
    model = model_class.load(fallback_model_path)
    if opening_model_path is not None:
        opening_model = model_class.load(opening_model_path)
        model = StagedOpeningPolicy(
            opening_model,
            model,
            opening_seconds,
            opening_model_path,
            fallback_model_path,
        )
    model = wrap_recovery_filter_for_eval(
        model,
        edge_recovery_filter=edge_recovery_filter,
        edge_recovery_distance=edge_recovery_distance,
        late_recovery_filter=late_recovery_filter,
        late_recovery_min_seconds=late_recovery_min_seconds,
        late_recovery_hazard_threshold=late_recovery_hazard_threshold,
        late_recovery_boss_threshold=late_recovery_boss_threshold,
        late_recovery_enemy_threshold=late_recovery_enemy_threshold,
        late_recovery_low_health_threshold=late_recovery_low_health_threshold,
        late_recovery_toward_dot_threshold=late_recovery_toward_dot_threshold,
    )
    upgrade_policy = (
        load_upgrade_choice_policy(upgrade_choice_model) if upgrade_choice_model else None
    )
    return evaluate_model(
        model,
        config,
        episodes=eval_episodes or config["evaluation"]["episodes"],
        seconds=eval_seconds or config["evaluation"]["seconds"],
        seed_start=seed_start,
        map_id=map_id,
        deterministic=deterministic,
        eval_random_seed=eval_random_seed,
        reward_profile=reward_profile,
        upgrade_policy=upgrade_policy,
        trace_dir=trace_dir,
        trace_failed_only=trace_failed_only,
        trace_sample_stride=trace_sample_stride,
        trace_include_observation=trace_include_observation,
        edge_recovery_samples_out=edge_recovery_samples_out,
    )


def evaluate_policy_model(
    config,
    algorithm,
    model_path=None,
    opening_model_path=None,
    opening_seconds=60.0,
    behavior_clone_model=None,
    eval_episodes=None,
    eval_seconds=None,
    seed_start=None,
    map_id=None,
    deterministic=True,
    eval_random_seed=None,
    reward_profile="standard",
    upgrade_choice_model=None,
    trace_dir=None,
    trace_failed_only=False,
    trace_sample_stride=30,
    trace_include_observation=False,
    edge_recovery_filter=False,
    edge_recovery_distance=32.0,
    edge_recovery_samples_out=None,
    late_recovery_filter=False,
    late_recovery_min_seconds=180.0,
    late_recovery_hazard_threshold=0.2,
    late_recovery_boss_threshold=0.05,
    late_recovery_enemy_threshold=0.05,
    late_recovery_low_health_threshold=0.25,
    late_recovery_toward_dot_threshold=0.15,
):
    if behavior_clone_model is not None:
        upgrade_policy = (
            load_upgrade_choice_policy(upgrade_choice_model)
            if upgrade_choice_model
            else None
        )
        return evaluate_behavior_clone_policy(
            config,
            algorithm,
            behavior_clone_model,
            opening_model_path=opening_model_path,
            opening_seconds=opening_seconds,
            eval_episodes=eval_episodes,
            eval_seconds=eval_seconds,
            seed_start=seed_start,
            map_id=map_id,
            deterministic=deterministic,
            eval_random_seed=eval_random_seed,
            reward_profile=reward_profile,
            upgrade_policy=upgrade_policy,
            trace_dir=trace_dir,
            trace_failed_only=trace_failed_only,
            trace_sample_stride=trace_sample_stride,
            trace_include_observation=trace_include_observation,
            edge_recovery_filter=edge_recovery_filter,
            edge_recovery_distance=edge_recovery_distance,
            edge_recovery_samples_out=edge_recovery_samples_out,
            late_recovery_filter=late_recovery_filter,
            late_recovery_min_seconds=late_recovery_min_seconds,
            late_recovery_hazard_threshold=late_recovery_hazard_threshold,
            late_recovery_boss_threshold=late_recovery_boss_threshold,
            late_recovery_enemy_threshold=late_recovery_enemy_threshold,
            late_recovery_low_health_threshold=late_recovery_low_health_threshold,
            late_recovery_toward_dot_threshold=late_recovery_toward_dot_threshold,
        )
    return evaluate_saved_policy(
        config,
        algorithm,
        model_path=model_path,
        opening_model_path=opening_model_path,
        opening_seconds=opening_seconds,
        eval_episodes=eval_episodes,
        eval_seconds=eval_seconds,
        seed_start=seed_start,
        map_id=map_id,
        deterministic=deterministic,
        eval_random_seed=eval_random_seed,
        reward_profile=reward_profile,
        upgrade_choice_model=upgrade_choice_model,
        trace_dir=trace_dir,
        trace_failed_only=trace_failed_only,
        trace_sample_stride=trace_sample_stride,
        trace_include_observation=trace_include_observation,
        edge_recovery_filter=edge_recovery_filter,
        edge_recovery_distance=edge_recovery_distance,
        edge_recovery_samples_out=edge_recovery_samples_out,
        late_recovery_filter=late_recovery_filter,
        late_recovery_min_seconds=late_recovery_min_seconds,
        late_recovery_hazard_threshold=late_recovery_hazard_threshold,
        late_recovery_boss_threshold=late_recovery_boss_threshold,
        late_recovery_enemy_threshold=late_recovery_enemy_threshold,
        late_recovery_low_health_threshold=late_recovery_low_health_threshold,
        late_recovery_toward_dot_threshold=late_recovery_toward_dot_threshold,
    )


def evaluate_behavior_clone_policy(
    config,
    algorithm,
    model_path,
    opening_model_path=None,
    opening_seconds=60.0,
    eval_episodes=None,
    eval_seconds=None,
    seed_start=None,
    map_id=None,
    deterministic=True,
    eval_random_seed=None,
    reward_profile="standard",
    upgrade_policy=None,
    trace_dir=None,
    trace_failed_only=False,
    trace_sample_stride=30,
    trace_include_observation=False,
    edge_recovery_filter=False,
    edge_recovery_distance=32.0,
    edge_recovery_samples_out=None,
    late_recovery_filter=False,
    late_recovery_min_seconds=180.0,
    late_recovery_hazard_threshold=0.2,
    late_recovery_boss_threshold=0.05,
    late_recovery_enemy_threshold=0.05,
    late_recovery_low_health_threshold=0.25,
    late_recovery_toward_dot_threshold=0.15,
):
    model_path = Path(model_path)
    policy = load_behavior_clone_policy_with_optional_opening(
        algorithm,
        model_path,
        opening_model_path=opening_model_path,
        opening_seconds=opening_seconds,
    )
    policy = wrap_recovery_filter_for_eval(
        policy,
        edge_recovery_filter=edge_recovery_filter,
        edge_recovery_distance=edge_recovery_distance,
        late_recovery_filter=late_recovery_filter,
        late_recovery_min_seconds=late_recovery_min_seconds,
        late_recovery_hazard_threshold=late_recovery_hazard_threshold,
        late_recovery_boss_threshold=late_recovery_boss_threshold,
        late_recovery_enemy_threshold=late_recovery_enemy_threshold,
        late_recovery_low_health_threshold=late_recovery_low_health_threshold,
        late_recovery_toward_dot_threshold=late_recovery_toward_dot_threshold,
    )
    evaluation = evaluate_model(
        policy,
        config,
        episodes=eval_episodes or config["evaluation"]["episodes"],
        seconds=eval_seconds or config["evaluation"]["seconds"],
        seed_start=seed_start,
        map_id=map_id,
        deterministic=deterministic,
        eval_random_seed=eval_random_seed,
        reward_profile=reward_profile,
        upgrade_policy=upgrade_policy,
        trace_dir=trace_dir,
        trace_failed_only=trace_failed_only,
        trace_sample_stride=trace_sample_stride,
        trace_include_observation=trace_include_observation,
        edge_recovery_samples_out=edge_recovery_samples_out,
    )
    evaluation["policy_kind"] = (
        "staged_sb3_opening_behavior_clone"
        if opening_model_path is not None
        else "behavior_clone"
    )
    evaluation["algorithm"] = "behavior_clone"
    evaluation["model_path"] = str(model_path)
    evaluation["limitations"] = [
        "Behavior clone evaluation reuses the Gym bridge and action diagnostics, but it is still not a balance or fun gate.",
        "The clone still predicts movement actions only; an optional upgrade-choice ranker can fill upgrade prompts during evaluation.",
    ]
    if upgrade_policy is not None:
        evaluation["upgrade_policy_kind"] = "upgrade_choice_ranker"
        evaluation["upgrade_choice_model"] = upgrade_policy.checkpoint_path
    return evaluation


def load_behavior_clone_policy_with_optional_opening(
    algorithm,
    behavior_clone_model_path,
    opening_model_path=None,
    opening_seconds=60.0,
):
    fallback_policy = load_behavior_clone_policy(behavior_clone_model_path)
    if opening_model_path is None:
        return fallback_policy
    opening_model = stable_baselines_model_classes()[algorithm].load(opening_model_path)
    return StagedOpeningPolicy(
        opening_model,
        fallback_policy,
        opening_seconds,
        opening_model_path,
        behavior_clone_model_path,
    )


def evaluate_model(
    model,
    config,
    episodes,
    seconds,
    seed_start=None,
    map_id=None,
    deterministic=True,
    eval_random_seed=None,
    reward_profile="standard",
    upgrade_policy=None,
    trace_dir=None,
    trace_failed_only=False,
    trace_sample_stride=30,
    trace_include_observation=False,
    edge_recovery_filter=False,
    edge_recovery_distance=32.0,
    edge_recovery_samples_out=None,
    late_recovery_filter=False,
    late_recovery_min_seconds=180.0,
    late_recovery_hazard_threshold=0.2,
    late_recovery_boss_threshold=0.05,
    late_recovery_enemy_threshold=0.05,
    late_recovery_low_health_threshold=0.25,
    late_recovery_toward_dot_threshold=0.15,
):
    eval_random_seed = validate_eval_random_seed(eval_random_seed, deterministic)
    action_random_seed_report = seed_stochastic_action_sampling(
        eval_random_seed,
        model=model,
    )
    seed_start = seed_start if seed_start is not None else config["evaluation"]["seed_start"]
    map_id = map_id or config["environment"].get("map_id", "frosting-grassland")
    max_steps = int(seconds * config["environment"]["tick_rate"]) + 10
    episode_reports = []
    edge_recovery_samples = []
    total_reward = 0.0
    env = None
    try:
        env = build_env(
            config,
            seed=seed_start,
            seconds=seconds,
            map_id=map_id,
            reward_profile=reward_profile,
            upgrade_policy=upgrade_policy,
        )
        for index in range(episodes):
            seed = seed_start + index
            observation, info = env.reset(seed=seed, options={"seconds": seconds, "map_id": map_id})
            reset_policy = getattr(model, "reset", None)
            if callable(reset_policy):
                reset_policy()
            set_policy_map = getattr(model, "set_map_id", None)
            if callable(set_policy_map):
                set_policy_map(info.get("map_id", map_id))
            terminated = False
            truncated = False
            steps = 0
            episode_reward = 0.0
            action_counts = {str(action): 0 for action in range(info["action_count"])}
            action_score_tracker = new_action_score_tracker(info["action_count"])
            upgrade_policy_decisions = []
            reward_breakdown_totals = {}
            trace_steps = []
            while not terminated and not truncated and steps < max_steps:
                pre_step_info = info
                pre_step_observation = observation
                set_policy_context = getattr(model, "set_step_context", None)
                if callable(set_policy_context):
                    set_policy_context(pre_step_info)
                action, _state = model.predict(
                    pre_step_observation, deterministic=deterministic
                )
                action_index = action_to_int(action)
                adapter_decision = consume_policy_adapter_decision(model)
                action_scores = policy_action_scores(model, pre_step_observation)
                record_action_scores(
                    action_score_tracker,
                    action_scores,
                    action_index,
                )
                action_counts[str(action_index)] = action_counts.get(str(action_index), 0) + 1
                if adapter_decision is not None:
                    edge_recovery_samples.append(
                        build_edge_recovery_sample(
                            episode_seed=seed,
                            step_number=steps + 1,
                            observation=pre_step_observation,
                            info=pre_step_info,
                            adapter_decision=adapter_decision,
                            action_scores=action_scores,
                            config=config,
                        )
                    )
                observation, reward, terminated, truncated, info = env.step(action_index)
                step_number = steps + 1
                if "upgrade_policy_decision" in info:
                    upgrade_policy_decisions.append(info["upgrade_policy_decision"])
                for key, value in info.get("reward_breakdown", {}).items():
                    reward_breakdown_totals[key] = reward_breakdown_totals.get(
                        key, 0.0
                    ) + float(value)
                if should_record_trace_step(
                    trace_dir,
                    step_number,
                    terminated,
                    truncated,
                    trace_sample_stride,
                ):
                    trace_steps.append(
                        build_trace_step(
                            step_number,
                            action_index,
                            reward,
                            info,
                            action_scores,
                            observation=pre_step_observation,
                            observation_version=config["environment"].get(
                                "observation_version",
                                2,
                            ),
                            include_observation=trace_include_observation,
                        )
                    )
                episode_reward += reward
                steps += 1

            total_reward += episode_reward
            terminal = info.get("terminal") or {}
            episode_report = {
                "seed": seed,
                "map_id": info["map_id"],
                "steps": steps,
                "reward": round(episode_reward, 4),
                "terminated": terminated,
                "truncated": truncated,
                "time_seconds": info["time_seconds"],
                "terminal_kind": terminal.get("kind"),
                "terminal_reason": terminal.get("reason"),
                "level": info["level"],
                "kills": info["kills"],
                "xp_collected": info["xp_collected"],
                "damage_taken": info["damage_taken"],
                "action_counts": action_counts,
                "action_score_diagnostic": summarize_action_score_tracker(
                    action_score_tracker
                ),
                "upgrade_policy_decisions": upgrade_policy_decisions,
                "upgrade_policy_decision_count": len(upgrade_policy_decisions),
                "edge_recovery_sample_count": sum(
                    1
                    for sample in edge_recovery_samples
                    if sample.get("seed") == seed and sample.get("map_id") == info["map_id"]
                ),
                "reward_breakdown": round_reward_breakdown(reward_breakdown_totals),
            }
            trace_path = write_episode_trace(
                trace_dir,
                episode_report,
                trace_steps,
                failed_only=trace_failed_only,
            )
            if trace_path is not None:
                episode_report["trace_path"] = trace_path
            episode_reports.append(episode_report)
    finally:
        if env is not None:
            env.close()

    summary = summarize_evaluation(episode_reports, total_reward)
    quality_findings = policy_quality_findings(summary)
    edge_recovery_samples_report = write_edge_recovery_samples(
        edge_recovery_samples_out,
        edge_recovery_samples,
    )
    return {
        "report_version": 1,
        "status": "evaluated",
        "phase": config["phase"],
        "map_id": map_id,
        "reward_profile": reward_profile,
        "policy_kind": getattr(model, "policy_kind", "sb3"),
        "opening_policy": opening_policy_report(model),
        "policy_adapter": policy_adapter_report(model),
        "action_selection": "deterministic" if deterministic else "stochastic",
        "action_random_seed": eval_random_seed,
        "action_random_seed_report": action_random_seed_report,
        "upgrade_policy": upgrade_policy_report(upgrade_policy),
        "trace_dir": str(trace_dir) if trace_dir is not None else None,
        "trace_failed_only": bool(trace_failed_only) if trace_dir is not None else None,
        "trace_sample_stride": trace_sample_stride if trace_dir is not None else None,
        "trace_include_observation": (
            bool(trace_include_observation) if trace_dir is not None else None
        ),
        "edge_recovery_samples": edge_recovery_samples_report,
        "episodes": episode_reports,
        "summary": summary,
        "findings": quality_findings,
        "gate_decision": evaluation_gate_decision(quality_findings),
    }


def should_record_trace_step(trace_dir, step_number, terminated, truncated, sample_stride):
    if trace_dir is None:
        return False
    stride = max(1, int(sample_stride or 1))
    return step_number == 1 or step_number % stride == 0 or terminated or truncated


def build_trace_step(
    step_number,
    action_index,
    reward,
    info,
    action_scores,
    *,
    observation=None,
    observation_version=None,
    include_observation=False,
):
    step = {
        "step": step_number,
        "tick": info.get("tick"),
        "time_seconds": round(float(info.get("time_seconds", 0.0)), 4),
        "action": int(action_index),
        "reward": round(float(reward), 4),
        "health": round(float(info.get("health", 0.0)), 4),
        "level": info.get("level"),
        "kills": info.get("kills"),
        "xp_collected": round(float(info.get("xp_collected", 0.0)), 4),
        "damage_taken": round(float(info.get("damage_taken", 0.0)), 4),
        "upgrade_options": list(info.get("upgrade_options", [])),
        "events": list(info.get("events", [])),
        "terminal": info.get("terminal"),
        "reward_breakdown": round_reward_breakdown(info.get("reward_breakdown", {})),
        "action_score": compact_action_score(action_scores, action_index),
    }
    if info.get("diagnostics") is not None:
        step["diagnostics"] = info["diagnostics"]
    if include_observation:
        observation_values = observation_to_list(observation)
        step["observation_version"] = observation_version
        step["observation_len"] = len(observation_values)
        step["observation"] = observation_values
    return step


def compact_action_score(action_scores, chosen_action):
    if not action_scores or action_scores.get("kind") == "unavailable":
        return {
            "kind": "unavailable",
            "reason": (action_scores or {}).get("reason", "no action score payload"),
        }
    scores = action_scores.get("scores", [])
    if not scores:
        return {"kind": action_scores.get("kind"), "top_actions": []}
    top_actions = [
        {"action": str(index), "score": round(float(score), 4)}
        for index, score in sorted(
            enumerate(scores), key=lambda item: item[1], reverse=True
        )[:3]
    ]
    chosen_score = None
    if 0 <= chosen_action < len(scores):
        chosen_score = round(float(scores[chosen_action]), 4)
    return {
        "kind": action_scores.get("kind"),
        "chosen_action_score": chosen_score,
        "top_actions": top_actions,
    }


def write_episode_trace(trace_dir, episode_report, trace_steps, *, failed_only=False):
    if trace_dir is None:
        return None
    if failed_only and episode_report.get("terminal_kind") == "victory":
        return None
    target_dir = Path(trace_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    map_id = str(episode_report.get("map_id", "unknown")).replace("/", "_")
    seed = episode_report.get("seed", "unknown")
    target = target_dir / f"{map_id}_seed{seed}_trace.json"
    payload = {
        "record_type": "policy_episode_trace",
        "episode": episode_report,
        "sample_count": len(trace_steps),
        "steps": trace_steps,
        "limitations": [
            "Trace rows are sampled from policy evaluation info and do not include full GameCore snapshots.",
            "Use this for RL action/reward/health diagnostics, not as a Replay replacement.",
        ],
    }
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return str(target)


def observation_to_list(observation):
    if hasattr(observation, "tolist"):
        observation = observation.tolist()
    if isinstance(observation, tuple):
        observation = list(observation)
    if not isinstance(observation, list):
        return [float(observation)]
    return [float(value) for value in observation]


def build_edge_recovery_sample(
    *,
    episode_seed,
    step_number,
    observation,
    info,
    adapter_decision,
    action_scores,
    config,
):
    observation_values = observation_to_list(observation)
    score_payload = compact_full_action_scores(action_scores)
    mode = adapter_decision.get("mode")
    is_late_recovery = mode == "late_recovery_filter"
    record_type = (
        "risk_recovery_supervision_sample"
        if is_late_recovery
        else "edge_recovery_supervision_sample"
    )
    target_source = "late_recovery_filter" if is_late_recovery else "edge_recovery_filter"
    target_label = (
        "highest_scored_late_safe_action"
        if is_late_recovery
        else "highest_scored_non_wallward_action"
    )
    return {
        "record_type": record_type,
        "schema_version": 1,
        "sample_role": "repair_training_input",
        "target_source": target_source,
        "seed": episode_seed,
        "map_id": info.get("map_id"),
        "step": step_number,
        "tick": info.get("tick"),
        "time_seconds": round(float(info.get("time_seconds", 0.0)), 4),
        "observation_version": config["environment"].get("observation_version", 2),
        "observation_len": len(observation_values),
        "observation": observation_values,
        "original_action": adapter_decision["original_action"],
        "target_action": adapter_decision["target_action"],
        "target_label": target_label,
        "adapter_decision": adapter_decision,
        "action_scores": score_payload,
        "diagnostics": info.get("diagnostics", {}),
        "limitations": [
            "This sample is produced by a hand-written diagnostic adapter.",
            "It may be used for repair training or behavior constraints only.",
            "It is not RL policy acceptance evidence and does not replace deterministic high-pressure gates.",
        ],
    }


def compact_full_action_scores(action_scores):
    if not action_scores or action_scores.get("kind") == "unavailable":
        return {
            "kind": "unavailable",
            "reason": (action_scores or {}).get("reason", "no action score payload"),
        }
    scores = [round(float(score), 6) for score in action_scores.get("scores", [])]
    return {
        "kind": action_scores.get("kind"),
        "scores": scores,
        "top_actions": [
            {
                "action": str(index),
                "score": round(float(score), 6),
            }
            for index, score in sorted(
                enumerate(scores),
                key=lambda item: item[1],
                reverse=True,
            )[:3]
        ],
    }


def write_edge_recovery_samples(samples_path, samples):
    if samples_path is None:
        return None
    target = Path(samples_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        for sample in samples:
            handle.write(json.dumps(sample, ensure_ascii=False, sort_keys=True) + "\n")
    record_type_counts = {}
    for sample in samples:
        record_type = sample.get("record_type", "unknown")
        record_type_counts[record_type] = record_type_counts.get(record_type, 0) + 1
    return {
        "path": str(target),
        "sample_count": len(samples),
        "record_type": (
            next(iter(record_type_counts)) if len(record_type_counts) == 1 else "mixed"
        ),
        "record_type_counts": record_type_counts,
        "sample_role": "repair_training_input",
        "limitations": [
            "Samples are emitted only when a deterministic recovery filter changes an action.",
            "They are training/diagnostic material, not policy acceptance evidence.",
        ],
    }


def action_to_int(action):
    if hasattr(action, "item"):
        return int(action.item())
    if isinstance(action, (list, tuple)):
        return int(action[0])
    return int(action)


def new_action_score_tracker(action_count):
    return {
        "action_count": action_count,
        "kind": None,
        "sample_count": 0,
        "totals": [0.0 for _ in range(action_count)],
        "top_counts": [0 for _ in range(action_count)],
        "chosen_score_total": 0.0,
        "chosen_score_sample_count": 0,
        "unavailable_reason": None,
    }


def policy_action_scores(model, observation):
    custom_action_scores = getattr(model, "action_scores", None)
    if callable(custom_action_scores):
        try:
            return custom_action_scores(observation)
        except Exception as exc:
            return unavailable_action_scores(f"{type(exc).__name__}: {exc}")
    try:
        import torch

        policy = getattr(model, "policy", None)
        if policy is None or not hasattr(policy, "obs_to_tensor"):
            return unavailable_action_scores("model policy does not expose obs_to_tensor")
        obs_tensor, _vectorized = policy.obs_to_tensor(observation)
        with torch.no_grad():
            distribution_getter = getattr(policy, "get_distribution", None)
            if distribution_getter is not None:
                distribution = distribution_getter(obs_tensor)
                probabilities = distribution_probabilities(distribution, torch)
                if probabilities is not None:
                    return {
                        "kind": "probability",
                        "scores": tensor_first_row_values(probabilities),
                    }

            q_net = getattr(policy, "q_net", None)
            if q_net is not None:
                return {
                    "kind": "q_value",
                    "scores": tensor_first_row_values(q_net(obs_tensor)),
                }
    except Exception as exc:
        return unavailable_action_scores(f"{type(exc).__name__}: {exc}")
    return unavailable_action_scores("policy does not expose probabilities or q_values")


def distribution_probabilities(distribution, torch):
    torch_distribution = getattr(distribution, "distribution", None)
    if torch_distribution is None:
        return None
    probabilities = getattr(torch_distribution, "probs", None)
    if probabilities is not None:
        return probabilities
    logits = getattr(torch_distribution, "logits", None)
    if logits is not None:
        return torch.softmax(logits, dim=-1)
    return None


def tensor_first_row_values(tensor):
    values = tensor.detach().cpu()
    while len(values.shape) > 1:
        values = values[0]
    return [float(value) for value in values.tolist()]


def unavailable_action_scores(reason):
    return {
        "kind": "unavailable",
        "reason": reason,
    }


def record_action_scores(tracker, payload, chosen_action):
    if tracker.get("unavailable_reason"):
        return
    if payload is None or payload.get("kind") == "unavailable":
        tracker["unavailable_reason"] = (payload or {}).get(
            "reason", "policy action scores unavailable"
        )
        return

    kind = payload["kind"]
    scores = payload.get("scores", [])
    action_count = tracker["action_count"]
    if len(scores) < action_count:
        tracker["unavailable_reason"] = (
            f"policy returned {len(scores)} scores for {action_count} actions"
        )
        return
    if tracker["kind"] is None:
        tracker["kind"] = kind
    elif tracker["kind"] != kind:
        tracker["unavailable_reason"] = (
            f"mixed score kinds: {tracker['kind']} and {kind}"
        )
        return

    limited_scores = scores[:action_count]
    for index, score in enumerate(limited_scores):
        tracker["totals"][index] += float(score)
    top_action = max(range(action_count), key=lambda index: limited_scores[index])
    tracker["top_counts"][top_action] += 1
    if 0 <= chosen_action < action_count:
        tracker["chosen_score_total"] += float(limited_scores[chosen_action])
        tracker["chosen_score_sample_count"] += 1
    tracker["sample_count"] += 1


def summarize_action_score_tracker(tracker):
    sample_count = tracker["sample_count"]
    if sample_count <= 0:
        return {
            "kind": "unavailable",
            "sample_count": 0,
            "reason": tracker.get("unavailable_reason")
            or "no policy action score samples recorded",
        }

    mean_scores = {
        str(index): round(score_total / sample_count, 4)
        for index, score_total in enumerate(tracker["totals"])
    }
    top_action_distribution = {
        str(index): {
            "count": count,
            "ratio": round(count / sample_count, 4),
        }
        for index, count in enumerate(tracker["top_counts"])
    }
    chosen_count = tracker["chosen_score_sample_count"]
    return {
        "kind": tracker["kind"],
        "sample_count": sample_count,
        "mean_scores": mean_scores,
        "mean_top_actions": top_mean_scores(mean_scores),
        "top_action_distribution": top_action_distribution,
        "dominant_top_action": dominant_action(top_action_distribution),
        "mean_chosen_action_score": round(
            tracker["chosen_score_total"] / max(1, chosen_count), 4
        ),
        "chosen_action_score_sample_count": chosen_count,
    }


def top_mean_scores(mean_scores, limit=3):
    return [
        {
            "action": action,
            "score": score,
        }
        for action, score in sorted(
            mean_scores.items(), key=lambda item: item[1], reverse=True
        )[:limit]
    ]


def dominant_action(distribution):
    action, value = max(
        distribution.items(), key=lambda item: item[1]["ratio"], default=(None, None)
    )
    if action is None:
        return None
    return {
        "action": action,
        "count": value["count"],
        "ratio": value["ratio"],
    }


def summarize_evaluation(episodes, total_reward):
    count = max(1, len(episodes))
    wins = sum(1 for episode in episodes if episode["terminal_kind"] == "victory")
    summary = {
        "episodes": len(episodes),
        "win_rate": round(wins / count, 4),
        "average_survival_seconds": round(
            sum(episode["time_seconds"] for episode in episodes) / count, 4
        ),
        "average_level": round(sum(episode["level"] for episode in episodes) / count, 4),
        "average_kills": round(sum(episode["kills"] for episode in episodes) / count, 4),
        "average_reward": round(total_reward / count, 4),
        "damage_taken_average": round(
            sum(episode["damage_taken"] for episode in episodes) / count, 4
        ),
    }
    summary["action_distribution"] = summarize_action_distribution(episodes)
    summary["action_entropy_bits"] = action_entropy_bits(summary["action_distribution"])
    summary["normalized_action_entropy"] = normalized_action_entropy(
        summary["action_distribution"]
    )
    summary["action_score_diagnostic"] = summarize_action_score_diagnostics(episodes)
    summary["upgrade_policy_decision_count"] = sum(
        episode.get("upgrade_policy_decision_count", 0) for episode in episodes
    )
    summary["reward_breakdown_average"] = summarize_reward_breakdown(episodes)
    return summary


def upgrade_policy_report(upgrade_policy):
    if upgrade_policy is None:
        return {
            "mode": "bridge_default_first_option",
            "model_path": None,
        }
    return {
        "mode": "upgrade_choice_ranker",
        "model_path": getattr(upgrade_policy, "checkpoint_path", None),
        "limitations": [
            "The upgrade policy fills upgrade prompts only; movement actions still come from the evaluated policy.",
            "Using an upgrade ranker during evaluation is not an RL policy acceptance gate.",
        ],
    }


def opening_policy_report(model):
    report = getattr(model, "opening_policy_report", None)
    if callable(report):
        return report()
    return {
        "mode": "single_policy",
        "opening_model_path": None,
        "fallback_model_path": None,
        "opening_seconds": None,
    }


def policy_adapter_report(model):
    report = getattr(model, "policy_adapter_report", None)
    if callable(report):
        return report()
    return None


def consume_policy_adapter_decision(model):
    consume = getattr(model, "consume_recovery_decision", None)
    if callable(consume):
        return consume()
    return None


def round_reward_breakdown(values):
    return {key: round(value, 4) for key, value in sorted(values.items())}


def summarize_action_distribution(episodes):
    counts = {}
    for episode in episodes:
        for action, count in episode.get("action_counts", {}).items():
            counts[action] = counts.get(action, 0) + count
    total = max(1, sum(counts.values()))
    return {
        action: {
            "count": count,
            "ratio": round(count / total, 4),
        }
        for action, count in sorted(counts.items(), key=lambda item: int(item[0]))
    }


def action_entropy_bits(distribution):
    entropy = 0.0
    for value in distribution.values():
        ratio = value["ratio"]
        if ratio > 0.0:
            entropy -= ratio * math.log2(ratio)
    return round(entropy, 4)


def normalized_action_entropy(distribution):
    action_count = max(1, len(distribution))
    max_entropy = math.log2(action_count) if action_count > 1 else 1.0
    if max_entropy <= 0.0:
        return 0.0
    return round(action_entropy_bits(distribution) / max_entropy, 4)


def summarize_reward_breakdown(episodes):
    totals = {}
    count = max(1, len(episodes))
    for episode in episodes:
        for key, value in episode.get("reward_breakdown", {}).items():
            totals[key] = totals.get(key, 0.0) + value
    return {key: round(value / count, 4) for key, value in sorted(totals.items())}


def summarize_action_score_diagnostics(episodes):
    diagnostics = [
        episode.get("action_score_diagnostic", {})
        for episode in episodes
        if episode.get("action_score_diagnostic", {}).get("sample_count", 0) > 0
    ]
    if not diagnostics:
        reasons = [
            episode.get("action_score_diagnostic", {}).get("reason")
            for episode in episodes
            if episode.get("action_score_diagnostic", {}).get("reason")
        ]
        return {
            "kind": "unavailable",
            "sample_count": 0,
            "reason": reasons[0] if reasons else "no policy action score samples recorded",
        }

    kinds = sorted({diagnostic["kind"] for diagnostic in diagnostics})
    action_keys = sorted(
        {
            action
            for diagnostic in diagnostics
            for action in diagnostic.get("mean_scores", {})
        },
        key=int,
    )
    sample_count = sum(diagnostic["sample_count"] for diagnostic in diagnostics)
    score_totals = {action: 0.0 for action in action_keys}
    top_counts = {action: 0 for action in action_keys}
    chosen_score_total = 0.0
    chosen_score_count = 0
    for diagnostic in diagnostics:
        diagnostic_count = diagnostic["sample_count"]
        for action in action_keys:
            score_totals[action] += (
                diagnostic.get("mean_scores", {}).get(action, 0.0) * diagnostic_count
            )
            top_counts[action] += diagnostic.get("top_action_distribution", {}).get(
                action, {}
            ).get("count", 0)
        chosen_count = diagnostic.get("chosen_action_score_sample_count", 0)
        chosen_score_total += diagnostic.get("mean_chosen_action_score", 0.0) * chosen_count
        chosen_score_count += chosen_count

    mean_scores = {
        action: round(score_totals[action] / sample_count, 4)
        for action in action_keys
    }
    top_action_distribution = {
        action: {
            "count": count,
            "ratio": round(count / sample_count, 4),
        }
        for action, count in top_counts.items()
    }
    return {
        "kind": kinds[0] if len(kinds) == 1 else "mixed",
        "sample_count": sample_count,
        "mean_scores": mean_scores,
        "mean_top_actions": top_mean_scores(mean_scores),
        "top_action_distribution": top_action_distribution,
        "dominant_top_action": dominant_action(top_action_distribution),
        "mean_chosen_action_score": round(
            chosen_score_total / max(1, chosen_score_count), 4
        ),
        "chosen_action_score_sample_count": chosen_score_count,
    }


def parse_rule_bots(value):
    bots = [bot.strip() for bot in value.split(",") if bot.strip()]
    if not bots:
        raise ValueError("--rule-bots must include at least one bot")
    return bots


def run_rule_bot_matrix(config, bots, seed_start, seeds, seconds, map_id):
    env_cfg = config["environment"]
    command = [
        "cargo",
        "run",
        "-q",
        "-p",
        "game_harness",
        "--",
        "matrix",
        "--seed-start",
        str(seed_start),
        "--seeds",
        str(seeds),
        "--seconds",
        str(seconds),
        "--tick-rate",
        str(env_cfg["tick_rate"]),
        "--map-id",
        map_id,
        "--bots",
        ",".join(bots),
        "--content-dir",
        env_cfg["content_dir"],
    ]
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return {
        "command": command,
        "stdout": json.loads(completed.stdout),
        "stderr": completed.stderr.strip(),
    }


def derived_edge_recovery_samples_path(samples_out, map_id):
    if samples_out is None:
        return None
    base = Path(samples_out)
    safe_map_id = str(map_id).replace("/", "_")
    if base.suffix:
        return base.with_name(f"{base.stem}_{safe_map_id}{base.suffix}")
    return base / f"{safe_map_id}_edge_recovery_samples.jsonl"


def compare_policy_to_rule_bots(
    config,
    algorithm,
    model_path=None,
    opening_model_path=None,
    opening_seconds=60.0,
    behavior_clone_model=None,
    eval_episodes=None,
    eval_seconds=None,
    seed_start=None,
    map_id=None,
    rule_bots=None,
    deterministic=True,
    eval_random_seed=None,
    reward_profile="standard",
    upgrade_choice_model=None,
    trace_dir=None,
    trace_failed_only=False,
    trace_sample_stride=30,
    trace_include_observation=False,
    edge_recovery_filter=False,
    edge_recovery_distance=32.0,
    edge_recovery_samples_out=None,
    late_recovery_filter=False,
    late_recovery_min_seconds=180.0,
    late_recovery_hazard_threshold=0.2,
    late_recovery_boss_threshold=0.05,
    late_recovery_enemy_threshold=0.05,
    late_recovery_low_health_threshold=0.25,
    late_recovery_toward_dot_threshold=0.15,
):
    episodes = eval_episodes or config["evaluation"]["episodes"]
    seconds = eval_seconds or config["evaluation"]["seconds"]
    seed_start = seed_start if seed_start is not None else config["evaluation"]["seed_start"]
    map_id = map_id or config["environment"].get("map_id", "frosting-grassland")
    bots = rule_bots or ["random", "kite", "tank"]
    policy = evaluate_policy_model(
        config,
        algorithm,
        model_path=model_path,
        opening_model_path=opening_model_path,
        opening_seconds=opening_seconds,
        behavior_clone_model=behavior_clone_model,
        eval_episodes=episodes,
        eval_seconds=seconds,
        seed_start=seed_start,
        map_id=map_id,
        deterministic=deterministic,
        eval_random_seed=eval_random_seed,
        reward_profile=reward_profile,
        upgrade_choice_model=upgrade_choice_model,
        trace_dir=trace_dir,
        trace_failed_only=trace_failed_only,
        trace_sample_stride=trace_sample_stride,
        trace_include_observation=trace_include_observation,
        edge_recovery_filter=edge_recovery_filter,
        edge_recovery_distance=edge_recovery_distance,
        edge_recovery_samples_out=edge_recovery_samples_out,
        late_recovery_filter=late_recovery_filter,
        late_recovery_min_seconds=late_recovery_min_seconds,
        late_recovery_hazard_threshold=late_recovery_hazard_threshold,
        late_recovery_boss_threshold=late_recovery_boss_threshold,
        late_recovery_enemy_threshold=late_recovery_enemy_threshold,
        late_recovery_low_health_threshold=late_recovery_low_health_threshold,
        late_recovery_toward_dot_threshold=late_recovery_toward_dot_threshold,
    )
    rule_matrix = run_rule_bot_matrix(config, bots, seed_start, episodes, seconds, map_id)
    findings = comparison_findings(policy, rule_matrix["stdout"])
    return {
        "report_version": 1,
        "status": "compared",
        "phase": config["phase"],
        "algorithm": policy_algorithm_label(algorithm, behavior_clone_model),
        "model_path": policy_model_path(
            config,
            algorithm,
            model_path,
            behavior_clone_model,
        ),
        "policy_kind": policy.get("policy_kind", "sb3"),
        "opening_policy": policy.get("opening_policy"),
        "policy_adapter": policy.get("policy_adapter"),
        "edge_recovery_samples": policy.get("edge_recovery_samples"),
        "upgrade_policy": policy.get("upgrade_policy"),
        "upgrade_choice_model": str(upgrade_choice_model) if upgrade_choice_model else None,
        "map_id": map_id,
        "action_selection": policy["action_selection"],
        "action_random_seed": policy.get("action_random_seed"),
        "reward_profile": reward_profile,
        "seed_start": seed_start,
        "seeds": episodes,
        "seconds": seconds,
        "tick_rate": config["environment"]["tick_rate"],
        "policy": policy,
        "rule_bots": rule_matrix["stdout"],
        "rule_bot_command": rule_matrix["command"],
        "rule_bot_stderr": rule_matrix["stderr"],
        "findings": findings,
        "limitations": [
            "This comparison uses the same seed/map/duration, but a smoke-scale policy is not a balance or fun gate.",
            "Rule Bot baselines remain the primary deterministic content gate until RL policies are trained and calibrated at larger scale.",
        ],
        "gate_decision": comparison_gate_decision(findings),
    }


def compare_policy_to_rule_bots_across_maps(
    config,
    algorithm,
    map_ids,
    model_path=None,
    opening_model_path=None,
    opening_seconds=60.0,
    behavior_clone_model=None,
    eval_episodes=None,
    eval_seconds=None,
    seed_start=None,
    rule_bots=None,
    deterministic=True,
    eval_random_seed=None,
    reward_profile="standard",
    map_preset=None,
    upgrade_choice_model=None,
    trace_dir=None,
    trace_failed_only=False,
    trace_sample_stride=30,
    trace_include_observation=False,
    edge_recovery_filter=False,
    edge_recovery_distance=32.0,
    edge_recovery_samples_out=None,
    late_recovery_filter=False,
    late_recovery_min_seconds=180.0,
    late_recovery_hazard_threshold=0.2,
    late_recovery_boss_threshold=0.05,
    late_recovery_enemy_threshold=0.05,
    late_recovery_low_health_threshold=0.25,
    late_recovery_toward_dot_threshold=0.15,
):
    comparisons = [
        compare_policy_to_rule_bots(
            config,
            algorithm,
            model_path=model_path,
            opening_model_path=opening_model_path,
            opening_seconds=opening_seconds,
            behavior_clone_model=behavior_clone_model,
            eval_episodes=eval_episodes,
            eval_seconds=eval_seconds,
            seed_start=seed_start,
            map_id=map_id,
            rule_bots=rule_bots,
            deterministic=deterministic,
            eval_random_seed=eval_random_seed,
            reward_profile=reward_profile,
            upgrade_choice_model=upgrade_choice_model,
            trace_dir=trace_dir,
            trace_failed_only=trace_failed_only,
            trace_sample_stride=trace_sample_stride,
            trace_include_observation=trace_include_observation,
            edge_recovery_filter=edge_recovery_filter,
            edge_recovery_distance=edge_recovery_distance,
            edge_recovery_samples_out=derived_edge_recovery_samples_path(
                edge_recovery_samples_out,
                map_id,
            ),
            late_recovery_filter=late_recovery_filter,
            late_recovery_min_seconds=late_recovery_min_seconds,
            late_recovery_hazard_threshold=late_recovery_hazard_threshold,
            late_recovery_boss_threshold=late_recovery_boss_threshold,
            late_recovery_enemy_threshold=late_recovery_enemy_threshold,
            late_recovery_low_health_threshold=late_recovery_low_health_threshold,
            late_recovery_toward_dot_threshold=late_recovery_toward_dot_threshold,
        )
        for map_id in map_ids
    ]
    findings = multimap_comparison_findings(comparisons)
    return {
        "report_version": 1,
        "status": "compared",
        "phase": config["phase"],
        "algorithm": policy_algorithm_label(algorithm, behavior_clone_model),
        "model_path": policy_model_path(
            config,
            algorithm,
            model_path,
            behavior_clone_model,
        ),
        "policy_kind": comparisons[0].get("policy_kind") if comparisons else None,
        "opening_policy": comparisons[0].get("opening_policy") if comparisons else None,
        "policy_adapter": comparisons[0].get("policy_adapter") if comparisons else None,
        "edge_recovery_samples": [
            comparison.get("edge_recovery_samples")
            for comparison in comparisons
            if comparison.get("edge_recovery_samples") is not None
        ],
        "upgrade_policy": comparisons[0].get("upgrade_policy") if comparisons else None,
        "upgrade_choice_model": str(upgrade_choice_model) if upgrade_choice_model else None,
        "action_selection": comparisons[0]["action_selection"] if comparisons else None,
        "action_random_seed": (
            comparisons[0].get("action_random_seed") if comparisons else eval_random_seed
        ),
        "reward_profile": reward_profile,
        "map_preset": map_preset,
        "map_ids": map_ids,
        "seed_start": comparisons[0]["seed_start"] if comparisons else seed_start,
        "seeds": comparisons[0]["seeds"] if comparisons else eval_episodes,
        "seconds": comparisons[0]["seconds"] if comparisons else eval_seconds,
        "tick_rate": config["environment"]["tick_rate"],
        "maps": comparisons,
        "summary": summarize_multimap_comparison(comparisons),
        "findings": findings,
        "limitations": [
            "This multi-map comparison records policy behavior against rule Bot baselines; it is not a balance or fun gate.",
            "A policy can pass action distribution checks and still fail high-pressure maps, so human review and rule Bot gates remain required.",
        ],
        "gate_decision": multimap_comparison_gate_decision(findings),
    }


def policy_algorithm_label(algorithm, behavior_clone_model=None):
    if behavior_clone_model is not None:
        return "behavior_clone"
    return algorithm


def policy_model_path(config, algorithm, model_path=None, behavior_clone_model=None):
    if behavior_clone_model is not None:
        return str(behavior_clone_model)
    return str(model_path or default_model_path(config, algorithm))


def summarize_multimap_comparison(comparisons):
    rows = []
    for report in comparisons:
        summary = report["policy"]["summary"]
        dominant = dominant_action(summary.get("action_distribution", {}))
        rule_win_rates = {
            bot["bot"]: bot["win_rate"]
            for bot in report.get("rule_bots", {}).get("bots", [])
        }
        rows.append(
            {
                "map_id": report["map_id"],
                "policy_win_rate": summary["win_rate"],
                "policy_average_survival_seconds": summary[
                    "average_survival_seconds"
                ],
                "policy_damage_taken_average": summary["damage_taken_average"],
                "policy_average_kills": summary["average_kills"],
                "policy_dominant_action": dominant,
                "policy_normalized_action_entropy": summary.get(
                    "normalized_action_entropy"
                ),
                "rule_bot_win_rates": rule_win_rates,
                "best_rule_bot_win_rate": max(rule_win_rates.values(), default=None),
                "inner_gate_decision": report["gate_decision"],
            }
        )
    count = max(1, len(rows))
    return {
        "maps": rows,
        "map_count": len(rows),
        "minimum_policy_win_rate": min(
            (row["policy_win_rate"] for row in rows),
            default=None,
        ),
        "average_policy_win_rate": round(
            sum(row["policy_win_rate"] for row in rows) / count,
            4,
        ),
        "average_policy_survival_seconds": round(
            sum(row["policy_average_survival_seconds"] for row in rows) / count,
            4,
        ),
        "repair_maps": [
            row["map_id"]
            for row in rows
            if row["inner_gate_decision"] != "comparison_recorded_not_balance_gate"
            or row["policy_win_rate"] <= 0.0
        ],
    }


def multimap_comparison_findings(comparisons):
    findings = []
    for report in comparisons:
        summary = report["policy"]["summary"]
        if report["gate_decision"] != "comparison_recorded_not_balance_gate":
            findings.append(
                {
                    "id": "map_action_distribution_repair",
                    "severity": "repair",
                    "map_id": report["map_id"],
                    "summary": "Policy action distribution failed the per-map comparison gate.",
                }
            )
        if summary["win_rate"] <= 0.0:
            findings.append(
                {
                    "id": "zero_policy_win_rate",
                    "severity": "repair",
                    "map_id": report["map_id"],
                    "summary": "Policy recorded 0% win rate on this map and should not be promoted as a multi-map RL test Bot.",
                }
            )
            continue
        rule_bots = report.get("rule_bots", {}).get("bots", [])
        best_rule_win_rate = max(
            (bot["win_rate"] for bot in rule_bots),
            default=0.0,
        )
        if best_rule_win_rate >= 0.5 and summary["win_rate"] < best_rule_win_rate * 0.5:
            findings.append(
                {
                    "id": "policy_underperforms_rule_bots",
                    "severity": "watch",
                    "map_id": report["map_id"],
                    "summary": "Policy win rate is less than half of the strongest compared rule Bot on this map.",
                }
            )
    return findings


def multimap_comparison_gate_decision(findings):
    if any(finding["severity"] == "repair" for finding in findings):
        return "multimap_comparison_recorded_needs_policy_repair"
    if any(finding["severity"] == "watch" for finding in findings):
        return "multimap_comparison_recorded_watch"
    return "multimap_comparison_recorded_not_balance_gate"


def comparison_findings(policy, rule_matrix):
    findings = []
    summary = policy["summary"]
    if summary["episodes"] < 10:
        findings.append(
            {
                "id": "small_sample",
                "severity": "info",
                "summary": "Comparison uses fewer than 10 seeds and should only be treated as a smoke check.",
            }
        )
    if summary["average_kills"] <= 1.0 and summary["win_rate"] >= 1.0:
        findings.append(
            {
                "id": "possible_passive_survival_policy",
                "severity": "watch",
                "summary": "Policy can finish the short evaluation with very low kills; inspect whether reward design overvalues passive survival.",
            }
        )
    findings.extend(policy_quality_findings(summary))
    rule_bots = rule_matrix.get("bots", [])
    if rule_bots:
        best_rule_kills = max(bot["average_kills"] for bot in rule_bots)
        if summary["average_kills"] < best_rule_kills * 0.5:
            findings.append(
                {
                    "id": "low_kill_output_vs_rule_bots",
                    "severity": "watch",
                    "summary": "Policy average kills are less than half of the strongest compared rule Bot in the same smoke window.",
                }
            )
    return findings


def policy_quality_findings(summary):
    findings = []
    distribution = summary.get("action_distribution", {})
    dominant = max(distribution.items(), key=lambda item: item[1]["ratio"], default=None)
    if dominant is not None and dominant[1]["ratio"] >= 0.75:
        findings.append(
            {
                "id": "dominant_action_bias",
                "severity": "repair",
                "summary": f"Action {dominant[0]} accounts for {dominant[1]['ratio']:.2%} of policy steps in this smoke.",
            }
        )
    if summary.get("normalized_action_entropy", 1.0) <= 0.25:
        findings.append(
            {
                "id": "low_action_entropy",
                "severity": "repair",
                "summary": "Policy action entropy is very low; inspect exploration, reward shaping, and training duration.",
            }
        )
    terminal_ratio = terminal_reward_ratio(summary)
    if terminal_ratio >= 0.75:
        findings.append(
            {
                "id": "terminal_reward_dominance",
                "severity": "watch",
                "summary": f"Terminal reward contributes {terminal_ratio:.2%} of absolute reward components in this evaluation.",
            }
        )
    return findings


def evaluation_gate_decision(findings):
    if any(finding["severity"] == "repair" for finding in findings):
        return "evaluation_recorded_needs_action_bias_repair"
    if any(finding["severity"] == "watch" for finding in findings):
        return "evaluation_recorded_watch"
    return "evaluation_recorded_not_policy_gate"


def terminal_reward_ratio(summary):
    breakdown = summary.get("reward_breakdown_average", {})
    denominator = sum(
        abs(float(value))
        for key, value in breakdown.items()
        if key != "total" and isinstance(value, (int, float))
    )
    if denominator <= 0.0:
        return 0.0
    return abs(float(breakdown.get("terminal", 0.0))) / denominator


def comparison_gate_decision(findings):
    if any(finding["severity"] == "repair" for finding in findings):
        return "comparison_recorded_needs_action_bias_repair"
    return "comparison_recorded_not_balance_gate"


def known_exploits_from_evaluation(evaluation):
    summary = evaluation["summary"]
    known_exploits = policy_quality_findings(summary)
    limitations = [
        "Short RL smoke proves the SB3 training/evaluation path only; it is not a fun or balance gate.",
        "Compare against rule Bot matrix before using an RL policy to judge new content.",
    ]
    if summary["win_rate"] >= 1.0 and summary["average_kills"] <= 1.0:
        known_exploits.append(
            {
                "id": "possible_passive_survival_policy",
                "summary": "Policy can finish the short evaluation with almost no kills; inspect whether the reward overvalues passive survival.",
                "severity": "watch",
            }
        )
    return {
        "report_version": 1,
        "known_exploits": known_exploits,
        "limitations": limitations,
    }


def training_gate_decision(known_exploit_notes):
    if any(
        finding["severity"] == "repair"
        for finding in known_exploit_notes["known_exploits"]
    ):
        return "trained_needs_action_bias_repair"
    return "trained_needs_rule_bot_comparison"


def write_report(path, payload):
    if path is None:
        print(json.dumps(payload, ensure_ascii=False))
        return
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def copy_template(target):
    template = Path("python/train/rl_training_report_template.json")
    destination = Path(target)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(template, destination)
    return {"status": "ok", "copied_template": str(destination)}


def main():
    parser = argparse.ArgumentParser(description="Train or validate Soft Candy Storm SB3 configs.")
    parser.add_argument("--config", default="python/train/rl_training_config.json")
    parser.add_argument("--algorithm", choices=["dqn", "ppo"], default="dqn")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--check-deps", action="store_true")
    parser.add_argument("--steps", type=int, default=90)
    parser.add_argument("--timesteps", type=int, default=None)
    parser.add_argument("--eval-episodes", type=int, default=None)
    parser.add_argument("--eval-seconds", type=float, default=None)
    parser.add_argument("--seed-start", type=int, default=None)
    parser.add_argument("--map-id", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument(
        "--opening-model",
        default=None,
        help="Optional SB3 zip used only before --opening-seconds during evaluation/comparison.",
    )
    parser.add_argument(
        "--opening-seconds",
        type=float,
        default=60.0,
        help="Duration for --opening-model before falling back to --model.",
    )
    parser.add_argument(
        "--behavior-clone-model",
        default=None,
        help="Evaluate or compare a train_behavior_clone.py checkpoint instead of an SB3 zip.",
    )
    parser.add_argument(
        "--upgrade-choice-model",
        default=None,
        help="Optional train_upgrade_choice.py checkpoint used to choose upgrade prompts during training, evaluation, and comparison.",
    )
    parser.add_argument(
        "--anchor-dataset",
        action="append",
        default=None,
        help="Trajectory JSONL file or directory used for offline anchor KL regularization during training. Repeat to combine datasets.",
    )
    parser.add_argument(
        "--anchor-model",
        default=None,
        help="Behavior-clone checkpoint used as the PPO anchor during offline KL regularization.",
    )
    parser.add_argument(
        "--anchor-opening-model",
        default=None,
        help="Optional SB3 opening checkpoint used by the anchor before --anchor-opening-seconds.",
    )
    parser.add_argument("--anchor-opening-seconds", type=float, default=60.0)
    parser.add_argument("--anchor-regularization-weight", type=float, default=1.0)
    parser.add_argument("--anchor-regularization-interval", type=int, default=2048)
    parser.add_argument("--anchor-regularization-epochs", type=int, default=1)
    parser.add_argument("--anchor-regularization-batch-size", type=int, default=256)
    parser.add_argument("--anchor-regularization-learning-rate", type=float, default=None)
    parser.add_argument("--anchor-limit-samples", type=int, default=None)
    parser.add_argument(
        "--anchor-sample-weighting",
        choices=sorted(ANCHOR_SAMPLE_WEIGHTING_MODES),
        default="none",
        help="Optional offline anchor KL sample weighting for imbalanced phase/map samples.",
    )
    parser.add_argument(
        "--anchor-include-time-buckets",
        default=None,
        help=(
            "Comma-separated anchor time buckets to keep for offline KL regularization "
            "(opening_lt_60, mid_60_to_180, late_180_to_300, post_300)."
        ),
    )
    parser.add_argument(
        "--anchor-time-bucket-weights",
        default=None,
        help=(
            "Comma-separated bucket=weight multipliers applied after "
            "--anchor-sample-weighting, for phase-specific anchor objectives."
        ),
    )
    parser.add_argument("--anchor-validation-split", type=float, default=0.2)
    parser.add_argument("--anchor-seed", type=int, default=12345)
    parser.add_argument(
        "--anchor-guard-max-validation-kl",
        type=float,
        default=None,
        help="Abort further PPO chunks when anchor validation mean KL exceeds this threshold.",
    )
    parser.add_argument(
        "--anchor-guard-min-argmax-agreement",
        type=float,
        default=None,
        help="Abort further PPO chunks when anchor validation argmax agreement drops below this threshold.",
    )
    parser.add_argument("--model-in", default=None)
    parser.add_argument("--model-out", default=None)
    parser.add_argument("--report-dir", default=None)
    parser.add_argument(
        "--reward-profile",
        choices=[
            "standard",
            "late-survival",
            "long-run-retention",
            "late-route-recovery",
            "late-win-conversion",
        ],
        default="standard",
        help="Select the Rust gym-bridge reward profile used by dry-run, training, and policy reward reports.",
    )
    parser.add_argument(
        "--train-seconds",
        type=float,
        default=None,
        help="Override training episode duration without changing evaluation seconds.",
    )
    parser.add_argument("--train-maps", default=None)
    parser.add_argument(
        "--train-map-preset",
        choices=sorted(BASE_DEMO_MAP_PRESETS),
        default=None,
        help="Use a predefined base_demo training map set.",
    )
    parser.add_argument(
        "--train-seeds",
        default=None,
        help="Comma-separated training seeds to replay during PPO/DQN training resets.",
    )
    parser.add_argument(
        "--train-seed-start",
        type=int,
        default=None,
        help="First training seed for a contiguous replay range.",
    )
    parser.add_argument(
        "--train-seed-count",
        type=int,
        default=None,
        help="Number of training seeds in the contiguous replay range.",
    )
    parser.add_argument(
        "--ent-coef",
        type=float,
        default=None,
        help="Override PPO entropy coefficient for exploration experiments.",
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=None,
        help="Override algorithm learning rate for auditable repair experiments.",
    )
    parser.add_argument(
        "--train-map-selection",
        choices=["cycle", "random"],
        default="cycle",
    )
    parser.add_argument(
        "--train-seed-selection",
        choices=["cycle", "random"],
        default="cycle",
    )
    parser.add_argument(
        "--eval-stochastic",
        action="store_true",
        help="Sample policy actions during evaluation instead of using deterministic argmax.",
    )
    parser.add_argument(
        "--eval-random-seed",
        type=int,
        default=None,
        help="Seed stochastic action sampling during evaluation/comparison; requires --eval-stochastic.",
    )
    parser.add_argument(
        "--edge-recovery-filter",
        action="store_true",
        help="Use a deterministic edge-recovery action filter during evaluation/comparison only.",
    )
    parser.add_argument(
        "--edge-recovery-distance",
        type=float,
        default=32.0,
        help="Boundary distance threshold for --edge-recovery-filter.",
    )
    parser.add_argument(
        "--edge-recovery-samples-out",
        default=None,
        help="Write JSONL supervision samples whenever a recovery filter changes a deterministic action.",
    )
    parser.add_argument(
        "--late-recovery-filter",
        action="store_true",
        help="Use a deterministic 180-300s safety recovery filter during evaluation/comparison only.",
    )
    parser.add_argument("--late-recovery-min-seconds", type=float, default=180.0)
    parser.add_argument("--late-recovery-hazard-threshold", type=float, default=0.2)
    parser.add_argument("--late-recovery-boss-threshold", type=float, default=0.05)
    parser.add_argument("--late-recovery-enemy-threshold", type=float, default=0.05)
    parser.add_argument("--late-recovery-low-health-threshold", type=float, default=0.25)
    parser.add_argument(
        "--late-recovery-toward-dot-threshold",
        type=float,
        default=0.15,
    )
    parser.add_argument(
        "--trace-dir",
        default=None,
        help="Write sampled policy episode traces during training evaluation, evaluation, or comparison.",
    )
    parser.add_argument(
        "--trace-failed-only",
        action="store_true",
        help="When --trace-dir is set, only write traces for non-victory policy episodes.",
    )
    parser.add_argument(
        "--trace-sample-stride",
        type=int,
        default=30,
        help="Record one trace row every N policy steps, plus the first and terminal steps.",
    )
    parser.add_argument(
        "--trace-include-observation",
        action="store_true",
        help="Include policy observation vectors in sampled traces for repair-sample extraction.",
    )
    parser.add_argument("--evaluate-model", action="store_true")
    parser.add_argument("--compare-rule-bots", action="store_true")
    parser.add_argument(
        "--compare-map-preset",
        choices=sorted(BASE_DEMO_MAP_PRESETS),
        default=None,
        help="Run --compare-rule-bots once for each map in a predefined preset.",
    )
    parser.add_argument("--rule-bots", default="random,kite,tank")
    parser.add_argument("--report", default=None)
    parser.add_argument("--copy-template", default=None)
    args = parser.parse_args()

    config = load_config(args.config)
    algorithm_config(config, args.algorithm)
    try:
        algorithm_overrides = algorithm_overrides_from_args(args)
        train_seconds = validate_positive_seconds(args.train_seconds, "--train-seconds")
        opening_seconds = validate_positive_seconds(
            args.opening_seconds,
            "--opening-seconds",
        )
        anchor_include_time_buckets = parse_anchor_time_bucket_list(
            args.anchor_include_time_buckets,
        )
        anchor_time_bucket_weights = parse_anchor_time_bucket_weights(
            args.anchor_time_bucket_weights,
        )
        anchor_regularization_requested = validate_anchor_regularization_request(
            anchor_model=args.anchor_model,
            anchor_datasets=args.anchor_dataset,
            anchor_opening_seconds=args.anchor_opening_seconds,
            anchor_regularization_weight=args.anchor_regularization_weight,
            anchor_regularization_interval=args.anchor_regularization_interval,
            anchor_regularization_epochs=args.anchor_regularization_epochs,
            anchor_regularization_batch_size=args.anchor_regularization_batch_size,
            anchor_regularization_learning_rate=args.anchor_regularization_learning_rate,
            anchor_limit_samples=args.anchor_limit_samples,
            anchor_sample_weighting=args.anchor_sample_weighting,
            anchor_include_time_buckets=anchor_include_time_buckets,
            anchor_time_bucket_weights=anchor_time_bucket_weights,
            anchor_validation_split=args.anchor_validation_split,
        )
        anchor_validation_guard_requested = validate_anchor_validation_guard_thresholds(
            max_validation_kl=args.anchor_guard_max_validation_kl,
            min_argmax_agreement=args.anchor_guard_min_argmax_agreement,
        )
        train_maps, train_map_preset = resolve_train_maps(
            args.train_maps,
            args.train_map_preset,
        )
        train_seed_values = resolve_train_seed_values(
            args.train_seeds,
            args.train_seed_start,
            args.train_seed_count,
        )
        eval_random_seed = validate_eval_random_seed(
            args.eval_random_seed,
            deterministic=not args.eval_stochastic,
        )
        if args.edge_recovery_distance < 0.0:
            raise ValueError("--edge-recovery-distance must be non-negative")
        if args.late_recovery_min_seconds < 0.0:
            raise ValueError("--late-recovery-min-seconds must be non-negative")
        for name in (
            "late_recovery_hazard_threshold",
            "late_recovery_boss_threshold",
            "late_recovery_enemy_threshold",
            "late_recovery_low_health_threshold",
        ):
            value = getattr(args, name)
            if not (0.0 <= value <= 1.0):
                raise ValueError(f"--{name.replace('_', '-')} must be between 0 and 1")
        if not (-1.0 <= args.late_recovery_toward_dot_threshold <= 1.0):
            raise ValueError("--late-recovery-toward-dot-threshold must be between -1 and 1")
    except ValueError as exc:
        parser.error(str(exc))
    if args.compare_map_preset is not None and not args.compare_rule_bots:
        parser.error("--compare-map-preset requires --compare-rule-bots")
    if args.compare_map_preset is not None and args.map_id is not None:
        parser.error("--compare-map-preset cannot be used together with --map-id")
    if args.behavior_clone_model and args.model:
        parser.error("--behavior-clone-model cannot be combined with --model")
    if args.opening_model and not (args.evaluate_model or args.compare_rule_bots):
        parser.error("--opening-model requires --evaluate-model or --compare-rule-bots")
    if args.behavior_clone_model and not (args.evaluate_model or args.compare_rule_bots):
        parser.error("--behavior-clone-model requires --evaluate-model or --compare-rule-bots")
    if args.edge_recovery_filter and not (args.evaluate_model or args.compare_rule_bots):
        parser.error("--edge-recovery-filter requires --evaluate-model or --compare-rule-bots")
    if args.late_recovery_filter and not (args.evaluate_model or args.compare_rule_bots):
        parser.error("--late-recovery-filter requires --evaluate-model or --compare-rule-bots")
    if anchor_regularization_requested and (
        args.dry_run or args.evaluate_model or args.compare_rule_bots
    ):
        parser.error("anchor regularization flags are only supported during training")
    if anchor_regularization_requested and args.algorithm != "ppo":
        parser.error("anchor regularization is currently supported only with --algorithm ppo")
    if args.anchor_opening_model and not anchor_regularization_requested:
        parser.error("--anchor-opening-model requires --anchor-model and --anchor-dataset")
    if args.anchor_include_time_buckets and not anchor_regularization_requested:
        parser.error("--anchor-include-time-buckets requires --anchor-model and --anchor-dataset")
    if args.anchor_time_bucket_weights and not anchor_regularization_requested:
        parser.error("--anchor-time-bucket-weights requires --anchor-model and --anchor-dataset")
    if anchor_validation_guard_requested and not anchor_regularization_requested:
        parser.error("--anchor-guard-* requires --anchor-model and --anchor-dataset")
    if args.edge_recovery_filter and args.late_recovery_filter:
        parser.error("--edge-recovery-filter and --late-recovery-filter cannot be combined")
    if args.edge_recovery_samples_out and not (
        args.edge_recovery_filter or args.late_recovery_filter
    ):
        parser.error("--edge-recovery-samples-out requires a recovery filter")
    if args.trace_sample_stride <= 0:
        parser.error("--trace-sample-stride must be greater than 0")

    if args.copy_template:
        write_report(args.report, copy_template(args.copy_template))
        return

    if args.check_deps:
        payload = {"status": "ok", "dependencies": dependency_status()}
        write_report(args.report, payload)
        return

    if args.dry_run:
        write_report(
            args.report,
            dry_run(
                config,
                args.algorithm,
                args.steps,
                train_seconds=train_seconds,
                train_maps=train_maps,
                train_map_selection=args.train_map_selection,
                train_map_preset=train_map_preset,
                reward_profile=args.reward_profile,
                train_seed_values=train_seed_values,
                train_seed_selection=args.train_seed_selection,
                upgrade_choice_model=(
                    Path(args.upgrade_choice_model)
                    if args.upgrade_choice_model
                    else None
                ),
            ),
        )
        return

    if args.evaluate_model:
        write_report(
            args.report,
            evaluate_policy_model(
                config,
                args.algorithm,
                model_path=Path(args.model) if args.model else None,
                opening_model_path=(
                    Path(args.opening_model)
                    if args.opening_model
                    else None
                ),
                opening_seconds=opening_seconds,
                behavior_clone_model=(
                    Path(args.behavior_clone_model)
                    if args.behavior_clone_model
                    else None
                ),
                eval_episodes=args.eval_episodes,
                eval_seconds=args.eval_seconds,
                seed_start=args.seed_start,
                map_id=args.map_id,
                deterministic=not args.eval_stochastic,
                eval_random_seed=eval_random_seed,
                reward_profile=args.reward_profile,
                upgrade_choice_model=(
                    Path(args.upgrade_choice_model)
                    if args.upgrade_choice_model
                    else None
                ),
                trace_dir=args.trace_dir,
                trace_failed_only=args.trace_failed_only,
                trace_sample_stride=args.trace_sample_stride,
                trace_include_observation=args.trace_include_observation,
                edge_recovery_filter=args.edge_recovery_filter,
                edge_recovery_distance=args.edge_recovery_distance,
                edge_recovery_samples_out=args.edge_recovery_samples_out,
                late_recovery_filter=args.late_recovery_filter,
                late_recovery_min_seconds=args.late_recovery_min_seconds,
                late_recovery_hazard_threshold=args.late_recovery_hazard_threshold,
                late_recovery_boss_threshold=args.late_recovery_boss_threshold,
                late_recovery_enemy_threshold=args.late_recovery_enemy_threshold,
                late_recovery_low_health_threshold=args.late_recovery_low_health_threshold,
                late_recovery_toward_dot_threshold=args.late_recovery_toward_dot_threshold,
            ),
        )
        return

    if args.compare_rule_bots:
        rule_bots = parse_rule_bots(args.rule_bots)
        if args.compare_map_preset:
            write_report(
                args.report,
                compare_policy_to_rule_bots_across_maps(
                    config,
                    args.algorithm,
                    BASE_DEMO_MAP_PRESETS[args.compare_map_preset],
                    model_path=Path(args.model) if args.model else None,
                    opening_model_path=(
                        Path(args.opening_model)
                        if args.opening_model
                        else None
                    ),
                    opening_seconds=opening_seconds,
                    behavior_clone_model=(
                        Path(args.behavior_clone_model)
                        if args.behavior_clone_model
                        else None
                    ),
                    eval_episodes=args.eval_episodes,
                    eval_seconds=args.eval_seconds,
                    seed_start=args.seed_start,
                    rule_bots=rule_bots,
                    deterministic=not args.eval_stochastic,
                    eval_random_seed=eval_random_seed,
                    reward_profile=args.reward_profile,
                    map_preset=args.compare_map_preset,
                    upgrade_choice_model=(
                        Path(args.upgrade_choice_model)
                        if args.upgrade_choice_model
                        else None
                    ),
                    trace_dir=args.trace_dir,
                    trace_failed_only=args.trace_failed_only,
                    trace_sample_stride=args.trace_sample_stride,
                    trace_include_observation=args.trace_include_observation,
                    edge_recovery_filter=args.edge_recovery_filter,
                    edge_recovery_distance=args.edge_recovery_distance,
                    edge_recovery_samples_out=args.edge_recovery_samples_out,
                    late_recovery_filter=args.late_recovery_filter,
                    late_recovery_min_seconds=args.late_recovery_min_seconds,
                    late_recovery_hazard_threshold=args.late_recovery_hazard_threshold,
                    late_recovery_boss_threshold=args.late_recovery_boss_threshold,
                    late_recovery_enemy_threshold=args.late_recovery_enemy_threshold,
                    late_recovery_low_health_threshold=args.late_recovery_low_health_threshold,
                    late_recovery_toward_dot_threshold=args.late_recovery_toward_dot_threshold,
                ),
            )
            return
        write_report(
            args.report,
            compare_policy_to_rule_bots(
                config,
                args.algorithm,
                model_path=Path(args.model) if args.model else None,
                opening_model_path=(
                    Path(args.opening_model)
                    if args.opening_model
                    else None
                ),
                opening_seconds=opening_seconds,
                behavior_clone_model=(
                    Path(args.behavior_clone_model)
                    if args.behavior_clone_model
                    else None
                ),
                eval_episodes=args.eval_episodes,
                eval_seconds=args.eval_seconds,
                seed_start=args.seed_start,
                map_id=args.map_id,
                rule_bots=rule_bots,
                deterministic=not args.eval_stochastic,
                eval_random_seed=eval_random_seed,
                reward_profile=args.reward_profile,
                upgrade_choice_model=(
                    Path(args.upgrade_choice_model)
                    if args.upgrade_choice_model
                    else None
                ),
                trace_dir=args.trace_dir,
                trace_failed_only=args.trace_failed_only,
                trace_sample_stride=args.trace_sample_stride,
                trace_include_observation=args.trace_include_observation,
                edge_recovery_filter=args.edge_recovery_filter,
                edge_recovery_distance=args.edge_recovery_distance,
                edge_recovery_samples_out=args.edge_recovery_samples_out,
                late_recovery_filter=args.late_recovery_filter,
                late_recovery_min_seconds=args.late_recovery_min_seconds,
                late_recovery_hazard_threshold=args.late_recovery_hazard_threshold,
                late_recovery_boss_threshold=args.late_recovery_boss_threshold,
                late_recovery_enemy_threshold=args.late_recovery_enemy_threshold,
                late_recovery_low_health_threshold=args.late_recovery_low_health_threshold,
                late_recovery_toward_dot_threshold=args.late_recovery_toward_dot_threshold,
            ),
        )
        return

    write_report(
        args.report,
        train(
            config,
            args.algorithm,
            total_timesteps=args.timesteps,
            eval_episodes=args.eval_episodes,
            eval_seconds=args.eval_seconds,
            model_out=args.model_out,
            report_dir_out=args.report_dir,
            train_seconds=train_seconds,
            train_maps=train_maps,
            train_map_selection=args.train_map_selection,
            train_map_preset=train_map_preset,
            reward_profile=args.reward_profile,
            train_seed_values=train_seed_values,
            train_seed_selection=args.train_seed_selection,
            algorithm_overrides=algorithm_overrides,
            eval_deterministic=not args.eval_stochastic,
            eval_random_seed=eval_random_seed,
            eval_map_id=args.map_id,
            model_in=args.model_in,
            trace_dir=args.trace_dir,
            trace_failed_only=args.trace_failed_only,
            trace_sample_stride=args.trace_sample_stride,
            trace_include_observation=args.trace_include_observation,
            edge_recovery_filter=args.edge_recovery_filter,
            edge_recovery_distance=args.edge_recovery_distance,
            edge_recovery_samples_out=args.edge_recovery_samples_out,
            late_recovery_filter=args.late_recovery_filter,
            late_recovery_min_seconds=args.late_recovery_min_seconds,
            late_recovery_hazard_threshold=args.late_recovery_hazard_threshold,
            late_recovery_boss_threshold=args.late_recovery_boss_threshold,
            late_recovery_enemy_threshold=args.late_recovery_enemy_threshold,
            late_recovery_low_health_threshold=args.late_recovery_low_health_threshold,
            late_recovery_toward_dot_threshold=args.late_recovery_toward_dot_threshold,
            upgrade_choice_model=(
                Path(args.upgrade_choice_model)
                if args.upgrade_choice_model
                else None
            ),
            anchor_model=Path(args.anchor_model) if args.anchor_model else None,
            anchor_datasets=args.anchor_dataset,
            anchor_opening_model=(
                Path(args.anchor_opening_model)
                if args.anchor_opening_model
                else None
            ),
            anchor_opening_seconds=args.anchor_opening_seconds,
            anchor_regularization_weight=args.anchor_regularization_weight,
            anchor_regularization_interval=args.anchor_regularization_interval,
            anchor_regularization_epochs=args.anchor_regularization_epochs,
            anchor_regularization_batch_size=args.anchor_regularization_batch_size,
            anchor_regularization_learning_rate=args.anchor_regularization_learning_rate,
            anchor_limit_samples=args.anchor_limit_samples,
            anchor_sample_weighting=args.anchor_sample_weighting,
            anchor_include_time_buckets=anchor_include_time_buckets,
            anchor_time_bucket_weights=anchor_time_bucket_weights,
            anchor_validation_split=args.anchor_validation_split,
            anchor_seed=args.anchor_seed,
            anchor_guard_max_validation_kl=args.anchor_guard_max_validation_kl,
            anchor_guard_min_argmax_agreement=args.anchor_guard_min_argmax_agreement,
        ),
    )


if __name__ == "__main__":
    main()
