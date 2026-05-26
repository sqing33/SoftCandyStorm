#!/usr/bin/env python3
"""Validate content simulation-candidate manifests.

This gate checks manifests produced after a human `simulate_candidate` design
review. It does not run Schema, static budget, Bot simulation, Replay, or
playtest gates, and it never accepts content into accepted_content.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from validate_content_candidate_design_review import (
    TYPE_TO_CATEGORY,
    build_report as build_design_review_report,
    load_json_object,
)


EXPECTED_CONTRACT_ID = "content-simulation-candidate-manifest-v0"
EXPECTED_STAGE = "content_simulation_candidate"
TODO_MARKERS = ("TODO", "<", ">")
REQUIRED_PROJECT_RULES = {
    "candidate_only": True,
    "accepted_content": False,
    "runtime_integrated": False,
}
REQUIRED_RULES = {
    "accepted_content": False,
    "runtime_integrated": False,
    "validated_candidates_written": False,
    "simulated_candidates_written": False,
    "playtest_candidate": False,
    "release_ready": False,
    "requires_schema_validation": True,
    "requires_static_budget": True,
    "requires_bot_simulation": True,
    "requires_replay_regression": True,
    "requires_manual_playtest": True,
    "requires_final_human_acceptance": True,
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


def is_inside(base_dir: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(base_dir.resolve())
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
    if not is_inside(repo_root, path):
        errors.append(f"{field} must stay inside repository: {value}")
        return None
    if not path.exists():
        errors.append(f"{field} does not exist: {value}")
        return None
    return path


def validate_project_rules(label: str, rules: Any, errors: list[str]) -> None:
    if not isinstance(rules, dict):
        errors.append(f"{label} project_rules must be an object")
        return
    for field, expected in REQUIRED_PROJECT_RULES.items():
        if rules.get(field) is not expected:
            errors.append(f"{label} project_rules.{field} must be {json.dumps(expected)}")


def validate_top_level(payload: dict[str, Any], errors: list[str]) -> None:
    if not isinstance(payload.get("manifest_version"), int) or payload["manifest_version"] <= 0:
        errors.append("manifest_version must be a positive integer")
    expected_strings = {
        "manifest_contract_id": EXPECTED_CONTRACT_ID,
        "stage": EXPECTED_STAGE,
        "manual_gate_decision": "simulate_candidate",
    }
    for field, expected in expected_strings.items():
        if payload.get(field) != expected:
            errors.append(f"{field} must be `{expected}`")
    for field in ("candidate_pack_id", "promoted_at"):
        if not is_nonempty_string(payload.get(field)):
            errors.append(f"{field} must be non-empty")
        elif has_placeholder(payload.get(field)):
            errors.append(f"{field} must not contain TODO or placeholder markers")


def validate_rules(payload: dict[str, Any], errors: list[str]) -> None:
    rules = payload.get("rules")
    if not isinstance(rules, dict):
        errors.append("rules must be an object")
        return
    for field, expected in REQUIRED_RULES.items():
        if rules.get(field) is not expected:
            errors.append(f"rules.{field} must be {json.dumps(expected)}")


def content_path_for_entry(candidate_pack: Path, entry: dict[str, Any]) -> Path:
    entry_path = entry.get("path")
    if is_nonempty_string(entry_path):
        return candidate_pack / str(entry_path)
    content_type = entry.get("type")
    content_id = entry.get("id")
    category = TYPE_TO_CATEGORY.get(str(content_type))
    if category is None or not is_nonempty_string(content_id):
        return candidate_pack / "__missing__"
    return candidate_pack / category / f"{content_id}.json"


def validate_source_candidate(
    candidate_dir: Path | None,
    source_patch_manifest: Path | None,
    payload: dict[str, Any],
    errors: list[str],
) -> dict[str, dict[str, Any]]:
    if candidate_dir is None:
        return {}
    if payload.get("candidate_pack_id") != candidate_dir.name:
        errors.append("candidate_pack_id must match source_candidate_pack directory name")

    manifest_path = candidate_dir / "metadata" / "manifest.json"
    if not manifest_path.exists():
        errors.append("source_candidate_pack missing metadata/manifest.json")
    else:
        try:
            manifest = load_json_object(manifest_path)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            errors.append(f"source candidate manifest is invalid: {error}")
        else:
            if manifest.get("candidate_kind") != "full_content_pack":
                errors.append("source candidate manifest candidate_kind must be full_content_pack")
            manifest_batch_id = manifest.get("batch_id")
            if is_nonempty_string(manifest_batch_id) and manifest_batch_id != candidate_dir.name:
                errors.append("source candidate manifest batch_id must match source_candidate_pack directory name")
            validate_project_rules("source candidate manifest", manifest.get("project_rules"), errors)

    if source_patch_manifest is None:
        return {}
    try:
        source_manifest = load_json_object(source_patch_manifest)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"source_patch_manifest is invalid: {error}")
        return {}
    validate_project_rules("source_patch_manifest", source_manifest.get("project_rules"), errors)

    contents = source_manifest.get("contents")
    if not isinstance(contents, list) or not contents:
        errors.append("source_patch_manifest.contents must be a non-empty list")
        return {}

    content_index: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(contents):
        if not isinstance(entry, dict):
            errors.append(f"source_patch_manifest.contents[{index}] must be an object")
            continue
        content_id = entry.get("id")
        content_type = entry.get("type")
        if not is_nonempty_string(content_id):
            errors.append(f"source_patch_manifest.contents[{index}] missing id")
            continue
        if not is_nonempty_string(content_type) or str(content_type) not in TYPE_TO_CATEGORY:
            errors.append(f"{content_id}: source_patch_manifest type is unsupported")
            continue
        if str(content_id) in content_index:
            errors.append(f"source_patch_manifest duplicate content id `{content_id}`")
            continue
        content_file = content_path_for_entry(candidate_dir, entry)
        if not content_file.exists():
            errors.append(f"{content_id}: source candidate missing content file {content_file}")
        content_index[str(content_id)] = {
            "id": str(content_id),
            "type": str(content_type),
            "path": relative_repo_path(candidate_dir, content_file),
        }
    return content_index


def validate_design_review(
    review_path: Path | None,
    repo_root: Path,
    payload: dict[str, Any],
    errors: list[str],
) -> dict[str, Any] | None:
    if review_path is None:
        return None
    report = build_design_review_report(review_path, repo_root)
    if report["decision"] != "content_candidate_design_review_valid":
        errors.append("manual_design_review_file must validate")
    if report.get("gate_decision") != "simulate_candidate":
        errors.append("manual_design_review_file gate_decision must be simulate_candidate")
    if report.get("content_review_count") != payload.get("content_count"):
        errors.append("content_count must match design review content count")
    return report


def validate_content_path(root_dir: Path, content_path: str, label: str, errors: list[str]) -> None:
    path = Path(content_path)
    if path.is_absolute():
        errors.append(f"{label} path must be relative to the candidate directory")
        return
    resolved = root_dir / path
    if not is_inside(root_dir, resolved):
        errors.append(f"{label} path must stay inside the candidate directory: {content_path}")
    elif not resolved.exists():
        errors.append(f"{label} path does not exist: {content_path}")


def validate_contents(
    payload: dict[str, Any],
    staged_dir: Path,
    source_dir: Path | None,
    source_index: dict[str, dict[str, Any]],
    errors: list[str],
) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    contents = payload.get("contents")
    if not isinstance(contents, list) or not contents:
        errors.append("contents must be a non-empty list")
        return reports
    if payload.get("content_count") != len(contents):
        errors.append("content_count must match contents length")
    if source_index and payload.get("content_count") != len(source_index):
        errors.append("content_count must match source_patch_manifest contents length")

    seen: set[str] = set()
    for index, entry in enumerate(contents):
        label = f"contents[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{label} must be an object")
            continue
        content_id = entry.get("id")
        if not is_nonempty_string(content_id):
            errors.append(f"{label}.id must be non-empty")
            continue
        display_id = str(content_id)
        if has_placeholder(display_id):
            errors.append(f"{display_id}: id must not contain TODO or placeholder markers")
        if display_id in seen:
            errors.append(f"{display_id}: duplicate content id")
        seen.add(display_id)

        source_entry = source_index.get(display_id)
        if source_index and source_entry is None:
            errors.append(f"{display_id}: id does not exist in source_patch_manifest.contents")
            source_entry = {}
        elif source_entry is None:
            source_entry = {}

        for field in ("type", "path"):
            value = entry.get(field)
            if not is_nonempty_string(value):
                errors.append(f"{display_id}: {field} must be non-empty")
            elif has_placeholder(value):
                errors.append(f"{display_id}: {field} must not contain TODO or placeholder markers")
            if source_entry and value != source_entry.get(field):
                errors.append(f"{display_id}: {field} must match source_patch_manifest")

        content_path = entry.get("path")
        if is_nonempty_string(content_path):
            validate_content_path(staged_dir, str(content_path), display_id, errors)
            if source_dir is not None:
                validate_content_path(source_dir, str(content_path), f"{display_id} source", errors)

        reports.append(
            {
                "id": display_id,
                "type": entry.get("type"),
            }
        )

    missing_ids = sorted(set(source_index) - seen)
    if missing_ids:
        errors.append(f"contents missing source_patch_manifest ids: {', '.join(missing_ids)}")
    return reports


def build_report(manifest_path: Path, repo_root: Path) -> dict[str, Any]:
    payload = load_json_object(manifest_path)
    errors: list[str] = []
    warnings: list[str] = []

    validate_top_level(payload, errors)
    validate_rules(payload, errors)
    source_candidate_dir = require_existing_repo_path(payload, "source_candidate_pack", repo_root, errors)
    source_patch_manifest = require_existing_repo_path(payload, "source_patch_manifest", repo_root, errors)
    design_review_path = require_existing_repo_path(payload, "manual_design_review_file", repo_root, errors)
    preflight_report_path = require_existing_repo_path(payload, "candidate_preflight_report", repo_root, errors)

    source_index = validate_source_candidate(source_candidate_dir, source_patch_manifest, payload, errors)
    design_review_report = validate_design_review(design_review_path, repo_root, payload, errors)
    content_reports = validate_contents(payload, manifest_path.parent, source_candidate_dir, source_index, errors)

    return {
        "report_version": 1,
        "source": relative_repo_path(repo_root, manifest_path),
        "repo_root": str(repo_root),
        "decision": "content_simulation_candidate_manifest_valid" if not errors else "content_simulation_candidate_manifest_invalid",
        "candidate_pack_id": payload.get("candidate_pack_id"),
        "content_count": payload.get("content_count"),
        "validated_content_count": len(content_reports),
        "candidate_preflight_report": relative_repo_path(repo_root, preflight_report_path)
        if preflight_report_path is not None
        else None,
        "design_review_decision": design_review_report["decision"] if design_review_report is not None else None,
        "manual_gate_decision": design_review_report["gate_decision"] if design_review_report is not None else None,
        "errors": errors,
        "warnings": warnings,
        "contents": content_reports,
        "limitations": [
            "This validator checks simulation-candidate manifest completeness only.",
            "A valid simulation-candidate manifest does not run Schema, budget, Bot, Replay, or playtest gates.",
            "A valid simulation-candidate manifest does not promote content into accepted_content or Runtime.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Content Simulation Candidate Manifest Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Decision: `{report['decision']}`",
        f"- Candidate: `{report['candidate_pack_id']}`",
        f"- Contents: {report['validated_content_count']} / {report['content_count']}",
        f"- Design review: `{report['design_review_decision']}` / `{report['manual_gate_decision']}`",
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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm content simulation candidate manifests.")
    parser.add_argument("manifest", type=Path, help="Content simulation candidate manifest JSON")
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
    return 0 if report["decision"] == "content_simulation_candidate_manifest_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
