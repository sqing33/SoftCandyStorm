#!/usr/bin/env python3
"""Summarize RL policy comparison failures into auditable buckets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


TIME_BUCKETS = [
    ("opening_lt_60", 0.0, 60.0),
    ("mid_60_to_180", 60.0, 180.0),
    ("late_180_to_300", 180.0, 300.0),
    ("post_300", 300.0, float("inf")),
]


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def bucket_for_time(time_seconds: float) -> str:
    for label, start, end in TIME_BUCKETS:
        if start <= time_seconds < end:
            return label
    return TIME_BUCKETS[-1][0]


def ratio_counts(counts: dict[str, int], total: int) -> dict[str, dict[str, float | int]]:
    return {
        key: {
            "count": int(value),
            "ratio": round(value / max(1, total), 4),
        }
        for key, value in counts.items()
    }


def average(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 4)


def dominant_action(action_distribution: dict[str, Any]) -> dict[str, Any] | None:
    if not action_distribution:
        return None
    total = sum(
        int(value) if isinstance(value, int) else int(value.get("count", 0))
        for value in action_distribution.values()
    )

    def item_ratio(item: tuple[str, Any]) -> float:
        value = item[1]
        if isinstance(value, int):
            return value / max(1, total)
        return float(value.get("ratio", 0.0))

    action, value = max(
        action_distribution.items(),
        key=item_ratio,
    )
    if isinstance(value, int):
        return {
            "action": action,
            "count": int(value),
            "ratio": round(value / max(1, total), 4),
        }
    return {
        "action": action,
        "count": int(value.get("count", 0)),
        "ratio": float(value.get("ratio", 0.0)),
    }


def episode_failure_row(map_id: str, episode: dict[str, Any]) -> dict[str, Any]:
    time_seconds = float(episode.get("time_seconds", 0.0))
    return {
        "map_id": map_id,
        "seed": episode.get("seed"),
        "time_seconds": round(time_seconds, 4),
        "time_bucket": bucket_for_time(time_seconds),
        "terminal_kind": episode.get("terminal_kind"),
        "terminal_reason": episode.get("terminal_reason"),
        "level": episode.get("level"),
        "kills": episode.get("kills"),
        "damage_taken": round(float(episode.get("damage_taken", 0.0)), 4),
        "dominant_action": dominant_action(episode.get("action_counts", {})),
        "reward_breakdown": episode.get("reward_breakdown", {}),
    }


def map_report(entry: dict[str, Any]) -> dict[str, Any]:
    map_id = str(entry.get("map_id", "unknown"))
    policy = entry.get("policy", {})
    summary = policy.get("summary", {})
    episodes = policy.get("episodes", [])
    failures = [
        episode_failure_row(map_id, episode)
        for episode in episodes
        if episode.get("terminal_kind") != "victory"
    ]
    terminal_counts: dict[str, int] = {}
    bucket_counts = {label: 0 for label, _start, _end in TIME_BUCKETS}
    for failure in failures:
        reason = str(failure.get("terminal_reason") or failure.get("terminal_kind") or "unknown")
        terminal_counts[reason] = terminal_counts.get(reason, 0) + 1
        bucket = str(failure["time_bucket"])
        bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1

    survival_values = [float(episode.get("time_seconds", 0.0)) for episode in episodes]
    failure_survival_values = [float(failure["time_seconds"]) for failure in failures]
    return {
        "map_id": map_id,
        "gate_decision": entry.get("gate_decision"),
        "episodes": len(episodes),
        "failure_count": len(failures),
        "win_rate": summary.get("win_rate"),
        "average_survival_seconds": summary.get("average_survival_seconds"),
        "minimum_survival_seconds": round(min(survival_values), 4) if survival_values else None,
        "average_failure_survival_seconds": average(failure_survival_values),
        "terminal_reason_distribution": ratio_counts(terminal_counts, len(failures)),
        "failure_time_bucket_distribution": ratio_counts(bucket_counts, len(failures)),
        "policy_normalized_action_entropy": summary.get("normalized_action_entropy"),
        "policy_dominant_action": dominant_action(summary.get("action_distribution", {})),
        "reward_breakdown_average": summary.get("reward_breakdown_average", {}),
        "failures": failures,
    }


def build_report(comparison_path: Path) -> dict[str, Any]:
    payload = load_json_object(comparison_path)
    maps = payload.get("maps")
    if not isinstance(maps, list):
        raise ValueError("comparison report must contain a `maps` list")

    map_reports = [map_report(entry) for entry in maps]
    total_failures = sum(item["failure_count"] for item in map_reports)
    repair_maps = [
        item["map_id"]
        for item in map_reports
        if item["failure_count"] > 0 or item["win_rate"] in (0, 0.0)
    ]
    return {
        "report_version": 1,
        "source": str(comparison_path),
        "decision": (
            "rl_policy_failure_analysis_recorded"
            if total_failures > 0
            else "rl_policy_failure_analysis_no_failures"
        ),
        "gate_decision": payload.get("gate_decision"),
        "algorithm": payload.get("algorithm"),
        "model_path": payload.get("model_path"),
        "map_preset": payload.get("map_preset"),
        "seconds": payload.get("seconds"),
        "seed_start": payload.get("seed_start"),
        "seeds": payload.get("seeds"),
        "map_count": len(map_reports),
        "total_failures": total_failures,
        "repair_maps": repair_maps,
        "findings": payload.get("findings", []),
        "maps": map_reports,
        "limitations": [
            "This report summarizes existing comparison output only.",
            "It does not replay episodes or prove a fix.",
            "Use it to choose the next curriculum, reward, or policy diagnostic target.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# RL Policy Failure Analysis",
        "",
        f"- Source: `{report['source']}`",
        f"- Decision: `{report['decision']}`",
        f"- Gate decision: `{report.get('gate_decision')}`",
        f"- Duration: `{report.get('seconds')}` seconds",
        f"- Total failures: {report['total_failures']}",
        f"- Repair maps: {', '.join(f'`{item}`' for item in report['repair_maps']) or 'None'}",
        "",
        "## Map Summary",
        "",
        "| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |",
        "|---|---:|---:|---:|---|---:|",
    ]
    for item in report["maps"]:
        dominant = item.get("policy_dominant_action") or {}
        dominant_text = (
            f"`{dominant.get('action')}` / {float(dominant.get('ratio', 0.0)):.2%}"
            if dominant
            else "n/a"
        )
        lines.append(
            "| {map_id} | {win_rate} | {failures} | {avg_fail} | {dominant} | {entropy} |".format(
                map_id=f"`{item['map_id']}`",
                win_rate=item.get("win_rate"),
                failures=item["failure_count"],
                avg_fail=item.get("average_failure_survival_seconds"),
                dominant=dominant_text,
                entropy=item.get("policy_normalized_action_entropy"),
            )
        )

    lines.extend(["", "## Failure Buckets", ""])
    for item in report["maps"]:
        lines.extend([f"### `{item['map_id']}`", ""])
        lines.extend(
            f"- `{bucket}`: {value['count']} ({value['ratio']:.2%})"
            for bucket, value in item["failure_time_bucket_distribution"].items()
        )
        if item["failures"]:
            lines.extend(["", "| Seed | Time | Bucket | Reason | Level | Kills | Damage |", "|---:|---:|---|---|---:|---:|---:|"])
            for failure in item["failures"]:
                lines.append(
                    f"| {failure.get('seed')} | {failure['time_seconds']} | `{failure['time_bucket']}` | `{failure.get('terminal_reason')}` | {failure.get('level')} | {failure.get('kills')} | {failure.get('damage_taken')} |"
                )
        lines.append("")

    lines.extend(["## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze RL policy comparison failures.")
    parser.add_argument("comparison", type=Path)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--markdown", type=Path, default=None)
    args = parser.parse_args()

    report = build_report(args.comparison)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
