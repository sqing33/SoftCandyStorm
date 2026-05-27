#!/usr/bin/env python3
import argparse
import json
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from python.train.train_behavior_clone import (
    dependency_status,
    load_trajectory_dataset,
    ratio_counts,
)


def load_trace(path):
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    steps = payload.get("steps")
    if not isinstance(steps, list) or not steps:
        raise ValueError("trace must contain a non-empty steps array")
    observations = []
    kept_steps = []
    for step in steps:
        observation = step.get("observation") if isinstance(step, dict) else None
        if not isinstance(observation, list) or not observation:
            continue
        observations.append([float(value) for value in observation])
        kept_steps.append(step)
    if not observations:
        raise ValueError("trace does not contain sampled observations")
    return {
        "path": str(path),
        "episode": payload.get("episode", {}),
        "steps": kept_steps,
        "observations": observations,
    }


def conditioned_trace_observation(step, observation, phase_duration_seconds):
    if phase_duration_seconds is None:
        return observation
    duration = float(phase_duration_seconds)
    if duration <= 0.0:
        raise ValueError("phase_duration_seconds must be greater than zero")
    adjusted = list(observation)
    adjusted[0] = max(0.0, min(1.0, float(step.get("time_seconds", 0.0)) / duration))
    return adjusted


def candidate_indices(dataset, *, map_id=None, min_seconds=None, max_seconds=None):
    indices = []
    for index, sample in enumerate(dataset["sample_metadata"]):
        if map_id is not None and str(sample.get("map_id")) != str(map_id):
            continue
        time_seconds = float(sample.get("time_seconds", 0.0))
        if min_seconds is not None and time_seconds < min_seconds:
            continue
        if max_seconds is not None and time_seconds > max_seconds:
            continue
        indices.append(index)
    if not indices:
        raise ValueError("dataset filters removed all candidate samples")
    return indices


def count_distribution(values):
    counts = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return ratio_counts(counts, len(values))


def dominant_distribution_entry(distribution):
    if not distribution:
        return ("none", {"count": 0, "ratio": 0.0})
    return max(distribution.items(), key=lambda item: (item[1]["count"], item[0]))


def entropy_bits(values):
    counts = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    total = len(values)
    entropy = 0.0
    for count in counts.values():
        ratio = count / max(1, total)
        entropy -= ratio * math.log2(ratio)
    return entropy


def summarize_distances(distances):
    if not distances:
        return {"min": 0.0, "average": 0.0, "max": 0.0}
    return {
        "min": round(min(distances), 6),
        "average": round(sum(distances) / len(distances), 6),
        "max": round(max(distances), 6),
    }


def first_action_change(records, key):
    if not records:
        return None
    first_action = records[0][key]
    for record in records[1:]:
        if record[key] != first_action:
            return {
                "trace_index": record["trace_index"],
                "time_seconds": round(record["time_seconds"], 4),
                "from_action": int(first_action),
                "to_action": int(record[key]),
            }
    return None


