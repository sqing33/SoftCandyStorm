#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from python.train.compare_behavior_clone_trace_to_dataset import (
    candidate_indices,
    conditioned_trace_observation,
    count_distribution,
    load_trace,
    summarize_distances,
)
from python.train.train_behavior_clone import dependency_status, load_trajectory_dataset


def parse_time_window(value):
    try:
        start_text, end_text = value.split(":", 1)
        start = float(start_text)
        end = float(end_text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("time windows must use START:END") from exc
    if end <= start:
        raise argparse.ArgumentTypeError("time window END must be greater than START")
    return (start, end)


def sample_key(sample):
    return (
        sample.get("path"),
        sample.get("map_id"),
        sample.get("seed"),
        sample.get("sample_source", "trajectory"),
    )


def build_episode_index(dataset):
    episodes = {}
    for index, sample in enumerate(dataset["sample_metadata"]):
        key = sample_key(sample)
        episodes.setdefault(key, []).append(index)
    for indices in episodes.values():
        indices.sort(
            key=lambda item: (
                float(dataset["sample_metadata"][item].get("time_seconds", 0.0)),
                int(dataset["sample_metadata"][item].get("tick", 0)),
            )
        )
    return episodes


def sequence_around(dataset, episodes, dataset_index, radius):
    sample = dataset["sample_metadata"][dataset_index]
    key = sample_key(sample)
    indices = episodes.get(key, [])
    try:
        position = indices.index(dataset_index)
    except ValueError:
        position = 0
    start = max(0, position - radius)
    end = min(len(indices), position + radius + 1)
    sequence = []
    for index in indices[start:end]:
        item = dataset["sample_metadata"][index]
        sequence.append(
            {
                "dataset_index": index,
                "time_seconds": round(float(item.get("time_seconds", 0.0)), 4),
                "tick": int(item.get("tick", 0)),
                "action": int(dataset["actions"][index]),
                "health_ratio": round(float(item.get("health_ratio", 1.0)), 4),
                "level": int(item.get("level", 0)),
                "kills": int(item.get("kills", 0)),
            }
        )
    return sequence


def trace_sequence_around(trace, trace_index, radius):
    start = max(0, trace_index - radius)
    end = min(len(trace["steps"]), trace_index + radius + 1)
    sequence = []
    for index in range(start, end):
        step = trace["steps"][index]
        sequence.append(
            {
                "trace_index": index,
                "time_seconds": round(float(step.get("time_seconds", 0.0)), 4),
                "step": int(step.get("step", 0)),
                "action": int(step.get("action", -1)),
                "health": round(float(step.get("health", 0.0)), 4),
                "level": int(step.get("level", 0)),
                "kills": int(step.get("kills", 0)),
            }
        )
    return sequence


def inspect_teacher_sequences(
    trace,
    dataset,
    *,
    time_windows,
    phase_duration_seconds=None,
    same_map_only=False,
    offline_min_seconds=None,
    offline_max_seconds=None,
    sequence_radius=4,
    examples_per_window=5,
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

    episodes = build_episode_index(dataset)
    window_reports = []
    for start_seconds, end_seconds in time_windows:
        records = []
        for trace_index, (step, observation) in enumerate(zip(trace["steps"], trace["observations"])):
            time_seconds = float(step.get("time_seconds", 0.0))
            if time_seconds < start_seconds or time_seconds >= end_seconds:
                continue
            conditioned = np.asarray(
                conditioned_trace_observation(step, observation, phase_duration_seconds),
                dtype=np.float32,
            )
            squared = np.sum((offline - conditioned.reshape(1, -1)) ** 2, axis=1)
            nearest_position = int(np.argmin(squared))
            dataset_index = indices[nearest_position]
            sample = dataset["sample_metadata"][dataset_index]
            online_action = int(step.get("action", -1))
            nearest_action = int(dataset["actions"][dataset_index])
            distance = float(np.sqrt(squared[nearest_position]))
            records.append(
                {
                    "trace_index": trace_index,
                    "trace_time_seconds": time_seconds,
                    "online_action": online_action,
                    "nearest_dataset_index": dataset_index,
                    "nearest_action": nearest_action,
                    "nearest_time_seconds": float(sample.get("time_seconds", 0.0)),
                    "nearest_seed": sample.get("seed"),
                    "nearest_map_id": sample.get("map_id"),
                    "nearest_sample_source": sample.get("sample_source", "trajectory"),
                    "nearest_path": sample.get("path"),
                    "distance": distance,
                    "matches": online_action == nearest_action,
                }
            )
        if not records:
            raise ValueError(f"time window {start_seconds}:{end_seconds} did not match trace samples")

        nearest_episode_counts = {}
        for record in records:
            key = "|".join(
                str(record.get(field))
                for field in (
                    "nearest_path",
                    "nearest_map_id",
                    "nearest_seed",
                    "nearest_sample_source",
                )
            )
            nearest_episode_counts[key] = nearest_episode_counts.get(key, 0) + 1

        mismatch_records = [record for record in records if not record["matches"]]
        representative_records = mismatch_records[:examples_per_window]
        if len(representative_records) < examples_per_window:
            representative_records.extend(records[: examples_per_window - len(representative_records)])

        examples = []
        for record in representative_records:
            dataset_index = record["nearest_dataset_index"]
            sample = dataset["sample_metadata"][dataset_index]
            examples.append(
                {
                    "trace_index": record["trace_index"],
                    "trace_time_seconds": round(record["trace_time_seconds"], 4),
                    "online_action": record["online_action"],
                    "nearest": {
                        "dataset_index": dataset_index,
                        "distance": round(record["distance"], 6),
                        "target_action": record["nearest_action"],
                        "map_id": sample.get("map_id"),
                        "seed": sample.get("seed"),
                        "time_seconds": round(float(sample.get("time_seconds", 0.0)), 4),
                        "sample_source": sample.get("sample_source", "trajectory"),
                        "path": sample.get("path"),
                    },
                    "online_sequence": trace_sequence_around(trace, record["trace_index"], sequence_radius),
                    "teacher_sequence": sequence_around(dataset, episodes, dataset_index, sequence_radius),
                }
            )

        window_reports.append(
            {
                "start_seconds": round(float(start_seconds), 4),
                "end_seconds": round(float(end_seconds), 4),
                "sample_count": len(records),
                "online_action_distribution": count_distribution(
                    [record["online_action"] for record in records]
                ),
                "nearest_target_action_distribution": count_distribution(
                    [record["nearest_action"] for record in records]
                ),
                "nearest_target_matches_online_action_ratio": round(
                    sum(1 for record in records if record["matches"]) / max(1, len(records)),
                    4,
                ),
                "nearest_distance": summarize_distances([record["distance"] for record in records]),
                "top_nearest_episode_keys": [
                    {"episode_key": key, "count": count}
                    for key, count in sorted(
                        nearest_episode_counts.items(),
                        key=lambda item: (-item[1], item[0]),
                    )[:5]
                ],
                "examples": examples,
            }
        )

    return {
        "report_version": 1,
        "status": "inspected",
        "gate_decision": "teacher_sequence_diagnostic_recorded_watch_only",
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
        "parameters": {
            "time_windows": [
                {"start_seconds": start, "end_seconds": end} for start, end in time_windows
            ],
            "sequence_radius": sequence_radius,
            "examples_per_window": examples_per_window,
        },
        "windows": window_reports,
        "limitations": [
            "Teacher sequence inspection is diagnostic evidence only.",
            "Nearest observations may come from different episodes and do not prove policy quality.",
            "This does not replace deterministic high-pressure gates, Replay, or human playtest.",
        ],
    }


def write_json(path, payload):
    if path is None:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def compact_distribution(distribution):
    return ", ".join(
        f"`{action}` {item['ratio']:.4f}" for action, item in distribution.items()
    )


def action_sequence_text(sequence):
    return " ".join(f"{item['time_seconds']}:{item['action']}" for item in sequence)


def write_markdown(path, report):
    if path is None:
        return
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Behavior Clone Teacher Sequence Diagnostic",
        "",
        f"- Gate decision: `{report['gate_decision']}`",
        f"- Trace samples: `{report['trace']['sample_count']}`",
        f"- Offline candidates: `{report['dataset']['candidate_count']}`",
        f"- Same map only: `{report['dataset']['same_map_only']}`",
        f"- Phase duration conditioning: `{report['conditioning']['phase_duration_seconds']}`",
        "",
        "## Windows",
        "",
        "| Window | Samples | Online | Nearest | Match Ratio | Avg Distance |",
        "|---|---:|---|---|---:|---:|",
    ]
    for window in report["windows"]:
        lines.append(
            "| `{}-{}` | `{}` | {} | {} | `{:.4f}` | `{:.6f}` |".format(
                window["start_seconds"],
                window["end_seconds"],
                window["sample_count"],
                compact_distribution(window["online_action_distribution"]),
                compact_distribution(window["nearest_target_action_distribution"]),
                window["nearest_target_matches_online_action_ratio"],
                window["nearest_distance"]["average"],
            )
        )
    lines.extend(["", "## Examples", ""])
    for window in report["windows"]:
        lines.append(f"### `{window['start_seconds']}-{window['end_seconds']}`")
        lines.append("")
        for example in window["examples"]:
            nearest = example["nearest"]
            lines.append(
                "- trace `{}` time `{}` online `{}` nearest `{}` seed `{}` offline_time `{}` distance `{}`".format(
                    example["trace_index"],
                    example["trace_time_seconds"],
                    example["online_action"],
                    nearest["target_action"],
                    nearest["seed"],
                    nearest["time_seconds"],
                    nearest["distance"],
                )
            )
            lines.append(f"  - online sequence: `{action_sequence_text(example['online_sequence'])}`")
            lines.append(f"  - teacher sequence: `{action_sequence_text(example['teacher_sequence'])}`")
        lines.append("")
    lines.extend(["## Limitations", ""])
    for limitation in report["limitations"]:
        lines.append(f"- {limitation}")
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Inspect nearest offline teacher sequences for behavior clone trace windows."
    )
    parser.add_argument("--trace", required=True)
    parser.add_argument("--dataset", action="append", required=True)
    parser.add_argument("--time-window", action="append", type=parse_time_window, required=True)
    parser.add_argument("--same-map-only", action="store_true")
    parser.add_argument("--offline-min-seconds", type=float, default=None)
    parser.add_argument("--offline-max-seconds", type=float, default=None)
    parser.add_argument("--phase-duration-seconds", type=float, default=None)
    parser.add_argument("--sequence-radius", type=int, default=4)
    parser.add_argument("--examples-per-window", type=int, default=5)
    parser.add_argument("--report", default=None)
    parser.add_argument("--markdown", default=None)
    args = parser.parse_args()

    if args.sequence_radius < 0:
        parser.error("--sequence-radius must be greater than or equal to zero")
    if args.examples_per_window <= 0:
        parser.error("--examples-per-window must be greater than zero")
    if (
        args.offline_min_seconds is not None
        and args.offline_max_seconds is not None
        and args.offline_max_seconds < args.offline_min_seconds
    ):
        parser.error("--offline-max-seconds must be greater than or equal to --offline-min-seconds")

    trace = load_trace(args.trace)
    dataset = load_trajectory_dataset(args.dataset)
    report = inspect_teacher_sequences(
        trace,
        dataset,
        time_windows=args.time_window,
        phase_duration_seconds=args.phase_duration_seconds,
        same_map_only=args.same_map_only,
        offline_min_seconds=args.offline_min_seconds,
        offline_max_seconds=args.offline_max_seconds,
        sequence_radius=args.sequence_radius,
        examples_per_window=args.examples_per_window,
    )
    report["dependency_status"] = dependency_status()
    write_json(args.report, report)
    write_markdown(args.markdown, report)


if __name__ == "__main__":
    main()
