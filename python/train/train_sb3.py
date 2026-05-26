import argparse
import importlib.util
import json
import math
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from python.gym_env import SoftCandyStormEnv
from python.train.train_behavior_clone import load_behavior_clone_policy
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


def parse_map_list(value):
    if value is None:
        return None
    maps = [item.strip() for item in value.split(",") if item.strip()]
    if not maps:
        raise ValueError("map list must include at least one map id")
    return maps


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


def validate_positive_seconds(value, flag_name):
    if value is None:
        return None
    if value <= 0.0:
        raise ValueError(f"{flag_name} must be greater than 0")
    return value


def build_env(
    config,
    seed=None,
    seconds=None,
    map_id=None,
    map_ids=None,
    map_selection="cycle",
    upgrade_policy=None,
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
):
    requested_seconds = train_seconds or config["environment"]["seconds"]
    env = build_env(
        config,
        seconds=min(requested_seconds, 5.0),
        map_ids=train_maps,
        map_selection=train_map_selection,
    )
    total_reward = 0.0
    try:
        observation, info = env.reset(seed=config["environment"]["seed"])
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
            "time_seconds": info["time_seconds"],
            "observation_len": info["observation_len"],
            "action_count": info["action_count"],
            "requested_train_seconds": requested_seconds,
            "dry_run_seconds": env.seconds,
            "training_maps": train_maps
            or [config["environment"].get("map_id", "frosting-grassland")],
            "training_map_selection": train_map_selection if train_maps else "single",
            "training_map_preset": train_map_preset,
            "total_reward": round(total_reward, 4),
            "dependencies": dependency_status(),
        }
    finally:
        env.close()


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
    algorithm_overrides=None,
    eval_deterministic=True,
    eval_map_id=None,
    model_in=None,
):
    require_dependencies()
    # Imports stay inside the real training path so dry-run remains dependency-light.
    model_classes = stable_baselines_model_classes()

    selected = algorithm_config(config, algorithm)
    train_steps = total_timesteps or selected["total_timesteps"]
    effective_train_seconds = train_seconds or config["environment"]["seconds"]
    env = build_env(
        config,
        seconds=effective_train_seconds,
        map_ids=train_maps,
        map_selection=train_map_selection,
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

    try:
        if warm_start_model is not None:
            model = model_class.load(warm_start_model, env=env)
            model.verbose = 1
            apply_loaded_model_overrides(model, algorithm_overrides)
        else:
            model = model_class(selected["policy"], env, verbose=1, **kwargs)
        model.learn(total_timesteps=train_steps)
        actual_timesteps = int(getattr(model, "num_timesteps", train_steps))
        completed_at = datetime.now(timezone.utc).isoformat()
        model.save(model_path)
    finally:
        env.close()

    evaluation = evaluate_model(
        model,
        config,
        episodes=eval_episodes or config["evaluation"]["episodes"],
        seconds=eval_seconds or config["evaluation"]["seconds"],
        map_id=eval_map_id,
        deterministic=eval_deterministic,
    )
    known_exploit_notes = known_exploits_from_evaluation(evaluation)
    gate_decision = training_gate_decision(known_exploit_notes)
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
    }
    metadata_path = metadata_path_for(config, algorithm, model_out=model_out)
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    report = {
        "status": "trained",
        "algorithm": algorithm,
        "model_path": str(model_path),
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
            "started_at": started_at,
            "completed_at": completed_at,
            "algorithm_parameters": algorithm_parameters,
            "algorithm_parameters_source": algorithm_parameters_source,
            "warm_start_model": str(warm_start_model) if warm_start_model else None,
            "warm_start_metadata_path": (
                str(warm_start_metadata_path) if warm_start_metadata_path else None
            ),
            "evaluation_policy": evaluation["action_selection"],
            "evaluation_map_id": evaluation["map_id"],
        },
        "evaluation": evaluation["summary"],
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
    eval_episodes=None,
    eval_seconds=None,
    seed_start=None,
    map_id=None,
    deterministic=True,
    upgrade_choice_model=None,
):
    model_class = stable_baselines_model_classes()[algorithm]
    model = model_class.load(model_path or default_model_path(config, algorithm))
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
        upgrade_policy=upgrade_policy,
    )


