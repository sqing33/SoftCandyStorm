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
from python.train.inspect_behavior_clone_teacher_sequences import (
    build_episode_index,
    parse_time_window,
)
from python.train.train_behavior_clone import (
    dependency_status,
    load_behavior_clone_policy,
    load_trajectory_dataset,
)


def prefix_indices(sequence_indices, target_index, prefix_frames):
    if prefix_frames <= 0:
        return []
    try:
        position = sequence_indices.index(target_index)
    except ValueError:
        return []
    start = max(0, position - prefix_frames)
    return sequence_indices[start:position]


def score_summary(scores, action_count, *, online_action, nearest_action):
    ordered = sorted(enumerate(scores), key=lambda item: (-item[1], item[0]))
    return {
        "top_action": int(ordered[0][0]),
        "top_score": round(float(ordered[0][1]), 6),
        "top_actions": [
            {"action": int(action), "score": round(float(score), 6)}
            for action, score in ordered[: min(3, action_count)]
        ],
        "online_action_score": round(float(scores[online_action]), 6)
        if 0 <= online_action < len(scores)
        else None,
        "nearest_action_score": round(float(scores[nearest_action]), 6)
        if 0 <= nearest_action < len(scores)
        else None,
    }


def set_policy_context(policy, *, map_id, time_seconds, phase_duration_seconds):
    policy.set_map_id(map_id)
    info = {"time_seconds": float(time_seconds)}
    if phase_duration_seconds is not None:
        info["phase_duration_seconds"] = float(phase_duration_seconds)
    policy.set_step_context(info)


def scores_with_prefix(
    policy_path,
    *,
    map_id,
    target_step,
    target_observation,
    prefix_steps,
    phase_duration_seconds,
):
    policy = load_behavior_clone_policy(policy_path)
    policy.reset()
    policy.set_map_id(map_id)
    for step in prefix_steps:
        observation = step.get("observation")
        if not isinstance(observation, list) or not observation:
            continue
        set_policy_context(
            policy,
            map_id=map_id,
            time_seconds=step.get("time_seconds", 0.0),
            phase_duration_seconds=phase_duration_seconds,
        )
        policy.predict(observation, deterministic=True)
    set_policy_context(
        policy,
        map_id=map_id,
        time_seconds=target_step.get("time_seconds", 0.0),
        phase_duration_seconds=phase_duration_seconds,
    )
    return policy.action_scores(target_observation)["scores"]


def dataset_step(dataset, dataset_index):
    sample = dataset["sample_metadata"][dataset_index]
    return {
        "time_seconds": float(sample.get("time_seconds", 0.0)),
        "observation": dataset["observations"][dataset_index],
    }


def top_action_distribution(records, mode):
    return count_distribution([record["score_modes"][mode]["top_action"] for record in records])


