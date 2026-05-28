import argparse
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from python.train.train_behavior_clone import (
    load_trajectory_dataset,
    summarize_dataset,
)
from python.train.train_sb3 import (
    algorithm_config,
    build_env,
    dependency_status,
    load_behavior_clone_policy_with_optional_opening,
    load_config,
    require_dependencies,
    stable_baselines_model_classes,
)


def one_hot(action, action_count, np_module):
    values = np_module.zeros(action_count, dtype=np_module.float32)
    values[int(action)] = 1.0
    return values


def normalized_probabilities(values, action_count, np_module):
    probabilities = np_module.asarray(values[:action_count], dtype=np_module.float32)
    probabilities = np_module.clip(probabilities, 0.0, 1.0)
    total = float(probabilities.sum())
    if total <= 0.0:
        raise ValueError("teacher returned an empty probability distribution")
    return probabilities / total


def target_entropy(probabilities, np_module):
    clipped = np_module.clip(probabilities, 1e-8, 1.0)
    return float(-(clipped * np_module.log(clipped)).sum())


def soften_probabilities(probabilities, temperature, np_module):
    if temperature == 1.0:
        return probabilities
    clipped = np_module.clip(probabilities, 1e-8, 1.0)
    logits = np_module.log(clipped) / temperature
    logits = logits - float(logits.max())
    softened = np_module.exp(logits)
    return softened / float(softened.sum())


def mix_with_uniform(probabilities, uniform_mix, np_module):
    if uniform_mix == 0.0:
        return probabilities
    action_count = int(len(probabilities))
    uniform = np_module.full(action_count, 1.0 / action_count, dtype=np_module.float32)
    mixed = probabilities * (1.0 - uniform_mix) + uniform * uniform_mix
    return mixed / float(mixed.sum())


def transform_target_probabilities(probabilities, temperature, uniform_mix, np_module):
    transformed = soften_probabilities(probabilities, temperature, np_module)
    return mix_with_uniform(transformed, uniform_mix, np_module)


def target_transform_report(temperature, uniform_mix):
    return {
        "teacher_temperature": temperature,
        "uniform_target_mix": uniform_mix,
    }


def collect_distillation_targets(
    dataset,
    teacher_model,
    target_mode,
    teacher_temperature,
    uniform_target_mix,
    np_module,
    opening_algorithm="ppo",
    opening_model=None,
    opening_seconds=60.0,
):
    action_count = int(dataset["action_count"])
    if target_mode == "dataset_actions":
        targets = [
            transform_target_probabilities(
                one_hot(action, action_count, np_module),
                1.0,
                uniform_target_mix,
                np_module,
            )
            for action in dataset["actions"]
        ]
        return np_module.asarray(targets, dtype=np_module.float32), {
            "mode": target_mode,
            "teacher_model": None,
            "opening_model": None,
            "opening_seconds": None,
            "teacher_argmax_agreement": None,
            "target_transform": target_transform_report(1.0, uniform_target_mix),
            "target_entropy_nats": round(
                sum(target_entropy(target, np_module) for target in targets)
                / max(1, len(targets)),
                6,
            ),
            "target_argmax_distribution": action_distribution(
                [int(action) for action in dataset["actions"]],
                action_count,
            ),
        }

    teacher = load_behavior_clone_policy_with_optional_opening(
        opening_algorithm,
        teacher_model,
        opening_model_path=opening_model,
        opening_seconds=opening_seconds,
    )
    targets = []
    teacher_argmax_actions = []
    agreement_count = 0
    active_episode = None
    for observation, action, sample in zip(
        dataset["observations"],
        dataset["actions"],
        dataset["sample_metadata"],
    ):
        episode_key = (sample.get("path"), sample.get("seed"))
        if episode_key != active_episode:
            teacher.reset()
            set_map_id = getattr(teacher, "set_map_id", None)
            if callable(set_map_id):
                set_map_id(sample.get("map_id"))
            active_episode = episode_key
        set_step_context = getattr(teacher, "set_step_context", None)
        if callable(set_step_context):
            set_step_context(
                {
                    "time_seconds": sample.get("time_seconds", 0.0),
                    "map_id": sample.get("map_id"),
                    "seed": sample.get("seed"),
                }
            )
        predicted_action, _state = teacher.predict(observation, deterministic=True)
        scores = teacher.action_scores(observation)
        if scores.get("kind") != "probability":
            raise ValueError(
                "teacher model must expose probability action_scores for soft distillation"
            )
        probabilities = normalized_probabilities(
            scores.get("scores", []),
            action_count,
            np_module,
        )
        probabilities = transform_target_probabilities(
            probabilities,
            teacher_temperature,
            uniform_target_mix,
            np_module,
        )
        targets.append(probabilities)
        teacher_argmax = int(predicted_action)
        teacher_argmax_actions.append(teacher_argmax)
        if teacher_argmax == int(action):
            agreement_count += 1

    return np_module.asarray(targets, dtype=np_module.float32), {
        "mode": target_mode,
        "teacher_model": str(teacher_model),
        "opening_model": str(opening_model) if opening_model else None,
        "opening_seconds": opening_seconds if opening_model else None,
        "teacher_argmax_agreement": round(
            agreement_count / max(1, len(dataset["actions"])),
            4,
        ),
        "target_transform": target_transform_report(
            teacher_temperature,
            uniform_target_mix,
        ),
        "target_entropy_nats": round(
            sum(target_entropy(target, np_module) for target in targets)
            / max(1, len(targets)),
            6,
        ),
        "target_argmax_distribution": action_distribution(
            teacher_argmax_actions,
            action_count,
        ),
    }