def evaluate_policy_model(
    config,
    algorithm,
    model_path=None,
    behavior_clone_model=None,
    eval_episodes=None,
    eval_seconds=None,
    seed_start=None,
    map_id=None,
    deterministic=True,
    upgrade_choice_model=None,
):
    if behavior_clone_model is not None:
        upgrade_policy = (
            load_upgrade_choice_policy(upgrade_choice_model)
            if upgrade_choice_model
            else None
        )
        return evaluate_behavior_clone_policy(
            config,
            behavior_clone_model,
            eval_episodes=eval_episodes,
            eval_seconds=eval_seconds,
            seed_start=seed_start,
            map_id=map_id,
            deterministic=deterministic,
            upgrade_policy=upgrade_policy,
        )
    return evaluate_saved_policy(
        config,
        algorithm,
        model_path=model_path,
        eval_episodes=eval_episodes,
        eval_seconds=eval_seconds,
        seed_start=seed_start,
        map_id=map_id,
        deterministic=deterministic,
        upgrade_choice_model=upgrade_choice_model,
    )


def evaluate_behavior_clone_policy(
    config,
    model_path,
    eval_episodes=None,
    eval_seconds=None,
    seed_start=None,
    map_id=None,
    deterministic=True,
    upgrade_policy=None,
):
    model_path = Path(model_path)
    policy = load_behavior_clone_policy(model_path)
    evaluation = evaluate_model(
        policy,
        config,
        episodes=eval_episodes or config["evaluation"]["episodes"],
        seconds=eval_seconds or config["evaluation"]["seconds"],
        seed_start=seed_start,
        map_id=map_id,
        deterministic=deterministic,
        upgrade_policy=upgrade_policy,
    )
    evaluation["policy_kind"] = "behavior_clone"
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


