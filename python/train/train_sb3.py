import argparse
import importlib.util
import json
import shutil
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


def build_env(config, seed=None, seconds=None):
    env_cfg = config["environment"]
    return SoftCandyStormEnv(
        seed=seed if seed is not None else env_cfg["seed"],
        seconds=seconds if seconds is not None else env_cfg["seconds"],
        tick_rate=env_cfg["tick_rate"],
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
    from stable_baselines3 import DQN, PPO

    selected = algorithm_config(config, algorithm)
    train_steps = total_timesteps or selected["total_timesteps"]
    env = build_env(config)
    model_dir = Path(config["outputs"]["model_dir"])
    report_dir = Path(config["outputs"]["report_dir"])
    model_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    model_class = {"dqn": DQN, "ppo": PPO}[algorithm]
    ignored_keys = {"enabled", "policy", "total_timesteps"}
    kwargs = {key: value for key, value in selected.items() if key not in ignored_keys}
    started_at = datetime.now(timezone.utc).isoformat()
    model_path = model_dir / f"{algorithm}_phase1_movement_survival.zip"
    try:
        model = model_class(selected["policy"], env, verbose=1, **kwargs)
        model.learn(total_timesteps=train_steps)
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
    metadata_path = model_dir / config["outputs"]["metadata_file"]
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
            "total_timesteps": train_steps,
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
        "gate_decision": "trained_needs_rule_bot_comparison",
    }
    report_path = report_dir / f"{algorithm}_training_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def evaluate_model(model, config, episodes, seconds):
    seed_start = config["evaluation"]["seed_start"]
    max_steps = int(seconds * config["environment"]["tick_rate"]) + 10
    episode_reports = []
    total_reward = 0.0
    env = None
    try:
        env = build_env(config, seed=seed_start, seconds=seconds)
        for index in range(episodes):
            seed = seed_start + index
            observation, info = env.reset(seed=seed, options={"seconds": seconds})
            terminated = False
            truncated = False
            steps = 0
            episode_reward = 0.0
            while not terminated and not truncated and steps < max_steps:
                action, _state = model.predict(observation, deterministic=True)
                observation, reward, terminated, truncated, info = env.step(action_to_int(action))
                episode_reward += reward
                steps += 1

            total_reward += episode_reward
            terminal = info.get("terminal") or {}
            episode_reports.append(
                {
                    "seed": seed,
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
    return {
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


def known_exploits_from_evaluation(evaluation):
    summary = evaluation["summary"]
    known_exploits = []
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
