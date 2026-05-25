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


def train(config, algorithm):
    require_dependencies()
    # Imports stay inside the real training path so dry-run remains dependency-light.
    from stable_baselines3 import DQN, PPO

    selected = algorithm_config(config, algorithm)
    env = build_env(config)
    model_dir = Path(config["outputs"]["model_dir"])
    report_dir = Path(config["outputs"]["report_dir"])
    model_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    model_class = {"dqn": DQN, "ppo": PPO}[algorithm]
    ignored_keys = {"enabled", "policy", "total_timesteps"}
    kwargs = {key: value for key, value in selected.items() if key not in ignored_keys}
    started_at = datetime.now(timezone.utc).isoformat()
    model = model_class(selected["policy"], env, verbose=1, **kwargs)
    model.learn(total_timesteps=selected["total_timesteps"])
    completed_at = datetime.now(timezone.utc).isoformat()

    model_path = model_dir / f"{algorithm}_phase1_movement_survival.zip"
    model.save(model_path)
    env.close()

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
        "known_exploits": [],
    }
    metadata_path = model_dir / config["outputs"]["metadata_file"]
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    report = {
        "status": "trained",
        "algorithm": algorithm,
        "model_path": str(model_path),
        "metadata_path": str(metadata_path),
        "dependency_status": dependency_status(),
        "training": {
            "total_timesteps": selected["total_timesteps"],
            "seed": config["environment"]["seed"],
            "seconds": config["environment"]["seconds"],
            "tick_rate": config["environment"]["tick_rate"],
            "content_dir": config["environment"]["content_dir"],
            "started_at": started_at,
            "completed_at": completed_at,
        },
        "gate_decision": "needs_evaluation",
    }
    report_path = report_dir / f"{algorithm}_training_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


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

    write_report(args.report, train(config, args.algorithm))


if __name__ == "__main__":
    main()
