import json
import random
from types import SimpleNamespace

import pytest

import python.train.train_sb3 as train_sb3
from python.train.train_sb3 import (
    EdgeRecoveryFilterPolicy,
    LateRecoveryFilterPolicy,
    StagedOpeningPolicy,
    action_pushes_into_edge,
    algorithm_parameters_source_label,
    algorithm_overrides_from_args,
    apply_loaded_model_overrides,
    build_edge_recovery_sample,
    build_env,
    build_trace_step,
    compact_action_score,
    consume_policy_adapter_decision,
    derived_edge_recovery_samples_path,
    merge_algorithm_parameters,
    load_behavior_clone_policy_with_optional_opening,
    resolve_train_seed_values,
    seed_stochastic_action_sampling,
    should_record_trace_step,
    validate_eval_random_seed,
    write_edge_recovery_samples,
    write_episode_trace,
)


class DummyPolicy:
    def __init__(self, action):
        self.action = action
        self.reset_count = 0
        self.map_id = None

    def reset(self):
        self.reset_count += 1

    def set_map_id(self, map_id):
        self.map_id = map_id

    def predict(self, observation, deterministic=True):
        return self.action, None

    def action_scores(self, observation):
        return {
            "kind": "probability",
            "scores": [1.0 if index == self.action else 0.0 for index in range(9)],
        }


def test_merge_algorithm_parameters_preserves_base_and_applies_overrides():
    merged = merge_algorithm_parameters(
        {"learning_rate": 0.0003, "gamma": 0.99, "ent_coef": 0.0},
        {"learning_rate": 0.0001, "ent_coef": 0.02},
    )

    assert merged == {"learning_rate": 0.0001, "gamma": 0.99, "ent_coef": 0.02}


def test_algorithm_overrides_accepts_learning_rate():
    args = SimpleNamespace(
        algorithm="ppo",
        learning_rate=0.0001,
        ent_coef=None,
    )

    assert algorithm_overrides_from_args(args) == {"learning_rate": 0.0001}


def test_algorithm_overrides_rejects_non_positive_learning_rate():
    args = SimpleNamespace(
        algorithm="ppo",
        learning_rate=0.0,
        ent_coef=None,
    )

    with pytest.raises(ValueError, match="--learning-rate"):
        algorithm_overrides_from_args(args)


def test_resolve_train_seed_values_accepts_range():
    assert resolve_train_seed_values(None, 62400, 3) == [62400, 62401, 62402]


def test_resolve_train_seed_values_accepts_explicit_list():
    assert resolve_train_seed_values("62400,62407", None, None) == [62400, 62407]


def test_resolve_train_seed_values_rejects_mixed_sources():
    with pytest.raises(ValueError, match="--train-seeds"):
        resolve_train_seed_values("62400", 62400, 2)


def test_validate_eval_random_seed_requires_stochastic_evaluation():
    assert validate_eval_random_seed(17, deterministic=False) == 17
    assert validate_eval_random_seed(None, deterministic=True) is None
    with pytest.raises(ValueError, match="--eval-random-seed"):
        validate_eval_random_seed(17, deterministic=True)
    with pytest.raises(ValueError, match="non-negative"):
        validate_eval_random_seed(-1, deterministic=False)


def test_build_env_passes_reward_profile(monkeypatch):
    captured = {}

    class DummyEnv:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(train_sb3, "SoftCandyStormEnv", DummyEnv)
    config = {
        "environment": {
            "seed": 12345,
            "seconds": 300,
            "tick_rate": 30,
            "map_id": "soda-creek",
            "observation_version": 2,
            "content_dir": "content/base_demo",
        }
    }

    env = build_env(config, reward_profile="long-run-retention")

    assert isinstance(env, DummyEnv)
    assert captured["reward_profile"] == "long-run-retention"


