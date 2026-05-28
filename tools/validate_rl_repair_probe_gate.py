#!/usr/bin/env python3
"""Validate whether an RL repair probe is safe to continue exploring.

This is not an acceptance gate. It combines training, anchor-alignment,
window-regression, and failure-analysis reports to decide whether a repair
probe is clean enough for a limited follow-up run, or whether the branch should
stop and be recorded as a failure case.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


FORBIDDEN_DECISION_TOKENS = {
    "acceptance",
    "accepted",
    "candidate",
    "playtest",
    "production",
    "release",
    "rl_test_bot_candidate",
}


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def decision_uses_forbidden_token(value: Any) -> bool:
    lowered = str(value or "").lower()
    return any(token in lowered for token in FORBIDDEN_DECISION_TOKENS)


def report_label(path: Path) -> str:
    return path.name.removesuffix(".json")


def collect_gate_wording_errors(label: str, report: dict[str, Any], errors: list[str]) -> None:
    for field in ("decision", "gate_decision"):
        if decision_uses_forbidden_token(report.get(field)):
            errors.append(f"{label}: {field} overclaims repair evidence: {report.get(field)}")


def summarize_training_report(path: Path, errors: list[str], warnings: list[str]) -> dict[str, Any]:
    try:
        report = load_json_object(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"training_report: unable to load {path}: {exc}")
        return {"path": str(path), "loaded": False}

    collect_gate_wording_errors("training_report", report, errors)
    status = report.get("status")
    gate_decision = report.get("gate_decision")
    if status != "trained":
        warnings.append(f"training_report: status is `{status}`, expected `trained`")
    return {
        "path": str(path),
        "loaded": True,
        "status": status,
        "gate_decision": gate_decision,
        "model_path": report.get("model_path"),
        "reward_profile": report.get("reward_profile"),
    }


def summarize_anchor_alignment(
    path: Path | None,
    errors: list[str],
    blockers: list[str],
) -> dict[str, Any] | None:
    if path is None:
        return None
    try:
        report = load_json_object(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"anchor_alignment: unable to load {path}: {exc}")
        return {"path": str(path), "loaded": False}

    collect_gate_wording_errors("anchor_alignment", report, errors)
    alignment_blockers = [str(item) for item in report.get("blockers", [])]
    for item in alignment_blockers:
        blockers.append(f"anchor_alignment: {item}")
    decision = report.get("decision")
    if decision == "behavior_clone_anchor_alignment_failed" and not alignment_blockers:
        blockers.append("anchor_alignment: failed without explicit blockers")
    return {
        "path": str(path),
        "loaded": True,
        "decision": decision,
        "overall": report.get("overall"),
        "blocker_count": len(alignment_blockers),
    }


def summarize_window_regression(
    paths: list[Path],
    errors: list[str],
    blockers: list[str],
) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for path in paths:
        label = report_label(path)
        try:
            report = load_json_object(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{label}: unable to load {path}: {exc}")
            summaries.append({"path": str(path), "loaded": False})
            continue

        collect_gate_wording_errors(label, report, errors)
        decision = report.get("decision")
        report_blockers = [str(item) for item in report.get("blockers", [])]
        report_errors = [str(item) for item in report.get("errors", [])]
        if decision == "policy_window_regression_invalid":
            errors.extend(f"{label}: {item}" for item in report_errors or ["invalid regression report"])
        if decision == "policy_window_regression_failed":
            blockers.extend(f"{label}: {item}" for item in report_blockers or ["window regression failed"])
        summaries.append(
            {
                "path": str(path),
                "loaded": True,
                "decision": decision,
                "blocker_count": len(report_blockers),
                "error_count": len(report_errors),
            }
        )
    return summaries


def summarize_failure_analysis(path: Path | None, errors: list[str]) -> dict[str, Any] | None:
    if path is None:
        return None
    try:
        report = load_json_object(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"failure_analysis: unable to load {path}: {exc}")
        return {"path": str(path), "loaded": False}

    collect_gate_wording_errors("failure_analysis", report, errors)
    return {
        "path": str(path),
        "loaded": True,
        "decision": report.get("decision"),
        "gate_decision": report.get("gate_decision"),
        "total_failures": report.get("total_failures"),
        "repair_maps": report.get("repair_maps"),
    }


def build_report(
    *,
    training_report: Path,
    window_regressions: list[Path],
    anchor_alignment: Path | None = None,
    failure_analysis: Path | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    blockers: list[str] = []
    warnings: list[str] = []

    training_summary = summarize_training_report(training_report, errors, warnings)
    anchor_summary = summarize_anchor_alignment(anchor_alignment, errors, blockers)
    regression_summaries = summarize_window_regression(window_regressions, errors, blockers)
    failure_summary = summarize_failure_analysis(failure_analysis, errors)

    if failure_summary is not None and failure_summary.get("total_failures"):
        warnings.append(
            "failure_analysis: remaining failures mean this can only be limited repair evidence"
        )

    decision = (
        "rl_repair_probe_gate_invalid"
        if errors
        else "rl_repair_probe_gate_failed"
        if blockers
        else "rl_repair_probe_gate_passed_for_limited_followup"
    )
    return {
        "report_version": 1,
        "decision": decision,
        "gate_decision": decision,
        "training_report": training_summary,
        "anchor_alignment": anchor_summary,
        "window_regressions": regression_summaries,
        "failure_analysis": failure_summary,
        "errors": errors,
        "blockers": blockers,
        "warnings": warnings,
        "limitations": [
            "This gate is for RL repair probes only; it is not policy acceptance.",
            "Passing means a limited follow-up run may be considered, not that the policy is a candidate.",
            "Release, playtest, and RL acceptance require their separate manifests and manual gates.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# RL Repair Probe Gate",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Errors: `{len(report['errors'])}`",
        f"- Blockers: `{len(report['blockers'])}`",
        f"- Warnings: `{len(report['warnings'])}`",
        "",
        "## Inputs",
        "",
        f"- Training report: `{report['training_report'].get('path')}`",
    ]
    if report.get("anchor_alignment"):
        lines.append(f"- Anchor alignment: `{report['anchor_alignment'].get('path')}`")
    for item in report["window_regressions"]:
        lines.append(f"- Window regression: `{item.get('path')}`")
    if report.get("failure_analysis"):
        lines.append(f"- Failure analysis: `{report['failure_analysis'].get('path')}`")
    if report["errors"]:
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {item}" for item in report["errors"])
    if report["blockers"]:
        lines.extend(["", "## Blockers", ""])
        lines.extend(f"- {item}" for item in report["blockers"])
    if report["warnings"]:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {item}" for item in report["warnings"])
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an RL repair probe evidence bundle.")
    parser.add_argument("--training-report", type=Path, required=True)
    parser.add_argument("--window-regression", type=Path, action="append", required=True)
    parser.add_argument("--anchor-alignment", type=Path, default=None)
    parser.add_argument("--failure-analysis", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--markdown", type=Path, default=None)
    parser.add_argument("--allow-fail", action="store_true")
    args = parser.parse_args()

    report = build_report(
        training_report=args.training_report,
        window_regressions=args.window_regression,
        anchor_alignment=args.anchor_alignment,
        failure_analysis=args.failure_analysis,
    )
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        print(json.dumps(report, ensure_ascii=False))
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if report["decision"] != "rl_repair_probe_gate_passed_for_limited_followup" and not args.allow_fail:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
