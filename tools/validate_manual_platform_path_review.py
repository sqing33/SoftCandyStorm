#!/usr/bin/env python3
"""Validate manual platform path review records.

This dependency-free gate checks that a human review covers the platform save
path policy, save contract bindings, delete/export boundaries, migration
retention, cloud-save limitations, and release evidence limits. It does not
provide legal, platform, or release approval.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from validate_save_path_policy import build_report as build_path_policy_report
from validate_save_state_contract import build_report as build_save_contract_report


ALLOWED_GATE_DECISIONS = {"pass", "repair", "reject", "needs_more_review"}
FORBIDDEN_GATE_DECISIONS = {"release_ready", "legal_approved", "platform_approved", "runtime_integrated"}
ALLOWED_CHECK_DECISIONS = {"pass", "repair", "reject", "needs_more_review"}
REQUIRED_CHECK_IDS = {
    "logical_roots",
    "no_host_absolute_paths",
    "delete_scope",
    "export_scope",
    "migration_original_retention",
    "cloud_sync_policy",
    "runtime_evidence_limits",
}
REQUIRED_SAVE_CONTRACTS = {"save-state-v0", "save-state-v1"}
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


def has_placeholder(value: Any) -> bool:
    if isinstance(value, str):
        return any(marker in value for marker in TODO_MARKERS)
    if isinstance(value, list):
        return any(has_placeholder(item) for item in value)
    if isinstance(value, dict):
        return any(has_placeholder(item) for item in value.values())
    return False


def require_existing_repo_path(value: Any, label: str, repo_root: Path, errors: list[str]) -> Path | None:
    if not is_nonempty_string(value):
        errors.append(f"{label} must be non-empty")
        return None
    path = resolve_repo_path(repo_root, str(value))
    if not is_inside_repo(repo_root, path):
        errors.append(f"{label} must stay inside repository: {value}")
        return None
    if not path.exists():
        errors.append(f"{label} does not exist: {value}")
        return None
    return path


def validate_existing_report(value: Any, label: str, repo_root: Path, errors: list[str]) -> None:
    require_existing_repo_path(value, label, repo_root, errors)


def validate_bound_policy(payload: dict[str, Any], repo_root: Path, errors: list[str]) -> dict[str, Any] | None:
    policy_path = require_existing_repo_path(payload.get("path_policy_path"), "path_policy_path", repo_root, errors)
    validate_existing_report(
        payload.get("path_policy_validation_report"),
        "path_policy_validation_report",
        repo_root,
        errors,
    )
    if policy_path is None:
        return None
    policy_report = build_path_policy_report(policy_path)
    if policy_report["decision"] != "save_path_policy_valid":
        errors.append("bound platform save path policy must validate")
    return policy_report


def validate_bound_save_contracts(
    payload: dict[str, Any],
    repo_root: Path,
    errors: list[str],
) -> list[dict[str, Any]]:
    paths = string_list(payload.get("save_contract_paths"))
    reports = string_list(payload.get("save_contract_validation_reports"))
    if payload.get("save_contract_paths") is not None and not isinstance(payload.get("save_contract_paths"), list):
        errors.append("save_contract_paths must be a list")
    if payload.get("save_contract_validation_reports") is not None and not isinstance(payload.get("save_contract_validation_reports"), list):
        errors.append("save_contract_validation_reports must be a list")
    if len(paths) != len(reports):
        errors.append("save_contract_paths and save_contract_validation_reports must have the same length")

    contract_reports: list[dict[str, Any]] = []
    seen_contracts: set[str] = set()
    for index, value in enumerate(paths):
        contract_path = require_existing_repo_path(value, f"save_contract_paths[{index}]", repo_root, errors)
        if index < len(reports):
            validate_existing_report(reports[index], f"save_contract_validation_reports[{index}]", repo_root, errors)
        if contract_path is None:
            continue
        report = build_save_contract_report(contract_path)
        contract_reports.append(report)
        if report["decision"] != "save_state_contract_valid":
            errors.append(f"save_contract_paths[{index}] must validate")
        if is_nonempty_string(report.get("contract_id")):
            seen_contracts.add(str(report["contract_id"]))

    missing = sorted(REQUIRED_SAVE_CONTRACTS - seen_contracts)
    if missing:
        errors.append(f"save_contract_paths missing required contracts: {', '.join(missing)}")
    return contract_reports


def validate_checks(checks: Any, gate_decision: str | None) -> tuple[list[dict[str, Any]], list[str]]:
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
            errors.append(f"{display_id}: id is not a required platform path review check")
        elif check_id in seen:
            errors.append(f"{display_id}: duplicate check id")
        else:
            seen.add(str(check_id))

        decision = check.get("decision")
        if decision not in ALLOWED_CHECK_DECISIONS:
            errors.append(
                f"{display_id}: decision must be one of {', '.join(sorted(ALLOWED_CHECK_DECISIONS))}"
            )

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
        if gate_decision == "pass":
            if decision != "pass":
                errors.append(f"{display_id}: pass gate requires every check decision to be pass")
            if required_change_count:
                errors.append(f"{display_id}: pass gate cannot have required_changes")

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

    policy_report = validate_bound_policy(payload, repo_root, errors)
    contract_reports = validate_bound_save_contracts(payload, repo_root, errors)
    check_reports, check_errors = validate_checks(
        payload.get("checks"),
        str(gate_decision) if isinstance(gate_decision, str) else None,
    )
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
    if gate_decision == "pass" and global_risks:
        errors.append("pass gate cannot list unresolved global_risks")
    if gate_decision in {"repair", "reject", "needs_more_review"} and not next_actions:
        errors.append(f"{gate_decision} gate requires non-empty next_actions")

    issue_check_count = sum(
        1
        for item in check_reports
        if item["decision"] in {"repair", "reject", "needs_more_review"}
        or item["required_change_count"] > 0
    )
    if gate_decision == "repair" and issue_check_count == 0 and not global_risks:
        errors.append("repair gate requires at least one check issue or global_risks entry")

    return {
        "report_version": 1,
        "source": relative_repo_path(repo_root, review_path),
        "repo_root": str(repo_root),
        "decision": "manual_platform_path_review_valid" if not errors else "manual_platform_path_review_invalid",
        "gate_decision": gate_decision,
        "check_count": len(check_reports),
        "required_check_count": len(REQUIRED_CHECK_IDS),
        "issue_check_count": issue_check_count,
        "global_risk_count": len(global_risks),
        "next_action_count": len(next_actions),
        "bound_path_policy_decision": policy_report["decision"] if policy_report is not None else None,
        "bound_save_contract_decisions": [report["decision"] for report in contract_reports],
        "errors": errors,
        "warnings": warnings,
        "limitations": [
            "This validator checks manual platform path review completeness only.",
            "It does not provide legal advice, platform approval, cloud save approval, or release readiness.",
            "A pass decision does not prove executable Runtime platform path behavior.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Manual Platform Path Review Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Decision: `{report['decision']}`",
        f"- Gate decision: `{report['gate_decision']}`",
        f"- Checks reviewed: {report['check_count']} / {report['required_check_count']}",
        f"- Issue checks: {report['issue_check_count']}",
        f"- Global risks: {report['global_risk_count']}",
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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm manual platform path reviews.")
    parser.add_argument("review", type=Path, help="Manual platform path review JSON")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON validation report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown validation summary")
    args = parser.parse_args()

    report = build_report(args.review, args.repo_root)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "manual_platform_path_review_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
