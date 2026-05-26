#!/usr/bin/env python3
"""Validate story/codex final acceptance manifests.

This gate is intentionally evidence-only. It checks that a story/codex pack has
already passed UI-candidate staging, Runtime UI review, and final human
acceptance before it can be treated as accepted story/codex content. It never
copies candidate text into Runtime and it never marks release readiness.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from validate_story_codex_ui_candidate_manifest import (
    build_report as build_ui_candidate_manifest_report,
    load_json_object,
)
from validate_story_codex_runtime_ui_review import build_report as build_runtime_ui_review_report
from validate_story_codex_final_acceptance import build_report as build_final_acceptance_report


EXPECTED_CONTRACT_ID = "story-codex-acceptance-manifest-v0"
EXPECTED_STAGE = "story_codex_acceptance"
TODO_MARKERS = ("TODO", "<", ">")
REQUIRED_RULES = {
    "accepted_content": True,
    "runtime_integrated": False,
    "release_ready": False,
    "requires_ui_candidate_manifest": True,
    "requires_runtime_ui_review": True,
    "requires_final_human_acceptance": True,
    "generated_candidate_direct_acceptance_allowed": False,
}


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


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


def validate_top_level(payload: dict[str, Any], errors: list[str]) -> None:
    if not isinstance(payload.get("manifest_version"), int) or payload["manifest_version"] <= 0:
        errors.append("manifest_version must be a positive integer")
    expected_strings = {
        "manifest_contract_id": EXPECTED_CONTRACT_ID,
        "stage": EXPECTED_STAGE,
    }
    for field, expected in expected_strings.items():
        if payload.get(field) != expected:
            errors.append(f"{field} must be `{expected}`")
    for field in ("candidate_pack_id", "accepted_at"):
        if not is_nonempty_string(payload.get(field)):
            errors.append(f"{field} must be non-empty")
        elif has_placeholder(payload.get(field)):
            errors.append(f"{field} must not contain TODO or placeholder markers")
    for field in ("chapter_count", "codex_entry_count"):
        if not isinstance(payload.get(field), int) or payload[field] <= 0:
            errors.append(f"{field} must be a positive integer")


def validate_rules(payload: dict[str, Any], errors: list[str]) -> None:
    rules = payload.get("rules")
    if not isinstance(rules, dict):
        errors.append("rules must be an object")
        return
    for field, expected in REQUIRED_RULES.items():
        if rules.get(field) is not expected:
            errors.append(f"rules.{field} must be {json.dumps(expected)}")


def validate_ui_candidate_manifest(
    path: Path | None,
    repo_root: Path,
    payload: dict[str, Any],
    errors: list[str],
) -> dict[str, Any] | None:
    if path is None:
        return None
    report = build_ui_candidate_manifest_report(path, repo_root)
    if report["decision"] != "story_codex_ui_candidate_manifest_valid":
        errors.append("source_ui_candidate_manifest must validate")
    if report.get("candidate_pack_id") != payload.get("candidate_pack_id"):
        errors.append("candidate_pack_id must match source_ui_candidate_manifest")
    if report.get("chapter_count") != payload.get("chapter_count"):
        errors.append("chapter_count must match source_ui_candidate_manifest")
    if report.get("codex_entry_count") != payload.get("codex_entry_count"):
        errors.append("codex_entry_count must match source_ui_candidate_manifest")
    if report.get("manual_gate_decision") != "ui_candidate":
        errors.append("source_ui_candidate_manifest manual_gate_decision must be ui_candidate")
    return report


def validate_runtime_ui_review_file(
    path: Path | None,
    repo_root: Path,
    manifest_payload: dict[str, Any],
    errors: list[str],
) -> dict[str, Any] | None:
    if path is None:
        return None
    try:
        report = build_runtime_ui_review_report(path, repo_root)
        payload = load_json_object(path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"runtime_ui_review_file is invalid JSON: {error}")
        return None

    if report["decision"] != "story_codex_runtime_ui_review_valid":
        errors.append("runtime_ui_review_file must validate")
    if report.get("gate_decision") != "runtime_ui_review_pass":
        errors.append("runtime_ui_review_file.decision must be `runtime_ui_review_pass`")
    if payload.get("candidate_pack_id") != manifest_payload.get("candidate_pack_id"):
        errors.append("runtime_ui_review_file.candidate_pack_id must match acceptance manifest")
    if payload.get("source_ui_candidate_manifest") != manifest_payload.get("source_ui_candidate_manifest"):
        errors.append("runtime_ui_review_file.source_ui_candidate_manifest must match acceptance manifest")

    return {"report": report, "payload": payload}


def validate_final_acceptance_file(
    path: Path | None,
    repo_root: Path,
    manifest_payload: dict[str, Any],
    errors: list[str],
) -> dict[str, Any] | None:
    if path is None:
        return None
    try:
        report = build_final_acceptance_report(path, repo_root)
        payload = load_json_object(path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"final_human_acceptance_file is invalid JSON: {error}")
        return None

    if report["decision"] != "story_codex_final_acceptance_valid":
        errors.append("final_human_acceptance_file must validate")
    if report.get("gate_decision") != "accepted_content":
        errors.append("final_human_acceptance_file.decision must be `accepted_content`")
    if payload.get("candidate_pack_id") != manifest_payload.get("candidate_pack_id"):
        errors.append("final_human_acceptance_file.candidate_pack_id must match acceptance manifest")
    if payload.get("source_ui_candidate_manifest") != manifest_payload.get("source_ui_candidate_manifest"):
        errors.append("final_human_acceptance_file.source_ui_candidate_manifest must match acceptance manifest")
    if payload.get("runtime_ui_review_file") != manifest_payload.get("runtime_ui_review_file"):
        errors.append("final_human_acceptance_file.runtime_ui_review_file must match acceptance manifest")

    return {"report": report, "payload": payload}


def build_report(manifest_path: Path, repo_root: Path) -> dict[str, Any]:
    payload = load_json_object(manifest_path)
    errors: list[str] = []
    warnings: list[str] = []

    validate_top_level(payload, errors)
    validate_rules(payload, errors)
    ui_manifest_path = require_existing_repo_path(payload, "source_ui_candidate_manifest", repo_root, errors)
    runtime_ui_review_path = require_existing_repo_path(payload, "runtime_ui_review_file", repo_root, errors)
    final_acceptance_path = require_existing_repo_path(payload, "final_human_acceptance_file", repo_root, errors)

    ui_report = validate_ui_candidate_manifest(ui_manifest_path, repo_root, payload, errors)
    runtime_ui_review = validate_runtime_ui_review_file(
        runtime_ui_review_path,
        repo_root,
        payload,
        errors,
    )
    final_acceptance = validate_final_acceptance_file(
        final_acceptance_path,
        repo_root,
        payload,
        errors,
    )

    runtime_ui_review_report = runtime_ui_review["report"] if runtime_ui_review is not None else None
    final_acceptance_report = final_acceptance["report"] if final_acceptance is not None else None

    return {
        "report_version": 1,
        "source": relative_repo_path(repo_root, manifest_path),
        "repo_root": str(repo_root),
        "decision": "story_codex_acceptance_manifest_valid" if not errors else "story_codex_acceptance_manifest_invalid",
        "candidate_pack_id": payload.get("candidate_pack_id"),
        "chapter_count": payload.get("chapter_count"),
        "codex_entry_count": payload.get("codex_entry_count"),
        "ui_candidate_manifest_decision": ui_report["decision"] if ui_report is not None else None,
        "runtime_ui_review_report_decision": runtime_ui_review_report["decision"]
        if runtime_ui_review_report is not None
        else None,
        "runtime_ui_review_decision": runtime_ui_review_report["gate_decision"]
        if runtime_ui_review_report is not None
        else None,
        "final_acceptance_report_decision": final_acceptance_report["decision"]
        if final_acceptance_report is not None
        else None,
        "final_acceptance_decision": final_acceptance_report["gate_decision"]
        if final_acceptance_report is not None
        else None,
        "errors": errors,
        "warnings": warnings,
        "limitations": [
            "This validator checks final story/codex acceptance evidence only.",
            "A valid acceptance manifest may mark story/codex text accepted, but it does not prove Runtime integration.",
            "A valid acceptance manifest is not release readiness and cannot bypass future packaging, privacy, playtest, or Runtime smoke gates.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Story Codex Acceptance Manifest Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Decision: `{report['decision']}`",
        f"- Candidate: `{report['candidate_pack_id']}`",
        f"- Chapters: {report['chapter_count']}",
        f"- Codex entries: {report['codex_entry_count']}",
        f"- UI candidate manifest: `{report['ui_candidate_manifest_decision']}`",
        f"- Runtime UI review: `{report['runtime_ui_review_decision']}`",
        f"- Final acceptance: `{report['final_acceptance_decision']}`",
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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm story/codex final acceptance manifests.")
    parser.add_argument("manifest", type=Path, help="Story/codex final acceptance manifest JSON")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown report")
    args = parser.parse_args()

    report = build_report(args.manifest, args.repo_root)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "story_codex_acceptance_manifest_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