def action_distribution(actions, action_count):
    counts = {str(action): 0 for action in range(action_count)}
    for action in actions:
        counts[str(action)] = counts.get(str(action), 0) + 1
    total = max(1, len(actions))
    return {
        action: {
            "count": count,
            "ratio": round(count / total, 4),
        }
        for action, count in counts.items()
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


def evaluate_supervised(model, observations, targets, torch_module):
    model.policy.set_training_mode(False)
    with torch_module.no_grad():
        logits = tensor_distribution_logits(model, observations, torch_module)
        log_probs = torch_module.log_softmax(logits, dim=-1)
        loss = -(targets * log_probs).sum(dim=1).mean()
        predictions = logits.argmax(dim=1)
        labels = targets.argmax(dim=1)
        accuracy = (predictions == labels).float().mean()
        entropy = -(torch_module.softmax(logits, dim=-1) * log_probs).sum(dim=1).mean()
    model.policy.set_training_mode(True)
    return {
        "loss": round(float(loss.item()), 6),
        "argmax_accuracy": round(float(accuracy.item()), 4),
        "policy_entropy_nats": round(float(entropy.item()), 6),
    }


def distill(config, args):
    require_dependencies()
    import numpy as np
    import torch
    from torch.utils.data import DataLoader, TensorDataset

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    dataset = load_trajectory_dataset(args.dataset, limit=args.limit_samples)
    targets, target_report = collect_distillation_targets(
        dataset,
        Path(args.teacher_model) if args.teacher_model else None,
        args.target_mode,
        args.teacher_temperature,
        args.uniform_target_mix,
        np,
        opening_algorithm=args.opening_algorithm,
        opening_model=Path(args.opening_model) if args.opening_model else None,
        opening_seconds=args.opening_seconds,
    )
    observations = np.asarray(dataset["observations"], dtype=np.float32)
    if observations.shape[1] != int(config["environment"]["observation_len"]):
        raise ValueError(
            "dataset observation length does not match rl_training_config observation_len"
        )

    indices = np.arange(len(observations))
    np.random.default_rng(args.seed).shuffle(indices)
    validation_count = int(round(len(indices) * args.validation_split))
    validation_count = min(max(validation_count, 1), max(1, len(indices) - 1))
    validation_indices = indices[:validation_count]
    train_indices = indices[validation_count:]

    selected = algorithm_config(config, "ppo")
    ignored_keys = {"enabled", "policy", "total_timesteps"}
    algorithm_parameters = {
        key: value for key, value in selected.items() if key not in ignored_keys
    }
    env = build_env(
        config,
        seed=config["environment"]["seed"],
        seconds=args.env_seconds or config["environment"]["seconds"],
    )
    model_path = Path(args.model_out)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    started_at = datetime.now(timezone.utc).isoformat()
    try:
        model = stable_baselines_model_classes()["ppo"](
            selected["policy"],
            env,
            verbose=0,
            **algorithm_parameters,
        )
        optimizer = torch.optim.Adam(model.policy.parameters(), lr=args.learning_rate)
        train_dataset = TensorDataset(
            torch.from_numpy(observations[train_indices]),
            torch.from_numpy(targets[train_indices]),
        )
        train_loader = DataLoader(
            train_dataset,
            batch_size=args.batch_size,
            shuffle=True,
        )
        validation_x = torch.from_numpy(observations[validation_indices])
        validation_y = torch.from_numpy(targets[validation_indices])
        history = []
        for epoch in range(1, args.epochs + 1):
            model.policy.set_training_mode(True)
            total_loss = 0.0
            total_seen = 0
            total_correct = 0
            for batch_x, batch_y in train_loader:
                logits = tensor_distribution_logits(model, batch_x, torch)
                log_probs = torch.log_softmax(logits, dim=-1)
                loss = -(batch_y * log_probs).sum(dim=1).mean()
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                total_loss += float(loss.item()) * len(batch_y)
                total_seen += len(batch_y)
                total_correct += int(
                    (logits.argmax(dim=1) == batch_y.argmax(dim=1)).sum().item()
                )
            validation_metrics = evaluate_supervised(model, validation_x, validation_y, torch)
            history.append(
                {
                    "epoch": epoch,
                    "train_loss": round(total_loss / max(1, total_seen), 6),
                    "train_argmax_accuracy": round(total_correct / max(1, total_seen), 4),
                    "validation_loss": validation_metrics["loss"],
                    "validation_argmax_accuracy": validation_metrics["argmax_accuracy"],
                    "validation_policy_entropy_nats": validation_metrics[
                        "policy_entropy_nats"
                    ],
                }
            )
        completed_at = datetime.now(timezone.utc).isoformat()
        model.save(model_path)
    finally:
        env.close()

    metadata_path = model_path.with_name(f"{model_path.stem}_metadata.json")
    metadata = {
        "model_version": 1,
        "algorithm": "ppo",
        "phase": config["phase"],
        "model_path": str(model_path),
        "config_file": str(args.config),
        "distillation_source": target_report,
        "observation_version": config["environment"].get("observation_version", 2),
        "observation_len": config["environment"]["observation_len"],
        "algorithm_parameters": algorithm_parameters,
        "started_at": started_at,
        "completed_at": completed_at,
    }
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    return {
        "status": "trained",
        "algorithm": "ppo",
        "model_path": str(model_path),
        "metadata_path": str(metadata_path),
        "gate_decision": "sb3_distillation_smoke_only_not_policy_gate",
        "dependency_status": dependency_status(),
        "dataset": summarize_dataset(dataset),
        "target": target_report,
        "training": {
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "learning_rate": args.learning_rate,
            "teacher_temperature": args.teacher_temperature,
            "uniform_target_mix": args.uniform_target_mix,
            "seed": args.seed,
            "train_samples": int(len(train_indices)),
            "validation_samples": int(len(validation_indices)),
            "started_at": started_at,
            "completed_at": completed_at,
        },
        "history": history,
        "final": history[-1] if history else {},
        "limitations": [
            "This script distills supervised targets into a PPO MlpPolicy initialization; it does not run PPO environment optimization.",
            "A distilled model must still pass high-pressure comparison and RL policy acceptance before it can become an RL test Bot candidate.",
        ],
    }


def write_report(path, payload):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Distill behavior clone or trajectory actions into an SB3 PPO policy."
    )
    parser.add_argument("--config", default="python/train/rl_training_config.json")
    parser.add_argument("--dataset", action="append", required=True)
    parser.add_argument("--teacher-model", default=None)
    parser.add_argument(
        "--opening-model",
        default=None,
        help="Optional SB3 zip used as teacher before --opening-seconds when target-mode is teacher_probs.",
    )
    parser.add_argument(
        "--opening-algorithm",
        choices=["dqn", "ppo"],
        default="ppo",
        help="SB3 algorithm class used to load --opening-model.",
    )
    parser.add_argument(
        "--opening-seconds",
        type=float,
        default=60.0,
        help="Duration for --opening-model before falling back to --teacher-model.",
    )
    parser.add_argument(
        "--target-mode",
        choices=["teacher_probs", "dataset_actions"],
        default="teacher_probs",
    )
    parser.add_argument("--limit-samples", type=int, default=None)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--learning-rate", type=float, default=0.0003)
    parser.add_argument(
        "--teacher-temperature",
        type=float,
        default=1.0,
        help="Soften teacher probability targets before supervised PPO distillation.",
    )
    parser.add_argument(
        "--uniform-target-mix",
        type=float,
        default=0.0,
        help="Mix target probabilities with a uniform distribution to raise entropy.",
    )
    parser.add_argument("--validation-split", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=12345)
    parser.add_argument("--env-seconds", type=float, default=None)
    parser.add_argument("--model-out", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()

    if args.target_mode == "teacher_probs" and not args.teacher_model:
        parser.error("--target-mode teacher_probs requires --teacher-model")
    if args.opening_model and args.target_mode != "teacher_probs":
        parser.error("--opening-model requires --target-mode teacher_probs")
    if args.opening_model and args.opening_seconds <= 0.0:
        parser.error("--opening-seconds must be greater than zero")
    if args.limit_samples is not None and args.limit_samples <= 0:
        parser.error("--limit-samples must be greater than zero")
    if args.epochs <= 0:
        parser.error("--epochs must be greater than zero")
    if args.batch_size <= 0:
        parser.error("--batch-size must be greater than zero")
    if args.learning_rate <= 0.0:
        parser.error("--learning-rate must be greater than zero")
    if args.teacher_temperature <= 0.0:
        parser.error("--teacher-temperature must be greater than zero")
    if not (0.0 <= args.uniform_target_mix <= 1.0):
        parser.error("--uniform-target-mix must be between 0 and 1")
    if not (0.0 < args.validation_split < 1.0):
        parser.error("--validation-split must be between 0 and 1")
    if args.env_seconds is not None and args.env_seconds <= 0.0:
        parser.error("--env-seconds must be greater than zero")

    config = load_config(args.config)
    report = distill(config, args)
    write_report(args.report, report)


if __name__ == "__main__":
    main()
