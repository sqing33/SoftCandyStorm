#!/usr/bin/env python3
"""Validate story/codex UI candidate manifests.

This gate checks manifests produced after a human `ui_candidate` review. It
never accepts generated content into accepted_content and never proves Runtime
integration.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from validate_story_codex_manual_review import build_report as build_manual_review_report


EXPECTED_CONTRACT_ID = "story-codex-ui-candidate-manifest-v0"
EXPECTED_STAGE = "story_codex_ui_candidate"
TODO_MARKERS = ("TODO", "<", ">")
REQUIRED_RULES = {
    "accepted_content": False,
    "runtime_integrated": False,
    "requires_runtime_ui_review": True,
    "requires_final_human_acceptance": True,
}


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


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


def count_json_items(directory: Path, subdir: str, errors: list[str]) -> int:
    path = directory / subdir
    if not path.exists():
        errors.append(f"candidate directory missing `{subdir}`")
        return 0
    count = 0
    for item_path in sorted(path.glob("*.json")):
        try:
            payload = load_json_object(item_path)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            errors.append(f"{subdir}/{item_path.name} is invalid JSON: {error}")
            continue
        if not is_nonempty_string(payload.get("id")):
            errors.append(f"{subdir}/{item_path.name} missing non-empty id")
        count += 1
    return count


def validate_top_level(payload: dict[str, Any], errors: list[str]) -> None:
    if not isinstance(payload.get("manifest_version"), int) or payload["manifest_version"] <= 0:
        errors.append("manifest_version must be a positive integer")
    expected_strings = {
        "manifest_contract_id": EXPECTED_CONTRACT_ID,
        "stage": EXPECTED_STAGE,
        "manual_gate_decision": "ui_candidate",
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


def validate_source_candidate(candidate_dir: Path | None, payload: dict[str, Any], errors: list[str]) -> tuple[int, int]:
    if candidate_dir is None:
        return 0, 0
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
            rules = manifest.get("project_rules")
            if not isinstance(rules, dict):
                errors.append("source candidate manifest project_rules must be an object")
            else:
                if rules.get("candidate_only") is not True:
                    errors.append("source candidate project_rules.candidate_only must be true")
                if rules.get("accepted_content") is not False:
                    errors.append("source candidate project_rules.accepted_content must be false")
                if rules.get("runtime_integrated") is not False:
                    errors.append("source candidate project_rules.runtime_integrated must be false")

    return count_json_items(candidate_dir, "chapters", errors), count_json_items(candidate_dir, "codex", errors)


def validate_manual_review(
    manual_review_path: Path | None,
    repo_root: Path,
    payload: dict[str, Any],
    errors: list[str],
) -> dict[str, Any] | None:
    if manual_review_path is None:
        return None
    report = build_manual_review_report(manual_review_path, repo_root)
    if report["decision"] != "story_codex_manual_review_valid":
        errors.append("manual_review_file must validate")
    if report.get("gate_decision") != "ui_candidate":
        errors.append("manual_review_file gate_decision must be ui_candidate")
    if report.get("chapter_review_count") != payload.get("chapter_count"):
        errors.append("chapter_count must match manual review chapter count")
    if report.get("codex_review_count") != payload.get("codex_entry_count"):
        errors.append("codex_entry_count must match manual review codex count")
    return report


def build_report(manifest_path: Path, repo_root: Path) -> dict[str, Any]:
    payload = load_json_object(manifest_path)
    errors: list[str] = []
    warnings: list[str] = []

    validate_top_level(payload, errors)
    validate_rules(payload, errors)
    candidate_dir = require_existing_repo_path(payload, "source_candidate_pack", repo_root, errors)
    manual_review_path = require_existing_repo_path(payload, "manual_review_file", repo_root, errors)
    candidate_validation_report = require_existing_repo_path(payload, "candidate_validation_report", repo_root, errors)

    actual_chapters, actual_codex = validate_source_candidate(candidate_dir, payload, errors)
    if payload.get("chapter_count") != actual_chapters:
        errors.append("chapter_count must match source_candidate_pack chapters")
    if payload.get("codex_entry_count") != actual_codex:
        errors.append("codex_entry_count must match source_candidate_pack codex entries")

    manual_review_report = validate_manual_review(manual_review_path, repo_root, payload, errors)

    return {
        "report_version": 1,
        "source": relative_repo_path(repo_root, manifest_path),
        "repo_root": str(repo_root),
        "decision": "story_codex_ui_candidate_manifest_valid" if not errors else "story_codex_ui_candidate_manifest_invalid",
        "candidate_pack_id": payload.get("candidate_pack_id"),
        "chapter_count": payload.get("chapter_count"),
        "codex_entry_count": payload.get("codex_entry_count"),
        "candidate_validation_report": relative_repo_path(repo_root, candidate_validation_report)
        if candidate_validation_report is not None
        else None,
        "manual_review_decision": manual_review_report["decision"] if manual_review_report is not None else None,
        "manual_gate_decision": manual_review_report["gate_decision"] if manual_review_report is not None else None,
        "errors": errors,
        "warnings": warnings,
        "limitations": [
            "This validator checks UI candidate manifest completeness only.",
            "A valid UI candidate manifest does not promote content into accepted_content.",
            "A valid UI candidate manifest does not prove Runtime UI integration, final human acceptance, or release readiness.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Story Codex UI Candidate Manifest Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Decision: `{report['decision']}`",
        f"- Candidate: `{report['candidate_pack_id']}`",
        f"- Chapters: {report['chapter_count']}",
        f"- Codex entries: {report['codex_entry_count']}",
        f"- Manual review: `{report['manual_review_decision']}` / `{report['manual_gate_decision']}`",
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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm story/codex UI candidate manifests.")
    parser.add_argument("manifest", type=Path, help="Story/codex UI candidate manifest JSON")
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
    return 0 if report["decision"] == "story_codex_ui_candidate_manifest_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
