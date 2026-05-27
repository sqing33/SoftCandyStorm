#!/usr/bin/env python3
"""Analyze sampled RL traces for route_recovery hotspots."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable


TIME_BUCKETS = [
    ("opening_lt_60", 0.0, 60.0),
    ("mid_60_to_180", 60.0, 180.0),
    ("late_180_to_300", 180.0, 300.0),
    ("post_300", 300.0, float("inf")),
]

PRESSURE_THRESHOLDS = {
    "boundary_edge": 0.75,
    "enemy_pressure": 0.6,
    "hazard_pressure": 0.4,
    "boss_pressure": 0.25,
    "low_health": 0.6,
}


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def trace_paths(inputs: Iterable[Path]) -> list[Path]:
    paths: list[Path] = []
    for item in inputs:
        if item.is_dir():
            paths.extend(sorted(item.rglob("*_trace.json")))
        elif item.is_file():
            paths.append(item)
        else:
            raise FileNotFoundError(item)
    return sorted(dict.fromkeys(paths))


def bucket_for_time(time_seconds: float) -> str:
    for label, start, end in TIME_BUCKETS:
        if start <= time_seconds < end:
            return label
    return TIME_BUCKETS[-1][0]


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def pressure_tags(diagnostics: dict[str, Any]) -> list[str]:
    boundary = diagnostics.get("boundary", {}) if isinstance(diagnostics, dict) else {}
    tags: list[str] = []
    if as_float(boundary.get("edge_risk")) >= PRESSURE_THRESHOLDS["boundary_edge"]:
        tags.append("boundary_edge")
    if as_float(diagnostics.get("enemy_pressure_risk")) >= PRESSURE_THRESHOLDS["enemy_pressure"]:
        tags.append("enemy_pressure")
    if as_float(diagnostics.get("hazard_pressure_risk")) >= PRESSURE_THRESHOLDS["hazard_pressure"]:
        tags.append("hazard_pressure")
    if as_float(diagnostics.get("boss_pressure_risk")) >= PRESSURE_THRESHOLDS["boss_pressure"]:
        tags.append("boss_pressure")
    if as_float(diagnostics.get("low_health_risk")) >= PRESSURE_THRESHOLDS["low_health"]:
        tags.append("low_health")
    if not tags:
        tags.append("no_major_pressure")
    return tags


def top_actions(action_score: dict[str, Any], limit: int = 3) -> list[dict[str, Any]]:
    raw = action_score.get("top_actions", []) if isinstance(action_score, dict) else []
    result = []
    for item in raw[:limit]:
        if not isinstance(item, dict):
            continue
        result.append(
            {
                "action": str(item.get("action")),
                "score": round(as_float(item.get("score")), 4),
            }
        )
    return result


def hotspot_row(path: Path, episode: dict[str, Any], step: dict[str, Any]) -> dict[str, Any] | None:
    reward_breakdown = step.get("reward_breakdown", {})
    route_recovery = as_float(reward_breakdown.get("route_recovery"), default=0.0)
    if route_recovery >= 0.0:
        return None
    diagnostics = step.get("diagnostics", {})
    boundary = diagnostics.get("boundary", {}) if isinstance(diagnostics, dict) else {}
    nearest_enemy = diagnostics.get("nearest_enemy") if isinstance(diagnostics, dict) else None
    time_seconds = as_float(step.get("time_seconds"))
    return {
        "trace_path": str(path),
        "map_id": episode.get("map_id"),
        "seed": episode.get("seed"),
        "step": int(step.get("step", 0)),
        "tick": int(step.get("tick", 0)),
        "time_seconds": round(time_seconds, 4),
        "time_bucket": bucket_for_time(time_seconds),
        "action": int(step.get("action", 0)),
        "route_recovery": round(route_recovery, 4),
        "reward": round(as_float(step.get("reward")), 4),
        "health": round(as_float(step.get("health")), 4),
        "level": step.get("level"),
        "kills": step.get("kills"),
        "terminal_kind": (step.get("terminal") or {}).get("kind") if isinstance(step.get("terminal"), dict) else None,
        "pressure_tags": pressure_tags(diagnostics if isinstance(diagnostics, dict) else {}),
        "boundary_min_distance": round(as_float(boundary.get("min_distance")), 4),
        "boundary_edge_risk": round(as_float(boundary.get("edge_risk")), 4),
        "low_health_risk": round(as_float(diagnostics.get("low_health_risk")), 4)
        if isinstance(diagnostics, dict)
        else 0.0,
        "enemy_pressure_risk": round(as_float(diagnostics.get("enemy_pressure_risk")), 4)
        if isinstance(diagnostics, dict)
        else 0.0,
        "hazard_pressure_risk": round(as_float(diagnostics.get("hazard_pressure_risk")), 4)
        if isinstance(diagnostics, dict)
        else 0.0,
        "boss_pressure_risk": round(as_float(diagnostics.get("boss_pressure_risk")), 4)
        if isinstance(diagnostics, dict)
        else 0.0,
        "safety_risk_score": round(as_float(diagnostics.get("safety_risk_score")), 4)
        if isinstance(diagnostics, dict)
        else 0.0,
        "nearest_enemy": summarize_enemy(nearest_enemy),
        "top_actions": top_actions(step.get("action_score", {})),
    }


def summarize_enemy(enemy: Any) -> dict[str, Any] | None:
    if not isinstance(enemy, dict):
        return None
    return {
        "enemy_id": enemy.get("enemy_id"),
        "behavior": enemy.get("behavior"),
        "hitbox_distance": round(as_float(enemy.get("hitbox_distance")), 4),
        "threat": round(as_float(enemy.get("threat")), 4),
        "is_boss": bool(enemy.get("is_boss", False)),
        "is_elite": bool(enemy.get("is_elite", False)),
    }


def average(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 4)


def count_map(values: Iterable[Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def grouped_summary(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(str(row.get(key)), []).append(row)
    return [
        {
            key: group_key,
            "hotspot_count": len(group_rows),
            "min_route_recovery": min(row["route_recovery"] for row in group_rows),
            "avg_route_recovery": average([row["route_recovery"] for row in group_rows]),
            "action_counts": count_map(row["action"] for row in group_rows),
        }
        for group_key, group_rows in sorted(groups.items())
    ]


def pressure_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        for tag in row.get("pressure_tags", []):
            groups.setdefault(str(tag), []).append(row)
    return [
        {
            "pressure_tag": tag,
            "hotspot_count": len(group_rows),
            "min_route_recovery": min(row["route_recovery"] for row in group_rows),
            "avg_route_recovery": average([row["route_recovery"] for row in group_rows]),
            "action_counts": count_map(row["action"] for row in group_rows),
        }
        for tag, group_rows in sorted(groups.items())
    ]


def build_report(inputs: Iterable[Path], top: int = 20) -> dict[str, Any]:
    paths = trace_paths(inputs)
    rows: list[dict[str, Any]] = []
    sample_count = 0
    episode_count = 0
    for path in paths:
        payload = load_json_object(path)
        steps = payload.get("steps")
        if not isinstance(steps, list):
            raise ValueError(f"{path} must contain a `steps` list")
        episode = payload.get("episode", {})
        if not isinstance(episode, dict):
            episode = {}
        episode_count += 1
        sample_count += len(steps)
        for step in steps:
            if not isinstance(step, dict):
                continue
            row = hotspot_row(path, episode, step)
            if row is not None:
                rows.append(row)

    rows.sort(key=lambda row: (row["route_recovery"], row["time_seconds"], row["trace_path"]))
    return {
        "report_version": 1,
        "decision": "route_recovery_trace_hotspots_recorded",
        "trace_count": len(paths),
        "episode_count": episode_count,
        "sample_count": sample_count,
        "negative_sample_count": len(rows),
        "negative_sample_ratio": round(len(rows) / max(1, sample_count), 4),
        "top_hotspots": rows[:top],
        "map_summary": grouped_summary(rows, "map_id"),
        "time_bucket_summary": grouped_summary(rows, "time_bucket"),
        "pressure_summary": pressure_summary(rows),
        "limitations": [
            "This report analyzes sampled trace rows only; unsampled frames are not inspected.",
            "Trace diagnostics are not full GameCore snapshots and do not replace Replay.",
            "A negative route_recovery hotspot is repair evidence, not policy acceptance evidence.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Route Recovery Trace Hotspots",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Traces: {report['trace_count']}",
        f"- Sampled rows: {report['sample_count']}",
        f"- Negative route_recovery rows: {report['negative_sample_count']} ({report['negative_sample_ratio']:.2%})",
        "",
        "## Worst Hotspots",
        "",
        "| Map | Seed | Time | Bucket | Action | route_recovery | Pressure | Boundary | Enemy | Top Actions |",
        "|---|---:|---:|---|---:|---:|---|---:|---|---|",
    ]
    for row in report["top_hotspots"]:
        enemy = row.get("nearest_enemy") or {}
        enemy_text = (
            f"{enemy.get('enemy_id')} d={enemy.get('hitbox_distance')}"
            if enemy
            else "n/a"
        )
        top_actions = ", ".join(
            f"{item['action']}:{item['score']}" for item in row.get("top_actions", [])
        )
        lines.append(
            "| {map_id} | {seed} | {time} | `{bucket}` | {action} | {route} | {pressure} | {boundary} | {enemy} | {top_actions} |".format(
                map_id=f"`{row.get('map_id')}`",
                seed=row.get("seed"),
                time=row.get("time_seconds"),
                bucket=row.get("time_bucket"),
                action=row.get("action"),
                route=row.get("route_recovery"),
                pressure=", ".join(f"`{tag}`" for tag in row.get("pressure_tags", [])),
                boundary=row.get("boundary_min_distance"),
                enemy=enemy_text,
                top_actions=top_actions,
            )
        )

    lines.extend(["", "## Map Summary", "", "| Map | Hotspots | Min | Avg | Actions |", "|---|---:|---:|---:|---|"])
    for item in report["map_summary"]:
        lines.append(
            f"| `{item['map_id']}` | {item['hotspot_count']} | {item['min_route_recovery']} | {item['avg_route_recovery']} | `{json.dumps(item['action_counts'], sort_keys=True)}` |"
        )

    lines.extend(["", "## Time Bucket Summary", "", "| Bucket | Hotspots | Min | Avg | Actions |", "|---|---:|---:|---:|---|"])
    for item in report["time_bucket_summary"]:
        lines.append(
            f"| `{item['time_bucket']}` | {item['hotspot_count']} | {item['min_route_recovery']} | {item['avg_route_recovery']} | `{json.dumps(item['action_counts'], sort_keys=True)}` |"
        )

    lines.extend(["", "## Pressure Summary", "", "| Pressure | Hotspots | Min | Avg | Actions |", "|---|---:|---:|---:|---|"])
    for item in report["pressure_summary"]:
        lines.append(
            f"| `{item['pressure_tag']}` | {item['hotspot_count']} | {item['min_route_recovery']} | {item['avg_route_recovery']} | `{json.dumps(item['action_counts'], sort_keys=True)}` |"
        )

    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze route_recovery hotspots in sampled RL traces.")
    parser.add_argument("traces", type=Path, nargs="+", help="Trace JSON files or directories.")
    parser.add_argument("--top", type=int, default=20)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--markdown", type=Path, default=None)
    args = parser.parse_args()

    report = build_report(args.traces, top=args.top)
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
