import argparse
import importlib.util
import json
import random
from datetime import datetime, timezone
from pathlib import Path


REQUIRED_MODULES = ["numpy", "torch"]


def build_behavior_clone_model(architecture, input_observation_len, hidden_size, action_count, nn_module):
    if architecture == "mlp":
        return nn_module.Sequential(
            nn_module.Linear(input_observation_len, hidden_size),
            nn_module.ReLU(),
            nn_module.Linear(hidden_size, hidden_size),
            nn_module.ReLU(),
            nn_module.Linear(hidden_size, action_count),
        )
    if architecture == "gru":
        class GruPolicy(nn_module.Module):
            def __init__(self):
                super().__init__()
                self.gru = nn_module.GRU(
                    input_size=input_observation_len,
                    hidden_size=hidden_size,
                    batch_first=True,
                )
                self.head = nn_module.Linear(hidden_size, action_count)

            def forward(self, values):
                output, _ = self.gru(values)
                return self.head(output[:, -1, :])

        return GruPolicy()
    raise ValueError(f"unsupported behavior clone architecture: {architecture}")


def model_input_width(observations):
    if len(observations.shape) == 3:
        return int(observations.shape[2])
    return int(observations.shape[1])


def model_total_input_len(observations):
    if len(observations.shape) == 3:
        return int(observations.shape[1] * observations.shape[2])
    return int(observations.shape[1])


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
    if isinstance(value, (list, tuple)):
        paths = []
        for item in value:
            paths.extend(dataset_paths(item))
        return sorted(paths)
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
    sample_metadata = []
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
                            "sample_start_seconds": record.get("sample_start_seconds"),
                            "sample_end_seconds": record.get("sample_end_seconds"),
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
                sample_metadata.append(
                    {
                        "path": str(dataset_path),
                        "seed": int(record.get("seed", 0)),
                        "map_id": record.get("map_id"),
                        "tick": int(record.get("tick", 0)),
                        "time_seconds": float(record.get("time_seconds", 0.0)),
                        "health_ratio": float(record.get("health_ratio", 1.0)),
                        "level": int(record.get("level", 0)),
                        "kills": int(record.get("kills", 0)),
                    }
                )

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
        "sample_metadata": sample_metadata,
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
        "sample_summary": summarize_sample_metadata(dataset["sample_metadata"]),
        "metadata": dataset["metadata"],
    }


def summarize_sample_metadata(sample_metadata):
    if not sample_metadata:
        return {}
    map_counts = {}
    times = []
    health_ratios = []
    for item in sample_metadata:
        map_id = item.get("map_id") or "unknown"
        map_counts[map_id] = map_counts.get(map_id, 0) + 1
        times.append(float(item.get("time_seconds", 0.0)))
        health_ratios.append(float(item.get("health_ratio", 1.0)))
    sample_count = len(sample_metadata)
    return {
        "time_seconds_min": round(min(times), 4),
        "time_seconds_max": round(max(times), 4),
        "health_ratio_min": round(min(health_ratios), 4),
        "health_ratio_average": round(sum(health_ratios) / sample_count, 4),
        "map_distribution": {
            map_id: {
                "count": count,
                "ratio": round(count / sample_count, 4),
            }
            for map_id, count in sorted(map_counts.items())
        },
    }


