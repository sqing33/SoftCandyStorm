import argparse
import importlib.util
import json
import random
from datetime import datetime, timezone
from pathlib import Path


REQUIRED_MODULES = ["numpy", "torch"]


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
            + "; run with python/train/requirements.txt before behavior cloning"
        )
    return status


def dataset_paths(value):
    root = Path(value)
    if root.is_file():
        return [root]
    if root.is_dir():
        paths = sorted(root.rglob("*.jsonl"))
        if paths:
            return paths
    raise ValueError(f"dataset path must be a JSONL file or directory with JSONL files: {value}")


def load_trajectory_dataset(path, limit=None):
    observations = []
    actions = []
    metadata = []
    episode_count = 0
    skipped_upgrade_samples = 0
    paths = dataset_paths(path)

    for dataset_path in paths:
        with dataset_path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if limit is not None and len(actions) >= limit:
                    break
                if not line.strip():
                    continue
                record = json.loads(line)
                record_type = record.get("record_type")
                if record_type == "metadata":
                    metadata.append(
                        {
                            "path": str(dataset_path),
                            "bot": record.get("bot"),
                            "map_id": record.get("map_id"),
                            "observation_version": record.get("observation_version"),
                            "observation_len": record.get("observation_len"),
                            "action_count": record.get("action_count"),
                            "content_hash": record.get("content_hash"),
                        }
                    )
                    continue
                if record_type == "episode":
                    episode_count += 1
                    skipped_upgrade_samples += int(record.get("skipped_upgrade_samples", 0))
                    continue
                if record_type == "summary":
                    continue
                if record_type != "sample":
                    raise ValueError(
                        f"unsupported record_type `{record_type}` in {dataset_path}:{line_number}"
                    )
                observation = record.get("observation")
                action = record.get("action")
                if not isinstance(observation, list) or not observation:
                    raise ValueError(f"sample missing observation in {dataset_path}:{line_number}")
                if not isinstance(action, int):
                    raise ValueError(f"sample missing integer action in {dataset_path}:{line_number}")
                observations.append([float(value) for value in observation])
                actions.append(action)

    if not actions:
        raise ValueError("trajectory dataset contains no sample records")

    observation_len = len(observations[0])
    if any(len(observation) != observation_len for observation in observations):
        raise ValueError("trajectory dataset contains mixed observation lengths")
    action_count = max(actions) + 1
    metadata_action_counts = [
        item["action_count"] for item in metadata if isinstance(item.get("action_count"), int)
    ]
    if metadata_action_counts:
        action_count = max(action_count, max(metadata_action_counts))

    return {
        "paths": [str(path) for path in paths],
        "observations": observations,
        "actions": actions,
        "metadata": metadata,
        "episode_count": episode_count,
        "skipped_upgrade_samples": skipped_upgrade_samples,
        "observation_len": observation_len,
        "action_count": action_count,
    }


def summarize_dataset(dataset):
    action_counts = {str(action): 0 for action in range(dataset["action_count"])}
    for action in dataset["actions"]:
        action_counts[str(action)] = action_counts.get(str(action), 0) + 1
    sample_count = len(dataset["actions"])
    return {
        "paths": dataset["paths"],
        "sample_count": sample_count,
        "episode_count": dataset["episode_count"],
        "skipped_upgrade_samples": dataset["skipped_upgrade_samples"],
        "observation_len": dataset["observation_len"],
        "action_count": dataset["action_count"],
        "action_distribution": {
            action: {
                "count": count,
                "ratio": round(count / max(1, sample_count), 4),
            }
            for action, count in action_counts.items()
        },
        "metadata": dataset["metadata"],
    }