def test_training_uses_upgrade_choice_model(monkeypatch, tmp_path):
    captured = {}
    upgrade_policy = object()

    class DummyEnv:
        def close(self):
            captured["env_closed"] = True

    class DummyModel:
        def __init__(self, policy, env, verbose=0, **kwargs):
            captured["model_policy"] = policy
            captured["model_env"] = env
            captured["model_kwargs"] = kwargs
            self.num_timesteps = 0

        def learn(self, total_timesteps):
            self.num_timesteps = total_timesteps

        def save(self, path):
            captured["model_saved"] = str(path)
            path.write_text("dummy model", encoding="utf-8")

    def fake_build_env(config, **kwargs):
        captured["build_env_kwargs"] = kwargs
        return DummyEnv()

    def fake_evaluate_model(model, config, **kwargs):
        captured["evaluate_kwargs"] = kwargs
        return {
            "action_selection": "deterministic",
            "action_random_seed": None,
            "map_id": "soda-creek",
            "upgrade_policy": {
                "mode": "upgrade_choice_ranker",
                "model_path": "ranker.pt",
            },
            "summary": {
                "episodes": 1,
                "win_rate": 0.0,
                "average_survival_seconds": 1.0,
                "average_level": 1.0,
                "average_kills": 1.0,
                "average_reward": 0.0,
                "damage_taken_average": 0.0,
                "action_distribution": {
                    str(index): {
                        "count": 1 if index == 0 else 0,
                        "ratio": 1.0 if index == 0 else 0.0,
                    }
                    for index in range(9)
                },
                "normalized_action_entropy": 1.0,
                "reward_breakdown_average": {"terminal": 0.0, "total": 0.0},
                "upgrade_policy_decision_count": 1,
            },
        }

    monkeypatch.setattr(train_sb3, "require_dependencies", lambda: {})
    monkeypatch.setattr(train_sb3, "stable_baselines_model_classes", lambda: {"ppo": DummyModel})
    monkeypatch.setattr(train_sb3, "load_upgrade_choice_policy", lambda path: upgrade_policy)
    monkeypatch.setattr(train_sb3, "build_env", fake_build_env)
    monkeypatch.setattr(train_sb3, "evaluate_model", fake_evaluate_model)
    monkeypatch.setattr(train_sb3, "dependency_status", lambda: {})

    config = {
        "phase": "test",
        "environment": {
            "seed": 12345,
            "seconds": 300,
            "tick_rate": 30,
            "map_id": "soda-creek",
            "observation_version": 2,
            "observation_len": 145,
            "content_dir": "content/base_demo",
        },
        "algorithms": {
            "ppo": {
                "enabled": True,
                "policy": "MlpPolicy",
                "total_timesteps": 2,
                "n_steps": 1,
            }
        },
        "outputs": {
            "model_dir": str(tmp_path / "models"),
            "report_dir": str(tmp_path / "reports"),
            "metadata_file": "{algorithm}_metadata.json",
        },
        "evaluation": {
            "episodes": 1,
            "seconds": 1,
            "seed_start": 1,
        },
    }

    report = train_sb3.train(
        config,
        "ppo",
        total_timesteps=2,
        model_out=tmp_path / "model.zip",
        report_dir_out=tmp_path / "reports",
        upgrade_choice_model=tmp_path / "ranker.pt",
    )

    assert captured["build_env_kwargs"]["upgrade_policy"] is upgrade_policy
    assert captured["evaluate_kwargs"]["upgrade_policy"] is upgrade_policy
    assert report["training"]["upgrade_choice_model"].endswith("ranker.pt")
    assert report["upgrade_policy"]["mode"] == "upgrade_choice_ranker"
    assert captured["env_closed"] is True


def test_seed_stochastic_action_sampling_replays_python_random_sequence():
    report = seed_stochastic_action_sampling(1234)
    first = random.random()
    seed_stochastic_action_sampling(1234)
    second = random.random()

    assert first == second
    assert report["seed"] == 1234
    assert "python_random" in report["seeded_sources"]


