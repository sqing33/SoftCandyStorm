#!/usr/bin/env python3
"""Validate final human content acceptance records.

This gate checks that a full content pack is only accepted after simulation
candidate staging and a valid accepted-content lockfile report exist. It does
not run Harness simulation, copy candidate content, integrate Runtime content,
or approve release readiness.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from validate_content_simulation_candidate_manifest import build_report as build_simulation_candidate_report


EXPECTED_REVIEW_TYPE = "content_final_acceptance"
ALLOWED_DECISIONS = {"accepted_content", "needs_more_review", "repair", "reject"}
PASS_DECISION = "accepted_content"
REQUIRED_CHECKS = {
    "accepts_content_pack": True,
    "accepted_content_only_after_reviews": True,
    "lockfile_valid": True,
    "release_ready": False,
    "runtime_integrated": False,
    "generated_candidate_direct_acceptance_allowed": False,
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


def validate_checks(payload: dict[str, Any], decision: Any, errors: list[str]) -> None:
    checks = payload.get("checks")
    if not isinstance(checks, dict):
        errors.append("checks must be an object")
        checks = {}
    for field, expected in REQUIRED_CHECKS.items():
        if checks.get(field) is not expected:
            errors.append(f"checks.{field} must be {json.dumps(expected)}")
    if decision == PASS_DECISION and any(checks.get(field) is not expected for field, expected in REQUIRED_CHECKS.items()):
        errors.append("accepted_content requires every required check to match")


def validate_simulation_candidate_manifest(
    path: Path | None,
    repo_root: Path,
    payload: dict[str, Any],
    errors: list[str],
) -> dict[str, Any] | None:
    if path is None:
        return None
    report = build_simulation_candidate_report(path, repo_root)
    if report["decision"] != "content_simulation_candidate_manifest_valid":
        errors.append("source_simulation_candidate_manifest must validate")
    if report.get("candidate_pack_id") != payload.get("candidate_pack_id"):
        errors.append("candidate_pack_id must match source_simulation_candidate_manifest")
    return report


def validate_lockfile_report(
    path: Path | None,
    candidate_pack_id: Any,
    errors: list[str],
) -> dict[str, Any] | None:
    if path is None:
        return None
    try:
        report = load_json_object(path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"accepted_content_lockfile_report is invalid JSON: {error}")
        return None

    if report.get("decision") != "accepted_content_lockfile_valid":
        errors.append("accepted_content_lockfile_report decision must be accepted_content_lockfile_valid")
    if not isinstance(report.get("locked_count"), int) or report["locked_count"] <= 0:
        errors.append("accepted_content_lockfile_report locked_count must be positive")
    entries = report.get("entries")
    if not isinstance(entries, list) or not entries:
        errors.append("accepted_content_lockfile_report entries must be non-empty")
        entries = []
    matching_entries = [
        entry
        for entry in entries
        if isinstance(entry, dict)
        and entry.get("id") == candidate_pack_id
        and entry.get("status") == "locked"
    ]
    if not matching_entries:
        errors.append("accepted_content_lockfile_report must include a locked entry for candidate_pack_id")
    return report


def build_report(review_path: Path, repo_root: Path) -> dict[str, Any]:
    payload = load_json_object(review_path)
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(payload.get("review_version"), int) or payload["review_version"] <= 0:
        errors.append("review_version must be a positive integer")
    if payload.get("review_type") != EXPECTED_REVIEW_TYPE:
        errors.append(f"review_type must be `{EXPECTED_REVIEW_TYPE}`")
    for field in ("candidate_pack_id", "reviewer", "reviewed_at", "summary"):
        if not is_nonempty_string(payload.get(field)):
            errors.append(f"{field} must be non-empty")
        elif has_placeholder(payload.get(field)):
            errors.append(f"{field} must not contain TODO or placeholder markers")

    decision = payload.get("decision")
    if decision not in ALLOWED_DECISIONS:
        errors.append(f"decision must be one of {', '.join(sorted(ALLOWED_DECISIONS))}")
    validate_checks(payload, decision, errors)

    observations = string_list(payload.get("concrete_observations"))
    unresolved = string_list(payload.get("unresolved_issues"))
    if len(observations) < 2:
        errors.append("concrete_observations must contain at least two concrete items")
    if has_placeholder(payload.get("concrete_observations")):
        errors.append("concrete_observations must not contain TODO or placeholder markers")
    if has_placeholder(payload.get("unresolved_issues")):
        errors.append("unresolved_issues must not contain TODO or placeholder markers")
    if decision == PASS_DECISION and unresolved:
        errors.append("accepted_content requires unresolved_issues to be empty")
    if decision in ALLOWED_DECISIONS and decision != PASS_DECISION and not unresolved:
        errors.append(f"{decision} requires at least one unresolved_issues item")

    simulation_manifest_path = require_existing_repo_path(
        payload.get("source_simulation_candidate_manifest"),
        "source_simulation_candidate_manifest",
        repo_root,
        errors,
    )
    lockfile_report_path = require_existing_repo_path(
        payload.get("accepted_content_lockfile_report"),
        "accepted_content_lockfile_report",
        repo_root,
        errors,
    )
    simulation_report = validate_simulation_candidate_manifest(simulation_manifest_path, repo_root, payload, errors)
    lockfile_report = validate_lockfile_report(lockfile_report_path, payload.get("candidate_pack_id"), errors)

    return {
        "report_version": 1,
        "source": relative_repo_path(repo_root, review_path),
        "repo_root": str(repo_root),
        "decision": "content_final_acceptance_valid" if not errors else "content_final_acceptance_invalid",
        "review_type": payload.get("review_type"),
        "candidate_pack_id": payload.get("candidate_pack_id"),
        "gate_decision": decision,
        "simulation_candidate_manifest_decision": simulation_report["decision"] if simulation_report is not None else None,
        "accepted_content_lockfile_decision": lockfile_report.get("decision") if lockfile_report is not None else None,
        "observation_count": len(observations),
        "unresolved_issue_count": len(unresolved),
        "errors": errors,
        "warnings": warnings,
        "limitations": [
            "This validator checks final content acceptance record completeness only.",
            "It does not run Harness simulation, copy candidate content, compute content hashes, or approve release readiness.",
            "Accepted content still needs release candidate, package, privacy, playtest, and Runtime smoke gates before release.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Content Final Acceptance Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Decision: `{report['decision']}`",
        f"- Candidate: `{report['candidate_pack_id']}`",
        f"- Gate decision: `{report['gate_decision']}`",
        f"- Simulation candidate manifest: `{report['simulation_candidate_manifest_decision']}`",
        f"- Accepted content lockfile: `{report['accepted_content_lockfile_decision']}`",
        f"- Observations: {report['observation_count']}",
        f"- Unresolved issues: {report['unresolved_issue_count']}",
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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm final content acceptance records.")
    parser.add_argument("review", type=Path, help="Final content acceptance JSON")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown report")
    args = parser.parse_args()

    report = build_report(args.review, args.repo_root)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "content_final_acceptance_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
