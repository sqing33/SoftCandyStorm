import argparse
import importlib.util
import json
import random
from datetime import datetime, timezone
from pathlib import Path


REQUIRED_MODULES = ["numpy", "torch"]
TIME_PHASE_LABELS = ["opening", "mid", "late"]
DEFAULT_TIME_PHASE_THRESHOLDS = [0.2, 0.6]
DEFAULT_MOVEMENT_ACTION_COUNT = 9
TIME_PHASE_BALANCE_WEIGHTING_MODES = {
    "time_phase_balance",
    "time_phase_balance_danger",
    "time_phase_balance_action_change",
    "time_phase_balance_danger_action_change",
}


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
    upgrade_sample_records = 0
    edge_recovery_sample_records = 0
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
                if record_type == "upgrade_sample":
                    upgrade_sample_records += 1
                    continue
                if record_type == "edge_recovery_supervision_sample":
                    if record.get("sample_role") != "repair_training_input":
                        raise ValueError(
                            f"edge recovery sample must be repair_training_input in {dataset_path}:{line_number}"
                        )
                    observation = record.get("observation")
                    action = record.get("target_action")
                    if not isinstance(observation, list) or not observation:
                        raise ValueError(
                            f"edge recovery sample missing observation in {dataset_path}:{line_number}"
                        )
                    if not isinstance(action, int):
                        raise ValueError(
                            f"edge recovery sample missing integer target_action in {dataset_path}:{line_number}"
                        )
                    observations.append([float(value) for value in observation])
                    actions.append(action)
                    edge_recovery_sample_records += 1
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
                            "sample_source": "edge_recovery_supervision",
                            "original_action": record.get("original_action"),
                        }
                    )
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
    if edge_recovery_sample_records:
        action_count = max(action_count, DEFAULT_MOVEMENT_ACTION_COUNT)

    return {
        "paths": [str(path) for path in paths],
        "observations": observations,
        "actions": actions,
        "sample_metadata": sample_metadata,
        "metadata": metadata,
        "episode_count": episode_count,
        "skipped_upgrade_samples": skipped_upgrade_samples,
        "upgrade_sample_records": upgrade_sample_records,
        "edge_recovery_sample_records": edge_recovery_sample_records,
        "observation_len": observation_len,
        "action_count": action_count,
    }


def load_upgrade_choice_dataset(path, limit=None):
    samples = []
    metadata = []
    paths = dataset_paths(path)

    for dataset_path in paths:
        with dataset_path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if limit is not None and len(samples) >= limit:
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
                            "include_upgrade_samples": record.get("include_upgrade_samples"),
                            "content_hash": record.get("content_hash"),
                        }
                    )
                    continue
                if record_type != "upgrade_sample":
                    continue
                options = record.get("upgrade_options")
                if not isinstance(options, list) or not options:
                    raise ValueError(
                        f"upgrade_sample missing upgrade_options in {dataset_path}:{line_number}"
                    )
                chosen_index = record.get("chosen_index")
                if chosen_index is not None and not isinstance(chosen_index, int):
                    raise ValueError(
                        f"upgrade_sample chosen_index must be integer or null in {dataset_path}:{line_number}"
                    )
                observation = record.get("observation")
                if not isinstance(observation, list) or not observation:
                    raise ValueError(
                        f"upgrade_sample missing observation in {dataset_path}:{line_number}"
                    )
                samples.append(
                    {
                        "path": str(dataset_path),
                        "seed": int(record.get("seed", 0)),
                        "map_id": record.get("map_id"),
                        "bot": record.get("bot"),
                        "tick": int(record.get("tick", 0)),
                        "time_seconds": float(record.get("time_seconds", 0.0)),
                        "health_ratio": float(record.get("health_ratio", 1.0)),
                        "level": int(record.get("level", 0)),
                        "kills": int(record.get("kills", 0)),
                        "upgrade_options": [str(option) for option in options],
                        "chosen_index": chosen_index,
                        "chosen_upgrade_id": record.get("chosen_upgrade_id"),
                        "observation": [float(value) for value in observation],
                    }
                )

    if not samples:
        raise ValueError("upgrade choice dataset contains no upgrade_sample records")

    return {
        "paths": [str(path) for path in paths],
        "metadata": metadata,
        "samples": samples,
    }


