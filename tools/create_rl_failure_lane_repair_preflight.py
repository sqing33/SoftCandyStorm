#!/usr/bin/env python3
"""Create required repair preflights from RL failure-lane trace diagnostics.

This tool turns trace diagnostics into a small gate plan for the next repair
attempt. It does not run training, approve a checkpoint, or replace the
underlying fixed-window no-regression checks.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


OPENING_LANE = "opening_repair"
LATE_LANE = "late_terminal_survival_conversion"


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def int_dict(value: Any) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    return {str(key): as_int(item) for key, item in value.items()}


def lane_by_id(summary: dict[str, Any]) -> dict[str, dict[str, Any]]:
    lanes = summary.get("lanes")
    if not isinstance(lanes, list):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for lane in lanes:
        if not isinstance(lane, dict):
            continue
        lane_id = str(lane.get("lane") or "")
        if lane_id:
            result[lane_id] = lane
    return result


def top_action(action_counts: dict[str, int]) -> str | None:
    if not action_counts:
        return None
    return sorted(action_counts.items(), key=lambda item: (-item[1], item[0]))[0][0]


def hotspot_summary(lane: dict[str, Any]) -> dict[str, Any]:
    summary = lane.get("hotspot_summary")
    return summary if isinstance(summary, dict) else {}


def pressure_hotspots(lane: dict[str, Any]) -> dict[str, int]:
    return int_dict(hotspot_summary(lane).get("pressure_hotspots"))


def time_bucket_hotspots(lane: dict[str, Any]) -> dict[str, int]:
    return int_dict(hotspot_summary(lane).get("time_bucket_hotspots"))


def action_counts(lane: dict[str, Any]) -> dict[str, int]:
    return int_dict(hotspot_summary(lane).get("action_counts"))


def trace_quality(lane: dict[str, Any]) -> dict[str, Any]:
    summary = hotspot_summary(lane)
    return {
        "trace_count": as_int(summary.get("trace_count")),
        "sample_count": as_int(summary.get("sample_count")),
        "negative_sample_count": as_int(summary.get("negative_sample_count")),
        "negative_sample_ratio": as_float(summary.get("negative_sample_ratio")),
    }


def opening_preflight(lane: dict[str, Any]) -> dict[str, Any]:
    actions = action_counts(lane)
    pressures = pressure_hotspots(lane)
    buckets = time_bucket_hotspots(lane)
    seeds = lane.get("seeds") if isinstance(lane.get("seeds"), list) else []
    return {
        "lane": OPENING_LANE,
        "classification": "opening_boundary_action_lock",
        "seeds": seeds,
        "repair_shape": "narrow state-conditioned opening branch or target-seed preflight",
        "dominant_action": top_action(actions),
        "trace_quality": trace_quality(lane),
        "evidence": {
            "route_hotspots": lane.get("route_hotspots"),
            "candidate_comparison": lane.get("candidate_comparison"),
            "time_bucket_hotspots": buckets,
            "pressure_hotspots": pressures,
            "action_counts": actions,
        },
        "required_preflights": [
            {
                "id": "opening_seed63402_target_preflight",
                "type": "target_seed_preflight",
                "map_id": "caramel-workshop",
                "seed": seeds[0] if seeds else 63402,
                "required_result": "non_defeat_or_survival_window_passed",
            },
            {
                "id": "short60_caramel_window_preflight",
                "type": "window_target_preflight",
                "map_id": "caramel-workshop",
                "window_seconds": 60,
                "minimum_win_rate": 0.6667,
                "minimum_average_survival_seconds": 55.0,
            },
            {
                "id": "high_pressure_parent_no_regression",
                "type": "window_regression",
                "windows_seconds": [60, 180, 300],
                "required_result": "policy_window_regression_passed",
            },
        ],
        "blocked_patterns": [
            "shared PPO continuation that also targets late_terminal_survival_conversion",
            "broad 0-60s branch without online action-distribution regression review",
            "treating route hotspot evidence as policy acceptance",
        ],
    }


def late_repair_shape(lane: dict[str, Any]) -> str:
    buckets = time_bucket_hotspots(lane)
    pre_late = buckets.get("opening_lt_60", 0) + buckets.get("mid_60_to_180", 0)
    late = buckets.get("late_180_to_300", 0)
    if pre_late > late:
        return "path-retention-preserving terminal conversion"
    return "terminal conversion with late route recovery"


def late_preflight(lane: dict[str, Any]) -> dict[str, Any]:
    actions = action_counts(lane)
    pressures = pressure_hotspots(lane)
    buckets = time_bucket_hotspots(lane)
    seeds = lane.get("seeds") if isinstance(lane.get("seeds"), list) else []
    extra_scan_seeds = lane.get("extra_scan_seeds") if isinstance(lane.get("extra_scan_seeds"), list) else []
    return {
        "lane": LATE_LANE,
        "classification": "terminal_conversion_with_opening_mid_route_debt",
        "seeds": seeds,
        "extra_scan_seeds": extra_scan_seeds,
        "repair_shape": late_repair_shape(lane),
        "dominant_action": top_action(actions),
        "trace_quality": trace_quality(lane),
        "evidence": {
            "route_hotspots_late_seeds_only": lane.get("route_hotspots_late_seeds_only"),
            "route_hotspots_all_scanned_seeds": lane.get("route_hotspots_all_scanned_seeds"),
            "candidate_comparison": lane.get("candidate_comparison"),
            "time_bucket_hotspots": buckets,
            "pressure_hotspots": pressures,
            "action_counts": actions,
        },
        "required_preflights": [
            {
                "id": "caramel_300s_10seed_followup",
                "type": "target_followup",
                "map_id": "caramel-workshop",
                "seed_start": 63400,
                "eval_episodes": 10,
                "window_seconds": 300,
                "required_result": "target_followup_no_regression_or_improvement",
            },
            {
                "id": "short60_caramel_window_preflight",
                "type": "window_target_preflight",
                "map_id": "caramel-workshop",
                "window_seconds": 60,
                "minimum_win_rate": 0.6667,
                "minimum_average_survival_seconds": 55.0,
            },
            {
                "id": "high_pressure_parent_no_regression",
                "type": "window_regression",
                "windows_seconds": [60, 180, 300],
                "required_result": "policy_window_regression_passed",
            },
        ],
        "blocked_patterns": [
            "pure 180s+ low-health-only continuation",
            "terminal branch that ignores 60-180s path retention debt",
            "using unfiltered continuous-seed trace hotspots as late-only evidence",
        ],
    }


def build_report(trace_summary: Path) -> dict[str, Any]:
    errors: list[str] = []
    try:
        summary = load_json_object(trace_summary)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {
            "report_version": 1,
            "decision": "rl_failure_lane_repair_preflight_invalid",
            "source_trace_summary": str(trace_summary),
            "errors": [f"unable to load trace summary: {exc}"],
            "preflight_lanes": [],
            "limitations": limitations(),
        }

    if summary.get("decision") != "rl_failure_lane_trace_diagnostics_recorded":
        errors.append("trace summary decision must be rl_failure_lane_trace_diagnostics_recorded")

    lanes = lane_by_id(summary)
    preflight_lanes: list[dict[str, Any]] = []
    opening = lanes.get(OPENING_LANE)
    late = lanes.get(LATE_LANE)
    if opening is None:
        errors.append("missing opening_repair lane")
    else:
        preflight_lanes.append(opening_preflight(opening))
    if late is None:
        errors.append("missing late_terminal_survival_conversion lane")
    else:
        preflight_lanes.append(late_preflight(late))

    if not preflight_lanes:
        decision = "rl_failure_lane_repair_preflight_invalid"
    elif errors:
        decision = "rl_failure_lane_repair_preflight_invalid"
    else:
        decision = "rl_failure_lane_repair_preflight_ready"

    return {
        "report_version": 1,
        "decision": decision,
        "source_trace_summary": str(trace_summary),
        "source_trace_plan": summary.get("source_trace_plan"),
        "source_failure_analysis": summary.get("source_failure_analysis"),
        "map_id": summary.get("map_id"),
        "gate_conclusion": "repair",
        "preflight_lanes": preflight_lanes,
        "blocked_until": [
            "opening_repair and late_terminal_survival_conversion are validated as separate lanes",
            "short60_caramel_window_preflight passes",
            "high_pressure_parent_no_regression passes for 60/180/300 seconds",
            "10 seed caramel follow-up does not regress baseline evidence",
        ],
        "errors": errors,
        "limitations": limitations(),
    }


def limitations() -> list[str]:
    return [
        "This report creates a preflight contract only; it does not run simulation or train a policy.",
        "Trace diagnostics are sampled evidence and must not be treated as Replay regression.",
        "A ready decision is repair routing evidence, not policy acceptance or RL test Bot approval.",
    ]


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# RL Failure Lane Repair Preflight",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Source trace summary: `{report['source_trace_summary']}`",
        f"- Map: `{report.get('map_id')}`",
        f"- Gate conclusion: `{report['gate_conclusion']}`",
        "",
        "## Preflight Lanes",
        "",
        "| Lane | Classification | Repair Shape | Dominant Action | Negative Samples | Required Preflights |",
        "|---|---|---|---|---:|---|",
    ]
    for lane in report["preflight_lanes"]:
        quality = lane["trace_quality"]
        required = ", ".join(item["id"] for item in lane["required_preflights"])
        lines.append(
            "| `{lane}` | `{classification}` | {repair_shape} | `{dominant_action}` | {negative} ({ratio:.2%}) | {required} |".format(
                lane=lane["lane"],
                classification=lane["classification"],
                repair_shape=lane["repair_shape"],
                dominant_action=lane.get("dominant_action"),
                negative=quality["negative_sample_count"],
                ratio=quality["negative_sample_ratio"],
                required=required,
            )
        )

    lines.extend(["", "## Blocked Patterns", ""])
    for lane in report["preflight_lanes"]:
        lines.append(f"### `{lane['lane']}`")
        lines.extend(f"- {item}" for item in lane["blocked_patterns"])
        lines.append("")

    lines.extend(["## Blocked Until", ""])
    lines.extend(f"- {item}" for item in report["blocked_until"])
    if report.get("errors"):
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {item}" for item in report["errors"])
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-summary", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--markdown", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(args.trace_summary)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        write_markdown(report, args.markdown)
    return 0 if report["decision"] == "rl_failure_lane_repair_preflight_ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