def test_action_pushes_into_edge_detects_wallward_movement():
    diagnostics = {
        "boundary": {
            "left_distance": 0.0,
            "right_distance": 400.0,
            "bottom_distance": 50.0,
            "top_distance": 400.0,
        }
    }

    assert action_pushes_into_edge(7, diagnostics, 32.0)
    assert action_pushes_into_edge(8, diagnostics, 32.0)
    assert not action_pushes_into_edge(3, diagnostics, 32.0)
    assert not action_pushes_into_edge(0, diagnostics, 32.0)


def test_edge_recovery_filter_chooses_best_non_wallward_action():
    policy = EdgeRecoveryFilterPolicy(DummyPolicy(7), edge_distance=32.0)
    policy.set_step_context(
        {
            "diagnostics": {
                "boundary": {
                    "left_distance": 0.0,
                    "right_distance": 400.0,
                    "bottom_distance": 400.0,
                    "top_distance": 400.0,
                }
            }
        }
    )

    action, _state = policy.predict(None, deterministic=True)

    assert action == 0
    assert policy.policy_adapter_report()["mode"] == "edge_recovery_filter"


def test_edge_recovery_filter_records_consumable_recovery_decision():
    policy = EdgeRecoveryFilterPolicy(DummyPolicy(7), edge_distance=32.0)
    policy.set_step_context(
        {
            "diagnostics": {
                "boundary": {
                    "left_distance": 0.0,
                    "right_distance": 400.0,
                    "bottom_distance": 400.0,
                    "top_distance": 400.0,
                }
            }
        }
    )

    action, _state = policy.predict(None, deterministic=True)
    decision = consume_policy_adapter_decision(policy)

    assert action == 0
    assert decision["mode"] == "edge_recovery_filter"
    assert decision["original_action"] == 7
    assert decision["target_action"] == 0
    assert decision["target_rank"] == 2
    assert consume_policy_adapter_decision(policy) is None


def test_edge_recovery_filter_does_not_override_stochastic_actions():
    policy = EdgeRecoveryFilterPolicy(DummyPolicy(7), edge_distance=32.0)
    policy.set_step_context(
        {
            "diagnostics": {
                "boundary": {
                    "left_distance": 0.0,
                    "right_distance": 400.0,
                    "bottom_distance": 400.0,
                    "top_distance": 400.0,
                }
            }
        }
    )

    action, _state = policy.predict(None, deterministic=False)

    assert action == 7
    assert consume_policy_adapter_decision(policy) is None


def test_late_recovery_filter_redirects_wallward_hazard_action():
    observation = [0.0] * 145
    observation[130] = 0.3
    observation[131] = -0.3
    observation[132] = 0.4
    policy = LateRecoveryFilterPolicy(
        DummyPolicy(4),
        min_seconds=180.0,
        edge_distance=32.0,
        hazard_threshold=0.2,
    )
    policy.set_step_context(
        {
            "time_seconds": 220.0,
            "diagnostics": {
                "player_position": {"x": 1150.0, "y": -850.0},
                "boundary": {
                    "left_distance": 2300.0,
                    "right_distance": 0.0,
                    "bottom_distance": 0.0,
                    "top_distance": 1700.0,
                },
                "hazard_pressure_risk": 1.0,
                "boss_pressure_risk": 0.0,
                "enemy_pressure_risk": 0.0,
                "low_health_risk": 0.5,
            },
        }
    )

    action, _state = policy.predict(observation, deterministic=True)
    decision = consume_policy_adapter_decision(policy)

    assert action == 1
    assert decision["mode"] == "late_recovery_filter"
    assert decision["original_action"] == 4
    assert decision["target_action"] == 1
    assert "wallward_edge" in decision["risk_reasons"]
    assert "toward_hazard" in decision["risk_reasons"]


def test_late_recovery_filter_ignores_opening_window():
    policy = LateRecoveryFilterPolicy(DummyPolicy(4), min_seconds=180.0)
    policy.set_step_context(
        {
            "time_seconds": 60.0,
            "diagnostics": {
                "boundary": {
                    "right_distance": 0.0,
                    "bottom_distance": 0.0,
                },
                "hazard_pressure_risk": 1.0,
            },
        }
    )

    action, _state = policy.predict([0.0] * 145, deterministic=True)

    assert action == 4
    assert consume_policy_adapter_decision(policy) is None


