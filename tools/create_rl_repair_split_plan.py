#!/usr/bin/env python3
"""Create a split repair plan from an RL repair-probe hard gate report.

The plan is a routing aid for failed repair probes. It groups blockers by
required evidence label so follow-up work can separate target-seed failures,
short-window hard preflights, parent preservation, and adapter scope issues.
It does not approve follow-up training or replace the original gate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SECTION_SPECS = [
    ("target_seed_preflights", "target_seed_preflight"),
    ("window_target_preflights", "window_target_preflight"),
    ("window_regressions", "window_regression"),
    ("policy_adapter_scopes", "policy_adapter_scope"),
]


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def string_list(value: Any) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def nonnegative_int(value: Any, fallback: int, errors: list[str], label: str, field: str) -> int:
    if value is None:
        return fallback
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        errors.append(f"{label}: {field} must be a non-negative integer")
        return fallback
    if parsed < 0:
        errors.append(f"{label}: {field} must be a non-negative integer")
        return fallback
    return parsed


def normalize_status(decision: Any, blocker_count: int, error_count: int) -> str:
    decision_text = str(decision or "")
    if error_count > 0 or "invalid" in decision_text:
        return "invalid"
    if blocker_count > 0 or "failed" in decision_text:
        return "failed"
    if decision_text.endswith("_passed") or decision_text == "policy_window_regression_passed":
        return "passed"
    return "unknown"


def recommendation_for_lane(source_type: str, status: str) -> str:
    if status == "passed":
        return "keep as required evidence in the next hard gate"
    if source_type == "target_seed_preflight":
        return "repair this target seed before rerunning full fixed-window matrices"
    if source_type == "window_target_preflight":
        return "treat this short-window target as an early-stop hard preflight"
    if source_type == "window_regression":
        return "restore parent/no-regression preservation before extending training"
    if source_type == "policy_adapter_scope":
        return "fix adapter provenance or dispatch scope before using wrapper evidence"
    return "inspect this lane before continuing"


def blockers_for_label(blockers: list[str], label: str) -> list[str]:
    prefix = f"{label}/"
    return [item for item in blockers if item.startswith(prefix)]


def build_plan(repair_gate: Path) -> dict[str, Any]:
    errors: list[str] = []
    try:
        gate = load_json_object(repair_gate)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {
            "report_version": 1,
            "decision": "rl_repair_split_plan_invalid",
            "repair_gate": str(repair_gate),
            "errors": [f"unable to load repair gate: {exc}"],
            "lanes": [],
            "unassigned_blockers": [],
            "limitations": limitations(),
        }

    gate_blockers = string_list(gate.get("blockers"))
    lanes: list[dict[str, Any]] = []
    assigned_blockers: set[str] = set()
    seen_labels: set[str] = set()
    for section_key, source_type in SECTION_SPECS:
        section = gate.get(section_key)
        if section is None:
            continue
        if not isinstance(section, list):
            errors.append(f"{section_key} must be a list when present")
            continue
        for item in section:
            if not isinstance(item, dict):
                errors.append(f"{section_key} contains a non-object item")
                continue
            label = str(item.get("label") or Path(str(item.get("path") or section_key)).stem)
            if label in seen_labels:
                errors.append(f"duplicate lane label `{label}`")
                continue
            seen_labels.add(label)
            lane_blockers = blockers_for_label(gate_blockers, label)
            assigned_blockers.update(lane_blockers)
            raw_blocker_count = item.get("blocker_count")
            source_blocker_count = nonnegative_int(
                raw_blocker_count,
                len(lane_blockers),
                errors,
                label,
                "blocker_count",
            )
            blocker_count = max(source_blocker_count, len(lane_blockers))
            error_count = nonnegative_int(item.get("error_count"), 0, errors, label, "error_count")
            status = normalize_status(item.get("decision"), blocker_count, error_count)
            lanes.append(
                {
                    "label": label,
                    "source_type": source_type,
                    "path": item.get("path"),
                    "required": bool(item.get("required")),
                    "decision": item.get("decision"),
                    "status": status,
                    "blocker_count": blocker_count,
                    "error_count": error_count,
                    "blockers": lane_blockers,
                    "recommendation": recommendation_for_lane(source_type, status),
                }
            )

    unassigned_blockers = [item for item in gate_blockers if item not in assigned_blockers]
    failed_lanes = [item["label"] for item in lanes if item["status"] == "failed"]
    invalid_lanes = [item["label"] for item in lanes if item["status"] == "invalid"]
    passed_lanes = [item["label"] for item in lanes if item["status"] == "passed"]
    decision = "rl_repair_split_plan_invalid" if errors or invalid_lanes else "rl_repair_split_plan_ready"
    return {
        "report_version": 1,
        "decision": decision,
        "repair_gate": str(repair_gate),
        "repair_gate_decision": gate.get("decision") or gate.get("gate_decision"),
        "lane_count": len(lanes),
        "passed_lanes": passed_lanes,
        "failed_lanes": failed_lanes,
        "invalid_lanes": invalid_lanes,
        "lanes": lanes,
        "unassigned_blockers": unassigned_blockers,
        "errors": errors,
        "limitations": limitations(),
    }


def limitations() -> list[str]:
    return [
        "This plan only groups existing repair-gate evidence; it does not rerun simulations.",
        "A passed lane remains repair evidence, not RL acceptance or policy-candidate approval.",
        "Follow-up checkpoints must rerun target preflights, fixed-window no-regression, and failure-case review.",
    ]


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# RL Repair Split Plan",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Repair gate: `{report['repair_gate']}`",
        f"- Repair gate decision: `{report.get('repair_gate_decision')}`",
        f"- Lanes: `{report['lane_count']}`",
        f"- Passed lanes: `{', '.join(report['passed_lanes']) or 'none'}`",
        f"- Failed lanes: `{', '.join(report['failed_lanes']) or 'none'}`",
        f"- Invalid lanes: `{', '.join(report.get('invalid_lanes', [])) or 'none'}`",
        "",
        "## Lanes",
        "",
        "| Label | Type | Status | Blockers | Recommendation |",
        "|---|---|---|---:|---|",
    ]
    for lane in report["lanes"]:
        lines.append(
            "| `{label}` | `{source_type}` | `{status}` | {blockers} | {recommendation} |".format(
                label=lane["label"],
                source_type=lane["source_type"],
                status=lane["status"],
                blockers=lane["blocker_count"],
                recommendation=lane["recommendation"],
            )
        )
    lines.extend(["", "## Blockers By Lane", ""])
    for lane in report["lanes"]:
        lines.append(f"### `{lane['label']}`")
        if lane["blockers"]:
            lines.extend(f"- {item}" for item in lane["blockers"])
        else:
            lines.append("- None")
        lines.append("")
    lines.append("## Unassigned Blockers")
    lines.append("")
    if report["unassigned_blockers"]:
        lines.extend(f"- {item}" for item in report["unassigned_blockers"])
    else:
        lines.append("- None")
    if report["errors"]:
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {item}" for item in report["errors"])
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an RL repair split plan.")
    parser.add_argument("--repair-gate", type=Path, required=True)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--markdown", type=Path, default=None)
    args = parser.parse_args()

    report = build_plan(args.repair_gate)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "rl_repair_split_plan_ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