def inspect_history_context(
    *,
    model,
    trace,
    dataset,
    time_windows,
    phase_duration_seconds=None,
    same_map_only=False,
    offline_min_seconds=None,
    offline_max_seconds=None,
    prefix_frames=7,
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

    windows = []
    for start_seconds, end_seconds in time_windows:
        records = []
        for trace_index, (step, observation) in enumerate(zip(trace["steps"], trace["observations"])):
            trace_time = float(step.get("time_seconds", 0.0))
            if trace_time < start_seconds or trace_time >= end_seconds:
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

            online_prefix_steps = trace["steps"][max(0, trace_index - prefix_frames) : trace_index]
            episode_indices = episodes.get(
                (
                    sample.get("path"),
                    sample.get("map_id"),
                    sample.get("seed"),
                    sample.get("sample_source", "trajectory"),
                ),
                [],
            )
            teacher_prefix = [
                dataset_step(dataset, index)
                for index in prefix_indices(episode_indices, dataset_index, prefix_frames)
            ]

            cold_scores = scores_with_prefix(
                model,
                map_id=trace_map_id,
                target_step=step,
                target_observation=observation,
                prefix_steps=[],
                phase_duration_seconds=phase_duration_seconds,
            )
            online_scores = scores_with_prefix(
                model,
                map_id=trace_map_id,
                target_step=step,
                target_observation=observation,
                prefix_steps=online_prefix_steps,
                phase_duration_seconds=phase_duration_seconds,
            )
            teacher_scores = scores_with_prefix(
                model,
                map_id=trace_map_id,
                target_step=step,
                target_observation=observation,
                prefix_steps=teacher_prefix,
                phase_duration_seconds=phase_duration_seconds,
            )
            action_count = max(len(cold_scores), len(online_scores), len(teacher_scores))
            records.append(
                {
                    "trace_index": trace_index,
                    "trace_time_seconds": round(trace_time, 4),
                    "online_action": online_action,
                    "nearest": {
                        "dataset_index": dataset_index,
                        "distance": round(float(np.sqrt(squared[nearest_position])), 6),
                        "target_action": nearest_action,
                        "map_id": sample.get("map_id"),
                        "seed": sample.get("seed"),
                        "time_seconds": round(float(sample.get("time_seconds", 0.0)), 4),
                        "sample_source": sample.get("sample_source", "trajectory"),
                    },
                    "prefix_lengths": {
                        "online": len(online_prefix_steps),
                        "teacher": len(teacher_prefix),
                    },
                    "score_modes": {
                        "cold": score_summary(
                            cold_scores,
                            action_count,
                            online_action=online_action,
                            nearest_action=nearest_action,
                        ),
                        "online_prefix": score_summary(
                            online_scores,
                            action_count,
                            online_action=online_action,
                            nearest_action=nearest_action,
                        ),
                        "teacher_prefix": score_summary(
                            teacher_scores,
                            action_count,
                            online_action=online_action,
                            nearest_action=nearest_action,
                        ),
                    },
                }
            )
        if not records:
            raise ValueError(f"time window {start_seconds}:{end_seconds} did not match trace samples")
        windows.append(
            {
                "start_seconds": round(float(start_seconds), 4),
                "end_seconds": round(float(end_seconds), 4),
                "sample_count": len(records),
                "online_action_distribution": count_distribution(
                    [record["online_action"] for record in records]
                ),
                "nearest_target_action_distribution": count_distribution(
                    [record["nearest"]["target_action"] for record in records]
                ),
                "nearest_distance": summarize_distances(
                    [record["nearest"]["distance"] for record in records]
                ),
                "top_action_distribution_by_mode": {
                    "cold": top_action_distribution(records, "cold"),
                    "online_prefix": top_action_distribution(records, "online_prefix"),
                    "teacher_prefix": top_action_distribution(records, "teacher_prefix"),
                },
                "examples": records[:examples_per_window],
            }
        )

    return {
        "report_version": 1,
        "status": "inspected",
        "gate_decision": "history_context_probe_recorded_watch_only",
        "model": str(model),
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
            "prefix_frames": prefix_frames,
            "examples_per_window": examples_per_window,
        },
        "windows": windows,
        "limitations": [
            "History context probing is diagnostic evidence only.",
            "It compares observation history prefixes, not supervised training or policy acceptance.",
            "It does not replace deterministic high-pressure gates, Replay, or human playtest.",
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


def write_markdown(path, report):
    if path is None:
        return
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Behavior Clone History Context Probe",
        "",
        f"- Gate decision: `{report['gate_decision']}`",
        f"- Model: `{report['model']}`",
        f"- Trace samples: `{report['trace']['sample_count']}`",
        f"- Prefix frames: `{report['parameters']['prefix_frames']}`",
        "",
        "## Windows",
        "",
        "| Window | Samples | Online | Nearest | Cold Top | Online-Prefix Top | Teacher-Prefix Top |",
        "|---|---:|---|---|---|---|---|",
    ]
    for window in report["windows"]:
        mode_distribution = window["top_action_distribution_by_mode"]
        lines.append(
            "| `{}-{}` | `{}` | {} | {} | {} | {} | {} |".format(
                window["start_seconds"],
                window["end_seconds"],
                window["sample_count"],
                compact_distribution(window["online_action_distribution"]),
                compact_distribution(window["nearest_target_action_distribution"]),
                compact_distribution(mode_distribution["cold"]),
                compact_distribution(mode_distribution["online_prefix"]),
                compact_distribution(mode_distribution["teacher_prefix"]),
            )
        )

    lines.extend(["", "## Examples", ""])
    for window in report["windows"]:
        lines.append(f"### `{window['start_seconds']}-{window['end_seconds']}`")
        lines.append("")
        for example in window["examples"]:
            lines.append(
                "- trace `{}` time `{}` online `{}` nearest `{}` distance `{}`".format(
                    example["trace_index"],
                    example["trace_time_seconds"],
                    example["online_action"],
                    example["nearest"]["target_action"],
                    example["nearest"]["distance"],
                )
            )
            for mode, summary in example["score_modes"].items():
                lines.append(
                    "  - `{}` top `{}` score `{}` online_score `{}` nearest_score `{}`".format(
                        mode,
                        summary["top_action"],
                        summary["top_score"],
                        summary["online_action_score"],
                        summary["nearest_action_score"],
                    )
                )
        lines.append("")

    lines.extend(["## Limitations", ""])
    for limitation in report["limitations"]:
        lines.append(f"- {limitation}")
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Probe behavior clone predictions under cold, online-prefix, and teacher-prefix histories."
    )
    parser.add_argument("--model", required=True)
    parser.add_argument("--trace", required=True)
    parser.add_argument("--dataset", action="append", required=True)
    parser.add_argument("--time-window", action="append", type=parse_time_window, required=True)
    parser.add_argument("--same-map-only", action="store_true")
    parser.add_argument("--offline-min-seconds", type=float, default=None)
    parser.add_argument("--offline-max-seconds", type=float, default=None)
    parser.add_argument("--phase-duration-seconds", type=float, default=None)
    parser.add_argument("--prefix-frames", type=int, default=7)
    parser.add_argument("--examples-per-window", type=int, default=5)
    parser.add_argument("--report", default=None)
    parser.add_argument("--markdown", default=None)
    args = parser.parse_args()

    if args.prefix_frames < 0:
        parser.error("--prefix-frames must be greater than or equal to zero")
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
    report = inspect_history_context(
        model=args.model,
        trace=trace,
        dataset=dataset,
        time_windows=args.time_window,
        phase_duration_seconds=args.phase_duration_seconds,
        same_map_only=args.same_map_only,
        offline_min_seconds=args.offline_min_seconds,
        offline_max_seconds=args.offline_max_seconds,
        prefix_frames=args.prefix_frames,
        examples_per_window=args.examples_per_window,
    )
    report["dependency_status"] = dependency_status()
    write_json(args.report, report)
    write_markdown(args.markdown, report)


if __name__ == "__main__":
    main()
