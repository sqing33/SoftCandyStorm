#!/usr/bin/env python3
"""Validate whether an RL repair probe is safe to continue exploring.

This is not an acceptance gate. It combines training, anchor-alignment,
window-regression, and failure-analysis reports to decide whether a repair
probe is clean enough for a limited follow-up run, or whether the branch should
stop and be recorded as a failure case.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
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


@dataclass(frozen=True)
class WindowRegressionInput:
    label: str
    path: Path
    required: bool = False


@dataclass(frozen=True)
class TargetSeedPreflightInput:
    label: str
    path: Path
    required: bool = False


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


def parse_optional_window_regression(value: str) -> tuple[str | None, Path]:
    if "=" not in value:
        return None, Path(value)
    label, path_text = value.split("=", 1)
    label = label.strip()
    path_text = path_text.strip()
    if not label:
        raise argparse.ArgumentTypeError("window regression label must be non-empty")
    if not path_text:
        raise argparse.ArgumentTypeError("window regression path must be non-empty")
    return label, Path(path_text)


def parse_required_window_regression(value: str) -> tuple[str, Path]:
    label, path = parse_optional_window_regression(value)
    if label is None:
        raise argparse.ArgumentTypeError("required window regression must use LABEL=PATH")
    return label, path


def parse_optional_target_seed_preflight(value: str) -> tuple[str | None, Path]:
    if "=" not in value:
        return None, Path(value)
    label, path_text = value.split("=", 1)
    label = label.strip()
    path_text = path_text.strip()
    if not label:
        raise argparse.ArgumentTypeError("target seed preflight label must be non-empty")
    if not path_text:
        raise argparse.ArgumentTypeError("target seed preflight path must be non-empty")
    return label, Path(path_text)


def parse_required_target_seed_preflight(value: str) -> tuple[str, Path]:
    label, path = parse_optional_target_seed_preflight(value)
    if label is None:
        raise argparse.ArgumentTypeError("required target seed preflight must use LABEL=PATH")
    return label, path


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
    window_inputs: list[WindowRegressionInput],
    errors: list[str],
    blockers: list[str],
) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for window_input in window_inputs:
        path = window_input.path
        path_label = report_label(path)
        display_label = (
            path_label
            if window_input.label == path_label
            else f"{window_input.label}/{path_label}"
        )
        try:
            report = load_json_object(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{display_label}: unable to load {path}: {exc}")
            summaries.append(
                {
                    "label": window_input.label,
                    "path": str(path),
                    "required": window_input.required,
                    "loaded": False,
                }
            )
            continue

        collect_gate_wording_errors(display_label, report, errors)
        decision = report.get("decision")
        report_blockers = [str(item) for item in report.get("blockers", [])]
        report_errors = [str(item) for item in report.get("errors", [])]
        if decision == "policy_window_regression_invalid":
            errors.extend(
                f"{display_label}: {item}" for item in report_errors or ["invalid regression report"]
            )
        if decision == "policy_window_regression_failed":
            blockers.extend(
                f"{display_label}: {item}"
                for item in report_blockers or ["window regression failed"]
            )
        summaries.append(
            {
                "label": window_input.label,
                "path": str(path),
                "required": window_input.required,
                "loaded": True,
                "decision": decision,
                "blocker_count": len(report_blockers),
                "error_count": len(report_errors),
            }
        )
    return summaries


def summarize_target_seed_preflight(
    preflight_inputs: list[TargetSeedPreflightInput],
    errors: list[str],
    blockers: list[str],
) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for preflight_input in preflight_inputs:
        path = preflight_input.path
        path_label = report_label(path)
        display_label = (
            path_label
            if preflight_input.label == path_label
            else f"{preflight_input.label}/{path_label}"
        )
        try:
            report = load_json_object(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{display_label}: unable to load {path}: {exc}")
            summaries.append(
                {
                    "label": preflight_input.label,
                    "path": str(path),
                    "required": preflight_input.required,
                    "loaded": False,
                }
            )
            continue

        collect_gate_wording_errors(display_label, report, errors)
        decision = report.get("decision")
        report_blockers = [str(item) for item in report.get("blockers", [])]
        report_errors = [str(item) for item in report.get("errors", [])]
        if decision == "policy_target_seed_preflight_invalid":
            errors.extend(
                f"{display_label}: {item}"
                for item in report_errors or ["invalid target seed preflight report"]
            )
        elif decision == "policy_target_seed_preflight_failed":
            blockers.extend(
                f"{display_label}: {item}"
                for item in report_blockers or ["target seed preflight failed"]
            )
        elif decision != "policy_target_seed_preflight_passed":
            errors.append(f"{display_label}: unknown target seed preflight decision `{decision}`")
        summaries.append(
            {
                "label": preflight_input.label,
                "path": str(path),
                "required": preflight_input.required,
                "loaded": True,
                "decision": decision,
                "target_count": report.get("target_count"),
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


def normalize_window_regression_inputs(
    window_regressions: list[Path | tuple[str, Path] | WindowRegressionInput],
    required_window_regressions: list[tuple[str, Path]] | dict[str, Path] | None,
    errors: list[str],
) -> list[WindowRegressionInput]:
    inputs: list[WindowRegressionInput] = []
    seen_labels: dict[str, Path] = {}

    def add_input(label: str, path: Path, *, required: bool) -> None:
        if not label:
            errors.append(f"window_regression: label for {path} must be non-empty")
            return
        existing = seen_labels.get(label)
        if existing is not None:
            errors.append(
                "window_regression: duplicate label "
                f"`{label}` for {existing} and {path}"
            )
            return
        seen_labels[label] = path
        inputs.append(WindowRegressionInput(label=label, path=path, required=required))

    for item in window_regressions:
        if isinstance(item, WindowRegressionInput):
            add_input(item.label, item.path, required=item.required)
        elif isinstance(item, tuple):
            label, path = item
            add_input(label, path, required=False)
        else:
            add_input(report_label(item), item, required=False)

    if isinstance(required_window_regressions, dict):
        required_items = list(required_window_regressions.items())
    else:
        required_items = required_window_regressions or []
    for label, path in required_items:
        add_input(label, path, required=True)

    if not inputs:
        errors.append("window_regression: at least one window regression report is required")
    return inputs


def normalize_target_seed_preflight_inputs(
    target_seed_preflights: list[Path | tuple[str, Path] | TargetSeedPreflightInput] | None,
    required_target_seed_preflights: list[tuple[str, Path]] | dict[str, Path] | None,
    errors: list[str],
) -> list[TargetSeedPreflightInput]:
    inputs: list[TargetSeedPreflightInput] = []
    seen_labels: dict[str, Path] = {}

    def add_input(label: str, path: Path, *, required: bool) -> None:
        if not label:
            errors.append(f"target_seed_preflight: label for {path} must be non-empty")
            return
        existing = seen_labels.get(label)
        if existing is not None:
            errors.append(
                "target_seed_preflight: duplicate label "
                f"`{label}` for {existing} and {path}"
            )
            return
        seen_labels[label] = path
        inputs.append(TargetSeedPreflightInput(label=label, path=path, required=required))

    for item in target_seed_preflights or []:
        if isinstance(item, TargetSeedPreflightInput):
            add_input(item.label, item.path, required=item.required)
        elif isinstance(item, tuple):
            label, path = item
            add_input(label, path, required=False)
        else:
            add_input(report_label(item), item, required=False)

    if isinstance(required_target_seed_preflights, dict):
        required_items = list(required_target_seed_preflights.items())
    else:
        required_items = required_target_seed_preflights or []
    for label, path in required_items:
        add_input(label, path, required=True)

    return inputs


def build_report(
    *,
    training_report: Path,
    window_regressions: list[Path | tuple[str, Path] | WindowRegressionInput],
    required_window_regressions: list[tuple[str, Path]] | dict[str, Path] | None = None,
    target_seed_preflights: list[Path | tuple[str, Path] | TargetSeedPreflightInput] | None = None,
    required_target_seed_preflights: list[tuple[str, Path]] | dict[str, Path] | None = None,
    anchor_alignment: Path | None = None,
    failure_analysis: Path | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    blockers: list[str] = []
    warnings: list[str] = []

    training_summary = summarize_training_report(training_report, errors, warnings)
    anchor_summary = summarize_anchor_alignment(anchor_alignment, errors, blockers)
    regression_inputs = normalize_window_regression_inputs(
        window_regressions,
        required_window_regressions,
        errors,
    )
    regression_summaries = summarize_window_regression(regression_inputs, errors, blockers)
    preflight_inputs = normalize_target_seed_preflight_inputs(
        target_seed_preflights,
        required_target_seed_preflights,
        errors,
    )
    preflight_summaries = summarize_target_seed_preflight(preflight_inputs, errors, blockers)
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
        "window_regression_requirement": (
            "required_labeled_baselines"
            if any(item.required for item in regression_inputs)
            else "provided_reports_only"
        ),
        "required_window_regression_labels": [
            item.label for item in regression_inputs if item.required
        ],
        "window_regressions": regression_summaries,
        "target_seed_preflight_requirement": (
            "required_labeled_preflights"
            if any(item.required for item in preflight_inputs)
            else "provided_reports_only"
            if preflight_inputs
            else "not_required"
        ),
        "required_target_seed_preflight_labels": [
            item.label for item in preflight_inputs if item.required
        ],
        "target_seed_preflights": preflight_summaries,
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
        required = "required" if item.get("required") else "provided"
        lines.append(
            f"- Window regression ({required}, `{item.get('label')}`): `{item.get('path')}`"
        )
    for item in report["target_seed_preflights"]:
        required = "required" if item.get("required") else "provided"
        lines.append(
            f"- Target seed preflight ({required}, `{item.get('label')}`): `{item.get('path')}`"
        )
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
    parser.add_argument(
        "--window-regression",
        type=parse_optional_window_regression,
        action="append",
        default=[],
        help="Window regression report as PATH or LABEL=PATH.",
    )
    parser.add_argument(
        "--required-window-regression",
        type=parse_required_window_regression,
        action="append",
        default=[],
        help="Required baseline-preservation report as LABEL=PATH.",
    )
    parser.add_argument(
        "--target-seed-preflight",
        type=parse_optional_target_seed_preflight,
        action="append",
        default=[],
        help="Target seed preflight report as PATH or LABEL=PATH.",
    )
    parser.add_argument(
        "--required-target-seed-preflight",
        type=parse_required_target_seed_preflight,
        action="append",
        default=[],
        help="Required target seed preflight report as LABEL=PATH.",
    )
    parser.add_argument("--anchor-alignment", type=Path, default=None)
    parser.add_argument("--failure-analysis", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--markdown", type=Path, default=None)
    parser.add_argument("--allow-fail", action="store_true")
    args = parser.parse_args()
    if not args.window_regression and not args.required_window_regression:
        parser.error("at least one --window-regression or --required-window-regression is required")

    report = build_report(
        training_report=args.training_report,
        window_regressions=[
            (label or report_label(path), path)
            for label, path in args.window_regression
        ],
        required_window_regressions=args.required_window_regression,
        target_seed_preflights=[
            (label or report_label(path), path)
            for label, path in args.target_seed_preflight
        ],
        required_target_seed_preflights=args.required_target_seed_preflight,
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