def summarize_upgrade_choice_dataset(dataset):
    chosen_counts = {}
    option_count_distribution = {}
    map_counts = {}
    for sample in dataset["samples"]:
        map_id = sample.get("map_id") or "unknown"
        map_counts[map_id] = map_counts.get(map_id, 0) + 1
        option_count = len(sample["upgrade_options"])
        option_count_distribution[str(option_count)] = (
            option_count_distribution.get(str(option_count), 0) + 1
        )
        chosen = sample.get("chosen_upgrade_id") or "none"
        chosen_counts[chosen] = chosen_counts.get(chosen, 0) + 1
    sample_count = len(dataset["samples"])
    return {
        "paths": dataset["paths"],
        "sample_count": sample_count,
        "map_distribution": ratio_counts(map_counts, sample_count),
        "option_count_distribution": ratio_counts(option_count_distribution, sample_count),
        "chosen_upgrade_distribution": ratio_counts(chosen_counts, sample_count),
        "metadata": dataset["metadata"],
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
        "upgrade_sample_records": dataset.get("upgrade_sample_records", 0),
        "edge_recovery_sample_records": dataset.get("edge_recovery_sample_records", 0),
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
    source_counts = {}
    times = []
    health_ratios = []
    for item in sample_metadata:
        map_id = item.get("map_id") or "unknown"
        map_counts[map_id] = map_counts.get(map_id, 0) + 1
        source = item.get("sample_source") or "trajectory"
        source_counts[source] = source_counts.get(source, 0) + 1
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
        "sample_source_distribution": {
            source: {
                "count": count,
                "ratio": round(count / sample_count, 4),
            }
            for source, count in sorted(source_counts.items())
        },
    }


def diagnose_sequence_dataset(
    dataset,
    context_frames,
    late_start_seconds=60.0,
    low_health_threshold=0.7,
):
    context_frames = max(1, int(context_frames))
    history_limit = context_frames - 1
    states = {}
    sample_count = len(dataset["actions"])
    per_map = {}
    time_buckets = {
        "opening_lt_late_start": 0,
        "mid_late_start_to_180": 0,
        "late_gte_180": 0,
    }
    span_values = []
    total_missing_frames = 0
    fully_seeded_samples = 0
    transition_count = 0
    same_action_count = 0
    late_low_health_samples = 0

    for action, sample in zip(dataset["actions"], dataset["sample_metadata"]):
        map_id = str(sample.get("map_id") or "unknown")
        time_seconds = float(sample.get("time_seconds", 0.0))
        health_ratio = float(sample.get("health_ratio", 1.0))
        key = (sample.get("path"), sample.get("seed"))
        state = states.setdefault(key, {"times": [], "last_action": None})
        previous_times = state["times"][-history_limit:] if history_limit > 0 else []
        missing_frames = max(0, history_limit - len(previous_times))
        span_seconds = time_seconds - previous_times[0] if previous_times else 0.0

        total_missing_frames += missing_frames
        if missing_frames == 0:
            fully_seeded_samples += 1
        span_values.append(max(0.0, span_seconds))

        if state["last_action"] is not None:
            transition_count += 1
            if int(state["last_action"]) == int(action):
                same_action_count += 1
        state["last_action"] = int(action)
        state["times"].append(time_seconds)
        if history_limit > 0:
            state["times"] = state["times"][-history_limit:]

        if time_seconds < late_start_seconds:
            time_buckets["opening_lt_late_start"] += 1
        elif time_seconds < 180.0:
            time_buckets["mid_late_start_to_180"] += 1
        else:
            time_buckets["late_gte_180"] += 1

        if time_seconds >= late_start_seconds and health_ratio <= low_health_threshold:
            late_low_health_samples += 1

        map_bucket = per_map.setdefault(
            map_id,
            {
                "sample_count": 0,
                "action_counts": {
                    str(index): 0 for index in range(dataset["action_count"])
                },
                "missing_frames_total": 0,
                "fully_seeded_samples": 0,
                "span_seconds_total": 0.0,
                "late_low_health_samples": 0,
                "time_seconds_min": time_seconds,
                "time_seconds_max": time_seconds,
            },
        )
        map_bucket["sample_count"] += 1
        action_key = str(action)
        map_bucket["action_counts"][action_key] = map_bucket["action_counts"].get(action_key, 0) + 1
        map_bucket["missing_frames_total"] += missing_frames
        map_bucket["fully_seeded_samples"] += 1 if missing_frames == 0 else 0
        map_bucket["span_seconds_total"] += max(0.0, span_seconds)
        if time_seconds >= late_start_seconds and health_ratio <= low_health_threshold:
            map_bucket["late_low_health_samples"] += 1
        map_bucket["time_seconds_min"] = min(map_bucket["time_seconds_min"], time_seconds)
        map_bucket["time_seconds_max"] = max(map_bucket["time_seconds_max"], time_seconds)

    diagnostics = {
        "context_frames": context_frames,
        "history_limit": history_limit,
        "sample_count": sample_count,
        "episode_key_count": len(states),
        "padding": {
            "total_missing_frames": int(total_missing_frames),
            "average_missing_frames": round(total_missing_frames / max(1, sample_count), 4),
            "fully_seeded_samples": int(fully_seeded_samples),
            "fully_seeded_ratio": round(fully_seeded_samples / max(1, sample_count), 4),
        },
        "sequence_span_seconds": summarize_float_values(span_values),
        "action_transitions": {
            "transition_count": transition_count,
            "same_action_count": same_action_count,
            "same_action_ratio": round(same_action_count / max(1, transition_count), 4),
            "changed_action_ratio": round(
                (transition_count - same_action_count) / max(1, transition_count),
                4,
            ),
        },
        "time_buckets": ratio_counts(time_buckets, sample_count),
        "late_low_health": {
            "threshold_time_seconds": late_start_seconds,
            "threshold_health_ratio": low_health_threshold,
            "sample_count": late_low_health_samples,
            "ratio": round(late_low_health_samples / max(1, sample_count), 4),
        },
        "per_map": finalize_sequence_map_diagnostics(per_map),
    }
    diagnostics["diagnosis_flags"] = sequence_diagnosis_flags(diagnostics)
    return diagnostics


