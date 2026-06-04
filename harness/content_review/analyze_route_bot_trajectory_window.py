#!/usr/bin/env python3
"""Summarize RouteBot trajectory samples for content repair decisions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
from typing import Any


def as_float(value: Any, default: float = 0.0) -> float:
    if isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return float(value)
    return default


def as_int(value: Any, default: int = 0) -> int:
    if isinstance(value, bool):
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    return default


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {error}") from error
            if not isinstance(payload, dict):
                raise ValueError(f"{path}:{line_number}: record must be an object")
            records.append(payload)
    return records


def route_runs_from_metrics(metrics: dict[str, Any]) -> dict[int, dict[str, Any]]:
    bots = metrics.get("bots")
    if not isinstance(bots, list):
        return {}
    for bot in bots:
        if isinstance(bot, dict) and bot.get("bot") == "route":
            runs = bot.get("runs")
            if not isinstance(runs, list):
                return {}
            return {
                as_int(run.get("seed")): run
                for run in runs
                if isinstance(run, dict) and isinstance(run.get("seed"), int)
            }
    return {}


def terminal_by_seed(records: list[dict[str, Any]]) -> dict[int, str]:
    return {
        as_int(record.get("seed")): str(record.get("terminal", ""))
        for record in records
        if record.get("record_type") == "episode"
    }


def metadata(records: list[dict[str, Any]]) -> dict[str, Any]:
    for record in records:
        if record.get("record_type") == "metadata":
            return record
    return {}


def sample_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [record for record in records if record.get("record_type") == "sample"]


def upgrade_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [record for record in records if record.get("record_type") == "upgrade_sample"]


def diagnostics(sample: dict[str, Any]) -> dict[str, Any]:
    value = sample.get("diagnostics")
    return value if isinstance(value, dict) else {}


def nested_number(payload: dict[str, Any], path: tuple[str, ...], default: float = 0.0) -> float:
    current: Any = payload
    for key in path:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
    return as_float(current, default)


def nearest_enemy_id(sample: dict[str, Any]) -> str:
    nearest = diagnostics(sample).get("nearest_enemy")
    if not isinstance(nearest, dict):
        return ""
    value = nearest.get("enemy_id")
    return str(value) if isinstance(value, str) else ""


def action_histogram(samples: list[dict[str, Any]]) -> dict[str, int]:
    histogram: dict[str, int] = {}
    for sample in samples:
        action = str(as_int(sample.get("action"), -1))
        histogram[action] = histogram.get(action, 0) + 1
    return dict(sorted(histogram.items(), key=lambda item: int(item[0])))


def top_counts(values: list[str], limit: int = 5) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    for value in values:
        if not value:
            continue
        counts[value] = counts.get(value, 0) + 1
    return [
        {"value": value, "count": count}
        for value, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]
    ]


def average(samples: list[dict[str, Any]], getter) -> float:
    values = [getter(sample) for sample in samples]
    return round(mean(values), 4) if values else 0.0


def empty_seed_summary(seed: int, route_run: dict[str, Any] | None) -> dict[str, Any]:
    route_run = route_run or {}
    return {
        "seed": seed,
        "terminal": str(route_run.get("terminal", "")),
        "duration_seconds": round(as_float(route_run.get("duration_seconds")), 3),
        "final_level": as_int(route_run.get("level")),
        "final_kills": as_int(route_run.get("kills")),
        "final_damage_taken": round(as_float(route_run.get("damage_taken")), 3),
        "sample_count": 0,
        "window_missing_reason": "run ended before sampled window or no matching sample was exported",
    }


def seed_summary(seed: int, samples: list[dict[str, Any]], route_run: dict[str, Any] | None) -> dict[str, Any]:
    if not samples:
        return empty_seed_summary(seed, route_run)
    first = min(samples, key=lambda sample: as_float(sample.get("time_seconds")))
    last = max(samples, key=lambda sample: as_float(sample.get("time_seconds")))
    final = route_run or {}
    return {
        "seed": seed,
        "terminal": str(final.get("terminal", "")),
        "duration_seconds": round(as_float(final.get("duration_seconds")), 3),
        "final_level": as_int(final.get("level")),
        "final_kills": as_int(final.get("kills")),
        "final_damage_taken": round(as_float(final.get("damage_taken")), 3),
        "sample_count": len(samples),
        "window_start_seconds": round(as_float(first.get("time_seconds")), 3),
        "window_end_seconds": round(as_float(last.get("time_seconds")), 3),
        "start_health_ratio": round(as_float(first.get("health_ratio")), 4),
        "end_health_ratio": round(as_float(last.get("health_ratio")), 4),
        "avg_health_ratio": average(samples, lambda sample: as_float(sample.get("health_ratio"))),
        "avg_level": average(samples, lambda sample: as_float(sample.get("level"))),
        "avg_kills": average(samples, lambda sample: as_float(sample.get("kills"))),
        "avg_boundary_edge_risk": average(
            samples,
            lambda sample: nested_number(diagnostics(sample), ("boundary", "edge_risk")),
        ),
        "avg_boundary_min_distance": average(
            samples,
            lambda sample: nested_number(diagnostics(sample), ("boundary", "min_distance")),
        ),
        "avg_enemy_pressure_risk": average(
            samples,
            lambda sample: nested_number(diagnostics(sample), ("enemy_pressure_risk",)),
        ),
        "avg_low_health_risk": average(
            samples,
            lambda sample: nested_number(diagnostics(sample), ("low_health_risk",)),
        ),
        "avg_hazard_pressure_risk": average(
            samples,
            lambda sample: nested_number(diagnostics(sample), ("hazard_pressure_risk",)),
        ),
        "avg_boss_pressure_risk": average(
            samples,
            lambda sample: nested_number(diagnostics(sample), ("boss_pressure_risk",)),
        ),
        "avg_safety_risk_score": average(
            samples,
            lambda sample: nested_number(diagnostics(sample), ("safety_risk_score",)),
        ),
        "avg_visible_enemy_count": average(
            samples,
            lambda sample: nested_number(diagnostics(sample), ("visible_enemy_count",)),
        ),
        "avg_nearby_enemy_count_160": average(
            samples,
            lambda sample: nested_number(diagnostics(sample), ("nearby_enemy_count_160",)),
        ),
        "avg_nearby_enemy_count_240": average(
            samples,
            lambda sample: nested_number(diagnostics(sample), ("nearby_enemy_count_240",)),
        ),
        "action_histogram": action_histogram(samples),
        "top_nearest_enemies": top_counts([nearest_enemy_id(sample) for sample in samples]),
    }


def group_summary(name: str, summaries: list[dict[str, Any]]) -> dict[str, Any]:
    sampled = [summary for summary in summaries if as_int(summary.get("sample_count")) > 0]
    return {
        "name": name,
        "seed_count": len(summaries),
        "seeds": [summary["seed"] for summary in summaries],
        "sampled_seed_count": len(sampled),
        "sampled_seeds": [summary["seed"] for summary in sampled],
        "missing_window_seeds": [
            summary["seed"] for summary in summaries if as_int(summary.get("sample_count")) == 0
        ],
        "avg_final_level": average(summaries, lambda item: as_float(item.get("final_level"))),
        "avg_final_damage_taken": average(summaries, lambda item: as_float(item.get("final_damage_taken"))),
        "avg_health_ratio": average(sampled, lambda item: as_float(item.get("avg_health_ratio"))),
        "avg_boundary_edge_risk": average(
            sampled, lambda item: as_float(item.get("avg_boundary_edge_risk"))
        ),
        "avg_enemy_pressure_risk": average(
            sampled, lambda item: as_float(item.get("avg_enemy_pressure_risk"))
        ),
        "avg_low_health_risk": average(sampled, lambda item: as_float(item.get("avg_low_health_risk"))),
        "avg_boss_pressure_risk": average(sampled, lambda item: as_float(item.get("avg_boss_pressure_risk"))),
        "avg_safety_risk_score": average(
            sampled, lambda item: as_float(item.get("avg_safety_risk_score"))
        ),
        "avg_nearby_enemy_count_160": average(
            sampled, lambda item: as_float(item.get("avg_nearby_enemy_count_160"))
        ),
    }


def build_report(trajectory_jsonl: Path, metrics_json: Path) -> dict[str, Any]:
    records = load_jsonl(trajectory_jsonl)
    route_runs = route_runs_from_metrics(load_json_object(metrics_json))
    samples = sample_records(records)
    by_seed: dict[int, list[dict[str, Any]]] = {}
    for sample in samples:
        by_seed.setdefault(as_int(sample.get("seed")), []).append(sample)

    summary_seeds = sorted(set(route_runs) | set(by_seed))
    seed_summaries = [
        seed_summary(seed, by_seed.get(seed, []), route_runs.get(seed))
        for seed in summary_seeds
    ]
    victory = [summary for summary in seed_summaries if summary.get("terminal") == "victory"]
    defeat = [summary for summary in seed_summaries if summary.get("terminal") != "victory"]
    meta = metadata(records)
    terminals = terminal_by_seed(records)

    missing_diagnostics = [
        as_int(sample.get("seed"))
        for sample in samples
        if not isinstance(sample.get("diagnostics"), dict)
    ]
    errors: list[str] = []
    if not samples:
        errors.append("trajectory dataset has no sample records")
    if not route_runs:
        errors.append("metrics file does not contain RouteBot runs")
    if missing_diagnostics:
        errors.append("sample records are missing diagnostics")
    if terminals and route_runs:
        for seed, terminal in terminals.items():
            matrix_terminal = str(route_runs.get(seed, {}).get("terminal", ""))
            if matrix_terminal and terminal != matrix_terminal:
                errors.append(f"seed {seed} terminal mismatch: trajectory={terminal}, matrix={matrix_terminal}")

    decision = "route_bot_trajectory_window_valid" if not errors else "route_bot_trajectory_window_invalid"
    recommendation = (
        "collect_named_diagnostics_before_v54_repair"
        if missing_diagnostics
        else "use_seed_specific_window_diagnostics_for_v54_repair"
    )
    if not errors and victory and defeat:
        victory_group = group_summary("victory", victory)
        defeat_group = group_summary("defeat", defeat)
        health_gap = victory_group["avg_health_ratio"] - defeat_group["avg_health_ratio"]
        safety_gap = victory_group["avg_safety_risk_score"] - defeat_group["avg_safety_risk_score"]
        if health_gap > 0.05 and safety_gap <= 0.08:
            recommendation = "inspect_xp_and_upgrade_timing_before_new_hazard"
        elif safety_gap < -0.05:
            recommendation = "avoid_broad_pressure_increase_and_target_route_specific_safe_lanes"

    return {
        "report_version": 1,
        "decision": decision,
        "recommendation": recommendation,
        "trajectory_jsonl": str(trajectory_jsonl),
        "metrics_json": str(metrics_json),
        "candidate_id": str(meta.get("content_dir", "")).rstrip("/").split("/")[-1],
        "content_hash": meta.get("content_hash", ""),
        "bot": meta.get("bot", "route"),
        "map_id": meta.get("map_id", ""),
        "sample_window": {
            "start_seconds": meta.get("sample_start_seconds"),
            "end_seconds": meta.get("sample_end_seconds"),
            "stride": meta.get("sample_stride"),
        },
        "sample_count": len(samples),
        "upgrade_sample_count": len(upgrade_records(records)),
        "episode_count": len([record for record in records if record.get("record_type") == "episode"]),
        "victory_seed_count": len(victory),
        "defeat_seed_count": len(defeat),
        "sampled_victory_seed_count": len([item for item in victory if as_int(item.get("sample_count")) > 0]),
        "sampled_defeat_seed_count": len([item for item in defeat if as_int(item.get("sample_count")) > 0]),
        "missing_window_seeds": [
            item["seed"] for item in seed_summaries if as_int(item.get("sample_count")) == 0
        ],
        "victory_group": group_summary("victory", victory),
        "defeat_group": group_summary("defeat", defeat),
        "seed_summaries": seed_summaries,
        "upgrade_samples": [
            {
                "seed": record.get("seed"),
                "time_seconds": record.get("time_seconds"),
                "level": record.get("level"),
                "chosen_upgrade_id": record.get("chosen_upgrade_id"),
                "upgrade_options": record.get("upgrade_options"),
                "health_ratio": record.get("health_ratio"),
            }
            for record in upgrade_records(records)
        ],
        "errors": errors,
        "limitations": [
            "This report uses sampled Harness trajectory diagnostics, not full frame-by-frame replay state.",
            "It does not promote generated content or prove a gameplay fix.",
            "Human playtest evidence is still required before content acceptance.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# RouteBot Trajectory Window Diagnostic",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Recommendation: `{report['recommendation']}`",
        f"- Candidate: `{report['candidate_id']}`",
        f"- Content hash: `{report['content_hash']}`",
        f"- Bot / map: `{report['bot']}` / `{report['map_id']}`",
        f"- Samples: `{report['sample_count']}`",
        f"- Upgrade samples: `{report['upgrade_sample_count']}`",
        f"- Victories / defeats: `{report['victory_seed_count']}` / `{report['defeat_seed_count']}`",
        f"- Sampled victories / defeats: `{report['sampled_victory_seed_count']}` / `{report['sampled_defeat_seed_count']}`",
        f"- Missing-window seeds: `{report['missing_window_seeds']}`",
        "",
        "## Group Summary",
        "",
        "| Group | Seeds | Sampled Seeds | Health | Edge Risk | Enemy Risk | Boss Risk | Safety Risk | Nearby 160 |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for group_key in ["victory_group", "defeat_group"]:
        group = report[group_key]
        lines.append(
            f"| `{group['name']}` | `{group['seeds']}` | `{group['sampled_seeds']}` | {group['avg_health_ratio']:.4f} | "
            f"{group['avg_boundary_edge_risk']:.4f} | {group['avg_enemy_pressure_risk']:.4f} | "
            f"{group['avg_boss_pressure_risk']:.4f} | {group['avg_safety_risk_score']:.4f} | "
            f"{group['avg_nearby_enemy_count_160']:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Seeds",
            "",
            "| Seed | Terminal | Level | Damage | Health | Edge Risk | Enemy Risk | Safety Risk | Top Nearest Enemies |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for summary in report["seed_summaries"]:
        top_enemies = ", ".join(
            f"{item['value']}:{item['count']}" for item in summary.get("top_nearest_enemies", [])
        )
        if summary.get("sample_count", 0) == 0:
            top_enemies = str(summary.get("window_missing_reason", "no window samples"))
        lines.append(
            f"| {summary['seed']} | `{summary['terminal']}` | {summary.get('final_level', 0)} | "
            f"{summary.get('final_damage_taken', 0.0):.3f} | {summary.get('avg_health_ratio', 0.0):.4f} | "
            f"{summary.get('avg_boundary_edge_risk', 0.0):.4f} | "
            f"{summary.get('avg_enemy_pressure_risk', 0.0):.4f} | "
            f"{summary.get('avg_safety_risk_score', 0.0):.4f} | {top_enemies} |"
        )

    if report["upgrade_samples"]:
        lines.extend(["", "## Upgrade Samples", ""])
        for sample in report["upgrade_samples"]:
            lines.append(
                f"- Seed `{sample['seed']}` at `{sample['time_seconds']}`s chose "
                f"`{sample['chosen_upgrade_id']}` from `{sample['upgrade_options']}`"
            )

    if report["errors"]:
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {error}" for error in report["errors"])

    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze RouteBot trajectory window diagnostics.")
    parser.add_argument("trajectory_jsonl", type=Path)
    parser.add_argument("--metrics", type=Path, required=True)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--markdown", type=Path, default=None)
    args = parser.parse_args()

    report = build_report(args.trajectory_jsonl, args.metrics)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "route_bot_trajectory_window_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
