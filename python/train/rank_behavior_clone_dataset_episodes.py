#!/usr/bin/env python3
"""Rank offline trajectory episodes by nearest coverage of online traces."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from python.train.compare_behavior_clone_trace_to_dataset import (  # noqa: E402
    candidate_indices,
    conditioned_trace_observation,
    count_distribution,
    load_trace,
    summarize_distances,
)
from python.train.train_behavior_clone import (  # noqa: E402
    dependency_status,
    load_trajectory_dataset,
)


def episode_key(sample: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(sample.get("map_id", "")),
        str(sample.get("seed", "")),
        str(sample.get("bot") or "unknown"),
    )


def new_episode_stats(key: tuple[str, str, str]) -> dict[str, Any]:
    return {
        "map_id": key[0],
        "seed": key[1],
        "bot": key[2],
        "candidate_sample_count": 0,
        "top1_hit_count": 0,
        "top1_action_match_count": 0,
        "top1_distances": [],
        "top1_online_actions": [],
        "top1_target_actions": [],
        "topk_hit_count": 0,
        "topk_action_match_count": 0,
        "topk_distances": [],
    }


def finalize_episode_stats(
    stats: dict[str, Any],
    *,
    trace_sample_count: int,
) -> dict[str, Any]:
    top1_hit_count = int(stats["top1_hit_count"])
    topk_hit_count = int(stats["topk_hit_count"])
    top1_matches = int(stats["top1_action_match_count"])
    topk_matches = int(stats["topk_action_match_count"])
    return {
        "map_id": stats["map_id"],
        "seed": stats["seed"],
        "bot": stats["bot"],
        "candidate_sample_count": int(stats["candidate_sample_count"]),
        "top1_hit_count": top1_hit_count,
        "top1_trace_coverage_ratio": round(
            top1_hit_count / max(1, trace_sample_count),
            4,
        ),
        "top1_action_match_count": top1_matches,
        "top1_action_match_ratio": round(top1_matches / max(1, top1_hit_count), 4),
        "top1_nearest_distance": summarize_distances(stats["top1_distances"]),
        "top1_online_action_distribution": count_distribution(stats["top1_online_actions"]),
        "top1_target_action_distribution": count_distribution(stats["top1_target_actions"]),
        "topk_hit_count": topk_hit_count,
        "topk_action_match_count": topk_matches,
        "topk_action_match_ratio": round(topk_matches / max(1, topk_hit_count), 4),
        "topk_nearest_distance": summarize_distances(stats["topk_distances"]),
    }


def episode_sort_key(item: dict[str, Any]) -> tuple[Any, ...]:
    distance = item["top1_nearest_distance"]["average"]
    if not math.isfinite(float(distance)):
        distance = 1_000_000.0
    return (
        -int(item["top1_action_match_count"]),
        -int(item["top1_hit_count"]),
        float(distance),
        item["map_id"],
        item["seed"],
        item["bot"],
    )


def rank_trace_against_dataset(
    trace: dict[str, Any],
    dataset: dict[str, Any],
    *,
    phase_duration_seconds: float | None = None,
    same_map_only: bool = False,
    offline_min_seconds: float | None = None,
    offline_max_seconds: float | None = None,
    nearest_k: int = 3,
    top_limit: int = 20,
) -> dict[str, Any]:
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
            f"observation length mismatch: trace {len(trace['observations'][0])}, "
            f"dataset {offline.shape[1]}"
        )

    stats_by_episode: dict[tuple[str, str, str], dict[str, Any]] = {}
    for dataset_index in indices:
        sample = dataset["sample_metadata"][dataset_index]
        key = episode_key(sample)
        stats = stats_by_episode.setdefault(key, new_episode_stats(key))
        stats["candidate_sample_count"] += 1

    k = max(1, min(int(nearest_k), len(indices)))
    all_top1_distances: list[float] = []
    all_online_actions: list[int] = []
    all_target_actions: list[int] = []
    trace_sample_count = len(trace["observations"])
    for step, observation in zip(trace["steps"], trace["observations"]):
        conditioned = np.asarray(
            conditioned_trace_observation(step, observation, phase_duration_seconds),
            dtype=np.float32,
        )
        squared = np.sum((offline - conditioned.reshape(1, -1)) ** 2, axis=1)
        nearest_positions = np.argpartition(squared, k - 1)[:k]
        nearest_positions = nearest_positions[np.argsort(squared[nearest_positions])]
        online_action = int(step.get("action", -1))
        all_online_actions.append(online_action)

        for rank, position in enumerate(nearest_positions):
            dataset_index = indices[int(position)]
            sample = dataset["sample_metadata"][dataset_index]
            target_action = int(dataset["actions"][dataset_index])
            distance = float(np.sqrt(squared[int(position)]))
            key = episode_key(sample)
            stats = stats_by_episode.setdefault(key, new_episode_stats(key))
            stats["topk_hit_count"] += 1
            stats["topk_distances"].append(distance)
            if online_action == target_action:
                stats["topk_action_match_count"] += 1

            if rank == 0:
                all_target_actions.append(target_action)
                all_top1_distances.append(distance)
                stats["top1_hit_count"] += 1
                stats["top1_distances"].append(distance)
                stats["top1_online_actions"].append(online_action)
                stats["top1_target_actions"].append(target_action)
                if online_action == target_action:
                    stats["top1_action_match_count"] += 1

    ranked = [
        finalize_episode_stats(stats, trace_sample_count=trace_sample_count)
        for stats in stats_by_episode.values()
        if stats["top1_hit_count"] or stats["topk_hit_count"]
    ]
    ranked.sort(key=episode_sort_key)

    match_count = sum(
        1
        for online_action, target_action in zip(all_online_actions, all_target_actions)
        if online_action == target_action
    )
    return {
        "trace": {
            "path": trace["path"],
            "map_id": trace_map_id,
            "sample_count": trace_sample_count,
        },
        "candidate_count": len(indices),
        "summary": {
            "top1_nearest_target_matches_online_action_ratio": round(
                match_count / max(1, trace_sample_count),
                4,
            ),
            "top1_nearest_distance": summarize_distances(all_top1_distances),
            "online_action_distribution": count_distribution(all_online_actions),
            "top1_target_action_distribution": count_distribution(all_target_actions),
        },
        "ranked_episodes": ranked[:top_limit],
    }


def merge_combined_rankings(
    trace_reports: list[dict[str, Any]],
    *,
    top_limit: int,
) -> dict[str, Any]:
    combined: dict[tuple[str, str, str], dict[str, Any]] = {}
    total_trace_samples = 0
    for trace_report in trace_reports:
        total_trace_samples += int(trace_report["trace"]["sample_count"])
        for episode in trace_report["ranked_episodes"]:
            key = (
                str(episode["map_id"]),
                str(episode["seed"]),
                str(episode["bot"]),
            )
            stats = combined.setdefault(key, new_episode_stats(key))
            stats["candidate_sample_count"] = max(
                int(stats["candidate_sample_count"]),
                int(episode["candidate_sample_count"]),
            )
            stats["top1_hit_count"] += int(episode["top1_hit_count"])
            stats["top1_action_match_count"] += int(episode["top1_action_match_count"])
            stats["top1_distances"].extend(
                [float(episode["top1_nearest_distance"]["average"])]
                * int(episode["top1_hit_count"])
            )
            stats["topk_hit_count"] += int(episode["topk_hit_count"])
            stats["topk_action_match_count"] += int(episode["topk_action_match_count"])
            stats["topk_distances"].extend(
                [float(episode["topk_nearest_distance"]["average"])]
                * int(episode["topk_hit_count"])
            )

    ranked = [
        finalize_episode_stats(stats, trace_sample_count=total_trace_samples)
        for stats in combined.values()
    ]
    ranked.sort(key=episode_sort_key)
    return {
        "trace_sample_count": total_trace_samples,
        "ranked_episodes": ranked[:top_limit],
    }


def rank_traces_against_dataset(
    traces: list[dict[str, Any]],
    dataset: dict[str, Any],
    *,
    phase_duration_seconds: float | None = None,
    same_map_only: bool = False,
    offline_min_seconds: float | None = None,
    offline_max_seconds: float | None = None,
    nearest_k: int = 3,
    top_limit: int = 20,
) -> dict[str, Any]:
    trace_reports = [
        rank_trace_against_dataset(
            trace,
            dataset,
            phase_duration_seconds=phase_duration_seconds,
            same_map_only=same_map_only,
            offline_min_seconds=offline_min_seconds,
            offline_max_seconds=offline_max_seconds,
            nearest_k=nearest_k,
            top_limit=top_limit,
        )
        for trace in traces
    ]
    return {
        "report_version": 1,
        "status": "ranked",
        "gate_decision": "dataset_episode_ranking_recorded_watch_only",
        "dataset": {
            "paths": dataset["paths"],
            "sample_count": len(dataset["actions"]),
            "episode_count": dataset["episode_count"],
            "observation_len": dataset["observation_len"],
            "action_count": dataset["action_count"],
            "same_map_only": same_map_only,
            "offline_min_seconds": offline_min_seconds,
            "offline_max_seconds": offline_max_seconds,
        },
        "conditioning": {
            "phase_duration_seconds": phase_duration_seconds,
            "nearest_k": nearest_k,
            "top_limit": top_limit,
        },
        "traces": trace_reports,
        "combined": merge_combined_rankings(trace_reports, top_limit=top_limit),
        "limitations": [
            "Episode ranking is diagnostic evidence only.",
            "High nearest coverage does not prove a trajectory should be imitated online.",
            "Any selected subset still needs training, action-distribution checks, and fixed-window no-regression gates.",
        ],
    }


def write_json(path: str | None, payload: dict[str, Any]) -> None:
    if path is None:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_markdown(path: str | None, report: dict[str, Any]) -> None:
    if path is None:
        return
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Behavior Clone Dataset Episode Ranking",
        "",
        f"- Gate decision: `{report['gate_decision']}`",
        f"- Dataset samples: `{report['dataset']['sample_count']}`",
        f"- Dataset episodes: `{report['dataset']['episode_count']}`",
        f"- Same map only: `{report['dataset']['same_map_only']}`",
        f"- Offline window: `{report['dataset']['offline_min_seconds']}` to `{report['dataset']['offline_max_seconds']}`",
        f"- Nearest k: `{report['conditioning']['nearest_k']}`",
        "",
        "## Combined Top Episodes",
        "",
        "| Rank | Map | Seed | Bot | Top1 hits | Match ratio | Avg distance |",
        "|---:|---|---:|---|---:|---:|---:|",
    ]
    for rank, episode in enumerate(report["combined"]["ranked_episodes"], start=1):
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{:.4f}` | `{:.6f}` |".format(
                rank,
                episode["map_id"],
                episode["seed"],
                episode["bot"],
                episode["top1_hit_count"],
                episode["top1_action_match_ratio"],
                episode["top1_nearest_distance"]["average"],
            )
        )
    lines.extend(["", "## Per Trace", ""])
    for trace_report in report["traces"]:
        lines.extend(
            [
                f"### `{trace_report['trace']['path']}`",
                "",
                f"- Samples: `{trace_report['trace']['sample_count']}`",
                f"- Top1 match ratio: `{trace_report['summary']['top1_nearest_target_matches_online_action_ratio']}`",
                f"- Average distance: `{trace_report['summary']['top1_nearest_distance']['average']}`",
                "",
                "| Rank | Seed | Bot | Top1 hits | Match ratio | Avg distance |",
                "|---:|---:|---|---:|---:|---:|",
            ]
        )
        for rank, episode in enumerate(trace_report["ranked_episodes"], start=1):
            lines.append(
                "| `{}` | `{}` | `{}` | `{}` | `{:.4f}` | `{:.6f}` |".format(
                    rank,
                    episode["seed"],
                    episode["bot"],
                    episode["top1_hit_count"],
                    episode["top1_action_match_ratio"],
                    episode["top1_nearest_distance"]["average"],
                )
            )
        lines.append("")
    lines.extend(["## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rank offline behavior-clone dataset episodes by trace nearest coverage."
    )
    parser.add_argument("--trace", action="append", required=True)
    parser.add_argument("--dataset", action="append", required=True)
    parser.add_argument("--same-map-only", action="store_true")
    parser.add_argument("--offline-min-seconds", type=float, default=None)
    parser.add_argument("--offline-max-seconds", type=float, default=None)
    parser.add_argument("--phase-duration-seconds", type=float, default=None)
    parser.add_argument("--nearest-k", type=int, default=3)
    parser.add_argument("--top-limit", type=int, default=20)
    parser.add_argument("--report", default=None)
    parser.add_argument("--markdown", default=None)
    args = parser.parse_args()

    if args.nearest_k <= 0:
        parser.error("--nearest-k must be greater than zero")
    if args.top_limit <= 0:
        parser.error("--top-limit must be greater than zero")
    if (
        args.offline_min_seconds is not None
        and args.offline_max_seconds is not None
        and args.offline_max_seconds < args.offline_min_seconds
    ):
        parser.error("--offline-max-seconds must be greater than or equal to --offline-min-seconds")

    traces = [load_trace(path) for path in args.trace]
    dataset = load_trajectory_dataset(args.dataset)
    report = rank_traces_against_dataset(
        traces,
        dataset,
        phase_duration_seconds=args.phase_duration_seconds,
        same_map_only=args.same_map_only,
        offline_min_seconds=args.offline_min_seconds,
        offline_max_seconds=args.offline_max_seconds,
        nearest_k=args.nearest_k,
        top_limit=args.top_limit,
    )
    report["dependency_status"] = dependency_status()
    write_json(args.report, report)
    write_markdown(args.markdown, report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