def summarize_float_values(values):
    if not values:
        return {"min": 0.0, "average": 0.0, "max": 0.0}
    return {
        "min": round(min(values), 4),
        "average": round(sum(values) / len(values), 4),
        "max": round(max(values), 4),
    }


def ratio_counts(counts, total):
    return {
        key: {
            "count": int(value),
            "ratio": round(value / max(1, total), 4),
        }
        for key, value in counts.items()
    }


def finalize_sequence_map_diagnostics(per_map):
    finalized = {}
    for map_id, item in sorted(per_map.items()):
        sample_count = int(item["sample_count"])
        finalized[map_id] = {
            "sample_count": sample_count,
            "sample_ratio": 0.0,
            "time_seconds_min": round(float(item["time_seconds_min"]), 4),
            "time_seconds_max": round(float(item["time_seconds_max"]), 4),
            "average_missing_frames": round(
                item["missing_frames_total"] / max(1, sample_count),
                4,
            ),
            "fully_seeded_ratio": round(
                item["fully_seeded_samples"] / max(1, sample_count),
                4,
            ),
            "average_sequence_span_seconds": round(
                item["span_seconds_total"] / max(1, sample_count),
                4,
            ),
            "late_low_health_ratio": round(
                item["late_low_health_samples"] / max(1, sample_count),
                4,
            ),
            "action_distribution": ratio_counts(item["action_counts"], sample_count),
        }
    total_samples = sum(item["sample_count"] for item in finalized.values())
    for item in finalized.values():
        item["sample_ratio"] = round(item["sample_count"] / max(1, total_samples), 4)
    return finalized


