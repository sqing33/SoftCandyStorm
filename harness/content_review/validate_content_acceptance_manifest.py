#!/usr/bin/env python3
"""Validate final content acceptance manifests.

This gate verifies that a generated full content pack has passed simulation
candidate staging, final human content acceptance, and accepted-content
lockfile validation before it can be treated as accepted content evidence. It
does not copy content into Runtime, mark release readiness, or run simulations.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from validate_content_simulation_candidate_manifest import (
    build_report as build_simulation_candidate_report,
    load_json_object,
)
from validate_content_final_acceptance import build_report as build_final_acceptance_report


EXPECTED_CONTRACT_ID = "content-acceptance-manifest-v0"
EXPECTED_STAGE = "content_acceptance"
TODO_MARKERS = ("TODO", "<", ">")
REQUIRED_RULES = {
    "accepted_content": True,
    "runtime_integrated": False,
    "release_ready": False,
    "requires_simulation_candidate_manifest": True,
    "requires_final_human_acceptance": True,
    "requires_accepted_content_lockfile": True,
    "generated_candidate_direct_acceptance_allowed": False,
}
FORBIDDEN_ACCEPTED_USES = {"runtime_integrated", "release_ready"}


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
    if not isinstance(payload.get("content_count"), int) or payload["content_count"] <= 0:
        errors.append("content_count must be a positive integer")


def validate_rules(payload: dict[str, Any], errors: list[str]) -> None:
    rules = payload.get("rules")
    if not isinstance(rules, dict):
        errors.append("rules must be an object")
        return
    for field, expected in REQUIRED_RULES.items():
        if rules.get(field) is not expected:
            errors.append(f"rules.{field} must be {json.dumps(expected)}")


def validate_simulation_candidate_manifest(
    path: Path | None,
    repo_root: Path,
    payload: dict[str, Any],
    errors: list[str],
) -> tuple[dict[str, Any] | None, dict[str, dict[str, Any]]]:
    if path is None:
        return None, {}
    simulation_payload = load_json_object(path)
    report = build_simulation_candidate_report(path, repo_root)
    if report["decision"] != "content_simulation_candidate_manifest_valid":
        errors.append("source_simulation_candidate_manifest must validate")
    if report.get("candidate_pack_id") != payload.get("candidate_pack_id"):
        errors.append("candidate_pack_id must match source_simulation_candidate_manifest")
    if report.get("content_count") != payload.get("content_count"):
        errors.append("content_count must match source_simulation_candidate_manifest")
    if report.get("manual_gate_decision") != "simulate_candidate":
        errors.append("source_simulation_candidate_manifest manual_gate_decision must be simulate_candidate")
    contents = {
        str(item["id"]): item
        for item in simulation_payload.get("contents", [])
        if isinstance(item, dict) and is_nonempty_string(item.get("id"))
    }
    return report, contents


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

    if report["decision"] != "content_final_acceptance_valid":
        errors.append("final_human_acceptance_file must validate")
    if report.get("gate_decision") != "accepted_content":
        errors.append("final_human_acceptance_file.decision must be `accepted_content`")
    if payload.get("candidate_pack_id") != manifest_payload.get("candidate_pack_id"):
        errors.append("final_human_acceptance_file.candidate_pack_id must match acceptance manifest")
    if payload.get("source_simulation_candidate_manifest") != manifest_payload.get("source_simulation_candidate_manifest"):
        errors.append("final_human_acceptance_file.source_simulation_candidate_manifest must match acceptance manifest")
    if payload.get("accepted_content_lockfile_report") != manifest_payload.get("accepted_content_lockfile_report"):
        errors.append("final_human_acceptance_file.accepted_content_lockfile_report must match acceptance manifest")
    return report


def validate_lockfile_report(
    path: Path | None,
    payload: dict[str, Any],
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
    if report.get("locked_count") != payload.get("content_pack_count", 1):
        errors.append("accepted_content_lockfile_report locked_count must match content_pack_count")
    entries = report.get("entries")
    if not isinstance(entries, list) or not entries:
        errors.append("accepted_content_lockfile_report entries must be non-empty")
        entries = []
    matching_entries = [
        entry
        for entry in entries
        if isinstance(entry, dict)
        and entry.get("id") == payload.get("candidate_pack_id")
        and entry.get("status") == "locked"
    ]
    if not matching_entries:
        errors.append("accepted_content_lockfile_report must include a locked entry for candidate_pack_id")
    return report


def validate_accepted_contents(
    payload: dict[str, Any],
    source_contents: dict[str, dict[str, Any]],
    errors: list[str],
) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    contents = payload.get("accepted_contents")
    if not isinstance(contents, list) or not contents:
        errors.append("accepted_contents must be a non-empty list")
        return reports
    if payload.get("content_count") != len(contents):
        errors.append("content_count must match accepted_contents length")

    seen: set[str] = set()
    for index, content in enumerate(contents):
        label = f"accepted_contents[{index}]"
        if not isinstance(content, dict):
            errors.append(f"{label} must be an object")
            continue
        content_id = content.get("id")
        display_id = str(content_id) if is_nonempty_string(content_id) else label
        if not is_nonempty_string(content_id):
            errors.append(f"{label}.id must be non-empty")
            continue
        if has_placeholder(display_id):
            errors.append(f"{display_id}: id must not contain TODO or placeholder markers")
        if display_id in seen:
            errors.append(f"{display_id}: duplicate accepted content id")
        seen.add(display_id)

        source_content = source_contents.get(display_id)
        if source_contents and source_content is None:
            errors.append(f"{display_id}: id does not exist in source simulation candidate manifest")
            source_content = {}
        elif source_content is None:
            source_content = {}

        accepted_use = content.get("accepted_use")
        if not is_nonempty_string(accepted_use):
            errors.append(f"{display_id}: accepted_use must be non-empty")
        elif has_placeholder(accepted_use):
            errors.append(f"{display_id}: accepted_use must not contain TODO or placeholder markers")
        elif accepted_use in FORBIDDEN_ACCEPTED_USES:
            errors.append(f"{display_id}: accepted_use must not claim {accepted_use}")

        for field in ("type", "path"):
            value = content.get(field)
            if not is_nonempty_string(value):
                errors.append(f"{display_id}: {field} must be non-empty")
            elif has_placeholder(value):
                errors.append(f"{display_id}: {field} must not contain TODO or placeholder markers")
            if source_content and value != source_content.get(field):
                errors.append(f"{display_id}: {field} must match source simulation candidate manifest")

        reports.append(
            {
                "id": display_id,
                "type": content.get("type"),
                "accepted_use": content.get("accepted_use"),
            }
        )

    missing_ids = sorted(set(source_contents) - seen)
    if missing_ids:
        errors.append(f"accepted_contents missing source simulation candidate ids: {', '.join(missing_ids)}")
    return reports


def build_report(manifest_path: Path, repo_root: Path) -> dict[str, Any]:
    payload = load_json_object(manifest_path)
    errors: list[str] = []
    warnings: list[str] = []

    validate_top_level(payload, errors)
    validate_rules(payload, errors)
    simulation_manifest_path = require_existing_repo_path(payload, "source_simulation_candidate_manifest", repo_root, errors)
    final_acceptance_path = require_existing_repo_path(payload, "final_human_acceptance_file", repo_root, errors)
    lockfile_report_path = require_existing_repo_path(payload, "accepted_content_lockfile_report", repo_root, errors)

    simulation_report, source_contents = validate_simulation_candidate_manifest(
        simulation_manifest_path,
        repo_root,
        payload,
        errors,
    )
    final_acceptance_report = validate_final_acceptance_file(
        final_acceptance_path,
        repo_root,
        payload,
        errors,
    )
    lockfile_report = validate_lockfile_report(lockfile_report_path, payload, errors)
    accepted_content_reports = validate_accepted_contents(payload, source_contents, errors)

    return {
        "report_version": 1,
        "source": relative_repo_path(repo_root, manifest_path),
        "repo_root": str(repo_root),
        "decision": "content_acceptance_manifest_valid" if not errors else "content_acceptance_manifest_invalid",
        "candidate_pack_id": payload.get("candidate_pack_id"),
        "content_count": payload.get("content_count"),
        "validated_content_count": len(accepted_content_reports),
        "simulation_candidate_manifest_decision": simulation_report["decision"] if simulation_report is not None else None,
        "final_acceptance_report_decision": final_acceptance_report["decision"]
        if final_acceptance_report is not None
        else None,
        "final_acceptance_decision": final_acceptance_report["gate_decision"]
        if final_acceptance_report is not None
        else None,
        "accepted_content_lockfile_decision": lockfile_report.get("decision") if lockfile_report is not None else None,
        "errors": errors,
        "warnings": warnings,
        "accepted_contents": accepted_content_reports,
        "limitations": [
            "This validator checks final content acceptance evidence only.",
            "A valid acceptance manifest may mark content accepted, but it does not prove Runtime integration.",
            "A valid acceptance manifest is not release readiness and cannot bypass future package, privacy, playtest, or Runtime smoke gates.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Content Acceptance Manifest Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Decision: `{report['decision']}`",
        f"- Candidate: `{report['candidate_pack_id']}`",
        f"- Contents: {report['validated_content_count']} / {report['content_count']}",
        f"- Simulation candidate manifest: `{report['simulation_candidate_manifest_decision']}`",
        f"- Final acceptance: `{report['final_acceptance_report_decision']}` / `{report['final_acceptance_decision']}`",
        f"- Accepted content lockfile: `{report['accepted_content_lockfile_decision']}`",
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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm final content acceptance manifests.")
    parser.add_argument("manifest", type=Path, help="Final content acceptance manifest JSON")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown summary")
    args = parser.parse_args()

    report = build_report(args.manifest, args.repo_root)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "content_acceptance_manifest_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
