#!/usr/bin/env python3
"""Validate final human story/codex acceptance records.

This gate checks that final acceptance only happens after a valid Runtime UI
review and that the acceptance does not claim Runtime integration or release
readiness. It does not copy candidate text into accepted content or approve a
release candidate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from validate_story_codex_runtime_ui_review import build_report as build_runtime_ui_review_report


EXPECTED_REVIEW_TYPE = "story_codex_final_acceptance"
ALLOWED_DECISIONS = {"accepted_content", "needs_more_review", "repair", "reject"}
PASS_DECISION = "accepted_content"
REQUIRED_CHECKS = {
    "accepts_story_codex_text": True,
    "accepted_content_only_after_reviews": True,
    "release_ready": False,
    "runtime_integrated": False,
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


def validate_checks(payload: dict[str, Any], decision: Any, errors: list[str]) -> dict[str, Any]:
    checks = payload.get("checks")
    if not isinstance(checks, dict):
        errors.append("checks must be an object")
        checks = {}
    for field, expected in REQUIRED_CHECKS.items():
        if checks.get(field) is not expected:
            errors.append(f"checks.{field} must be {json.dumps(expected)}")
    if decision == PASS_DECISION and any(checks.get(field) is not expected for field, expected in REQUIRED_CHECKS.items()):
        errors.append("accepted_content requires every required check to match")
    return checks


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
    if decision != PASS_DECISION and not unresolved:
        errors.append(f"{decision} requires at least one unresolved_issues item")

    runtime_ui_review_path = require_existing_repo_path(
        payload.get("runtime_ui_review_file"),
        "runtime_ui_review_file",
        repo_root,
        errors,
    )
    runtime_ui_review_decision = None
    source_ui_manifest = None
    if runtime_ui_review_path is not None:
        runtime_report = build_runtime_ui_review_report(runtime_ui_review_path, repo_root)
        runtime_ui_review_decision = runtime_report["decision"]
        if runtime_ui_review_decision != "story_codex_runtime_ui_review_valid":
            errors.append("runtime_ui_review_file must validate")
        if runtime_report.get("gate_decision") != "runtime_ui_review_pass":
            errors.append("runtime_ui_review_file gate_decision must be runtime_ui_review_pass")
        if runtime_report.get("candidate_pack_id") != payload.get("candidate_pack_id"):
            errors.append("candidate_pack_id must match runtime_ui_review_file")
        runtime_payload = load_json_object(runtime_ui_review_path)
        source_ui_manifest = runtime_payload.get("source_ui_candidate_manifest")

    source_value = payload.get("source_ui_candidate_manifest")
    if not is_nonempty_string(source_value):
        errors.append("source_ui_candidate_manifest must be non-empty")
    elif has_placeholder(source_value):
        errors.append("source_ui_candidate_manifest must not contain TODO or placeholder markers")
    elif source_ui_manifest is not None and source_value != source_ui_manifest:
        errors.append("source_ui_candidate_manifest must match runtime_ui_review_file")

    return {
        "report_version": 1,
        "source": relative_repo_path(repo_root, review_path),
        "repo_root": str(repo_root),
        "decision": "story_codex_final_acceptance_valid" if not errors else "story_codex_final_acceptance_invalid",
        "review_type": payload.get("review_type"),
        "candidate_pack_id": payload.get("candidate_pack_id"),
        "gate_decision": decision,
        "runtime_ui_review_decision": runtime_ui_review_decision,
        "observation_count": len(observations),
        "unresolved_issue_count": len(unresolved),
        "errors": errors,
        "warnings": warnings,
        "limitations": [
            "This validator checks final story/codex acceptance record completeness only.",
            "It does not copy candidate text, integrate Runtime UI, or approve release readiness.",
            "Accepted story/codex text still needs package, privacy, playtest, and Runtime smoke gates before release.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Story Codex Final Acceptance Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Decision: `{report['decision']}`",
        f"- Candidate: `{report['candidate_pack_id']}`",
        f"- Gate decision: `{report['gate_decision']}`",
        f"- Runtime UI review: `{report['runtime_ui_review_decision']}`",
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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm story/codex final acceptance records.")
    parser.add_argument("review", type=Path, help="Story/codex final acceptance JSON")
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
    return 0 if report["decision"] == "story_codex_final_acceptance_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