def train_behavior_clone(dataset, args):
    require_dependencies()
    import numpy as np
    import torch
    from torch import nn
    from torch.utils.data import DataLoader, TensorDataset

    if len(dataset["actions"]) < 2:
        raise ValueError("behavior cloning requires at least two trajectory samples")

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    observations = np.asarray(dataset["observations"], dtype=np.float32)
    actions = np.asarray(dataset["actions"], dtype=np.int64)
    indices = np.arange(len(actions))
    np.random.default_rng(args.seed).shuffle(indices)

    validation_count = int(round(len(indices) * args.validation_split))
    validation_count = min(max(validation_count, 1), max(1, len(indices) - 1))
    validation_indices = indices[:validation_count]
    train_indices = indices[validation_count:]

    train_loader = DataLoader(
        TensorDataset(
            torch.from_numpy(observations[train_indices]),
            torch.from_numpy(actions[train_indices]),
        ),
        batch_size=args.batch_size,
        shuffle=True,
    )
    validation_x = torch.from_numpy(observations[validation_indices])
    validation_y = torch.from_numpy(actions[validation_indices])

    model = nn.Sequential(
        nn.Linear(dataset["observation_len"], args.hidden_size),
        nn.ReLU(),
        nn.Linear(args.hidden_size, args.hidden_size),
        nn.ReLU(),
        nn.Linear(args.hidden_size, dataset["action_count"]),
    )
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate)
    class_weight_values, class_weight_report = build_class_weights(
        actions[train_indices],
        dataset["action_count"],
        args.class_weighting,
        np,
        torch,
    )
    loss_fn = nn.CrossEntropyLoss(weight=class_weight_values)
    history = []
    started_at = datetime.now(timezone.utc).isoformat()

    for epoch in range(1, args.epochs + 1):
        model.train()
        total_loss = 0.0
        total_correct = 0
        total_seen = 0
        for batch_x, batch_y in train_loader:
            logits = model(batch_x)
            loss = loss_fn(logits, batch_y)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += float(loss.item()) * len(batch_y)
            total_correct += int((logits.argmax(dim=1) == batch_y).sum().item())
            total_seen += len(batch_y)

        validation_metrics = evaluate_classifier(model, validation_x, validation_y, loss_fn)
        history.append(
            {
                "epoch": epoch,
                "train_loss": round(total_loss / max(1, total_seen), 6),
                "train_accuracy": round(total_correct / max(1, total_seen), 4),
                "validation_loss": validation_metrics["loss"],
                "validation_accuracy": validation_metrics["accuracy"],
            }
        )

    completed_at = datetime.now(timezone.utc).isoformat()
    model_path = Path(args.model_out)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_version": 1,
            "kind": "behavior_clone_mlp",
            "observation_len": dataset["observation_len"],
            "action_count": dataset["action_count"],
            "hidden_size": args.hidden_size,
            "class_weighting": args.class_weighting,
            "class_weights": class_weight_report,
            "state_dict": model.state_dict(),
            "dataset_paths": dataset["paths"],
        },
        model_path,
    )

    return {
        "status": "trained",
        "gate_decision": "behavior_clone_smoke_only_not_policy_gate",
        "model_path": str(model_path),
        "started_at": started_at,
        "completed_at": completed_at,
        "dependency_status": dependency_status(),
        "dataset": summarize_dataset(dataset),
        "training": {
            "seed": args.seed,
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "learning_rate": args.learning_rate,
            "hidden_size": args.hidden_size,
            "validation_split": args.validation_split,
            "class_weighting": args.class_weighting,
            "class_weights": class_weight_report,
            "train_samples": int(len(train_indices)),
            "validation_samples": int(len(validation_indices)),
        },
        "history": history,
        "final": history[-1],
        "limitations": [
            "Behavior cloning imitates rule Bot movement only; it is not a balance or fun gate.",
            "The exported Phase 1 dataset skips upgrade-choice states, matching the current movement-only RL action space.",
            "A cloned policy must still pass Gym evaluation and rule Bot comparison before it can become an RL test Bot candidate.",
        ],
    }


def build_class_weights(actions, action_count, mode, np_module, torch_module):
    if mode == "none":
        return None, [1.0 for _ in range(action_count)]
    counts = np_module.bincount(actions, minlength=action_count).astype(np_module.float32)
    weights = np_module.zeros(action_count, dtype=np_module.float32)
    present = counts > 0.0
    if present.any():
        weights[present] = counts[present].sum() / (present.sum() * counts[present])
    return (
        torch_module.from_numpy(weights),
        [round(float(weight), 6) for weight in weights.tolist()],
    )


