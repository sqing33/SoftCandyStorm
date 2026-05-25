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


REQUIRED_MODULES = ["gymnasium", "numpy", "stable_baselines3"]


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
            + "; install gymnasium, numpy and stable-baselines3 before real training"
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


def build_env(config, seed=None, seconds=None, map_id=None):
    env_cfg = config["environment"]
    return SoftCandyStormEnv(
        seed=seed if seed is not None else env_cfg["seed"],
        seconds=seconds if seconds is not None else env_cfg["seconds"],
        tick_rate=env_cfg["tick_rate"],
        map_id=map_id if map_id is not None else env_cfg.get("map_id", "frosting-grassland"),
        content_dir=env_cfg["content_dir"],
    )


def dry_run(config, algorithm, steps):
    env = build_env(config, seconds=min(config["environment"]["seconds"], 5.0))
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
            "total_reward": round(total_reward, 4),
            "dependencies": dependency_status(),
        }
    finally:
        env.close()


def train(config, algorithm, total_timesteps=None, eval_episodes=None, eval_seconds=None):
    require_dependencies()
    # Imports stay inside the real training path so dry-run remains dependency-light.
    model_classes = stable_baselines_model_classes()

    selected = algorithm_config(config, algorithm)
    train_steps = total_timesteps or selected["total_timesteps"]
    env = build_env(config)
    model_dir = Path(config["outputs"]["model_dir"])
    report_dir = Path(config["outputs"]["report_dir"])
    model_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    model_class = model_classes[algorithm]
    ignored_keys = {"enabled", "policy", "total_timesteps"}
    kwargs = {key: value for key, value in selected.items() if key not in ignored_keys}
    started_at = datetime.now(timezone.utc).isoformat()
    model_path = model_dir / f"{algorithm}_phase1_movement_survival.zip"
    try:
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
        "started_at": started_at,
        "completed_at": completed_at,
        "evaluation_path": str(evaluation_path),
        "known_exploits_path": str(exploit_path),
        "known_exploits": known_exploit_notes["known_exploits"],
    }
    metadata_path = metadata_path_for(config, algorithm)
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
            "seconds": config["environment"]["seconds"],
            "tick_rate": config["environment"]["tick_rate"],
            "content_dir": config["environment"]["content_dir"],
            "started_at": started_at,
            "completed_at": completed_at,
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


def metadata_path_for(config, algorithm):
    metadata_file = config["outputs"]["metadata_file"].format(algorithm=algorithm)
    return Path(config["outputs"]["model_dir"]) / metadata_file


def evaluate_saved_policy(config, algorithm, model_path=None, eval_episodes=None, eval_seconds=None, seed_start=None, map_id=None):
    model_class = stable_baselines_model_classes()[algorithm]
    model = model_class.load(model_path or default_model_path(config, algorithm))
    return evaluate_model(
        model,
        config,
        episodes=eval_episodes or config["evaluation"]["episodes"],
        seconds=eval_seconds or config["evaluation"]["seconds"],
        seed_start=seed_start,
        map_id=map_id,
    )


def evaluate_model(model, config, episodes, seconds, seed_start=None, map_id=None):
    seed_start = seed_start if seed_start is not None else config["evaluation"]["seed_start"]
    map_id = map_id or config["environment"].get("map_id", "frosting-grassland")
    max_steps = int(seconds * config["environment"]["tick_rate"]) + 10
    episode_reports = []
    total_reward = 0.0
    env = None
    try:
        env = build_env(config, seed=seed_start, seconds=seconds, map_id=map_id)
        for index in range(episodes):
            seed = seed_start + index
            observation, info = env.reset(seed=seed, options={"seconds": seconds, "map_id": map_id})
            terminated = False
            truncated = False
            steps = 0
            episode_reward = 0.0
            action_counts = {str(action): 0 for action in range(info["action_count"])}
            reward_breakdown_totals = {}
            while not terminated and not truncated and steps < max_steps:
                action, _state = model.predict(observation, deterministic=True)
                action_index = action_to_int(action)
                action_counts[str(action_index)] = action_counts.get(str(action_index), 0) + 1
                observation, reward, terminated, truncated, info = env.step(action_index)
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
        "episodes": episode_reports,
        "summary": summary,
    }


def action_to_int(action):
    if hasattr(action, "item"):
        return int(action.item())
    if isinstance(action, (list, tuple)):
        return int(action[0])
    return int(action)


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
    summary["reward_breakdown_average"] = summarize_reward_breakdown(episodes)
    return summary


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
    eval_episodes=None,
    eval_seconds=None,
    seed_start=None,
    map_id=None,
    rule_bots=None,
):
    episodes = eval_episodes or config["evaluation"]["episodes"]
    seconds = eval_seconds or config["evaluation"]["seconds"]
    seed_start = seed_start if seed_start is not None else config["evaluation"]["seed_start"]
    map_id = map_id or config["environment"].get("map_id", "frosting-grassland")
    bots = rule_bots or ["random", "kite", "tank"]
    policy = evaluate_saved_policy(
        config,
        algorithm,
        model_path=model_path,
        eval_episodes=episodes,
        eval_seconds=seconds,
        seed_start=seed_start,
        map_id=map_id,
    )
    rule_matrix = run_rule_bot_matrix(config, bots, seed_start, episodes, seconds, map_id)
    findings = comparison_findings(policy, rule_matrix["stdout"])
    return {
        "report_version": 1,
        "status": "compared",
        "phase": config["phase"],
        "algorithm": algorithm,
        "model_path": str(model_path or default_model_path(config, algorithm)),
        "map_id": map_id,
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
    parser.add_argument("--evaluate-model", action="store_true")
    parser.add_argument("--compare-rule-bots", action="store_true")
    parser.add_argument("--rule-bots", default="random,kite,tank")
    parser.add_argument("--report", default=None)
    parser.add_argument("--copy-template", default=None)
    args = parser.parse_args()

    config = load_config(args.config)
    algorithm_config(config, args.algorithm)

    if args.copy_template:
        write_report(args.report, copy_template(args.copy_template))
        return

    if args.check_deps:
        payload = {"status": "ok", "dependencies": dependency_status()}
        write_report(args.report, payload)
        return

    if args.dry_run:
        write_report(args.report, dry_run(config, args.algorithm, args.steps))
        return

    if args.evaluate_model:
        write_report(
            args.report,
            evaluate_saved_policy(
                config,
                args.algorithm,
                model_path=Path(args.model) if args.model else None,
                eval_episodes=args.eval_episodes,
                eval_seconds=args.eval_seconds,
                seed_start=args.seed_start,
                map_id=args.map_id,
            ),
        )
        return

    if args.compare_rule_bots:
        write_report(
            args.report,
            compare_policy_to_rule_bots(
                config,
                args.algorithm,
                model_path=Path(args.model) if args.model else None,
                eval_episodes=args.eval_episodes,
                eval_seconds=args.eval_seconds,
                seed_start=args.seed_start,
                map_id=args.map_id,
                rule_bots=parse_rule_bots(args.rule_bots),
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
        ),
    )


if __name__ == "__main__":
    main()
