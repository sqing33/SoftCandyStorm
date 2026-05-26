#!/usr/bin/env python3
"""Validate manual base UI review records.

This dependency-free gate checks that a human review covers the Sugar Jar
Station base UI surface, meta panel navigation, selection affordances, codex
navigation, local data controls, and candidate-content boundaries. It does not
run Bevy, certify UX quality, integrate assets, or approve release readiness.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(REPO_ROOT / "harness" / "runtime_contract"))

from validate_runtime_surface_contract import build_report as build_runtime_surface_report
from validate_save_state_contract import build_report as build_save_contract_report


EXPECTED_REVIEW_TYPE = "base_ui_manual_review"
ALLOWED_GATE_DECISIONS = {"base_ui_review_pass", "needs_more_review", "repair", "reject"}
PASS_DECISION = "base_ui_review_pass"
FORBIDDEN_GATE_DECISIONS = {"release_ready", "runtime_integrated", "playtest_accepted", "platform_approved"}
ALLOWED_CHECK_DECISIONS = {"pass", "needs_more_review", "repair", "reject"}
REQUIRED_CHECK_IDS = {
    "overview_panel",
    "chapter_navigation",
    "character_map_selection",
    "codex_navigation",
    "privacy_settings_access",
    "local_data_controls",
    "candidate_content_boundaries",
    "runtime_evidence_limits",
}
TODO_MARKERS = ("TODO", "<", ">")


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]


def has_placeholder(value: Any) -> bool:
    if isinstance(value, str):
        return any(marker in value for marker in TODO_MARKERS)
    if isinstance(value, list):
        return any(has_placeholder(item) for item in value)
    if isinstance(value, dict):
        return any(has_placeholder(item) for item in value.values())
    return False


def resolve_repo_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def relative_repo_path(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(path)


def is_inside_repo(repo_root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return False
    return True


def require_existing_repo_path(value: Any, label: str, repo_root: Path, errors: list[str]) -> Path | None:
    if not is_nonempty_string(value):
        errors.append(f"{label} must be non-empty")
        return None
    if has_placeholder(value):
        errors.append(f"{label} must not contain TODO or placeholder markers")
        return None
    path = resolve_repo_path(repo_root, str(value))
    if not is_inside_repo(repo_root, path):
        errors.append(f"{label} must stay inside repository: {value}")
        return None
    if not path.exists():
        errors.append(f"{label} does not exist: {value}")
        return None
    return path


def validate_bound_runtime_surface(payload: dict[str, Any], repo_root: Path, errors: list[str]) -> str | None:
    contract_path = require_existing_repo_path(
        payload.get("runtime_surface_contract"),
        "runtime_surface_contract",
        repo_root,
        errors,
    )
    require_existing_repo_path(
        payload.get("runtime_surface_validation_report"),
        "runtime_surface_validation_report",
        repo_root,
        errors,
    )
    if contract_path is None:
        return None
    report = build_runtime_surface_report(contract_path, repo_root)
    if report["decision"] != "runtime_surface_contract_valid":
        errors.append("runtime_surface_contract must validate")
    return str(report["decision"])


def validate_bound_save_contract(payload: dict[str, Any], repo_root: Path, errors: list[str]) -> str | None:
    contract_path = require_existing_repo_path(
        payload.get("save_state_contract"),
        "save_state_contract",
        repo_root,
        errors,
    )
    require_existing_repo_path(
        payload.get("save_state_validation_report"),
        "save_state_validation_report",
        repo_root,
        errors,
    )
    if contract_path is None:
        return None
    report = build_save_contract_report(contract_path)
    if report["decision"] != "save_state_contract_valid":
        errors.append("save_state_contract must validate")
    if report.get("contract_id") != "save-state-v1":
        errors.append("save_state_contract must be save-state-v1")
    return str(report["decision"])


def validate_checks(checks: Any, gate_decision: Any) -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    reports: list[dict[str, Any]] = []
    if not isinstance(checks, list):
        return reports, ["checks must be a list"]

    seen: set[str] = set()
    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            errors.append(f"checks[{index}] must be an object")
            continue
        check_id = check.get("id")
        display_id = str(check_id) if is_nonempty_string(check_id) else f"checks[{index}]"
        if not is_nonempty_string(check_id):
            errors.append(f"{display_id}: id must be non-empty")
        elif check_id not in REQUIRED_CHECK_IDS:
            errors.append(f"{display_id}: id is not a required base UI review check")
        elif check_id in seen:
            errors.append(f"{display_id}: duplicate check id")
        else:
            seen.add(str(check_id))

        decision = check.get("decision")
        if decision not in ALLOWED_CHECK_DECISIONS:
            errors.append(f"{display_id}: decision must be one of {', '.join(sorted(ALLOWED_CHECK_DECISIONS))}")

        notes = check.get("notes")
        if not is_nonempty_string(notes):
            errors.append(f"{display_id}: notes must contain a concrete human observation")
        elif has_placeholder(notes):
            errors.append(f"{display_id}: notes must not contain TODO or placeholder markers")

        required_changes = check.get("required_changes")
        if not isinstance(required_changes, list) or not all(isinstance(item, str) for item in required_changes):
            errors.append(f"{display_id}: required_changes must be a list of strings")
            required_change_count = 0
        else:
            required_change_count = len([item for item in required_changes if item.strip()])
            if has_placeholder(required_changes):
                errors.append(f"{display_id}: required_changes must not contain TODO or placeholder markers")

        if decision in {"repair", "reject", "needs_more_review"} and required_change_count == 0:
            errors.append(f"{display_id}: {decision} requires at least one required_changes item")
        if gate_decision == PASS_DECISION:
            if decision != "pass":
                errors.append(f"{display_id}: base_ui_review_pass requires every check decision to be pass")
            if required_change_count:
                errors.append(f"{display_id}: base_ui_review_pass cannot have required_changes")

        reports.append(
            {
                "id": check_id if is_nonempty_string(check_id) else display_id,
                "decision": decision,
                "required_change_count": required_change_count,
            }
        )

    missing_ids = sorted(REQUIRED_CHECK_IDS - seen)
    if missing_ids:
        errors.append(f"checks missing required ids: {', '.join(missing_ids)}")
    return reports, errors


def build_report(review_path: Path, repo_root: Path) -> dict[str, Any]:
    payload = load_json_object(review_path)
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(payload.get("review_version"), int) or payload["review_version"] <= 0:
        errors.append("review_version must be a positive integer")
    if payload.get("review_type") != EXPECTED_REVIEW_TYPE:
        errors.append(f"review_type must be `{EXPECTED_REVIEW_TYPE}`")
    for field in ("review_id", "reviewer", "reviewed_at", "summary"):
        if not is_nonempty_string(payload.get(field)):
            errors.append(f"{field} must be non-empty")
        elif has_placeholder(payload.get(field)):
            errors.append(f"{field} must not contain TODO or placeholder markers")

    gate_decision = payload.get("gate_decision")
    if gate_decision in FORBIDDEN_GATE_DECISIONS:
        errors.append(f"forbidden gate_decision `{gate_decision}`")
    elif gate_decision not in ALLOWED_GATE_DECISIONS:
        errors.append(f"gate_decision must be one of {', '.join(sorted(ALLOWED_GATE_DECISIONS))}")

    runtime_surface_decision = validate_bound_runtime_surface(payload, repo_root, errors)
    save_state_decision = validate_bound_save_contract(payload, repo_root, errors)
    check_reports, check_errors = validate_checks(payload.get("checks"), gate_decision)
    errors.extend(check_errors)

    global_risks = string_list(payload.get("global_risks"))
    next_actions = string_list(payload.get("next_actions"))
    if payload.get("global_risks") is not None and not isinstance(payload.get("global_risks"), list):
        errors.append("global_risks must be a list")
    if payload.get("next_actions") is not None and not isinstance(payload.get("next_actions"), list):
        errors.append("next_actions must be a list")
    if has_placeholder(payload.get("global_risks")):
        errors.append("global_risks must not contain TODO or placeholder markers")
    if has_placeholder(payload.get("next_actions")):
        errors.append("next_actions must not contain TODO or placeholder markers")
    if gate_decision == PASS_DECISION and global_risks:
        errors.append("base_ui_review_pass cannot list unresolved global_risks")
    if gate_decision in {"repair", "reject", "needs_more_review"} and not next_actions:
        errors.append(f"{gate_decision} gate requires non-empty next_actions")

    return {
        "report_version": 1,
        "source": relative_repo_path(repo_root, review_path),
        "repo_root": str(repo_root),
        "decision": "base_ui_manual_review_valid" if not errors else "base_ui_manual_review_invalid",
        "review_type": payload.get("review_type"),
        "review_id": payload.get("review_id"),
        "gate_decision": gate_decision,
        "runtime_surface_contract_decision": runtime_surface_decision,
        "save_state_contract_decision": save_state_decision,
        "check_count": len(check_reports),
        "issue_check_count": sum(1 for item in check_reports if item["decision"] != "pass"),
        "global_risk_count": len(global_risks),
        "next_action_count": len(next_actions),
        "errors": errors,
        "warnings": warnings,
        "checks": check_reports,
        "limitations": [
            "This validator checks manual base UI review record completeness only.",
            "It does not run Bevy, inspect screenshots, certify UX quality, integrate candidates, or approve release readiness.",
            "A valid base UI manual review does not replace manual playtest, privacy, platform path, content, or asset acceptance gates.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Base UI Manual Review Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Decision: `{report['decision']}`",
        f"- Review id: `{report['review_id']}`",
        f"- Gate decision: `{report['gate_decision']}`",
        f"- Runtime surface contract: `{report['runtime_surface_contract_decision']}`",
        f"- Save state contract: `{report['save_state_contract_decision']}`",
        f"- Checks: {report['check_count']}",
        f"- Issue checks: {report['issue_check_count']}",
        f"- Global risks: {report['global_risk_count']}",
        f"- Next actions: {report['next_action_count']}",
        "",
        "## Errors",
        "",
    ]
    if report["errors"]:
        lines.extend(f"- {error}" for error in report["errors"])
    else:
        lines.append("- None")
    lines.extend(["", "## Warnings", ""])
    if report["warnings"]:
        lines.extend(f"- {warning}" for warning in report["warnings"])
    else:
        lines.append("- None")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm manual base UI reviews.")
    parser.add_argument("review", type=Path, help="Manual base UI review JSON")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown report")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    review_path = args.review if args.review.is_absolute() else repo_root / args.review
    report = build_report(review_path, repo_root)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "base_ui_manual_review_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
