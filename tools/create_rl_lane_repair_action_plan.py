#!/usr/bin/env python3
"""Create an action plan for one RL repair lane from trace diagnostics.

The report turns lane inventory, parent-vs-candidate trace comparison, and
route hotspot diagnostics into a conservative follow-up plan. It does not train
or approve a policy; it only records what must be fixed and which gates must
pass before another checkpoint can continue.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


OPENING_BUCKET = "opening_lt_60"
MID_BUCKET = "mid_60_to_180"
LATE_BUCKET = "late_180_to_300"
BOUNDARY_PRESSURE = "boundary_edge"


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


def find_lane(inventory: dict[str, Any], lane_label: str) -> dict[str, Any] | None:
    lanes = inventory.get("lanes")
    if not isinstance(lanes, list):
        return None
    for lane in lanes:
        if isinstance(lane, dict) and lane.get("label") == lane_label:
            return lane
    return None


def target_match(trace_compare: dict[str, Any], target_seed: int | None) -> dict[str, Any] | None:
    rows = trace_compare.get("matched_seed_comparison")
    if not isinstance(rows, list):
        return None
    for row in rows:
        if not isinstance(row, dict):
            continue
        if target_seed is None or as_int(row.get("seed"), -1) == target_seed:
            return row
    return None


def label_trace(row: dict[str, Any], label: str) -> dict[str, Any]:
    per_label = row.get("per_label")
    if not isinstance(per_label, dict):
        return {}
    value = per_label.get(label)
    return value if isinstance(value, dict) else {}


def first_pressure_time(trace: dict[str, Any]) -> float | None:
    step = trace.get("first_boundary_enemy_pressure_step")
    if not isinstance(step, dict):
        return None
    return as_float(step.get("time_seconds"))


def first_low_health_time(trace: dict[str, Any]) -> float | None:
    step = trace.get("first_low_health_step")
    if not isinstance(step, dict):
        return None
    return as_float(step.get("time_seconds"))


def summary_count(report: dict[str, Any], section: str, key: str, label: str) -> int:
    rows = report.get(section)
    if not isinstance(rows, list):
        return 0
    for row in rows:
        if isinstance(row, dict) and row.get(key) == label:
            return as_int(row.get("hotspot_count"))
    return 0


def ratio(part: int, whole: int) -> float:
    return round(part / max(1, whole), 4)


def top_action_counts(report: dict[str, Any], section: str, key: str, label: str) -> dict[str, int]:
    rows = report.get(section)
    if not isinstance(rows, list):
        return {}
    for row in rows:
        if not isinstance(row, dict) or row.get(key) != label:
            continue
        actions = row.get("action_counts")
        if not isinstance(actions, dict):
            return {}
        return {str(action): as_int(count) for action, count in actions.items()}
    return {}


def infer_diagnosis(metrics: dict[str, Any]) -> dict[str, Any]:
    opening_hotspots = metrics["time_bucket_hotspots"].get(OPENING_BUCKET, 0)
    mid_hotspots = metrics["time_bucket_hotspots"].get(MID_BUCKET, 0)
    late_hotspots = metrics["time_bucket_hotspots"].get(LATE_BUCKET, 0)
    negative_count = metrics["negative_sample_count"]
    opening_mid_ratio = ratio(opening_hotspots + mid_hotspots, negative_count)
    late_ratio = ratio(late_hotspots, negative_count)
    boundary_ratio = ratio(metrics["pressure_hotspots"].get(BOUNDARY_PRESSURE, 0), negative_count)
    first_divergent_time = metrics.get("first_divergent_time_seconds")
    candidate_pressure_time = metrics.get("candidate_first_high_pressure_time_seconds")
    parent_pressure_time = metrics.get("parent_first_high_pressure_time_seconds")
    early_divergence = first_divergent_time is not None and first_divergent_time < 60.0
    earlier_pressure = (
        candidate_pressure_time is not None
        and parent_pressure_time is not None
        and candidate_pressure_time < parent_pressure_time
    )
    boundary_path_lane = (
        opening_mid_ratio >= 0.5
        and boundary_ratio >= 0.5
        and (early_divergence or earlier_pressure)
    )
    if boundary_path_lane:
        classification = "opening_mid_boundary_path_retention"
    elif late_ratio >= 0.5:
        classification = "late_retention_candidate"
    else:
        classification = "mixed_retention_diagnostic"
    return {
        "classification": classification,
        "opening_mid_hotspot_ratio": opening_mid_ratio,
        "late_hotspot_ratio": late_ratio,
        "boundary_edge_hotspot_ratio": boundary_ratio,
        "early_divergence": early_divergence,
        "candidate_enters_pressure_earlier": earlier_pressure,
        "not_pure_late_low_health": classification == "opening_mid_boundary_path_retention",
    }


def build_report(
    *,
    lane_inventory: Path,
    trace_comparison: Path,
    route_hotspots: Path,
    lane_label: str,
    parent_label: str,
    candidate_label: str,
    target_seed: int | None,
) -> dict[str, Any]:
    errors: list[str] = []
    try:
        inventory = load_json_object(lane_inventory)
        trace = load_json_object(trace_comparison)
        hotspots = load_json_object(route_hotspots)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return invalid_report(lane_inventory, trace_comparison, route_hotspots, lane_label, [str(exc)])

    lane = find_lane(inventory, lane_label)
    if lane is None:
        errors.append(f"lane `{lane_label}` not found in lane inventory")
    matched = target_match(trace, target_seed)
    if matched is None:
        errors.append("target seed comparison not found")
        matched = {}
    parent = label_trace(matched, parent_label)
    candidate = label_trace(matched, candidate_label)
    if not parent:
        errors.append(f"parent label `{parent_label}` not found in trace comparison")
    if not candidate:
        errors.append(f"candidate label `{candidate_label}` not found in trace comparison")

    negative_count = as_int(hotspots.get("negative_sample_count"))
    time_bucket_hotspots = {
        OPENING_BUCKET: summary_count(hotspots, "time_bucket_summary", "time_bucket", OPENING_BUCKET),
        MID_BUCKET: summary_count(hotspots, "time_bucket_summary", "time_bucket", MID_BUCKET),
        LATE_BUCKET: summary_count(hotspots, "time_bucket_summary", "time_bucket", LATE_BUCKET),
    }
    pressure_hotspots = {
        BOUNDARY_PRESSURE: summary_count(hotspots, "pressure_summary", "pressure_tag", BOUNDARY_PRESSURE),
        "hazard_pressure": summary_count(hotspots, "pressure_summary", "pressure_tag", "hazard_pressure"),
        "low_health": summary_count(hotspots, "pressure_summary", "pressure_tag", "low_health"),
    }
    first_divergent = matched.get("first_divergent_action") if isinstance(matched, dict) else {}
    if not isinstance(first_divergent, dict):
        first_divergent = {}
    parent_pressure = first_pressure_time(parent)
    candidate_pressure = first_pressure_time(candidate)
    parent_low_health = first_low_health_time(parent)
    candidate_low_health = first_low_health_time(candidate)
    metrics = {
        "target_seed": target_seed,
        "parent_episode_time_seconds": parent.get("episode_time_seconds"),
        "candidate_episode_time_seconds": candidate.get("episode_time_seconds"),
        "episode_time_delta_seconds": matched.get("time_delta_seconds"),
        "first_divergent_time_seconds": first_divergent.get("time_seconds"),
        "first_divergent_parent_action": first_divergent.get("left_action"),
        "first_divergent_candidate_action": first_divergent.get("right_action"),
        "parent_first_high_pressure_time_seconds": parent_pressure,
        "candidate_first_high_pressure_time_seconds": candidate_pressure,
        "high_pressure_delta_seconds": round(candidate_pressure - parent_pressure, 4)
        if candidate_pressure is not None and parent_pressure is not None
        else None,
        "parent_first_low_health_time_seconds": parent_low_health,
        "candidate_first_low_health_time_seconds": candidate_low_health,
        "low_health_delta_seconds": round(candidate_low_health - parent_low_health, 4)
        if candidate_low_health is not None and parent_low_health is not None
        else None,
        "sample_count": as_int(hotspots.get("sample_count")),
        "negative_sample_count": negative_count,
        "negative_sample_ratio": as_float(hotspots.get("negative_sample_ratio")),
        "time_bucket_hotspots": time_bucket_hotspots,
        "pressure_hotspots": pressure_hotspots,
        "opening_action_counts": top_action_counts(hotspots, "time_bucket_summary", "time_bucket", OPENING_BUCKET),
        "mid_action_counts": top_action_counts(hotspots, "time_bucket_summary", "time_bucket", MID_BUCKET),
        "boundary_action_counts": top_action_counts(hotspots, "pressure_summary", "pressure_tag", BOUNDARY_PRESSURE),
    }
    diagnosis = infer_diagnosis(metrics)
    decision = "rl_lane_repair_action_plan_invalid" if errors else "rl_lane_repair_action_plan_ready"
    return {
        "report_version": 1,
        "decision": decision,
        "lane_label": lane_label,
        "lane_status": lane.get("split_status") if isinstance(lane, dict) else None,
        "lane_reuse_decision": lane.get("reuse_decision") if isinstance(lane, dict) else None,
        "source_reports": {
            "lane_inventory": str(lane_inventory),
            "trace_comparison": str(trace_comparison),
            "route_hotspots": str(route_hotspots),
        },
        "metrics": metrics,
        "diagnosis": diagnosis,
        "action_plan": action_plan(diagnosis),
        "errors": errors,
        "limitations": limitations(),
    }


def invalid_report(
    lane_inventory: Path,
    trace_comparison: Path,
    route_hotspots: Path,
    lane_label: str,
    errors: list[str],
) -> dict[str, Any]:
    return {
        "report_version": 1,
        "decision": "rl_lane_repair_action_plan_invalid",
        "lane_label": lane_label,
        "source_reports": {
            "lane_inventory": str(lane_inventory),
            "trace_comparison": str(trace_comparison),
            "route_hotspots": str(route_hotspots),
        },
        "metrics": {},
        "diagnosis": {},
        "action_plan": {},
        "errors": errors,
        "limitations": limitations(),
    }


def action_plan(diagnosis: dict[str, Any]) -> dict[str, Any]:
    classification = diagnosis.get("classification")
    if classification == "opening_mid_boundary_path_retention":
        objective_scope = [
            "opening_lt_60 boundary escape / route retention",
            "mid_60_to_180 boundary/path retention",
        ]
        disallowed = [
            "pure late low-health continuation",
            "shared PPO continuation that also tries to solve target63407",
            "relaxing short60 or parent-preservation gates to make the lane pass",
        ]
        repair_shapes = [
            "lane-specific reward/profile or adapter focused on boundary_edge route recovery",
            "narrow state-conditioned branch triggered by boundary pressure and bad route_recovery",
            "small-step continuation only after predefining all hard preflights",
        ]
    else:
        objective_scope = ["inspect mixed retention diagnostics before training"]
        disallowed = ["promoting the checkpoint without lane-specific preflights"]
        repair_shapes = ["collect more trace evidence before choosing a training objective"]
    return {
        "objective_scope": objective_scope,
        "disallowed_next_steps": disallowed,
        "candidate_repair_shapes": repair_shapes,
        "required_gates": [
            "target seed 63405 180s retention preflight must pass",
            "60s/caramel-workshop window target preflight must pass",
            "60/180/300s high-pressure parent no-regression must pass",
            "10 seed caramel-workshop follow-up must not hide seed-local tradeoffs",
            "failure-case review must stay attached if any gate fails",
        ],
        "acceptance_boundary": "This plan is repair routing only; it is not RL acceptance, stage 03 approval, or policy-candidate approval.",
    }


def limitations() -> list[str]:
    return [
        "This plan reads existing diagnostics only; it does not rerun simulation or train a policy.",
        "Sampled traces can miss unsampled frames and do not replace Replay or GameCore snapshots.",
        "Any follow-up checkpoint still requires target preflight, fixed-window no-regression, failure-case review, and RL acceptance gates.",
    ]


def write_markdown(report: dict[str, Any], path: Path) -> None:
    metrics = report.get("metrics", {})
    diagnosis = report.get("diagnosis", {})
    plan = report.get("action_plan", {})
    lines = [
        "# RL Lane Repair Action Plan",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Lane: `{report['lane_label']}`",
        f"- Lane status: `{report.get('lane_status')}`",
        f"- Classification: `{diagnosis.get('classification')}`",
        "",
        "## Diagnostic Summary",
        "",
        f"- Episode delta: `{metrics.get('episode_time_delta_seconds')}` seconds",
        f"- First divergent action: `{metrics.get('first_divergent_time_seconds')}`s, `{metrics.get('first_divergent_parent_action')}` -> `{metrics.get('first_divergent_candidate_action')}`",
        f"- First high pressure: parent `{metrics.get('parent_first_high_pressure_time_seconds')}`s, candidate `{metrics.get('candidate_first_high_pressure_time_seconds')}`s",
        f"- Negative route_recovery: `{metrics.get('negative_sample_count')}` / `{metrics.get('sample_count')}` (`{metrics.get('negative_sample_ratio')}`)",
        f"- Opening + mid hotspot ratio: `{diagnosis.get('opening_mid_hotspot_ratio')}`",
        f"- Boundary-edge hotspot ratio: `{diagnosis.get('boundary_edge_hotspot_ratio')}`",
        "",
        "## Hotspot Counts",
        "",
        "| Group | Count |",
        "|---|---:|",
    ]
    for label, count in (metrics.get("time_bucket_hotspots") or {}).items():
        lines.append(f"| `{label}` | {count} |")
    for label, count in (metrics.get("pressure_hotspots") or {}).items():
        lines.append(f"| `{label}` | {count} |")

    lines.extend(["", "## Action Plan", ""])
    for key, title in [
        ("objective_scope", "Objective Scope"),
        ("candidate_repair_shapes", "Candidate Repair Shapes"),
        ("required_gates", "Required Gates"),
        ("disallowed_next_steps", "Disallowed Next Steps"),
    ]:
        lines.append(f"### {title}")
        for item in plan.get(key, []) or []:
            lines.append(f"- {item}")
        lines.append("")
    lines.append(f"- Acceptance boundary: {plan.get('acceptance_boundary')}")
    if report.get("errors"):
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {item}" for item in report["errors"])
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an RL lane repair action plan.")
    parser.add_argument("--lane-inventory", type=Path, required=True)
    parser.add_argument("--trace-comparison", type=Path, required=True)
    parser.add_argument("--route-hotspots", type=Path, required=True)
    parser.add_argument("--lane-label", default="retention63405")
    parser.add_argument("--parent-label", default="a_parent")
    parser.add_argument("--candidate-label", default="b_candidate")
    parser.add_argument("--target-seed", type=int, default=None)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--markdown", type=Path, default=None)
    args = parser.parse_args()

    report = build_report(
        lane_inventory=args.lane_inventory,
        trace_comparison=args.trace_comparison,
        route_hotspots=args.route_hotspots,
        lane_label=args.lane_label,
        parent_label=args.parent_label,
        candidate_label=args.candidate_label,
        target_seed=args.target_seed,
    )
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "rl_lane_repair_action_plan_ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