def test_build_edge_recovery_sample_includes_observation_and_diagnostics():
    sample = build_edge_recovery_sample(
        episode_seed=62201,
        step_number=1801,
        observation=[0.1, 0.2, 0.3],
        info={
            "map_id": "soda-creek",
            "tick": 1800,
            "time_seconds": 60.0,
            "diagnostics": {
                "boundary": {
                    "left_distance": 0.0,
                    "right_distance": 2400.0,
                    "bottom_distance": 900.0,
                    "top_distance": 900.0,
                }
            },
        },
        adapter_decision={
            "mode": "edge_recovery_filter",
            "edge_distance": 32.0,
            "original_action": 7,
            "target_action": 0,
            "score_kind": "probability",
            "original_action_score": 0.9,
            "target_action_score": 0.1,
            "score_margin": -0.8,
            "target_rank": 2,
        },
        action_scores={
            "kind": "probability",
            "scores": [0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.0],
        },
        config={"environment": {"observation_version": 2}},
    )

    assert sample["record_type"] == "edge_recovery_supervision_sample"
    assert sample["sample_role"] == "repair_training_input"
    assert sample["observation_len"] == 3
    assert sample["original_action"] == 7
    assert sample["target_action"] == 0
    assert sample["diagnostics"]["boundary"]["left_distance"] == 0.0


def test_build_late_recovery_sample_uses_risk_record_type():
    sample = build_edge_recovery_sample(
        episode_seed=62300,
        step_number=6601,
        observation=[0.1, 0.2, 0.3],
        info={
            "map_id": "caramel-workshop",
            "tick": 6600,
            "time_seconds": 220.0,
            "diagnostics": {"hazard_pressure_risk": 1.0},
        },
        adapter_decision={
            "mode": "late_recovery_filter",
            "original_action": 4,
            "target_action": 1,
            "risk_reasons": ["wallward_edge", "toward_hazard"],
        },
        action_scores={
            "kind": "probability",
            "scores": [0.1, 0.2, 0.0, 0.0, 0.7, 0.0, 0.0, 0.0, 0.0],
        },
        config={"environment": {"observation_version": 2}},
    )

    assert sample["record_type"] == "risk_recovery_supervision_sample"
    assert sample["target_source"] == "late_recovery_filter"
    assert sample["target_label"] == "highest_scored_late_safe_action"


def test_write_edge_recovery_samples_writes_jsonl(tmp_path):
    target = tmp_path / "edge_samples.jsonl"
    report = write_edge_recovery_samples(
        target,
        [
            {
                "record_type": "edge_recovery_supervision_sample",
                "target_action": 0,
            }
        ],
    )

    lines = target.read_text(encoding="utf-8").splitlines()
    assert report["sample_count"] == 1
    assert json.loads(lines[0])["target_action"] == 0


def test_derived_edge_recovery_samples_path_uses_map_suffix():
    assert (
        derived_edge_recovery_samples_path("samples.jsonl", "soda-creek").name
        == "samples_soda-creek.jsonl"
    )
    assert (
        derived_edge_recovery_samples_path("samples", "soda-creek").name
        == "soda-creek_edge_recovery_samples.jsonl"
    )


def test_algorithm_parameter_source_records_warm_start_overrides():
    source = algorithm_parameters_source_label(
        warm_start_metadata={"algorithm_parameters": {"ent_coef": 0.0}},
        warm_start_model="model.zip",
        overrides={"ent_coef": 0.02},
    )

    assert source == "warm_start_metadata_with_overrides"


def test_apply_loaded_model_overrides_updates_supported_parameters():
    model = SimpleNamespace(ent_coef=0.0)

    apply_loaded_model_overrides(model, {"ent_coef": 0.03})

    assert model.ent_coef == 0.03


