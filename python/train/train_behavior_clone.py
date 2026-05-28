import argparse
import importlib.util
import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path


REQUIRED_MODULES = ["numpy", "torch"]
TIME_PHASE_LABELS = ["opening", "mid", "late"]
DEFAULT_TIME_PHASE_THRESHOLDS = [0.2, 0.6]
DEFAULT_MOVEMENT_ACTION_COUNT = 9
ACTION_DISTRIBUTION_TARGET_MODES = {
    "uniform_present",
    "uniform_all",
    "empirical",
    "per_map_uniform_present",
    "per_map_empirical",
}
PER_MAP_ACTION_DISTRIBUTION_TARGET_MODES = {
    "per_map_uniform_present",
    "per_map_empirical",
}
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
    risk_recovery_sample_records = 0
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
                if record_type in {
                    "edge_recovery_supervision_sample",
                    "risk_recovery_supervision_sample",
                }:
                    if record.get("sample_role") != "repair_training_input":
                        raise ValueError(
                            f"recovery sample must be repair_training_input in {dataset_path}:{line_number}"
                        )
                    observation = record.get("observation")
                    action = record.get("target_action")
                    if not isinstance(observation, list) or not observation:
                        raise ValueError(
                            f"edge recovery sample missing observation in {dataset_path}:{line_number}"
                        )
                    if not isinstance(action, int):
                        raise ValueError(
                            f"recovery sample missing integer target_action in {dataset_path}:{line_number}"
                        )
                    observations.append([float(value) for value in observation])
                    actions.append(action)
                    sample_source = (
                        "risk_recovery_supervision"
                        if record_type == "risk_recovery_supervision_sample"
                        else "edge_recovery_supervision"
                    )
                    if sample_source == "risk_recovery_supervision":
                        risk_recovery_sample_records += 1
                    else:
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
                            "sample_source": sample_source,
                            "original_action": record.get("original_action"),
                            "target_source": record.get("target_source"),
                            "action_scores": record.get("action_scores"),
                            "adapter_decision": record.get("adapter_decision"),
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
    if edge_recovery_sample_records or risk_recovery_sample_records:
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
        "risk_recovery_sample_records": risk_recovery_sample_records,
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
        "risk_recovery_sample_records": dataset.get("risk_recovery_sample_records", 0),
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
    (
        action_distribution_target,
        sample_map_indices,
        action_distribution_report,
    ) = build_action_distribution_regularization_targets(
        dataset,
        train_indices,
        args,
        np,
    )
    action_distribution_target_tensor = (
        torch.from_numpy(action_distribution_target)
        if action_distribution_target is not None
        else None
    )
    soft_targets, soft_target_report = build_recovery_soft_targets(dataset, args, np)
    train_map_indices = torch.from_numpy(sample_map_indices[train_indices])
    if soft_targets is None:
        train_dataset = TensorDataset(
            torch.from_numpy(observations[train_indices]),
            torch.from_numpy(actions[train_indices]),
            train_map_indices,
        )
        validation_soft_targets = None
    else:
        train_dataset = TensorDataset(
            torch.from_numpy(observations[train_indices]),
            torch.from_numpy(actions[train_indices]),
            torch.from_numpy(soft_targets[train_indices]),
            train_map_indices,
        )
        validation_soft_targets = torch.from_numpy(soft_targets[validation_indices])
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
    validation_map_indices = torch.from_numpy(sample_map_indices[validation_indices])

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
        total_action_distribution_loss = 0.0
        total_correct = 0
        total_seen = 0
        for batch in train_loader:
            if soft_targets is None:
                batch_x, batch_y, batch_map_indices = batch
                batch_soft_y = None
            else:
                batch_x, batch_y, batch_soft_y, batch_map_indices = batch
            logits = model(batch_x)
            if batch_soft_y is None:
                cross_entropy_loss = loss_fn(logits, batch_y)
            else:
                cross_entropy_loss = soft_cross_entropy_loss(
                    logits,
                    batch_soft_y,
                    class_weight_values,
                    torch,
                )
            entropy = logit_entropy_nats(logits, torch)
            action_distribution_loss = action_distribution_regularization_loss(
                logits,
                action_distribution_target_tensor,
                torch,
                batch_map_indices,
            )
            loss = (
                cross_entropy_loss
                - args.entropy_regularization * entropy
                + args.action_distribution_regularization * action_distribution_loss
            )
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += float(loss.item()) * len(batch_y)
            total_cross_entropy_loss += float(cross_entropy_loss.item()) * len(batch_y)
            total_entropy += float(entropy.item()) * len(batch_y)
            total_action_distribution_loss += float(action_distribution_loss.item()) * len(batch_y)
            total_correct += int((logits.argmax(dim=1) == batch_y).sum().item())
            total_seen += len(batch_y)

        validation_metrics = evaluate_classifier(
            model,
            validation_x,
            validation_y,
            loss_fn,
            soft_targets=validation_soft_targets,
            class_weights=class_weight_values,
            action_distribution_target=action_distribution_target_tensor,
            map_indices=validation_map_indices,
        )
        history.append(
            {
                "epoch": epoch,
                "train_loss": round(total_loss / max(1, total_seen), 6),
                "train_cross_entropy_loss": round(
                    total_cross_entropy_loss / max(1, total_seen),
                    6,
                ),
                "train_entropy_nats": round(total_entropy / max(1, total_seen), 6),
                "train_action_distribution_loss": round(
                    total_action_distribution_loss / max(1, total_seen),
                    6,
                ),
                "train_accuracy": round(total_correct / max(1, total_seen), 4),
                "validation_loss": validation_metrics["loss"],
                "validation_entropy_nats": validation_metrics["entropy_nats"],
                "validation_action_distribution_loss": validation_metrics[
                    "action_distribution_loss"
                ],
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
            "recovery_soft_targets": soft_target_report,
            "entropy_regularization": args.entropy_regularization,
            "action_distribution_regularization": action_distribution_report,
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
            "recovery_soft_targets": soft_target_report,
            "entropy_regularization": args.entropy_regularization,
            "action_distribution_regularization": action_distribution_report,
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


def build_recovery_soft_targets(dataset, args, np_module):
    mode = getattr(args, "recovery_soft_target", "none")
    action_count = int(dataset["action_count"])
    if mode == "none":
        return None, {
            "mode": "none",
            "soft_sample_count": 0,
            "fallback_one_hot_count": 0,
        }
    if mode != "top_k_scores":
        raise ValueError(f"unsupported recovery soft target mode: {mode}")

    actions = [int(action) for action in dataset["actions"]]
    targets = np_module.zeros((len(actions), action_count), dtype=np_module.float32)
    soft_sample_count = 0
    fallback_one_hot_count = 0
    nonzero_action_total = 0
    primary_mass = clamp(float(args.recovery_soft_target_primary_mass), 0.0, 1.0)
    top_k = int(args.recovery_soft_target_top_k)

    for index, action in enumerate(actions):
        sample = dataset["sample_metadata"][index]
        distribution = None
        if sample.get("sample_source") in {
            "edge_recovery_supervision",
            "risk_recovery_supervision",
        }:
            distribution = recovery_top_k_distribution(
                sample,
                action,
                action_count,
                primary_mass,
                top_k,
                np_module,
            )
        if distribution is None:
            targets[index, action] = 1.0
            fallback_one_hot_count += 1 if sample.get("sample_source") else 0
            nonzero_action_total += 1
            continue
        targets[index] = distribution
        soft_sample_count += 1
        nonzero_action_total += int((distribution > 0.0).sum())

    return targets, {
        "mode": mode,
        "primary_mass": round(primary_mass, 6),
        "top_k": top_k,
        "soft_sample_count": int(soft_sample_count),
        "fallback_one_hot_count": int(fallback_one_hot_count),
        "average_nonzero_actions": round(nonzero_action_total / max(1, len(actions)), 4),
    }


def recovery_top_k_distribution(sample, target_action, action_count, primary_mass, top_k, np_module):
    if top_k <= 1:
        return None
    if not (0 <= int(target_action) < action_count):
        return None
    action_scores = sample.get("action_scores")
    top_actions = action_scores.get("top_actions") if isinstance(action_scores, dict) else None
    if not isinstance(top_actions, list):
        return None

    original_action = sample.get("original_action")
    candidates = []
    seen = {int(target_action)}
    if isinstance(original_action, int):
        seen.add(int(original_action))
    for item in top_actions:
        if not isinstance(item, dict):
            continue
        action = item.get("action")
        try:
            action = int(action)
        except (TypeError, ValueError):
            continue
        if action in seen or not (0 <= action < action_count):
            continue
        score = item.get("score", 0.0)
        try:
            score_value = max(0.0, float(score))
        except (TypeError, ValueError):
            score_value = 0.0
        candidates.append((action, score_value))
        seen.add(action)
        if len(candidates) >= max(0, top_k - 1):
            break
    if not candidates:
        return None

    distribution = np_module.zeros(action_count, dtype=np_module.float32)
    distribution[int(target_action)] = primary_mass
    residual = max(0.0, 1.0 - primary_mass)
    score_total = sum(score for _, score in candidates)
    for action, score in candidates:
        if score_total > 0.0:
            mass = residual * (score / score_total)
        else:
            mass = residual / len(candidates)
        distribution[action] = float(mass)
    total = float(distribution.sum())
    if total <= 0.0:
        return None
    return distribution / total


def build_action_distribution_regularization_targets(dataset, train_indices, args, np_module):
    coefficient = float(getattr(args, "action_distribution_regularization", 0.0))
    target_mode = getattr(args, "action_distribution_target", "uniform_present")
    sample_map_indices, map_ids = build_sample_map_indices(dataset, np_module)
    base_report = {
        "enabled": coefficient > 0.0,
        "coefficient": round(coefficient, 6),
        "target_mode": target_mode,
        "map_ids": map_ids,
    }
    if target_mode not in ACTION_DISTRIBUTION_TARGET_MODES:
        raise ValueError(f"unsupported action distribution target mode: {target_mode}")
    if coefficient <= 0.0:
        base_report["scope"] = "none"
        return None, sample_map_indices, base_report

    actions = np_module.asarray(dataset["actions"], dtype=np_module.int64)
    action_count = int(dataset["action_count"])
    if target_mode in PER_MAP_ACTION_DISTRIBUTION_TARGET_MODES:
        per_map_targets = []
        per_map_reports = {}
        per_map_counts = {}
        local_mode = target_mode.removeprefix("per_map_")
        for map_index, map_id in enumerate(map_ids):
            map_train_indices = [
                int(index)
                for index in train_indices
                if int(sample_map_indices[int(index)]) == map_index
            ]
            counts = np_module.bincount(actions[map_train_indices], minlength=action_count)
            target = action_distribution_target_from_counts(
                counts,
                action_count,
                local_mode,
                np_module,
            )
            per_map_targets.append(target)
            per_map_reports[map_id] = action_distribution_report_from_array(target)
            per_map_counts[map_id] = {
                str(action): int(count) for action, count in enumerate(counts.tolist())
            }
        target_array = np_module.asarray(per_map_targets, dtype=np_module.float32)
        base_report.update(
            {
                "scope": "per_map",
                "target_distribution_by_map": per_map_reports,
                "train_action_counts_by_map": per_map_counts,
            }
        )
        return target_array, sample_map_indices, base_report

    counts = np_module.bincount(actions[train_indices], minlength=action_count)
    target_array = action_distribution_target_from_counts(
        counts,
        action_count,
        target_mode,
        np_module,
    )
    base_report.update(
        {
            "scope": "global",
            "target_distribution": action_distribution_report_from_array(target_array),
            "train_action_counts": {
                str(action): int(count) for action, count in enumerate(counts.tolist())
            },
        }
    )
    return target_array.astype(np_module.float32), sample_map_indices, base_report


def build_sample_map_indices(dataset, np_module):
    map_ids = sorted(
        {
            str(sample.get("map_id") or "unknown")
            for sample in dataset["sample_metadata"]
        }
    )
    if not map_ids:
        map_ids = ["unknown"]
    map_index = {map_id: index for index, map_id in enumerate(map_ids)}
    sample_map_indices = np_module.asarray(
        [
            map_index[str(sample.get("map_id") or "unknown")]
            for sample in dataset["sample_metadata"]
        ],
        dtype=np_module.int64,
    )
    return sample_map_indices, map_ids


def action_distribution_target_from_counts(counts, action_count, mode, np_module):
    counts = np_module.asarray(counts, dtype=np_module.float32)
    target = np_module.zeros(action_count, dtype=np_module.float32)
    if mode == "empirical":
        total = float(counts.sum())
        if total > 0.0:
            return (counts / total).astype(np_module.float32)
        target.fill(1.0 / max(1, action_count))
        return target
    if mode == "uniform_all":
        target.fill(1.0 / max(1, action_count))
        return target
    if mode != "uniform_present":
        raise ValueError(f"unsupported action distribution target mode: {mode}")
    present = counts > 0.0
    present_count = int(present.sum())
    if present_count <= 0:
        target.fill(1.0 / max(1, action_count))
        return target
    target[present] = 1.0 / present_count
    return target


def action_distribution_report_from_array(values):
    return {
        str(index): round(float(value), 6)
        for index, value in enumerate(values.tolist())
    }


def action_distribution_regularization_loss(
    logits,
    target_distribution,
    torch_module,
    map_indices=None,
):
    if target_distribution is None:
        return logits.sum() * 0.0
    probabilities = torch_module.softmax(logits, dim=1)
    target_distribution = target_distribution.to(logits.device)
    if len(target_distribution.shape) == 1:
        predicted_distribution = probabilities.mean(dim=0)
        return ((predicted_distribution - target_distribution) ** 2).sum()
    if map_indices is None:
        return logits.sum() * 0.0
    map_indices = map_indices.to(logits.device)
    losses = []
    for map_index in torch_module.unique(map_indices):
        int_map_index = int(map_index.item())
        if not (0 <= int_map_index < target_distribution.shape[0]):
            continue
        mask = map_indices == map_index
        if not bool(mask.any()):
            continue
        predicted_distribution = probabilities[mask].mean(dim=0)
        losses.append(
            ((predicted_distribution - target_distribution[int_map_index]) ** 2).sum()
        )
    if not losses:
        return logits.sum() * 0.0
    return torch_module.stack(losses).mean()


def soft_cross_entropy_loss(logits, targets, class_weights, torch_module):
    log_probabilities = torch_module.log_softmax(logits, dim=1)
    losses = -(targets * log_probabilities)
    if class_weights is not None:
        losses = losses * class_weights.to(logits.device)
    return losses.sum(dim=1).mean()


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


def new_policy_prediction_bucket(action_count):
    return {
        "sample_count": 0,
        "correct_count": 0,
        "target_action_counts": {str(action): 0 for action in range(action_count)},
        "predicted_action_counts": {str(action): 0 for action in range(action_count)},
        "score_totals": {str(action): 0.0 for action in range(action_count)},
        "target_action_score_total": 0.0,
        "predicted_action_score_total": 0.0,
        "policy_entropy_nats_total": 0.0,
    }


def record_policy_prediction(bucket, target_action, predicted_action, scores, action_count):
    target_key = str(int(target_action))
    predicted_key = str(int(predicted_action))
    bucket["sample_count"] += 1
    if int(target_action) == int(predicted_action):
        bucket["correct_count"] += 1
    bucket["target_action_counts"][target_key] = bucket["target_action_counts"].get(target_key, 0) + 1
    bucket["predicted_action_counts"][predicted_key] = (
        bucket["predicted_action_counts"].get(predicted_key, 0) + 1
    )
    for action in range(action_count):
        score = float(scores[action]) if action < len(scores) else 0.0
        bucket["score_totals"][str(action)] = bucket["score_totals"].get(str(action), 0.0) + score
    if 0 <= int(target_action) < len(scores):
        bucket["target_action_score_total"] += float(scores[int(target_action)])
    if 0 <= int(predicted_action) < len(scores):
        bucket["predicted_action_score_total"] += float(scores[int(predicted_action)])
    for score in scores:
        value = max(0.0, float(score))
        if value > 0.0:
            bucket["policy_entropy_nats_total"] -= value * math.log(value)


def distribution_entropy_bits(counts):
    total = sum(int(value) for value in counts.values())
    entropy = 0.0
    for count in counts.values():
        if count <= 0:
            continue
        ratio = count / max(1, total)
        entropy -= ratio * math.log2(ratio)
    return entropy


def dominant_action_from_counts(counts):
    if not counts:
        return None
    action, count = max(counts.items(), key=lambda item: int(item[1]))
    total = sum(int(value) for value in counts.values())
    return {
        "action": str(action),
        "count": int(count),
        "ratio": round(int(count) / max(1, total), 4),
    }


def finalize_policy_prediction_bucket(bucket, action_count):
    sample_count = int(bucket["sample_count"])
    predicted_entropy = distribution_entropy_bits(bucket["predicted_action_counts"])
    max_entropy_bits = math.log2(max(2, action_count))
    max_entropy_nats = math.log(max(2, action_count))
    return {
        "sample_count": sample_count,
        "accuracy": round(bucket["correct_count"] / max(1, sample_count), 4),
        "target_action_distribution": ratio_counts(bucket["target_action_counts"], sample_count),
        "predicted_action_distribution": ratio_counts(bucket["predicted_action_counts"], sample_count),
        "dominant_predicted_action": dominant_action_from_counts(bucket["predicted_action_counts"]),
        "predicted_action_entropy_bits": round(predicted_entropy, 4),
        "normalized_predicted_action_entropy": round(predicted_entropy / max_entropy_bits, 4),
        "mean_policy_scores": {
            str(action): round(bucket["score_totals"].get(str(action), 0.0) / max(1, sample_count), 6)
            for action in range(action_count)
        },
        "mean_target_action_score": round(
            bucket["target_action_score_total"] / max(1, sample_count),
            6,
        ),
        "mean_predicted_action_score": round(
            bucket["predicted_action_score_total"] / max(1, sample_count),
            6,
        ),
        "mean_policy_entropy_nats": round(
            bucket["policy_entropy_nats_total"] / max(1, sample_count),
            6,
        ),
        "normalized_mean_policy_entropy": round(
            (bucket["policy_entropy_nats_total"] / max(1, sample_count)) / max_entropy_nats,
            4,
        ),
    }


def policy_diagnostic_phase(policy, observation, sample):
    phase_thresholds = getattr(policy, "phase_thresholds", DEFAULT_TIME_PHASE_THRESHOLDS)
    phase_duration_seconds = getattr(policy, "phase_duration_seconds", None)
    if phase_duration_seconds is not None:
        progress = float(sample.get("time_seconds", 0.0)) / max(0.0001, float(phase_duration_seconds))
    else:
        progress = float(observation[0]) if observation else 0.0
    return time_phase_label(progress, phase_thresholds)


def diagnose_behavior_clone_policy_on_dataset(
    policy,
    dataset,
    *,
    model_path=None,
    dominant_action_threshold=0.85,
    low_entropy_threshold=0.1,
):
    action_count = int(getattr(policy, "action_count", dataset["action_count"]))
    overall = new_policy_prediction_bucket(action_count)
    by_phase = {}
    by_map = {}
    by_sample_source = {}
    last_episode_key = None

    for observation, target_action, sample in zip(
        dataset["observations"],
        dataset["actions"],
        dataset["sample_metadata"],
    ):
        episode_key = (sample.get("path"), sample.get("seed"))
        if episode_key != last_episode_key:
            reset = getattr(policy, "reset", None)
            if callable(reset):
                reset()
            last_episode_key = episode_key
        map_id = sample.get("map_id")
        set_map_id = getattr(policy, "set_map_id", None)
        if callable(set_map_id):
            set_map_id(map_id)
        set_step_context = getattr(policy, "set_step_context", None)
        if callable(set_step_context):
            set_step_context(
                {
                    "time_seconds": float(sample.get("time_seconds", 0.0)),
                    "map_id": map_id,
                }
            )
        predicted_action, _ = policy.predict(observation, deterministic=True)
        scores_payload = policy.action_scores(observation)
        scores = scores_payload.get("scores", []) if isinstance(scores_payload, dict) else []

        record_policy_prediction(overall, target_action, predicted_action, scores, action_count)
        phase = policy_diagnostic_phase(policy, observation, sample)
        record_policy_prediction(
            by_phase.setdefault(phase, new_policy_prediction_bucket(action_count)),
            target_action,
            predicted_action,
            scores,
            action_count,
        )
        record_policy_prediction(
            by_map.setdefault(str(map_id or "unknown"), new_policy_prediction_bucket(action_count)),
            target_action,
            predicted_action,
            scores,
            action_count,
        )
        sample_source = sample.get("sample_source") or "trajectory"
        record_policy_prediction(
            by_sample_source.setdefault(sample_source, new_policy_prediction_bucket(action_count)),
            target_action,
            predicted_action,
            scores,
            action_count,
        )

    overall_report = finalize_policy_prediction_bucket(overall, action_count)
    phase_report = {
        phase: finalize_policy_prediction_bucket(bucket, action_count)
        for phase, bucket in sorted(by_phase.items())
    }
    map_report = {
        map_id: finalize_policy_prediction_bucket(bucket, action_count)
        for map_id, bucket in sorted(by_map.items())
    }
    source_report = {
        source: finalize_policy_prediction_bucket(bucket, action_count)
        for source, bucket in sorted(by_sample_source.items())
    }
    findings = policy_prediction_findings(
        overall_report,
        phase_report,
        dominant_action_threshold=dominant_action_threshold,
        low_entropy_threshold=low_entropy_threshold,
    )
    return {
        "report_version": 1,
        "status": "diagnosed",
        "gate_decision": (
            "offline_policy_diagnostic_recorded_needs_action_bias_repair"
            if findings
            else "offline_policy_diagnostic_recorded_watch_only"
        ),
        "model_path": str(model_path) if model_path is not None else getattr(policy, "checkpoint_path", None),
        "dataset": summarize_dataset(dataset),
        "overall": overall_report,
        "by_phase": phase_report,
        "by_map": map_report,
        "by_sample_source": source_report,
        "findings": findings,
        "limitations": [
            "Offline behavior clone diagnostics compare model predictions against a dataset only.",
            "They are not high-pressure Gym comparisons, Replay regression, balance evidence, or RL acceptance.",
        ],
    }


def policy_prediction_findings(
    overall_report,
    phase_report,
    *,
    dominant_action_threshold,
    low_entropy_threshold,
):
    findings = []

    def inspect(label, report):
        if report.get("sample_count", 0) <= 0:
            return
        dominant = report.get("dominant_predicted_action") or {}
        dominant_ratio = float(dominant.get("ratio", 0.0) or 0.0)
        entropy = float(report.get("normalized_predicted_action_entropy", 0.0) or 0.0)
        if dominant_ratio >= dominant_action_threshold:
            findings.append(
                {
                    "id": "offline_dominant_action_bias",
                    "scope": label,
                    "severity": "repair",
                    "summary": (
                        f"{label} predicts action {dominant.get('action')} for "
                        f"{dominant_ratio:.2%} of offline samples."
                    ),
                }
            )
        if entropy <= low_entropy_threshold:
            findings.append(
                {
                    "id": "offline_low_predicted_action_entropy",
                    "scope": label,
                    "severity": "repair",
                    "summary": f"{label} normalized predicted action entropy is {entropy:.4f}.",
                }
            )

    inspect("overall", overall_report)
    for phase, report in phase_report.items():
        inspect(f"phase:{phase}", report)
    return findings


def diagnose_behavior_clone_policy_path(
    model_path,
    dataset,
    *,
    dominant_action_threshold=0.85,
    low_entropy_threshold=0.1,
):
    policy = load_behavior_clone_policy(model_path)
    return diagnose_behavior_clone_policy_on_dataset(
        policy,
        dataset,
        model_path=model_path,
        dominant_action_threshold=dominant_action_threshold,
        low_entropy_threshold=low_entropy_threshold,
    )


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
    filtered["risk_recovery_sample_records"] = sum(
        1
        for sample in filtered["sample_metadata"]
        if sample.get("sample_source") == "risk_recovery_supervision"
    )
    return filtered, {
        "mode": phase,
        "thresholds": thresholds,
        "before_sample_count": len(dataset["actions"]),
        "after_sample_count": len(keep_indices),
        "phase_distribution": summarize_time_phase_distribution(filtered, thresholds),
    }


def filter_edge_recovery_samples_by_time_window(dataset, min_seconds=None, max_seconds=None):
    return filter_recovery_samples_by_time_window(
        dataset,
        source_name="edge_recovery_supervision",
        count_key="edge_recovery_sample_records",
        label="edge_recovery",
        min_seconds=min_seconds,
        max_seconds=max_seconds,
    )


def filter_risk_recovery_samples_by_time_window(dataset, min_seconds=None, max_seconds=None):
    return filter_recovery_samples_by_time_window(
        dataset,
        source_name="risk_recovery_supervision",
        count_key="risk_recovery_sample_records",
        label="risk_recovery",
        min_seconds=min_seconds,
        max_seconds=max_seconds,
    )


def filter_recovery_samples_by_time_window(
    dataset,
    *,
    source_name,
    count_key,
    label,
    min_seconds=None,
    max_seconds=None,
):
    if min_seconds is None and max_seconds is None:
        recovery_count = int(dataset.get(count_key, 0))
        return dataset, {
            "mode": "all",
            "min_seconds": None,
            "max_seconds": None,
            "before_sample_count": len(dataset["actions"]),
            "after_sample_count": len(dataset["actions"]),
            f"before_{label}_sample_count": recovery_count,
            f"after_{label}_sample_count": recovery_count,
            f"dropped_{label}_sample_count": 0,
        }

    min_seconds = None if min_seconds is None else float(min_seconds)
    max_seconds = None if max_seconds is None else float(max_seconds)
    keep_indices = []
    before_recovery_count = 0
    after_recovery_count = 0
    dropped_recovery_count = 0
    for index, sample in enumerate(dataset["sample_metadata"]):
        if sample.get("sample_source") != source_name:
            keep_indices.append(index)
            continue
        before_recovery_count += 1
        time_seconds = float(sample.get("time_seconds", 0.0))
        keep = True
        if min_seconds is not None and time_seconds < min_seconds:
            keep = False
        if max_seconds is not None and time_seconds >= max_seconds:
            keep = False
        if keep:
            keep_indices.append(index)
            after_recovery_count += 1
        else:
            dropped_recovery_count += 1

    if len(keep_indices) < 2:
        raise ValueError("edge recovery time window filter leaves fewer than two samples")

    filtered = dict(dataset)
    filtered["observations"] = [dataset["observations"][index] for index in keep_indices]
    filtered["actions"] = [dataset["actions"][index] for index in keep_indices]
    filtered["sample_metadata"] = [dataset["sample_metadata"][index] for index in keep_indices]
    filtered[count_key] = after_recovery_count
    return filtered, {
        "mode": "time_window",
        "min_seconds": min_seconds,
        "max_seconds": max_seconds,
        "before_sample_count": len(dataset["actions"]),
        "after_sample_count": len(keep_indices),
        f"before_{label}_sample_count": before_recovery_count,
        f"after_{label}_sample_count": after_recovery_count,
        f"dropped_{label}_sample_count": dropped_recovery_count,
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


def parse_sample_path_weight_spec(value):
    if "=" not in value:
        raise argparse.ArgumentTypeError("sample path weight must use PATH=WEIGHT")
    path_text, weight_text = value.split("=", 1)
    path_text = path_text.strip()
    if not path_text:
        raise argparse.ArgumentTypeError("sample path weight path must be non-empty")
    try:
        weight = float(weight_text.strip())
    except ValueError as exc:
        raise argparse.ArgumentTypeError("sample path weight must be numeric") from exc
    if weight <= 0.0:
        raise argparse.ArgumentTypeError("sample path weight must be greater than zero")
    return {"path": path_text, "weight": weight}


def normalize_sample_path_weights(value):
    if not value:
        return []
    if isinstance(value, dict):
        return [
            {"path": str(path), "weight": float(weight)}
            for path, weight in sorted(value.items())
        ]
    entries = []
    for item in value:
        if isinstance(item, str):
            entries.append(parse_sample_path_weight_spec(item))
        elif isinstance(item, dict):
            entries.append(
                {
                    "path": str(item["path"]),
                    "weight": float(item["weight"]),
                }
            )
        elif isinstance(item, (list, tuple)) and len(item) == 2:
            entries.append({"path": str(item[0]), "weight": float(item[1])})
        else:
            raise ValueError(f"unsupported sample path weight entry: {item!r}")
    for item in entries:
        if not item["path"]:
            raise ValueError("sample path weight path must be non-empty")
        if item["weight"] <= 0.0:
            raise ValueError("sample path weight must be greater than zero")
    return entries


def sample_path_matches_weight(sample_path, weighted_path):
    sample_path = str(sample_path or "")
    weighted_path = str(weighted_path or "").rstrip("/")
    return sample_path == weighted_path or sample_path.startswith(weighted_path + "/")


def sample_path_weight_for(sample_path, path_weights):
    multiplier = 1.0
    matched_paths = []
    for item in path_weights:
        if sample_path_matches_weight(sample_path, item["path"]):
            multiplier *= float(item["weight"])
            matched_paths.append(item["path"])
    return multiplier, matched_paths


def sample_weight_mode(base_mode, use_edge_recovery_weight, use_risk_recovery_weight, use_path_weight):
    if base_mode != "none":
        return base_mode
    active = []
    if use_edge_recovery_weight:
        active.append("edge_recovery")
    if use_risk_recovery_weight:
        active.append("risk_recovery")
    if use_path_weight:
        active.append("sample_path")
    if not active:
        return "none"
    if active == ["edge_recovery"]:
        return "edge_recovery_auxiliary"
    if active == ["risk_recovery"]:
        return "risk_recovery_auxiliary"
    if active == ["sample_path"]:
        return "sample_path_auxiliary"
    return "mixed_" + "_".join(active) + "_auxiliary"


def build_sample_weights(dataset, indices, args, np_module):
    edge_recovery_sample_weight = float(getattr(args, "edge_recovery_sample_weight", 1.0))
    risk_recovery_sample_weight = float(getattr(args, "risk_recovery_sample_weight", 1.0))
    sample_path_weights = normalize_sample_path_weights(
        getattr(args, "sample_path_weights", None)
    )
    use_edge_recovery_weight = abs(edge_recovery_sample_weight - 1.0) > 1e-6
    use_risk_recovery_weight = abs(risk_recovery_sample_weight - 1.0) > 1e-6
    use_path_weight = bool(sample_path_weights)
    if (
        args.sample_weighting == "none"
        and not use_edge_recovery_weight
        and not use_risk_recovery_weight
        and not use_path_weight
    ):
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
    risk_recovery_weighted_count = 0
    path_weighted_count = 0
    path_weight_matches = {
        item["path"]: {"path": item["path"], "weight": item["weight"], "matched_train_samples": 0}
        for item in sample_path_weights
    }
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
        if sample.get("sample_source") == "risk_recovery_supervision":
            weight *= risk_recovery_sample_weight
            risk_recovery_weighted_count += 1
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
        path_multiplier, matched_paths = sample_path_weight_for(
            sample.get("path"),
            sample_path_weights,
        )
        if matched_paths:
            path_weighted_count += 1
            for path in matched_paths:
                path_weight_matches[path]["matched_train_samples"] += 1
            weight *= path_multiplier
        weights.append(weight)

    values = np_module.asarray(weights, dtype=np_module.float32)
    report = {
        "mode": sample_weight_mode(
            args.sample_weighting,
            use_edge_recovery_weight,
            use_risk_recovery_weight,
            use_path_weight,
        ),
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
        "risk_recovery_sample_weight": round(risk_recovery_sample_weight, 6),
        "risk_recovery_weighted_sample_count": int(risk_recovery_weighted_count),
        "risk_recovery_weighted_sample_ratio": round(
            risk_recovery_weighted_count / max(1, len(indices)),
            4,
        ),
        "sample_path_weights": {
            "enabled": use_path_weight,
            "weighted_sample_count": int(path_weighted_count),
            "weighted_sample_ratio": round(path_weighted_count / max(1, len(indices)), 4),
            "entries": list(path_weight_matches.values()),
        },
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
        self._time_phase_progress_override = None
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
        self._time_phase_progress_override = None

    def set_map_id(self, map_id):
        self.current_map_id = str(map_id) if map_id is not None else None
        self._last_observation = None
        self._last_scores = None

    def set_step_context(self, info):
        duration = info.get("phase_duration_seconds") if isinstance(info, dict) else None
        time_seconds = info.get("time_seconds") if isinstance(info, dict) else None
        if duration is None or time_seconds is None:
            self._time_phase_progress_override = None
            return
        duration = float(duration)
        if duration <= 0.0:
            self._time_phase_progress_override = None
            return
        self._time_phase_progress_override = clamp(float(time_seconds) / duration, 0.0, 1.0)

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
        conditioning_values = self._conditioning_values(values)
        features = self._features(conditioning_values, np, update_history=update_history)
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

    def _conditioning_values(self, values):
        if self._time_phase_progress_override is None:
            return values
        adjusted = values.copy()
        adjusted[0] = self._time_phase_progress_override
        return adjusted

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
        progress = (
            self._time_phase_progress_override
            if self._time_phase_progress_override is not None
            else float(values[0])
        )
        return time_phase_one_hot([progress], thresholds, np_module)[0]

    def _time_phase_sequence_features(self, sequence, np_module):
        mode = self.time_phase_conditioning.get("mode", "none")
        if mode == "none":
            return np_module.zeros((sequence.shape[0], 0), dtype=np_module.float32)
        thresholds = normalize_time_phase_thresholds(
            self.time_phase_conditioning.get("thresholds", DEFAULT_TIME_PHASE_THRESHOLDS)
        )
        if self._time_phase_progress_override is not None:
            progress_values = np_module.repeat(
                np_module.asarray([self._time_phase_progress_override], dtype=np_module.float32),
                sequence.shape[0],
            )
            return time_phase_one_hot(progress_values, thresholds, np_module)
        return time_phase_one_hot(sequence[:, 0], thresholds, np_module)


class StagedBehaviorClonePolicy:
    def __init__(self, checkpoint_path, checkpoint):
        self.checkpoint_path = Path(checkpoint_path)
        self.checkpoint = checkpoint
        self.phase_thresholds = normalize_time_phase_thresholds(
            checkpoint.get("phase_thresholds", DEFAULT_TIME_PHASE_THRESHOLDS)
        )
        phase_duration_seconds = checkpoint.get("phase_duration_seconds")
        self.phase_duration_seconds = (
            None if phase_duration_seconds is None else float(phase_duration_seconds)
        )
        if self.phase_duration_seconds is not None and self.phase_duration_seconds <= 0.0:
            raise ValueError("staged behavior clone phase_duration_seconds must be greater than 0")
        self._time_seconds = 0.0
        self._has_step_context = False
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
        self._time_seconds = 0.0
        self._has_step_context = False
        for policy in self.subpolicies.values():
            policy.reset()

    def set_map_id(self, map_id):
        for policy in self.subpolicies.values():
            policy.set_map_id(map_id)

    def set_step_context(self, info):
        self._time_seconds = float(info.get("time_seconds", 0.0) or 0.0)
        self._has_step_context = True
        child_info = dict(info)
        if self.phase_duration_seconds is not None:
            child_info.setdefault("phase_duration_seconds", self.phase_duration_seconds)
        for policy in self.subpolicies.values():
            set_step_context = getattr(policy, "set_step_context", None)
            if callable(set_step_context):
                set_step_context(child_info)

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
        phase = time_phase_label(self._phase_value(values), self.phase_thresholds)
        return self.subpolicies[phase]

    def _phase_value(self, values):
        if self.phase_duration_seconds is not None and self._has_step_context:
            return max(0.0, self._time_seconds / self.phase_duration_seconds)
        return float(values[0])


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


def save_staged_behavior_clone_policy(
    model_out,
    phase_model_paths,
    thresholds,
    phase_duration_seconds=None,
):
    require_dependencies()
    import torch

    thresholds = normalize_time_phase_thresholds(thresholds)
    if phase_duration_seconds is not None:
        phase_duration_seconds = float(phase_duration_seconds)
        if phase_duration_seconds <= 0.0:
            raise ValueError("phase_duration_seconds must be greater than 0")
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
        "phase_duration_seconds": phase_duration_seconds,
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
        "phase_duration_seconds": phase_duration_seconds,
        "phase_dispatch": (
            "absolute_time_seconds"
            if phase_duration_seconds is not None
            else "observation_normalized_time"
        ),
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


def evaluate_classifier(
    model,
    x,
    y,
    loss_fn,
    *,
    soft_targets=None,
    class_weights=None,
    action_distribution_target=None,
    map_indices=None,
):
    import torch

    model.eval()
    with torch.no_grad():
        logits = model(x)
        if soft_targets is None:
            loss = loss_fn(logits, y)
        else:
            loss = soft_cross_entropy_loss(logits, soft_targets, class_weights, torch)
        entropy = logit_entropy_nats(logits, torch)
        action_distribution_loss = action_distribution_regularization_loss(
            logits,
            action_distribution_target,
            torch,
            map_indices,
        )
        accuracy = (logits.argmax(dim=1) == y).float().mean()
    return {
        "loss": round(float(loss.item()), 6),
        "entropy_nats": round(float(entropy.item()), 6),
        "action_distribution_loss": round(float(action_distribution_loss.item()), 6),
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
        "--risk-recovery-sample-weight",
        type=float,
        default=1.0,
        help="Multiply risk_recovery_supervision_sample rows when mixing late safety repair samples.",
    )
    parser.add_argument(
        "--sample-path-weight",
        dest="sample_path_weights",
        action="append",
        type=parse_sample_path_weight_spec,
        default=[],
        metavar="PATH=WEIGHT",
        help=(
            "Multiply samples from a specific JSONL path or directory prefix. "
            "Repeat to split repair and retention anchors without changing the dataset."
        ),
    )
    parser.add_argument(
        "--edge-recovery-min-seconds",
        type=float,
        default=None,
        help="Keep edge recovery repair samples at or after this time; regular trajectory samples are unaffected.",
    )
    parser.add_argument(
        "--edge-recovery-max-seconds",
        type=float,
        default=None,
        help="Keep edge recovery repair samples before this time; regular trajectory samples are unaffected.",
    )
    parser.add_argument(
        "--risk-recovery-min-seconds",
        type=float,
        default=None,
        help="Keep risk recovery repair samples at or after this time; regular trajectory samples are unaffected.",
    )
    parser.add_argument(
        "--risk-recovery-max-seconds",
        type=float,
        default=None,
        help="Keep risk recovery repair samples before this time; regular trajectory samples are unaffected.",
    )
    parser.add_argument(
        "--recovery-soft-target",
        choices=["none", "top_k_scores"],
        default="none",
        help="Use soft targets for recovery samples instead of a single hard repair action.",
    )
    parser.add_argument(
        "--recovery-soft-target-primary-mass",
        type=float,
        default=0.65,
        help="Probability mass assigned to the recovery target action when --recovery-soft-target is enabled.",
    )
    parser.add_argument(
        "--recovery-soft-target-top-k",
        type=int,
        default=3,
        help="Maximum number of actions kept in a recovery soft target, including the target action.",
    )
    parser.add_argument(
        "--entropy-regularization",
        type=float,
        default=0.0,
        help="Subtract mean policy entropy from the training objective to reduce overconfident action collapse.",
    )
    parser.add_argument(
        "--action-distribution-regularization",
        type=float,
        default=0.0,
        help="Penalize mismatch between batch mean predicted action probabilities and an explicit target distribution.",
    )
    parser.add_argument(
        "--action-distribution-target",
        choices=sorted(ACTION_DISTRIBUTION_TARGET_MODES),
        default="uniform_present",
        help="Target distribution used by --action-distribution-regularization.",
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
    if args.action_distribution_regularization < 0.0:
        parser.error("--action-distribution-regularization must be greater than or equal to zero")
    if args.action_change_weight < 0.0:
        parser.error("--action-change-weight must be greater than or equal to zero")
    if args.edge_recovery_sample_weight <= 0.0:
        parser.error("--edge-recovery-sample-weight must be greater than zero")
    if args.risk_recovery_sample_weight <= 0.0:
        parser.error("--risk-recovery-sample-weight must be greater than zero")
    if not (0.0 < args.recovery_soft_target_primary_mass <= 1.0):
        parser.error("--recovery-soft-target-primary-mass must be in (0, 1]")
    if args.recovery_soft_target_top_k < 2:
        parser.error("--recovery-soft-target-top-k must be at least 2")
    if args.edge_recovery_min_seconds is not None and args.edge_recovery_min_seconds < 0.0:
        parser.error("--edge-recovery-min-seconds must be greater than or equal to zero")
    if args.edge_recovery_max_seconds is not None and args.edge_recovery_max_seconds <= 0.0:
        parser.error("--edge-recovery-max-seconds must be greater than zero")
    if (
        args.edge_recovery_min_seconds is not None
        and args.edge_recovery_max_seconds is not None
        and args.edge_recovery_max_seconds <= args.edge_recovery_min_seconds
    ):
        parser.error("--edge-recovery-max-seconds must be greater than --edge-recovery-min-seconds")
    if args.risk_recovery_min_seconds is not None and args.risk_recovery_min_seconds < 0.0:
        parser.error("--risk-recovery-min-seconds must be greater than or equal to zero")
    if args.risk_recovery_max_seconds is not None and args.risk_recovery_max_seconds <= 0.0:
        parser.error("--risk-recovery-max-seconds must be greater than zero")
    if (
        args.risk_recovery_min_seconds is not None
        and args.risk_recovery_max_seconds is not None
        and args.risk_recovery_max_seconds <= args.risk_recovery_min_seconds
    ):
        parser.error("--risk-recovery-max-seconds must be greater than --risk-recovery-min-seconds")
    try:
        args.time_phase_thresholds = normalize_time_phase_thresholds(args.time_phase_thresholds)
    except ValueError as exc:
        parser.error(str(exc))

    try:
        dataset = load_trajectory_dataset(args.dataset, limit=args.limit_samples)
        dataset, edge_recovery_time_window_report = filter_edge_recovery_samples_by_time_window(
            dataset,
            min_seconds=args.edge_recovery_min_seconds,
            max_seconds=args.edge_recovery_max_seconds,
        )
        dataset, risk_recovery_time_window_report = filter_risk_recovery_samples_by_time_window(
            dataset,
            min_seconds=args.risk_recovery_min_seconds,
            max_seconds=args.risk_recovery_max_seconds,
        )
        dataset, time_phase_filter_report = filter_dataset_by_time_phase(
            dataset,
            args.time_phase_filter,
            args.time_phase_thresholds,
        )
        if args.dry_run:
            import numpy as np

            _, soft_target_report = build_recovery_soft_targets(dataset, args, np)
            _, sample_weight_report = build_sample_weights(
                dataset,
                list(range(len(dataset["actions"]))),
                args,
                np,
            )
            _, _, action_distribution_report = build_action_distribution_regularization_targets(
                dataset,
                list(range(len(dataset["actions"]))),
                args,
                np,
            )
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
                    "edge_recovery_time_window_filter": edge_recovery_time_window_report,
                    "risk_recovery_time_window_filter": risk_recovery_time_window_report,
                    "recovery_soft_targets": soft_target_report,
                    "sample_weights": sample_weight_report,
                    "action_distribution_regularization": action_distribution_report,
                    "dependencies": dependency_status(),
                },
            )
            return
        report = train_behavior_clone(dataset, args)
        report["time_phase_filter"] = time_phase_filter_report
        report["edge_recovery_time_window_filter"] = edge_recovery_time_window_report
        report["risk_recovery_time_window_filter"] = risk_recovery_time_window_report
        write_report(args.report, report)
    except (OSError, RuntimeError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