def summarize_time_buckets(records, bucket_seconds):
    if bucket_seconds is None:
        return []
    bucket_seconds = float(bucket_seconds)
    if bucket_seconds <= 0.0:
        raise ValueError("time_bucket_seconds must be greater than zero")

    buckets = {}
    for record in records:
        bucket_index = int(record["time_seconds"] // bucket_seconds)
        bucket = buckets.setdefault(
            bucket_index,
            {
                "bucket_index": bucket_index,
                "start_seconds": round(bucket_index * bucket_seconds, 4),
                "end_seconds": round((bucket_index + 1) * bucket_seconds, 4),
                "online_actions": [],
                "nearest_actions": [],
                "nearest_distances": [],
                "match_count": 0,
            },
        )
        bucket["online_actions"].append(record["online_action"])
        bucket["nearest_actions"].append(record["nearest_action"])
        bucket["nearest_distances"].append(record["nearest_distance"])
        if record["online_action"] == record["nearest_action"]:
            bucket["match_count"] += 1

    summaries = []
    for bucket_index in sorted(buckets):
        bucket = buckets[bucket_index]
        sample_count = len(bucket["online_actions"])
        summaries.append(
            {
                "bucket_index": bucket["bucket_index"],
                "start_seconds": bucket["start_seconds"],
                "end_seconds": bucket["end_seconds"],
                "sample_count": sample_count,
                "online_action_distribution": count_distribution(bucket["online_actions"]),
                "nearest_target_action_distribution": count_distribution(bucket["nearest_actions"]),
                "nearest_target_matches_online_action_ratio": round(
                    bucket["match_count"] / max(1, sample_count),
                    4,
                ),
                "nearest_distance": summarize_distances(bucket["nearest_distances"]),
            }
        )
    return summaries


def compare_trace_to_dataset(
    trace,
    dataset,
    *,
    phase_duration_seconds=None,
    same_map_only=False,
    offline_min_seconds=None,
    offline_max_seconds=None,
    nearest_k=3,
    example_limit=12,
    time_bucket_seconds=None,
):
    import numpy as np

    trace_map_id = trace.get("episode", {}).get("map_id")
    filter_map_id = trace_map_id if same_map_only else None
    indices = candidate_indices(
        dataset,
        map_id=filter_map_id,
        min_seconds=offline_min_seconds,
        max_seconds=offline_max_seconds,
    )
    offline = np.asarray([dataset["observations"][index] for index in indices], dtype=np.float32)
    if offline.shape[1] != len(trace["observations"][0]):
        raise ValueError(
            f"observation length mismatch: trace {len(trace['observations'][0])}, dataset {offline.shape[1]}"
        )

    nearest_actions = []
    online_actions = []
    distances = []
    records = []
    examples = []
    k = max(1, min(int(nearest_k), len(indices)))
    for trace_index, (step, observation) in enumerate(zip(trace["steps"], trace["observations"])):
        conditioned = np.asarray(
            conditioned_trace_observation(step, observation, phase_duration_seconds),
            dtype=np.float32,
        )
        squared = np.sum((offline - conditioned.reshape(1, -1)) ** 2, axis=1)
        nearest_positions = np.argpartition(squared, k - 1)[:k]
        nearest_positions = nearest_positions[np.argsort(squared[nearest_positions])]
        nearest_dataset_indices = [indices[int(position)] for position in nearest_positions]
        nearest_distance = float(np.sqrt(squared[int(nearest_positions[0])]))
        nearest_action = int(dataset["actions"][nearest_dataset_indices[0]])
        online_action = int(step.get("action", -1))
        nearest_actions.append(nearest_action)
        online_actions.append(online_action)
        distances.append(nearest_distance)
        records.append(
            {
                "trace_index": trace_index,
                "time_seconds": float(step.get("time_seconds", 0.0)),
                "online_action": online_action,
                "nearest_action": nearest_action,
                "nearest_distance": nearest_distance,
            }
        )
        if len(examples) < example_limit:
            neighbors = []
            for position in nearest_positions:
                dataset_index = indices[int(position)]
                sample = dataset["sample_metadata"][dataset_index]
                neighbors.append(
                    {
                        "distance": round(float(np.sqrt(squared[int(position)])), 6),
                        "target_action": int(dataset["actions"][dataset_index]),
                        "map_id": sample.get("map_id"),
                        "time_seconds": round(float(sample.get("time_seconds", 0.0)), 4),
                        "sample_source": sample.get("sample_source", "trajectory"),
                    }
                )
            examples.append(
                {
                    "trace_index": trace_index,
                    "step": int(step.get("step", 0)),
                    "time_seconds": round(float(step.get("time_seconds", 0.0)), 4),
                    "online_action": online_action,
                    "trace_observation_progress": round(float(observation[0]), 6),
                    "conditioned_progress": round(float(conditioned[0]), 6),
                    "nearest": neighbors,
                }
            )

    action_count = max(dataset["action_count"], max(online_actions + nearest_actions) + 1)
    action_entropy = entropy_bits(online_actions)
    max_entropy = math.log2(max(2, action_count))
    match_count = sum(
        1
        for online_action, nearest_action in zip(online_actions, nearest_actions)
        if int(online_action) == int(nearest_action)
    )
    return {
        "report_version": 1,
        "status": "compared",
        "gate_decision": "trace_dataset_nearest_neighbor_recorded_watch_only",
        "trace": {
            "path": trace["path"],
            "map_id": trace_map_id,
            "sample_count": len(trace["steps"]),
        },
        "dataset": {
            "paths": dataset["paths"],
            "candidate_count": len(indices),
            "same_map_only": same_map_only,
            "offline_min_seconds": offline_min_seconds,
            "offline_max_seconds": offline_max_seconds,
        },
        "conditioning": {
            "phase_duration_seconds": phase_duration_seconds,
        },
        "summary": {
            "online_action_distribution": count_distribution(online_actions),
            "nearest_target_action_distribution": count_distribution(nearest_actions),
            "nearest_target_matches_online_action_ratio": round(match_count / max(1, len(online_actions)), 4),
            "online_action_entropy_bits": round(action_entropy, 4),
            "normalized_online_action_entropy": round(action_entropy / max_entropy, 4),
            "nearest_distance": summarize_distances(distances),
            "first_online_action_change": first_action_change(records, "online_action"),
            "first_nearest_target_change": first_action_change(records, "nearest_action"),
        },
        "time_buckets": summarize_time_buckets(records, time_bucket_seconds),
        "examples": examples,
        "limitations": [
            "Nearest-neighbor trace comparison is diagnostic evidence only.",
            "It does not prove policy quality, Replay stability, balance, or fun.",
        ],
    }


def write_json(path, payload):
    if path is None:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_markdown(path, report):
    if path is None:
        return
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    distance = report["summary"]["nearest_distance"]
    lines = [
        "# Behavior Clone Trace Dataset Comparison",
        "",
        f"- Gate decision: `{report['gate_decision']}`",
        f"- Trace samples: `{report['trace']['sample_count']}`",
        f"- Offline candidates: `{report['dataset']['candidate_count']}`",
        f"- Same map only: `{report['dataset']['same_map_only']}`",
        f"- Offline window: `{report['dataset']['offline_min_seconds']}` to `{report['dataset']['offline_max_seconds']}`",
        f"- Phase duration conditioning: `{report['conditioning']['phase_duration_seconds']}`",
        f"- Nearest target matches online action ratio: `{report['summary']['nearest_target_matches_online_action_ratio']}`",
        f"- Online normalized action entropy: `{report['summary']['normalized_online_action_entropy']}`",
        f"- Nearest distance average: `{distance['average']}`",
        "",
        "## Transitions",
        "",
        "```json",
        json.dumps(
            {
                "first_online_action_change": report["summary"]["first_online_action_change"],
                "first_nearest_target_change": report["summary"]["first_nearest_target_change"],
            },
            indent=2,
            ensure_ascii=False,
        ),
        "```",
        "",
        "## Action Distributions",
        "",
        "### Online",
        "",
        "```json",
        json.dumps(report["summary"]["online_action_distribution"], indent=2, ensure_ascii=False),
        "```",
        "",
        "### Nearest Offline Target",
        "",
        "```json",
        json.dumps(report["summary"]["nearest_target_action_distribution"], indent=2, ensure_ascii=False),
        "```",
        "",
        "## Time Buckets",
        "",
    ]
    if report["time_buckets"]:
        lines.extend(
            [
                "| Window | Samples | Online Top | Nearest Top | Match Ratio | Avg Distance |",
                "|---|---:|---|---|---:|---:|",
            ]
        )
        for bucket in report["time_buckets"]:
            online_top = dominant_distribution_entry(bucket["online_action_distribution"])
            nearest_top = dominant_distribution_entry(bucket["nearest_target_action_distribution"])
            lines.append(
                "| `{:.4g}-{:.4g}` | `{}` | `{}` `{:.4f}` | `{}` `{:.4f}` | `{:.4f}` | `{:.6f}` |".format(
                    bucket["start_seconds"],
                    bucket["end_seconds"],
                    bucket["sample_count"],
                    online_top[0],
                    online_top[1]["ratio"],
                    nearest_top[0],
                    nearest_top[1]["ratio"],
                    bucket["nearest_target_matches_online_action_ratio"],
                    bucket["nearest_distance"]["average"],
                )
            )
        lines.append("")
    else:
        lines.extend(["No time buckets requested.", ""])
    lines.extend(
        [
            "## Examples",
            "",
        ]
    )
    for example in report["examples"]:
        nearest = example["nearest"][0]
        lines.append(
            "- step `{}` time `{}` online `{}` conditioned_progress `{}` nearest action `{}` distance `{}` offline_time `{}`".format(
                example["step"],
                example["time_seconds"],
                example["online_action"],
                example["conditioned_progress"],
                nearest["target_action"],
                nearest["distance"],
                nearest["time_seconds"],
            )
        )
    lines.extend(["", "## Limitations", ""])
    for limitation in report["limitations"]:
        lines.append(f"- {limitation}")
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Compare behavior clone online trace observations to offline training samples."
    )
    parser.add_argument("--trace", required=True)
    parser.add_argument("--dataset", action="append", required=True)
    parser.add_argument("--same-map-only", action="store_true")
    parser.add_argument("--offline-min-seconds", type=float, default=None)
    parser.add_argument("--offline-max-seconds", type=float, default=None)
    parser.add_argument("--phase-duration-seconds", type=float, default=None)
    parser.add_argument("--nearest-k", type=int, default=3)
    parser.add_argument("--example-limit", type=int, default=12)
    parser.add_argument("--time-bucket-seconds", type=float, default=None)
    parser.add_argument("--report", default=None)
    parser.add_argument("--markdown", default=None)
    args = parser.parse_args()

    if args.nearest_k <= 0:
        parser.error("--nearest-k must be greater than zero")
    if args.example_limit < 0:
        parser.error("--example-limit must be greater than or equal to zero")
    if args.time_bucket_seconds is not None and args.time_bucket_seconds <= 0:
        parser.error("--time-bucket-seconds must be greater than zero")
    if (
        args.offline_min_seconds is not None
        and args.offline_max_seconds is not None
        and args.offline_max_seconds < args.offline_min_seconds
    ):
        parser.error("--offline-max-seconds must be greater than or equal to --offline-min-seconds")

    trace = load_trace(args.trace)
    dataset = load_trajectory_dataset(args.dataset)
    report = compare_trace_to_dataset(
        trace,
        dataset,
        phase_duration_seconds=args.phase_duration_seconds,
        same_map_only=args.same_map_only,
        offline_min_seconds=args.offline_min_seconds,
        offline_max_seconds=args.offline_max_seconds,
        nearest_k=args.nearest_k,
        example_limit=args.example_limit,
        time_bucket_seconds=args.time_bucket_seconds,
    )
    report["dependency_status"] = dependency_status()
    write_json(args.report, report)
    write_markdown(args.markdown, report)


if __name__ == "__main__":
    main()