class BehaviorClonePolicy:
    def __init__(self, checkpoint_path):
        require_dependencies()
        import torch
        from torch import nn

        self.checkpoint_path = str(checkpoint_path)
        self.checkpoint = torch.load(checkpoint_path, map_location="cpu")
        self.observation_len = int(self.checkpoint["observation_len"])
        self.action_count = int(self.checkpoint["action_count"])
        self.hidden_size = int(self.checkpoint["hidden_size"])
        self.model = nn.Sequential(
            nn.Linear(self.observation_len, self.hidden_size),
            nn.ReLU(),
            nn.Linear(self.hidden_size, self.hidden_size),
            nn.ReLU(),
            nn.Linear(self.hidden_size, self.action_count),
        )
        self.model.load_state_dict(self.checkpoint["state_dict"])
        self.model.eval()

    def predict(self, observation, deterministic=True):
        import torch

        probabilities = self._probabilities(observation)
        if deterministic:
            action = int(torch.argmax(probabilities, dim=1).item())
        else:
            action = int(torch.multinomial(probabilities[0], 1).item())
        return action, None

    def action_scores(self, observation):
        probabilities = self._probabilities(observation)
        return {
            "kind": "probability",
            "scores": [float(value) for value in probabilities[0].tolist()],
        }

    def _probabilities(self, observation):
        import numpy as np
        import torch

        values = np.asarray(observation, dtype=np.float32).reshape(1, -1)
        if values.shape[1] != self.observation_len:
            raise ValueError(
                f"expected observation length {self.observation_len}, got {values.shape[1]}"
            )
        with torch.no_grad():
            logits = self.model(torch.from_numpy(values))
            return torch.softmax(logits, dim=1)


def load_behavior_clone_policy(path):
    checkpoint_path = Path(path)
    if not checkpoint_path.exists():
        raise ValueError(f"behavior clone model does not exist: {checkpoint_path}")
    return BehaviorClonePolicy(checkpoint_path)


def evaluate_classifier(model, x, y, loss_fn):
    import torch

    model.eval()
    with torch.no_grad():
        logits = model(x)
        loss = loss_fn(logits, y)
        accuracy = (logits.argmax(dim=1) == y).float().mean()
    return {
        "loss": round(float(loss.item()), 6),
        "accuracy": round(float(accuracy.item()), 4),
    }


def write_report(path, payload):
    if path is None:
        print(json.dumps(payload, ensure_ascii=False))
        return
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Train a movement behavior clone from Soft Candy Storm rule Bot trajectories."
    )
    parser.add_argument("--dataset", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--check-deps", action="store_true")
    parser.add_argument("--limit-samples", type=int, default=None)
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--hidden-size", type=int, default=128)
    parser.add_argument("--learning-rate", type=float, default=0.001)
    parser.add_argument("--validation-split", type=float, default=0.2)
    parser.add_argument(
        "--class-weighting",
        choices=["none", "inverse_frequency"],
        default="none",
        help="Reweight cross entropy by action frequency to reduce majority-action collapse.",
    )
    parser.add_argument("--seed", type=int, default=12345)
    parser.add_argument(
        "--model-out",
        default="python/train/models/behavior_clone_movement_policy.pt",
    )
    parser.add_argument("--report", default=None)
    args = parser.parse_args()

    if args.check_deps:
        write_report(args.report, {"status": "ok", "dependencies": dependency_status()})
        return
    if args.dataset is None:
        parser.error("--dataset is required unless --check-deps is used")
    if args.epochs <= 0:
        parser.error("--epochs must be greater than zero")
    if args.batch_size <= 0:
        parser.error("--batch-size must be greater than zero")
    if args.hidden_size <= 0:
        parser.error("--hidden-size must be greater than zero")
    if not (0.0 < args.validation_split < 1.0):
        parser.error("--validation-split must be between 0 and 1")
    if args.limit_samples is not None and args.limit_samples <= 0:
        parser.error("--limit-samples must be greater than zero")

    try:
        dataset = load_trajectory_dataset(args.dataset, limit=args.limit_samples)
        if args.dry_run:
            write_report(
                args.report,
                {
                    "status": "ok",
                    "mode": "dry_run",
                    "gate_decision": "dataset_validated_not_training_gate",
                    "dataset": summarize_dataset(dataset),
                    "dependencies": dependency_status(),
                },
            )
            return
        write_report(args.report, train_behavior_clone(dataset, args))
    except (OSError, RuntimeError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