def train_behavior_clone(dataset, args):
    require_dependencies()
    import numpy as np
    import torch
    from torch import nn
    from torch.utils.data import DataLoader, TensorDataset, WeightedRandomSampler

    if len(dataset["actions"]) < 2:
        raise ValueError("behavior cloning requires at least two trajectory samples")

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    if args.architecture == "gru":
        observations, context_report = build_context_observation_sequences(
            dataset,
            args.context_frames,
            np,
        )
    else:
        observations, context_report = build_context_observations(dataset, args.context_frames, np)
    observations, map_conditioning_report = apply_map_conditioning(
        observations,
        dataset,
        args.map_conditioning,
        np,
    )
    actions = np.asarray(dataset["actions"], dtype=np.int64)
    indices = np.arange(len(actions))
    np.random.default_rng(args.seed).shuffle(indices)

    validation_count = int(round(len(indices) * args.validation_split))
    validation_count = min(max(validation_count, 1), max(1, len(indices) - 1))
    validation_indices = indices[:validation_count]
    train_indices = indices[validation_count:]

    train_weights, sample_weight_report = build_sample_weights(
        dataset["sample_metadata"],
        train_indices,
        args,
        np,
    )
    train_dataset = TensorDataset(
        torch.from_numpy(observations[train_indices]),
        torch.from_numpy(actions[train_indices]),
    )
    sampler = None
    shuffle = True
    if train_weights is not None:
        generator = torch.Generator()
        generator.manual_seed(args.seed)
        sampler = WeightedRandomSampler(
            weights=torch.from_numpy(train_weights),
            num_samples=len(train_indices),
            replacement=True,
            generator=generator,
        )
        shuffle = False
    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=shuffle,
        sampler=sampler,
    )
    validation_x = torch.from_numpy(observations[validation_indices])
    validation_y = torch.from_numpy(actions[validation_indices])

    model = build_behavior_clone_model(
        args.architecture,
        model_input_width(observations),
        args.hidden_size,
        dataset["action_count"],
        nn,
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
            "model_version": 2,
            "kind": f"behavior_clone_{args.architecture}",
            "architecture": args.architecture,
            "observation_len": context_report["input_observation_len"],
            "base_observation_len": dataset["observation_len"],
            "context_frames": args.context_frames,
            "map_conditioning": map_conditioning_report,
            "sequence_input_len": model_input_width(observations),
            "total_input_observation_len": model_total_input_len(observations),
            "action_count": dataset["action_count"],
            "hidden_size": args.hidden_size,
            "class_weighting": args.class_weighting,
            "class_weights": class_weight_report,
            "sample_weighting": args.sample_weighting,
            "sample_weights": sample_weight_report,
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
            "architecture": args.architecture,
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "learning_rate": args.learning_rate,
            "hidden_size": args.hidden_size,
            "context_frames": args.context_frames,
            "input_observation_len": model_total_input_len(observations),
            "sequence_input_len": model_input_width(observations),
            "base_observation_len": dataset["observation_len"],
            "map_conditioning": map_conditioning_report,
            "validation_split": args.validation_split,
            "class_weighting": args.class_weighting,
            "class_weights": class_weight_report,
            "sample_weighting": args.sample_weighting,
            "sample_weights": sample_weight_report,
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


def build_context_observations(dataset, context_frames, np_module):
    base_observations = np_module.asarray(dataset["observations"], dtype=np_module.float32)
    if context_frames <= 1:
        return base_observations, {
            "context_frames": 1,
            "base_observation_len": dataset["observation_len"],
            "input_observation_len": dataset["observation_len"],
        }

    histories = {}
    context_rows = []
    history_limit = context_frames - 1
    for observation, sample in zip(base_observations, dataset["sample_metadata"]):
        key = (sample.get("path"), sample.get("seed"))
        history = histories.get(key, [])
        previous = history[-history_limit:]
        missing = history_limit - len(previous)
        frames = [observation for _ in range(missing)]
        frames.extend(previous)
        frames.append(observation)
        context_rows.append(np_module.concatenate(frames).astype(np_module.float32))
        history.append(observation)
        histories[key] = history[-history_limit:]

    return np_module.asarray(context_rows, dtype=np_module.float32), {
        "context_frames": context_frames,
        "base_observation_len": dataset["observation_len"],
        "input_observation_len": dataset["observation_len"] * context_frames,
    }


def build_context_observation_sequences(dataset, context_frames, np_module):
    base_observations = np_module.asarray(dataset["observations"], dtype=np_module.float32)
    histories = {}
    sequence_rows = []
    history_limit = context_frames - 1
    for observation, sample in zip(base_observations, dataset["sample_metadata"]):
        key = (sample.get("path"), sample.get("seed"))
        history = histories.get(key, [])
        previous = history[-history_limit:] if history_limit > 0 else []
        missing = history_limit - len(previous)
        frames = [observation for _ in range(missing)]
        frames.extend(previous)
        frames.append(observation)
        sequence_rows.append(np_module.stack(frames).astype(np_module.float32))
        history.append(observation)
        histories[key] = history[-history_limit:] if history_limit > 0 else []

    return np_module.asarray(sequence_rows, dtype=np_module.float32), {
        "context_frames": context_frames,
        "base_observation_len": dataset["observation_len"],
        "input_observation_len": dataset["observation_len"] * context_frames,
        "sequence_input_len": dataset["observation_len"],
    }


def apply_map_conditioning(observations, dataset, mode, np_module):
    base_len = int(observations.shape[-1])
    sequence_len = int(observations.shape[1]) if len(observations.shape) == 3 else None
    if mode == "none":
        report = {
            "mode": "none",
            "map_ids": [],
            "dimension": 0,
            "base_input_observation_len": base_len,
            "input_observation_len": base_len,
        }
        if sequence_len is not None:
            report["sequence_len"] = sequence_len
            report["total_input_observation_len"] = sequence_len * base_len
        return observations, report

    map_ids = sorted(
        {
            str(sample.get("map_id") or "unknown")
            for sample in dataset["sample_metadata"]
        }
    )
    map_index = {map_id: index for index, map_id in enumerate(map_ids)}
    one_hot = np_module.zeros((len(dataset["sample_metadata"]), len(map_ids)), dtype=np_module.float32)
    for row, sample in enumerate(dataset["sample_metadata"]):
        map_id = str(sample.get("map_id") or "unknown")
        one_hot[row, map_index[map_id]] = 1.0
    if len(observations.shape) == 3:
        repeated = np_module.repeat(one_hot[:, None, :], observations.shape[1], axis=1)
        conditioned = np_module.concatenate([observations, repeated], axis=2).astype(np_module.float32)
    else:
        conditioned = np_module.concatenate([observations, one_hot], axis=1).astype(np_module.float32)
    report = {
        "mode": "one_hot",
        "map_ids": map_ids,
        "dimension": len(map_ids),
        "base_input_observation_len": base_len,
        "input_observation_len": int(conditioned.shape[-1]),
    }
    if sequence_len is not None:
        report["sequence_len"] = sequence_len
        report["total_input_observation_len"] = int(conditioned.shape[1] * conditioned.shape[2])
    return conditioned, report


def build_sample_weights(sample_metadata, indices, args, np_module):
    if args.sample_weighting == "none":
        return None, {
            "mode": "none",
            "min": 1.0,
            "max": 1.0,
            "mean": 1.0,
        }

    weights = []
    for index in indices:
        sample = sample_metadata[int(index)]
        health_ratio = clamp(float(sample.get("health_ratio", 1.0)), 0.0, 1.0)
        time_seconds = max(0.0, float(sample.get("time_seconds", 0.0)))
        low_health_pressure = max(
            0.0,
            (args.danger_health_threshold - health_ratio)
            / max(0.0001, args.danger_health_threshold),
        )
        late_pressure = clamp(
            (time_seconds - args.danger_late_start_seconds)
            / max(0.0001, args.danger_late_horizon_seconds - args.danger_late_start_seconds),
            0.0,
            1.0,
        )
        weights.append(
            1.0
            + args.danger_low_health_weight * low_health_pressure
            + args.danger_late_weight * late_pressure
        )

    values = np_module.asarray(weights, dtype=np_module.float32)
    return values, {
        "mode": args.sample_weighting,
        "min": round(float(values.min()), 6),
        "max": round(float(values.max()), 6),
        "mean": round(float(values.mean()), 6),
        "danger_health_threshold": args.danger_health_threshold,
        "danger_low_health_weight": args.danger_low_health_weight,
        "danger_late_start_seconds": args.danger_late_start_seconds,
        "danger_late_horizon_seconds": args.danger_late_horizon_seconds,
        "danger_late_weight": args.danger_late_weight,
    }


def clamp(value, minimum, maximum):
    return min(max(value, minimum), maximum)


class BehaviorClonePolicy:
    def __init__(self, checkpoint_path):
        require_dependencies()
        import torch
        from torch import nn

        self.checkpoint_path = str(checkpoint_path)
        self.checkpoint = torch.load(checkpoint_path, map_location="cpu")
        self.architecture = self.checkpoint.get(
            "architecture",
            "gru" if self.checkpoint.get("kind") == "behavior_clone_gru" else "mlp",
        )
        self.context_observation_len = int(self.checkpoint["observation_len"])
        self.base_observation_len = int(
            self.checkpoint.get("base_observation_len", self.context_observation_len)
        )
        self.context_frames = int(self.checkpoint.get("context_frames", 1))
        self.map_conditioning = self.checkpoint.get(
            "map_conditioning",
            {
                "mode": "none",
                "map_ids": [],
                "dimension": 0,
                "base_input_observation_len": self.context_observation_len,
                "input_observation_len": self.context_observation_len,
            },
        )
        self.input_observation_len = int(
            self.map_conditioning.get("input_observation_len", self.context_observation_len)
        )
        self.sequence_input_len = int(
            self.checkpoint.get("sequence_input_len", self.input_observation_len)
        )
        self.current_map_id = None
        self.action_count = int(self.checkpoint["action_count"])
        self.hidden_size = int(self.checkpoint["hidden_size"])
        self.history = []
        self._last_observation = None
        self._last_scores = None
        model_input_len = (
            self.sequence_input_len
            if self.architecture == "gru"
            else self.input_observation_len
        )
        self.model = build_behavior_clone_model(
            self.architecture,
            model_input_len,
            self.hidden_size,
            self.action_count,
            nn,
        )
        self.model.load_state_dict(self.checkpoint["state_dict"])
        self.model.eval()

    def reset(self):
        self.history = []
        self._last_observation = None
        self._last_scores = None

    def set_map_id(self, map_id):
        self.current_map_id = str(map_id) if map_id is not None else None
        self._last_observation = None
        self._last_scores = None

    def predict(self, observation, deterministic=True):
        import torch

        probabilities = self._probabilities(observation, update_history=True)
        if deterministic:
            action = int(torch.argmax(probabilities, dim=1).item())
        else:
            action = int(torch.multinomial(probabilities[0], 1).item())
        return action, None

    def action_scores(self, observation):
        values = self._base_observation_values(observation)
        if (
            self._last_observation is not None
            and values.shape == self._last_observation.shape
            and (values == self._last_observation).all()
            and self._last_scores is not None
        ):
            return {
                "kind": "probability",
                "scores": list(self._last_scores),
            }
        probabilities = self._probabilities(values, update_history=False)
        return {
            "kind": "probability",
            "scores": [float(value) for value in probabilities[0].tolist()],
        }

    def _probabilities(self, observation, update_history):
        import numpy as np
        import torch

        values = self._base_observation_values(observation)
        features = self._features(values, np, update_history=update_history)
        with torch.no_grad():
            if self.architecture == "gru":
                logits = self.model(torch.from_numpy(features.reshape(1, features.shape[0], features.shape[1])))
            else:
                logits = self.model(torch.from_numpy(features.reshape(1, -1)))
            probabilities = torch.softmax(logits, dim=1)
        if update_history:
            self._last_observation = values.copy()
            self._last_scores = [float(value) for value in probabilities[0].tolist()]
        return probabilities

    def _base_observation_values(self, observation):
        import numpy as np

        values = np.asarray(observation, dtype=np.float32).reshape(-1)
        if values.shape[0] != self.base_observation_len:
            raise ValueError(
                f"expected observation length {self.base_observation_len}, got {values.shape[0]}"
            )
        return values

    def _features(self, values, np_module, update_history):
        if self.architecture == "gru":
            context_sequence = self._context_sequence(values, np_module, update_history)
            map_features = self._map_features(np_module)
            if map_features.shape[0] > 0:
                repeated = np_module.repeat(map_features.reshape(1, -1), context_sequence.shape[0], axis=0)
                features = np_module.concatenate([context_sequence, repeated], axis=1).astype(np_module.float32)
            else:
                features = context_sequence
            if features.shape[1] != self.sequence_input_len:
                raise ValueError(
                    f"expected behavior clone sequence feature length {self.sequence_input_len}, got {features.shape[1]}"
                )
            return features

        context_features = self._context_features(values, np_module, update_history)
        map_features = self._map_features(np_module)
        if map_features.shape[0] > 0:
            features = np_module.concatenate([context_features, map_features]).astype(np_module.float32)
        else:
            features = context_features
        if features.shape[0] != self.input_observation_len:
            raise ValueError(
                f"expected behavior clone feature length {self.input_observation_len}, got {features.shape[0]}"
            )
        return features

    def _context_features(self, values, np_module, update_history):
        if self.context_frames <= 1:
            return values
        history_limit = self.context_frames - 1
        previous = self.history[-history_limit:]
        missing = history_limit - len(previous)
        frames = [values for _ in range(missing)]
        frames.extend(previous)
        frames.append(values)
        if update_history:
            self.history.append(values.copy())
            self.history = self.history[-history_limit:]
        features = np_module.concatenate(frames).astype(np_module.float32)
        return features

    def _context_sequence(self, values, np_module, update_history):
        history_limit = self.context_frames - 1
        previous = self.history[-history_limit:] if history_limit > 0 else []
        missing = history_limit - len(previous)
        frames = [values for _ in range(missing)]
        frames.extend(previous)
        frames.append(values)
        if update_history and history_limit > 0:
            self.history.append(values.copy())
            self.history = self.history[-history_limit:]
        return np_module.stack(frames).astype(np_module.float32)

    def _map_features(self, np_module):
        mode = self.map_conditioning.get("mode", "none")
        if mode == "none":
            return np_module.zeros(0, dtype=np_module.float32)
        map_ids = list(self.map_conditioning.get("map_ids", []))
        features = np_module.zeros(len(map_ids), dtype=np_module.float32)
        if self.current_map_id is None:
            raise ValueError("behavior clone checkpoint requires map_id conditioning but current map_id is unset")
        try:
            features[map_ids.index(str(self.current_map_id))] = 1.0
        except ValueError as exc:
            raise ValueError(
                f"map_id `{self.current_map_id}` is not in behavior clone map conditioning vocabulary"
            ) from exc
        return features


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
    parser.add_argument(
        "--dataset",
        action="append",
        default=None,
        help="JSONL file or directory with JSONL files. Repeat to combine datasets.",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--check-deps", action="store_true")
    parser.add_argument("--limit-samples", type=int, default=None)
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--hidden-size", type=int, default=128)
    parser.add_argument(
        "--architecture",
        choices=["mlp", "gru"],
        default="mlp",
        help="Classifier architecture. gru keeps context frames as a sequence instead of a flat vector.",
    )
    parser.add_argument("--context-frames", type=int, default=1)
    parser.add_argument(
        "--map-conditioning",
        choices=["none", "one_hot"],
        default="none",
        help="Append map-id features to behavior clone observations.",
    )
    parser.add_argument("--learning-rate", type=float, default=0.001)
    parser.add_argument("--validation-split", type=float, default=0.2)
    parser.add_argument(
        "--class-weighting",
        choices=["none", "inverse_frequency"],
        default="none",
        help="Reweight cross entropy by action frequency to reduce majority-action collapse.",
    )
    parser.add_argument(
        "--sample-weighting",
        choices=["none", "danger"],
        default="none",
        help="Use weighted sampling to revisit dangerous states more often.",
    )
    parser.add_argument("--danger-health-threshold", type=float, default=0.7)
    parser.add_argument("--danger-low-health-weight", type=float, default=2.0)
    parser.add_argument("--danger-late-start-seconds", type=float, default=60.0)
    parser.add_argument("--danger-late-horizon-seconds", type=float, default=300.0)
    parser.add_argument("--danger-late-weight", type=float, default=1.0)
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
    if args.context_frames <= 0:
        parser.error("--context-frames must be greater than zero")
    if not (0.0 < args.validation_split < 1.0):
        parser.error("--validation-split must be between 0 and 1")
    if args.limit_samples is not None and args.limit_samples <= 0:
        parser.error("--limit-samples must be greater than zero")
    if not (0.0 < args.danger_health_threshold <= 1.0):
        parser.error("--danger-health-threshold must be in (0, 1]")
    if args.danger_low_health_weight < 0.0:
        parser.error("--danger-low-health-weight must be greater than or equal to zero")
    if args.danger_late_weight < 0.0:
        parser.error("--danger-late-weight must be greater than or equal to zero")
    if args.danger_late_start_seconds < 0.0:
        parser.error("--danger-late-start-seconds must be greater than or equal to zero")
    if args.danger_late_horizon_seconds <= args.danger_late_start_seconds:
        parser.error("--danger-late-horizon-seconds must be greater than --danger-late-start-seconds")

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