def test_apply_loaded_model_overrides_refreshes_learning_rate_schedule():
    class LoadedModel:
        def __init__(self):
            self.learning_rate = 0.0003
            self.lr_schedule = None

        def _setup_lr_schedule(self):
            self.lr_schedule = f"schedule:{self.learning_rate}"

    model = LoadedModel()

    apply_loaded_model_overrides(model, {"learning_rate": 0.0001})

    assert model.learning_rate == 0.0001
    assert model.lr_schedule == "schedule:0.0001"


def test_apply_loaded_model_overrides_rejects_unknown_parameters():
    with pytest.raises(ValueError, match="does not expose"):
        apply_loaded_model_overrides(SimpleNamespace(), {"ent_coef": 0.03})


def test_trace_step_sampling_records_first_stride_and_terminal_steps():
    assert not should_record_trace_step(None, 1, False, False, 30)
    assert should_record_trace_step("traces", 1, False, False, 30)
    assert should_record_trace_step("traces", 60, False, False, 30)
    assert should_record_trace_step("traces", 17, True, False, 30)
    assert not should_record_trace_step("traces", 17, False, False, 30)


def test_build_trace_step_compacts_policy_scores():
    info = {
        "tick": 30,
        "time_seconds": 1.0,
        "health": 91.5,
        "level": 2,
        "kills": 3,
        "xp_collected": 4.25,
        "damage_taken": 8.5,
        "upgrade_options": ["mint"],
        "events": ["hit"],
        "terminal": None,
        "reward_breakdown": {"survival": 0.1, "total": -0.25},
        "diagnostics": {
            "player_position": {"x": 12.0, "y": -3.0},
            "boundary": {"min_distance": 42.0, "edge_risk": 0.0},
            "nearest_enemy": {"enemy_id": "soda-bubble", "hitbox_distance": 55.0},
        },
    }

    step = build_trace_step(
        30,
        4,
        -0.25,
        info,
        {"kind": "probability", "scores": [0.1, 0.2, 0.05, 0.15, 0.5]},
    )

    assert step["action"] == 4
    assert step["health"] == 91.5
    assert step["reward_breakdown"] == {"survival": 0.1, "total": -0.25}
    assert step["action_score"]["chosen_action_score"] == 0.5
    assert step["action_score"]["top_actions"][0] == {"action": "4", "score": 0.5}
    assert step["diagnostics"]["nearest_enemy"]["enemy_id"] == "soda-bubble"


def test_build_trace_step_can_include_observation_for_repair_sampling():
    step = build_trace_step(
        1,
        3,
        0.25,
        {
            "tick": 1,
            "time_seconds": 0.0333,
            "health": 120.0,
            "level": 1,
            "kills": 0,
            "xp_collected": 0.0,
            "damage_taken": 0.0,
            "reward_breakdown": {"route_recovery": -0.002},
        },
        {"kind": "probability", "scores": [0.1, 0.2, 0.3, 0.4]},
        observation=[0.1, 0.2, 0.3],
        observation_version=2,
        include_observation=True,
    )

    assert step["observation_version"] == 2
    assert step["observation_len"] == 3
    assert step["observation"] == [0.1, 0.2, 0.3]


def test_write_episode_trace_respects_failed_only(tmp_path):
    victory = {"seed": 1, "map_id": "soda-creek", "terminal_kind": "victory"}
    failure = {
        "seed": 2,
        "map_id": "soda-creek",
        "terminal_kind": "defeat",
        "terminal_reason": "player_health_depleted",
    }

    assert write_episode_trace(tmp_path, victory, [], failed_only=True) is None
    trace_path = write_episode_trace(
        tmp_path,
        failure,
        [{"step": 1, "action": 4}],
        failed_only=True,
    )

    payload = json.loads((tmp_path / "soda-creek_seed2_trace.json").read_text())
    assert trace_path.endswith("soda-creek_seed2_trace.json")
    assert payload["record_type"] == "policy_episode_trace"
    assert payload["sample_count"] == 1
    assert payload["episode"]["terminal_kind"] == "defeat"