def sequence_diagnosis_flags(diagnostics):
    flags = []
    fully_seeded_ratio = diagnostics["padding"]["fully_seeded_ratio"]
    if diagnostics["history_limit"] > 0 and fully_seeded_ratio < 0.5:
        flags.append(
            {
                "id": "high_context_padding",
                "severity": "watch",
                "summary": "More than half of samples use padded context frames; export longer contiguous windows or lower context_frames before increasing model size.",
            }
        )
    if diagnostics["action_transitions"]["same_action_ratio"] >= 0.75:
        flags.append(
            {
                "id": "high_action_persistence",
                "severity": "watch",
                "summary": "Consecutive samples often keep the same action; inspect sample stride and deterministic target bias.",
            }
        )
    if diagnostics["late_low_health"]["ratio"] < 0.05:
        flags.append(
            {
                "id": "low_late_low_health_coverage",
                "severity": "watch",
                "summary": "Few samples cover late low-health recovery states; this can hide long-run policy failures.",
            }
        )
    map_ratios = [
        item["sample_ratio"] for item in diagnostics["per_map"].values() if item["sample_count"] > 0
    ]
    if map_ratios and min(map_ratios) > 0.0 and max(map_ratios) / min(map_ratios) >= 2.0:
        flags.append(
            {
                "id": "map_sample_imbalance",
                "severity": "watch",
                "summary": "Map sample coverage is imbalanced; map-conditioned policies should be checked for shifted failure surfaces.",
            }
        )
    return flags


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
    observations, time_phase_conditioning_report = apply_time_phase_conditioning(
        observations,
        dataset,
        args.time_phase_conditioning,
        args.time_phase_thresholds,
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
        dataset,
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
        total_cross_entropy_loss = 0.0
        total_entropy = 0.0
        total_correct = 0
        total_seen = 0
        for batch_x, batch_y in train_loader:
            logits = model(batch_x)
            cross_entropy_loss = loss_fn(logits, batch_y)
            entropy = logit_entropy_nats(logits, torch)
            loss = cross_entropy_loss - args.entropy_regularization * entropy
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += float(loss.item()) * len(batch_y)
            total_cross_entropy_loss += float(cross_entropy_loss.item()) * len(batch_y)
            total_entropy += float(entropy.item()) * len(batch_y)
            total_correct += int((logits.argmax(dim=1) == batch_y).sum().item())
            total_seen += len(batch_y)

        validation_metrics = evaluate_classifier(model, validation_x, validation_y, loss_fn)
        history.append(
            {
                "epoch": epoch,
                "train_loss": round(total_loss / max(1, total_seen), 6),
                "train_cross_entropy_loss": round(
                    total_cross_entropy_loss / max(1, total_seen),
                    6,
                ),
                "train_entropy_nats": round(total_entropy / max(1, total_seen), 6),
                "train_accuracy": round(total_correct / max(1, total_seen), 4),
                "validation_loss": validation_metrics["loss"],
                "validation_entropy_nats": validation_metrics["entropy_nats"],
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
            "time_phase_conditioning": time_phase_conditioning_report,
            "sequence_input_len": model_input_width(observations),
            "total_input_observation_len": model_total_input_len(observations),
            "action_count": dataset["action_count"],
            "hidden_size": args.hidden_size,
            "class_weighting": args.class_weighting,
            "class_weights": class_weight_report,
            "sample_weighting": args.sample_weighting,
            "sample_weights": sample_weight_report,
            "entropy_regularization": args.entropy_regularization,
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
        "sequence_diagnostics": diagnose_sequence_dataset(
            dataset,
            args.context_frames,
            args.danger_late_start_seconds,
            args.danger_health_threshold,
        ),
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
            "time_phase_conditioning": time_phase_conditioning_report,
            "validation_split": args.validation_split,
            "class_weighting": args.class_weighting,
            "class_weights": class_weight_report,
            "sample_weighting": args.sample_weighting,
            "sample_weights": sample_weight_report,
            "entropy_regularization": args.entropy_regularization,
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


def normalize_time_phase_thresholds(thresholds):
    values = [float(value) for value in thresholds]
    if len(values) != 2:
        raise ValueError("time phase conditioning requires exactly two thresholds")
    if not (0.0 < values[0] < values[1] < 1.0):
        raise ValueError("time phase thresholds must satisfy 0 < first < second < 1")
    return values


def apply_time_phase_conditioning(observations, dataset, mode, thresholds, np_module):
    thresholds = normalize_time_phase_thresholds(thresholds)
    base_len = int(observations.shape[-1])
    sequence_len = int(observations.shape[1]) if len(observations.shape) == 3 else None
    if mode == "none":
        report = {
            "mode": "none",
            "labels": [],
            "thresholds": thresholds,
            "dimension": 0,
            "base_input_observation_len": base_len,
            "input_observation_len": base_len,
            "phase_distribution": summarize_time_phase_distribution(dataset, thresholds),
        }
        if sequence_len is not None:
            report["sequence_len"] = sequence_len
            report["total_input_observation_len"] = sequence_len * base_len
        return observations, report

    if mode != "one_hot":
        raise ValueError(f"unsupported time phase conditioning mode: {mode}")

    if len(observations.shape) == 3:
        phase_features = time_phase_one_hot(observations[:, :, 0], thresholds, np_module)
        conditioned = np_module.concatenate([observations, phase_features], axis=2).astype(
            np_module.float32
        )
    else:
        base_observations = np_module.asarray(dataset["observations"], dtype=np_module.float32)
        phase_features = time_phase_one_hot(base_observations[:, 0], thresholds, np_module)
        conditioned = np_module.concatenate([observations, phase_features], axis=1).astype(
            np_module.float32
        )

    report = {
        "mode": "one_hot",
        "labels": TIME_PHASE_LABELS,
        "thresholds": thresholds,
        "dimension": len(TIME_PHASE_LABELS),
        "base_input_observation_len": base_len,
        "input_observation_len": int(conditioned.shape[-1]),
        "phase_distribution": summarize_time_phase_distribution(dataset, thresholds),
    }
    if sequence_len is not None:
        report["sequence_len"] = sequence_len
        report["total_input_observation_len"] = int(conditioned.shape[1] * conditioned.shape[2])
    return conditioned, report


def time_phase_one_hot(time_progress_values, thresholds, np_module):
    progress = np_module.clip(np_module.asarray(time_progress_values, dtype=np_module.float32), 0.0, 1.0)
    indices = np_module.zeros(progress.shape, dtype=np_module.int64)
    indices += progress >= thresholds[0]
    indices += progress >= thresholds[1]
    features = np_module.zeros((*progress.shape, len(TIME_PHASE_LABELS)), dtype=np_module.float32)
    for index in range(len(TIME_PHASE_LABELS)):
        features[..., index] = indices == index
    return features


def summarize_time_phase_distribution(dataset, thresholds):
    counts = {label: 0 for label in TIME_PHASE_LABELS}
    for observation in dataset["observations"]:
        label = time_phase_label(float(observation[0]) if observation else 0.0, thresholds)
        counts[label] += 1
    return ratio_counts(counts, len(dataset["observations"]))


def time_phase_label(progress, thresholds):
    progress = clamp(float(progress), 0.0, 1.0)
    if progress < thresholds[0]:
        return TIME_PHASE_LABELS[0]
    if progress < thresholds[1]:
        return TIME_PHASE_LABELS[1]
    return TIME_PHASE_LABELS[2]


def filter_dataset_by_time_phase(dataset, phase, thresholds):
    thresholds = normalize_time_phase_thresholds(thresholds)
    if phase == "all":
        return dataset, {
            "mode": "all",
            "thresholds": thresholds,
            "before_sample_count": len(dataset["actions"]),
            "after_sample_count": len(dataset["actions"]),
            "phase_distribution": summarize_time_phase_distribution(dataset, thresholds),
        }
    if phase not in TIME_PHASE_LABELS:
        raise ValueError(f"unsupported time phase filter: {phase}")

    keep_indices = [
        index
        for index, observation in enumerate(dataset["observations"])
        if time_phase_label(float(observation[0]) if observation else 0.0, thresholds) == phase
    ]
    if len(keep_indices) < 2:
        raise ValueError(f"time phase filter `{phase}` leaves fewer than two samples")
    filtered = dict(dataset)
    filtered["observations"] = [dataset["observations"][index] for index in keep_indices]
    filtered["actions"] = [dataset["actions"][index] for index in keep_indices]
    filtered["sample_metadata"] = [dataset["sample_metadata"][index] for index in keep_indices]
    filtered["edge_recovery_sample_records"] = sum(
        1
        for sample in filtered["sample_metadata"]
        if sample.get("sample_source") == "edge_recovery_supervision"
    )
    return filtered, {
        "mode": phase,
        "thresholds": thresholds,
        "before_sample_count": len(dataset["actions"]),
        "after_sample_count": len(keep_indices),
        "phase_distribution": summarize_time_phase_distribution(filtered, thresholds),
    }


def build_action_change_flags(sample_metadata, actions):
    flags = []
    previous_actions = {}
    for sample, action in zip(sample_metadata, actions):
        key = (sample.get("path"), sample.get("seed"))
        previous = previous_actions.get(key)
        changed = previous is not None and int(previous) != int(action)
        flags.append(changed)
        previous_actions[key] = int(action)
    return flags


def build_sample_weights(dataset, indices, args, np_module):
    edge_recovery_sample_weight = float(getattr(args, "edge_recovery_sample_weight", 1.0))
    use_edge_recovery_weight = abs(edge_recovery_sample_weight - 1.0) > 1e-6
    if args.sample_weighting == "none" and not use_edge_recovery_weight:
        return None, {
            "mode": "none",
            "min": 1.0,
            "max": 1.0,
            "mean": 1.0,
        }

    sample_metadata = dataset["sample_metadata"]
    action_change_flags = build_action_change_flags(sample_metadata, dataset["actions"])
    use_danger = args.sample_weighting in {
        "danger",
        "danger_action_change",
        "time_phase_balance_danger",
        "time_phase_balance_danger_action_change",
    }
    use_action_change = args.sample_weighting in {
        "action_change",
        "danger_action_change",
        "time_phase_balance_action_change",
        "time_phase_balance_danger_action_change",
    }
    use_time_phase_balance = args.sample_weighting in TIME_PHASE_BALANCE_WEIGHTING_MODES
    phase_multipliers = {}
    phase_balance_report = None
    edge_recovery_weighted_count = 0
    if use_time_phase_balance:
        phase_multipliers, phase_balance_report = build_time_phase_balance_weights(
            dataset,
            indices,
            args.time_phase_thresholds,
        )
    weights = []
    action_change_count = 0
    for index in indices:
        sample = sample_metadata[int(index)]
        weight = 1.0
        if use_danger:
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
            weight += (
                args.danger_low_health_weight * low_health_pressure
                + args.danger_late_weight * late_pressure
            )
        if sample.get("sample_source") == "edge_recovery_supervision":
            weight *= edge_recovery_sample_weight
            edge_recovery_weighted_count += 1
        if use_action_change and action_change_flags[int(index)]:
            weight += args.action_change_weight
            action_change_count += 1
        if use_time_phase_balance:
            observation = dataset["observations"][int(index)]
            phase = time_phase_label(
                float(observation[0]) if observation else 0.0,
                args.time_phase_thresholds,
            )
            weight *= phase_multipliers.get(phase, 1.0)
        weights.append(weight)

    values = np_module.asarray(weights, dtype=np_module.float32)
    report = {
        "mode": "edge_recovery_auxiliary"
        if args.sample_weighting == "none" and use_edge_recovery_weight
        else args.sample_weighting,
        "base_mode": args.sample_weighting,
        "min": round(float(values.min()), 6),
        "max": round(float(values.max()), 6),
        "mean": round(float(values.mean()), 6),
        "edge_recovery_sample_weight": round(edge_recovery_sample_weight, 6),
        "edge_recovery_weighted_sample_count": int(edge_recovery_weighted_count),
        "edge_recovery_weighted_sample_ratio": round(
            edge_recovery_weighted_count / max(1, len(indices)),
            4,
        ),
        "danger_health_threshold": args.danger_health_threshold,
        "danger_low_health_weight": args.danger_low_health_weight,
        "danger_late_start_seconds": args.danger_late_start_seconds,
        "danger_late_horizon_seconds": args.danger_late_horizon_seconds,
        "danger_late_weight": args.danger_late_weight,
    }
    if use_action_change:
        report.update(
            {
                "action_change_weight": args.action_change_weight,
                "action_change_sample_count": int(action_change_count),
                "action_change_sample_ratio": round(
                    action_change_count / max(1, len(indices)),
                    4,
                ),
            }
        )
    if phase_balance_report is not None:
        report["time_phase_balance"] = phase_balance_report
    return values, report


def build_time_phase_balance_weights(dataset, indices, thresholds):
    thresholds = normalize_time_phase_thresholds(thresholds)
    counts = {label: 0 for label in TIME_PHASE_LABELS}
    for index in indices:
        observation = dataset["observations"][int(index)]
        label = time_phase_label(float(observation[0]) if observation else 0.0, thresholds)
        counts[label] += 1
    total = len(indices)
    present_labels = [label for label, count in counts.items() if count > 0]
    phase_count = max(1, len(present_labels))
    multipliers = {
        label: (total / (phase_count * count)) if count > 0 else 0.0
        for label, count in counts.items()
    }
    return multipliers, {
        "labels": TIME_PHASE_LABELS,
        "thresholds": thresholds,
        "train_sample_count": int(total),
        "phase_distribution": ratio_counts(counts, total),
        "phase_multipliers": {
            label: round(float(value), 6) for label, value in multipliers.items()
        },
        "present_phase_count": len(present_labels),
    }


def clamp(value, minimum, maximum):
    return min(max(value, minimum), maximum)


class BehaviorClonePolicy:
    def __init__(self, checkpoint_path, checkpoint=None):
        require_dependencies()
        import torch
        from torch import nn

        self.checkpoint_path = str(checkpoint_path)
        self.checkpoint = checkpoint or torch.load(checkpoint_path, map_location="cpu")
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
        self.time_phase_conditioning = self.checkpoint.get(
            "time_phase_conditioning",
            {
                "mode": "none",
                "labels": [],
                "thresholds": DEFAULT_TIME_PHASE_THRESHOLDS,
                "dimension": 0,
                "base_input_observation_len": self.map_conditioning.get(
                    "input_observation_len",
                    self.context_observation_len,
                ),
                "input_observation_len": self.map_conditioning.get(
                    "input_observation_len",
                    self.context_observation_len,
                ),
            },
        )
        self.input_observation_len = int(
            self.time_phase_conditioning.get(
                "input_observation_len",
                self.map_conditioning.get("input_observation_len", self.context_observation_len),
            )
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
            phase_features = self._time_phase_sequence_features(context_sequence, np_module)
            if phase_features.shape[1] > 0:
                features = np_module.concatenate([features, phase_features], axis=1).astype(np_module.float32)
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
        phase_features = self._time_phase_features(values, np_module)
        if phase_features.shape[0] > 0:
            features = np_module.concatenate([features, phase_features]).astype(np_module.float32)
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

    def _time_phase_features(self, values, np_module):
        mode = self.time_phase_conditioning.get("mode", "none")
        if mode == "none":
            return np_module.zeros(0, dtype=np_module.float32)
        thresholds = normalize_time_phase_thresholds(
            self.time_phase_conditioning.get("thresholds", DEFAULT_TIME_PHASE_THRESHOLDS)
        )
        return time_phase_one_hot([float(values[0])], thresholds, np_module)[0]

    def _time_phase_sequence_features(self, sequence, np_module):
        mode = self.time_phase_conditioning.get("mode", "none")
        if mode == "none":
            return np_module.zeros((sequence.shape[0], 0), dtype=np_module.float32)
        thresholds = normalize_time_phase_thresholds(
            self.time_phase_conditioning.get("thresholds", DEFAULT_TIME_PHASE_THRESHOLDS)
        )
        return time_phase_one_hot(sequence[:, 0], thresholds, np_module)


class StagedBehaviorClonePolicy:
    def __init__(self, checkpoint_path, checkpoint):
        self.checkpoint_path = Path(checkpoint_path)
        self.checkpoint = checkpoint
        self.phase_thresholds = normalize_time_phase_thresholds(
            checkpoint.get("phase_thresholds", DEFAULT_TIME_PHASE_THRESHOLDS)
        )
        self.phase_labels = list(checkpoint.get("phase_labels", TIME_PHASE_LABELS))
        subpolicies = checkpoint.get("subpolicies", [])
        if self.phase_labels != TIME_PHASE_LABELS:
            raise ValueError("staged behavior clone checkpoint has unsupported phase labels")
        self.subpolicies = {}
        for item in subpolicies:
            if not isinstance(item, dict):
                raise ValueError("staged behavior clone subpolicies must be objects")
            phase = item.get("phase")
            model_path = item.get("model_path")
            if phase not in TIME_PHASE_LABELS or not isinstance(model_path, str):
                raise ValueError("staged behavior clone subpolicy must include phase and model_path")
            self.subpolicies[phase] = load_behavior_clone_policy(
                resolve_staged_model_path(self.checkpoint_path, model_path)
            )
        missing = [phase for phase in TIME_PHASE_LABELS if phase not in self.subpolicies]
        if missing:
            raise ValueError(f"staged behavior clone checkpoint missing phases: {', '.join(missing)}")
        first_policy = self.subpolicies[TIME_PHASE_LABELS[0]]
        self.action_count = first_policy.action_count
        self.base_observation_len = first_policy.base_observation_len
        for phase, policy in self.subpolicies.items():
            if policy.action_count != self.action_count:
                raise ValueError(f"staged behavior clone `{phase}` action_count mismatch")
            if policy.base_observation_len != self.base_observation_len:
                raise ValueError(f"staged behavior clone `{phase}` observation length mismatch")

    def reset(self):
        for policy in self.subpolicies.values():
            policy.reset()

    def set_map_id(self, map_id):
        for policy in self.subpolicies.values():
            policy.set_map_id(map_id)

    def predict(self, observation, deterministic=True):
        return self._policy_for_observation(observation).predict(observation, deterministic=deterministic)

    def action_scores(self, observation):
        return self._policy_for_observation(observation).action_scores(observation)

    def _policy_for_observation(self, observation):
        import numpy as np

        values = np.asarray(observation, dtype=np.float32).reshape(-1)
        if values.shape[0] != self.base_observation_len:
            raise ValueError(
                f"expected observation length {self.base_observation_len}, got {values.shape[0]}"
            )
        phase = time_phase_label(float(values[0]), self.phase_thresholds)
        return self.subpolicies[phase]


def load_behavior_clone_policy(path):
    checkpoint_path = Path(path)
    if not checkpoint_path.exists():
        raise ValueError(f"behavior clone model does not exist: {checkpoint_path}")
    require_dependencies()
    import torch

    checkpoint = torch.load(checkpoint_path, map_location="cpu")
    if checkpoint.get("kind") == "behavior_clone_staged":
        return StagedBehaviorClonePolicy(checkpoint_path, checkpoint)
    return BehaviorClonePolicy(checkpoint_path, checkpoint=checkpoint)


def resolve_staged_model_path(checkpoint_path, model_path):
    path = Path(model_path)
    if path.is_absolute():
        return path
    return Path(checkpoint_path).parent / path


def relativize_staged_model_path(bundle_path, model_path):
    bundle_parent = Path(bundle_path).parent.resolve()
    path = Path(model_path)
    if not path.is_absolute():
        path = path.resolve()
    try:
        return str(path.relative_to(bundle_parent))
    except ValueError:
        return str(path)


def save_staged_behavior_clone_policy(model_out, phase_model_paths, thresholds):
    require_dependencies()
    import torch

    thresholds = normalize_time_phase_thresholds(thresholds)
    model_out = Path(model_out)
    missing = [phase for phase in TIME_PHASE_LABELS if phase not in phase_model_paths]
    if missing:
        raise ValueError(f"missing staged policy phase models: {', '.join(missing)}")

    loaded = {}
    for phase in TIME_PHASE_LABELS:
        path = Path(phase_model_paths[phase])
        if not path.exists():
            raise ValueError(f"staged policy model does not exist: {path}")
        policy = load_behavior_clone_policy(path)
        if isinstance(policy, StagedBehaviorClonePolicy):
            raise ValueError("nested staged behavior clone policies are not supported")
        loaded[phase] = policy

    first = loaded[TIME_PHASE_LABELS[0]]
    mismatches = []
    for phase, policy in loaded.items():
        if policy.action_count != first.action_count:
            mismatches.append(f"{phase}: action_count {policy.action_count} != {first.action_count}")
        if policy.base_observation_len != first.base_observation_len:
            mismatches.append(
                f"{phase}: base_observation_len {policy.base_observation_len} != {first.base_observation_len}"
            )
    if mismatches:
        raise ValueError("staged policy submodel mismatch: " + "; ".join(mismatches))

    model_out.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = {
        "model_version": 1,
        "kind": "behavior_clone_staged",
        "phase_labels": TIME_PHASE_LABELS,
        "phase_thresholds": thresholds,
        "action_count": first.action_count,
        "base_observation_len": first.base_observation_len,
        "subpolicies": [
            {
                "phase": phase,
                "model_path": relativize_staged_model_path(model_out, phase_model_paths[phase]),
            }
            for phase in TIME_PHASE_LABELS
        ],
    }
    torch.save(checkpoint, model_out)
    return {
        "status": "packaged",
        "gate_decision": "staged_behavior_clone_packaged_not_policy_gate",
        "model_path": str(model_out),
        "phase_thresholds": thresholds,
        "phase_labels": TIME_PHASE_LABELS,
        "subpolicies": checkpoint["subpolicies"],
        "validation": {
            "action_count": first.action_count,
            "base_observation_len": first.base_observation_len,
        },
        "limitations": [
            "A staged behavior clone only dispatches between supervised movement clones; it is not an RL test Bot gate.",
            "Each staged checkpoint must still pass high-pressure comparison and RL policy acceptance review.",
        ],
    }


def evaluate_classifier(model, x, y, loss_fn):
    import torch

    model.eval()
    with torch.no_grad():
        logits = model(x)
        loss = loss_fn(logits, y)
        entropy = logit_entropy_nats(logits, torch)
        accuracy = (logits.argmax(dim=1) == y).float().mean()
    return {
        "loss": round(float(loss.item()), 6),
        "entropy_nats": round(float(entropy.item()), 6),
        "accuracy": round(float(accuracy.item()), 4),
    }


def logit_entropy_nats(logits, torch_module):
    probabilities = torch_module.softmax(logits, dim=1)
    log_probabilities = torch_module.log_softmax(logits, dim=1)
    return -(probabilities * log_probabilities).sum(dim=1).mean()


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
    parser.add_argument(
        "--time-phase-conditioning",
        choices=["none", "one_hot"],
        default="none",
        help="Append normalized run-progress phase features to behavior clone observations.",
    )
    parser.add_argument(
        "--time-phase-thresholds",
        type=float,
        nargs=2,
        default=DEFAULT_TIME_PHASE_THRESHOLDS,
        metavar=("OPENING_END", "MID_END"),
        help="Normalized run-progress thresholds for opening/mid/late phase conditioning.",
    )
    parser.add_argument(
        "--time-phase-filter",
        choices=["all", *TIME_PHASE_LABELS],
        default="all",
        help="Train or dry-run only samples whose normalized run-progress falls in this phase.",
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
        choices=[
            "none",
            "danger",
            "action_change",
            "danger_action_change",
            "time_phase_balance",
            "time_phase_balance_danger",
            "time_phase_balance_action_change",
            "time_phase_balance_danger_action_change",
        ],
        default="none",
        help="Use weighted sampling to revisit dangerous states or action transition samples more often.",
    )
    parser.add_argument("--danger-health-threshold", type=float, default=0.7)
    parser.add_argument("--danger-low-health-weight", type=float, default=2.0)
    parser.add_argument("--danger-late-start-seconds", type=float, default=60.0)
    parser.add_argument("--danger-late-horizon-seconds", type=float, default=300.0)
    parser.add_argument("--danger-late-weight", type=float, default=1.0)
    parser.add_argument("--action-change-weight", type=float, default=2.0)
    parser.add_argument(
        "--edge-recovery-sample-weight",
        type=float,
        default=1.0,
        help="Multiply edge_recovery_supervision_sample rows when mixing repair samples with trajectory data.",
    )
    parser.add_argument(
        "--entropy-regularization",
        type=float,
        default=0.0,
        help="Subtract mean policy entropy from the training objective to reduce overconfident action collapse.",
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
    if args.entropy_regularization < 0.0:
        parser.error("--entropy-regularization must be greater than or equal to zero")
    if args.action_change_weight < 0.0:
        parser.error("--action-change-weight must be greater than or equal to zero")
    if args.edge_recovery_sample_weight <= 0.0:
        parser.error("--edge-recovery-sample-weight must be greater than zero")
    try:
        args.time_phase_thresholds = normalize_time_phase_thresholds(args.time_phase_thresholds)
    except ValueError as exc:
        parser.error(str(exc))

    try:
        dataset = load_trajectory_dataset(args.dataset, limit=args.limit_samples)
        dataset, time_phase_filter_report = filter_dataset_by_time_phase(
            dataset,
            args.time_phase_filter,
            args.time_phase_thresholds,
        )
        if args.dry_run:
            write_report(
                args.report,
                {
                    "status": "ok",
                    "mode": "dry_run",
                    "gate_decision": "dataset_validated_not_training_gate",
                    "dataset": summarize_dataset(dataset),
                    "sequence_diagnostics": diagnose_sequence_dataset(
                        dataset,
                        args.context_frames,
                        args.danger_late_start_seconds,
                        args.danger_health_threshold,
                    ),
                    "time_phase_conditioning": {
                        "mode": args.time_phase_conditioning,
                        "labels": TIME_PHASE_LABELS if args.time_phase_conditioning != "none" else [],
                        "thresholds": args.time_phase_thresholds,
                        "dimension": len(TIME_PHASE_LABELS)
                        if args.time_phase_conditioning != "none"
                        else 0,
                        "phase_distribution": summarize_time_phase_distribution(
                            dataset,
                            args.time_phase_thresholds,
                        ),
                    },
                    "time_phase_filter": time_phase_filter_report,
                    "dependencies": dependency_status(),
                },
            )
            return
        report = train_behavior_clone(dataset, args)
        report["time_phase_filter"] = time_phase_filter_report
        write_report(args.report, report)
    except (OSError, RuntimeError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