def evaluate_model(
    model,
    config,
    episodes,
    seconds,
    seed_start=None,
    map_id=None,
    deterministic=True,
    upgrade_policy=None,
):
    seed_start = seed_start if seed_start is not None else config["evaluation"]["seed_start"]
    map_id = map_id or config["environment"].get("map_id", "frosting-grassland")
    max_steps = int(seconds * config["environment"]["tick_rate"]) + 10
    episode_reports = []
    total_reward = 0.0
    env = None
    try:
        env = build_env(
            config,
            seed=seed_start,
            seconds=seconds,
            map_id=map_id,
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
            while not terminated and not truncated and steps < max_steps:
                action, _state = model.predict(
                    observation, deterministic=deterministic
                )
                action_index = action_to_int(action)
                record_action_scores(
                    action_score_tracker,
                    policy_action_scores(model, observation),
                    action_index,
                )
                action_counts[str(action_index)] = action_counts.get(str(action_index), 0) + 1
                observation, reward, terminated, truncated, info = env.step(action_index)
                if "upgrade_policy_decision" in info:
                    upgrade_policy_decisions.append(info["upgrade_policy_decision"])
                for key, value in info.get("reward_breakdown", {}).items():
                    reward_breakdown_totals[key] = reward_breakdown_totals.get(
                        key, 0.0
                    ) + float(value)
                episode_reward += reward
                steps += 1

            total_reward += episode_reward
            terminal = info.get("terminal") or {}
            episode_reports.append(
                {
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
                    "reward_breakdown": round_reward_breakdown(reward_breakdown_totals),
                }
            )
    finally:
        if env is not None:
            env.close()

    summary = summarize_evaluation(episode_reports, total_reward)
    return {
        "report_version": 1,
        "status": "evaluated",
        "phase": config["phase"],
        "map_id": map_id,
        "action_selection": "deterministic" if deterministic else "stochastic",
        "upgrade_policy": upgrade_policy_report(upgrade_policy),
        "episodes": episode_reports,
        "summary": summary,
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


def compare_policy_to_rule_bots(
    config,
    algorithm,
    model_path=None,
    behavior_clone_model=None,
    eval_episodes=None,
    eval_seconds=None,
    seed_start=None,
    map_id=None,
    rule_bots=None,
    deterministic=True,
    upgrade_choice_model=None,
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
        behavior_clone_model=behavior_clone_model,
        eval_episodes=episodes,
        eval_seconds=seconds,
        seed_start=seed_start,
        map_id=map_id,
        deterministic=deterministic,
        upgrade_choice_model=upgrade_choice_model,
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
        "upgrade_policy": policy.get("upgrade_policy"),
        "upgrade_choice_model": str(upgrade_choice_model) if upgrade_choice_model else None,
        "map_id": map_id,
        "action_selection": policy["action_selection"],
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
    behavior_clone_model=None,
    eval_episodes=None,
    eval_seconds=None,
    seed_start=None,
    rule_bots=None,
    deterministic=True,
    map_preset=None,
    upgrade_choice_model=None,
):
    comparisons = [
        compare_policy_to_rule_bots(
            config,
            algorithm,
            model_path=model_path,
            behavior_clone_model=behavior_clone_model,
            eval_episodes=eval_episodes,
            eval_seconds=eval_seconds,
            seed_start=seed_start,
            map_id=map_id,
            rule_bots=rule_bots,
            deterministic=deterministic,
            upgrade_choice_model=upgrade_choice_model,
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
        "policy_kind": "behavior_clone" if behavior_clone_model is not None else "sb3",
        "upgrade_policy": comparisons[0].get("upgrade_policy") if comparisons else None,
        "upgrade_choice_model": str(upgrade_choice_model) if upgrade_choice_model else None,
        "action_selection": comparisons[0]["action_selection"] if comparisons else None,
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
        "--behavior-clone-model",
        default=None,
        help="Evaluate or compare a train_behavior_clone.py checkpoint instead of an SB3 zip.",
    )
    parser.add_argument(
        "--upgrade-choice-model",
        default=None,
        help="Optional train_upgrade_choice.py checkpoint used to choose upgrade prompts during evaluation/comparison.",
    )
    parser.add_argument("--model-in", default=None)
    parser.add_argument("--model-out", default=None)
    parser.add_argument("--report-dir", default=None)
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
        "--ent-coef",
        type=float,
        default=None,
        help="Override PPO entropy coefficient for exploration experiments.",
    )
    parser.add_argument(
        "--train-map-selection",
        choices=["cycle", "random"],
        default="cycle",
    )
    parser.add_argument(
        "--eval-stochastic",
        action="store_true",
        help="Sample policy actions during evaluation instead of using deterministic argmax.",
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
        train_maps, train_map_preset = resolve_train_maps(
            args.train_maps,
            args.train_map_preset,
        )
    except ValueError as exc:
        parser.error(str(exc))
    if args.compare_map_preset is not None and not args.compare_rule_bots:
        parser.error("--compare-map-preset requires --compare-rule-bots")
    if args.compare_map_preset is not None and args.map_id is not None:
        parser.error("--compare-map-preset cannot be used together with --map-id")
    if args.behavior_clone_model and args.model:
        parser.error("--behavior-clone-model cannot be combined with --model")
    if args.behavior_clone_model and not (args.evaluate_model or args.compare_rule_bots):
        parser.error("--behavior-clone-model requires --evaluate-model or --compare-rule-bots")
    if args.upgrade_choice_model and not (args.evaluate_model or args.compare_rule_bots):
        parser.error("--upgrade-choice-model requires --evaluate-model or --compare-rule-bots")

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
                upgrade_choice_model=(
                    Path(args.upgrade_choice_model)
                    if args.upgrade_choice_model
                    else None
                ),
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
                    map_preset=args.compare_map_preset,
                    upgrade_choice_model=(
                        Path(args.upgrade_choice_model)
                        if args.upgrade_choice_model
                        else None
                    ),
                ),
            )
            return
        write_report(
            args.report,
            compare_policy_to_rule_bots(
                config,
                args.algorithm,
                model_path=Path(args.model) if args.model else None,
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
                upgrade_choice_model=(
                    Path(args.upgrade_choice_model)
                    if args.upgrade_choice_model
                    else None
                ),
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
            algorithm_overrides=algorithm_overrides,
            eval_deterministic=not args.eval_stochastic,
            eval_map_id=args.map_id,
            model_in=args.model_in,
        ),
    )


if __name__ == "__main__":
    main()