def test_staged_opening_policy_switches_after_opening_seconds():
    opening = DummyPolicy(7)
    fallback = DummyPolicy(4)
    policy = StagedOpeningPolicy(
        opening,
        fallback,
        60.0,
        "opening.zip",
        "fallback.zip",
    )

    policy.reset()
    policy.set_map_id("soda-creek")
    policy.set_step_context({"time_seconds": 59.9})
    opening_action, _ = policy.predict(None)
    opening_scores = policy.action_scores(None)
    policy.set_step_context({"time_seconds": 60.0})
    fallback_action, _ = policy.predict(None)

    assert opening.reset_count == 1
    assert fallback.reset_count == 1
    assert opening.map_id == "soda-creek"
    assert fallback.map_id == "soda-creek"
    assert opening_action == 7
    assert opening_scores["scores"][7] == 1.0
    assert fallback_action == 4
    assert policy.opening_policy_report()["mode"] == "staged_sb3_opening"


def test_compare_policy_to_rule_bots_forwards_late_recovery_options(monkeypatch):
    captured = {}

    def fake_evaluate_policy_model(config, algorithm, **kwargs):
        captured.update(kwargs)
        return {
            "policy_kind": "late_recovery_filter",
            "opening_policy": None,
            "policy_adapter": {"mode": "late_recovery_filter"},
            "edge_recovery_samples": None,
            "upgrade_policy": None,
            "action_selection": "deterministic",
            "summary": {
                "episodes": 1,
                "win_rate": 1.0,
                "average_kills": 5.0,
                "dominant_action_ratio": 0.1,
                "normalized_action_entropy": 1.0,
            },
        }

    monkeypatch.setattr(train_sb3, "evaluate_policy_model", fake_evaluate_policy_model)
    monkeypatch.setattr(
        train_sb3,
        "run_rule_bot_matrix",
        lambda config, bots, seed_start, episodes, seconds, map_id: {
            "stdout": {"bots": []},
            "command": ["game_harness", "matrix"],
            "stderr": "",
        },
    )

    report = train_sb3.compare_policy_to_rule_bots(
        {
            "phase": "test",
            "evaluation": {"episodes": 1, "seconds": 5, "seed_start": 10},
            "environment": {"tick_rate": 30},
            "models": {"ppo": "unused.zip"},
            "outputs": {"model_dir": "python/train/models"},
        },
        "ppo",
        late_recovery_filter=True,
        late_recovery_min_seconds=180.0,
        late_recovery_hazard_threshold=0.3,
        late_recovery_boss_threshold=0.2,
        late_recovery_enemy_threshold=0.1,
        late_recovery_low_health_threshold=0.4,
        late_recovery_toward_dot_threshold=0.25,
    )

    assert captured["late_recovery_filter"] is True
    assert captured["late_recovery_hazard_threshold"] == 0.3
    assert captured["late_recovery_boss_threshold"] == 0.2
    assert captured["late_recovery_enemy_threshold"] == 0.1
    assert captured["late_recovery_low_health_threshold"] == 0.4
    assert captured["late_recovery_toward_dot_threshold"] == 0.25
    assert report["policy_adapter"]["mode"] == "late_recovery_filter"


def test_behavior_clone_fallback_can_be_wrapped_with_sb3_opening(monkeypatch):
    class DummyModelClass:
        @staticmethod
        def load(path):
            assert str(path) == "opening.zip"
            return DummyPolicy(7)

    monkeypatch.setattr(
        train_sb3,
        "stable_baselines_model_classes",
        lambda: {"ppo": DummyModelClass},
    )
    monkeypatch.setattr(
        train_sb3,
        "load_behavior_clone_policy",
        lambda path: DummyPolicy(4),
    )

    policy = load_behavior_clone_policy_with_optional_opening(
        "ppo",
        "fallback.pt",
        opening_model_path="opening.zip",
        opening_seconds=60.0,
    )

    policy.set_step_context({"time_seconds": 10.0})
    opening_action, _ = policy.predict(None)
    policy.set_step_context({"time_seconds": 60.0})
    fallback_action, _ = policy.predict(None)

    assert opening_action == 7
    assert fallback_action == 4
    assert policy.opening_policy_report()["fallback_model_path"] == "fallback.pt"
