#!/usr/bin/env python3
"""Validate manual legal/compliance review records.

This dependency-free gate checks that a human legal or compliance review record
covers privacy, upload transport, platform path, retention, notices, and release
evidence limits. It does not provide legal advice, platform approval, or release
readiness.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from validate_runtime_privacy_settings_contract import build_report as build_runtime_contract_report
from validate_telemetry_privacy_policy import build_report as build_policy_report
from validate_upload_transport_contract import build_report as build_upload_contract_report


ALLOWED_GATE_DECISIONS = {"pass", "repair", "reject", "needs_more_review"}
FORBIDDEN_GATE_DECISIONS = {
    "release_ready",
    "accepted_content",
    "runtime_integrated",
    "legal_approved",
    "platform_approved",
}
ALLOWED_CHECK_DECISIONS = {"pass", "repair", "reject", "needs_more_review"}
REQUIRED_CHECK_IDS = {
    "privacy_notice_claims",
    "consent_and_default_off",
    "prohibited_data_fields",
    "raw_replay_and_crash_reports",
    "retention_delete_export",
    "platform_path_and_local_data_scope",
    "upload_transport_status",
    "jurisdiction_and_store_requirements",
    "release_evidence_limits",
}
REQUIRED_DECISION_REPORTS = {
    "manual_privacy_review_report": "manual_privacy_review_valid",
    "manual_platform_path_review_report": "manual_platform_path_review_valid",
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


def require_existing_repo_path(
    payload: dict[str, Any],
    field: str,
    repo_root: Path,
    errors: list[str],
) -> Path | None:
    value = payload.get(field)
    if not is_nonempty_string(value):
        errors.append(f"{field} must be non-empty")
        return None
    if has_placeholder(value):
        errors.append(f"{field} must not contain TODO or placeholder markers")
        return None
    path = resolve_repo_path(repo_root, str(value))
    if not is_inside_repo(repo_root, path):
        errors.append(f"{field} must stay inside repository: {value}")
        return None
    if not path.exists():
        errors.append(f"{field} does not exist: {value}")
        return None
    return path


def report_decision(path: Path) -> str | None:
    if path.suffix != ".json":
        return None
    payload = load_json_object(path)
    decision = payload.get("decision")
    return str(decision) if is_nonempty_string(decision) else None


def validate_top_level(payload: dict[str, Any], errors: list[str]) -> None:
    if not isinstance(payload.get("review_version"), int) or payload["review_version"] <= 0:
        errors.append("review_version must be a positive integer")
    for field in ("review_id", "reviewer", "reviewer_role", "reviewed_at", "summary"):
        if not is_nonempty_string(payload.get(field)):
            errors.append(f"{field} must be non-empty")
        elif has_placeholder(payload.get(field)):
            errors.append(f"{field} must not contain TODO or placeholder markers")

    scope = string_list(payload.get("jurisdiction_scope"))
    if not scope:
        errors.append("jurisdiction_scope must be a non-empty list of strings")
    elif len(scope) != len(payload.get("jurisdiction_scope", [])) or has_placeholder(scope):
        errors.append("jurisdiction_scope must contain only concrete strings")

    gate_decision = payload.get("gate_decision")
    if gate_decision in FORBIDDEN_GATE_DECISIONS:
        errors.append(f"forbidden gate_decision `{gate_decision}`")
    elif gate_decision not in ALLOWED_GATE_DECISIONS:
        errors.append(f"gate_decision must be one of {', '.join(sorted(ALLOWED_GATE_DECISIONS))}")


def validate_existing_reports(payload: dict[str, Any], repo_root: Path, errors: list[str]) -> dict[str, str | None]:
    report_fields = [
        "policy_validation_report",
        "runtime_contract_validation_report",
        "upload_transport_validation_report",
        "manual_privacy_review_report",
        "manual_platform_path_review_report",
    ]
    decisions: dict[str, str | None] = {}
    for field in report_fields:
        path = require_existing_repo_path(payload, field, repo_root, errors)
        decisions[field] = None
        if path is not None:
            try:
                decisions[field] = report_decision(path)
            except (OSError, ValueError, json.JSONDecodeError) as error:
                errors.append(f"{field} is invalid JSON: {error}")

    for field, expected in REQUIRED_DECISION_REPORTS.items():
        decision = decisions.get(field)
        if decision != expected:
            errors.append(f"{field} decision must be `{expected}`")
    return decisions


def validate_bound_contracts(
    payload: dict[str, Any],
    repo_root: Path,
    errors: list[str],
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None]:
    policy_path = require_existing_repo_path(payload, "policy_path", repo_root, errors)
    runtime_contract_path = require_existing_repo_path(
        payload,
        "runtime_privacy_contract_path",
        repo_root,
        errors,
    )
    save_contract_path = require_existing_repo_path(payload, "save_contract_path", repo_root, errors)
    upload_contract_path = require_existing_repo_path(payload, "upload_transport_contract_path", repo_root, errors)

    policy_report: dict[str, Any] | None = None
    runtime_report: dict[str, Any] | None = None
    upload_report: dict[str, Any] | None = None
    if policy_path is not None:
        policy_report = build_policy_report(policy_path)
        if policy_report["decision"] != "telemetry_privacy_policy_valid":
            errors.append("bound telemetry privacy policy must validate")
    if runtime_contract_path is not None:
        runtime_report = build_runtime_contract_report(
            runtime_contract_path,
            policy_path,
            save_contract_path,
        )
        if runtime_report["decision"] != "runtime_privacy_settings_contract_valid":
            errors.append("bound runtime privacy settings contract must validate")
    if upload_contract_path is not None:
        upload_report = build_upload_contract_report(
            upload_contract_path,
            policy_path,
            runtime_contract_path,
        )
        if upload_report["decision"] != "upload_transport_contract_valid":
            errors.append("bound upload transport contract must validate")
        if upload_report.get("implementation_status") == "implemented":
            errors.append("implemented upload transport requires separate Runtime smoke evidence before legal pass")
    return policy_report, runtime_report, upload_report


def validate_checks(checks: Any, gate_decision: str | None) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    reports: list[dict[str, Any]] = []
    if not isinstance(checks, list):
        return reports, ["checks must be a list"], warnings

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
            errors.append(f"{display_id}: id is not a required legal review check")
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
    return reports, errors, warnings


def build_report(review_path: Path, repo_root: Path) -> dict[str, Any]:
    payload = load_json_object(review_path)
    errors: list[str] = []
    warnings: list[str] = []

    validate_top_level(payload, errors)
    report_decisions = validate_existing_reports(payload, repo_root, errors)
    policy_report, runtime_report, upload_report = validate_bound_contracts(payload, repo_root, errors)
    gate_decision = payload.get("gate_decision") if isinstance(payload.get("gate_decision"), str) else None
    check_reports, check_errors, check_warnings = validate_checks(payload.get("checks"), gate_decision)
    errors.extend(check_errors)
    warnings.extend(check_warnings)

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

    issue_count = sum(
        1
        for item in check_reports
        if item["decision"] in {"repair", "reject", "needs_more_review"} or item["required_change_count"] > 0
    )
    if gate_decision == "repair" and issue_count == 0 and not global_risks:
        errors.append("repair gate requires at least one check issue or global_risks entry")

    return {
        "report_version": 1,
        "source": relative_repo_path(repo_root, review_path),
        "repo_root": str(repo_root),
        "decision": "manual_legal_review_valid" if not errors else "manual_legal_review_invalid",
        "gate_decision": gate_decision,
        "jurisdiction_scope": string_list(payload.get("jurisdiction_scope")),
        "check_count": len(check_reports),
        "issue_count": issue_count,
        "global_risk_count": len(global_risks),
        "next_action_count": len(next_actions),
        "bound_policy_decision": policy_report["decision"] if policy_report is not None else None,
        "bound_runtime_contract_decision": runtime_report["decision"] if runtime_report is not None else None,
        "bound_upload_contract_decision": upload_report["decision"] if upload_report is not None else None,
        "manual_privacy_review_decision": report_decisions.get("manual_privacy_review_report"),
        "manual_platform_path_review_decision": report_decisions.get("manual_platform_path_review_report"),
        "errors": errors,
        "warnings": warnings,
        "limitations": [
            "This validator checks manual legal/compliance review record completeness only.",
            "It does not provide legal advice, platform approval, or release readiness.",
            "A pass gate still requires executable Runtime evidence and Release Candidate gates.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Manual Legal Review Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Decision: `{report['decision']}`",
        f"- Gate decision: `{report['gate_decision']}`",
        f"- Jurisdiction scope: `{', '.join(report['jurisdiction_scope'])}`",
        f"- Checks: {report['check_count']}",
        f"- Issues: {report['issue_count']}",
        f"- Global risks: {report['global_risk_count']}",
        f"- Policy: `{report['bound_policy_decision']}`",
        f"- Runtime privacy contract: `{report['bound_runtime_contract_decision']}`",
        f"- Upload transport contract: `{report['bound_upload_contract_decision']}`",
        f"- Manual privacy review: `{report['manual_privacy_review_decision']}`",
        f"- Manual platform path review: `{report['manual_platform_path_review_decision']}`",
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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm manual legal review records.")
    parser.add_argument("review", type=Path, help="Manual legal/compliance review JSON file")
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
    return 0 if report["decision"] == "manual_legal_review_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
