#!/usr/bin/env python3
"""Validate human design reviews for generated content candidate packs.

This gate checks review evidence completeness only. It does not run Schema,
budget, simulation, replay, or playtest gates, and it never promotes content
into accepted_content.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ALLOWED_GATE_DECISIONS = {"simulate_candidate", "repair", "reject", "needs_more_review"}
FORBIDDEN_GATE_DECISIONS = {"accepted_content", "runtime_integrated", "release_ready", "accept_candidate"}
ALLOWED_ITEM_DECISIONS = {"pass", "revise", "reject"}
ALLOWED_BALANCE_RISKS = {"low", "medium", "high"}
RATING_FIELDS = [
    "theme_fit",
    "novelty",
    "build_potential",
    "counterplay_clarity",
    "visual_audio_fit",
]
TYPE_TO_CATEGORY = {
    "character": "characters",
    "weapon": "weapons",
    "passive": "passives",
    "evolution": "evolutions",
    "enemy": "enemies",
    "boss": "bosses",
    "wave": "waves",
    "map": "maps",
    "event": "events",
}
REQUIRED_PROJECT_RULES = {
    "candidate_only": True,
    "accepted_content": False,
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


def validate_rating(value: Any) -> bool:
    return isinstance(value, int) and 1 <= value <= 5


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


def validate_project_rules(label: str, project_rules: Any, errors: list[str]) -> None:
    if not isinstance(project_rules, dict):
        errors.append(f"{label} project_rules must be an object")
        return
    for key, expected in REQUIRED_PROJECT_RULES.items():
        if project_rules.get(key) is not expected:
            errors.append(f"{label} project_rules.{key} must be {json.dumps(expected)}")


def load_candidate_index(
    repo_root: Path,
    payload: dict[str, Any],
    errors: list[str],
) -> dict[str, dict[str, Any]]:
    candidate_path = payload.get("candidate_pack_path")
    if not is_nonempty_string(candidate_path):
        errors.append("candidate_pack_path must be non-empty")
        return {}
    candidate_pack = resolve_repo_path(repo_root, str(candidate_path))
    if not is_inside_repo(repo_root, candidate_pack):
        errors.append(f"candidate_pack_path must stay inside repository: {candidate_path}")
        return {}
    if not candidate_pack.exists():
        errors.append(f"candidate_pack_path does not exist: {candidate_path}")
        return {}

    candidate_id = payload.get("candidate_pack_id")
    if is_nonempty_string(candidate_id) and candidate_pack.name != candidate_id:
        errors.append("candidate_pack_id must match candidate_pack_path directory name")

    manifest_path = candidate_pack / "metadata" / "manifest.json"
    if not manifest_path.exists():
        errors.append("candidate pack missing metadata/manifest.json")
    else:
        try:
            manifest = load_json_object(manifest_path)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            errors.append(f"candidate manifest is invalid: {error}")
        else:
            if manifest.get("candidate_kind") != "full_content_pack":
                errors.append("candidate manifest candidate_kind must be full_content_pack")
            validate_project_rules("candidate manifest", manifest.get("project_rules"), errors)

    source_manifest_value = payload.get("source_patch_manifest")
    if not is_nonempty_string(source_manifest_value):
        errors.append("source_patch_manifest must be non-empty")
        return {}
    source_manifest_path = resolve_repo_path(repo_root, str(source_manifest_value))
    if not is_inside_repo(repo_root, source_manifest_path):
        errors.append(f"source_patch_manifest must stay inside repository: {source_manifest_value}")
        return {}
    if not source_manifest_path.exists():
        errors.append(f"source_patch_manifest does not exist: {source_manifest_value}")
        return {}

    try:
        source_manifest = load_json_object(source_manifest_path)
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
        content_file = content_path_for_entry(candidate_pack, entry)
        if not content_file.exists():
            errors.append(f"{content_id}: candidate pack missing content file {content_file}")
        content_index[str(content_id)] = {
            "id": str(content_id),
            "type": str(content_type),
            "path": relative_repo_path(repo_root, content_file),
        }

    return content_index


def validate_existing_report(repo_root: Path, payload: dict[str, Any], errors: list[str]) -> None:
    report_path = payload.get("candidate_preflight_report")
    if not is_nonempty_string(report_path):
        errors.append("candidate_preflight_report must be non-empty")
        return
    resolved = resolve_repo_path(repo_root, str(report_path))
    if not is_inside_repo(repo_root, resolved):
        errors.append(f"candidate_preflight_report must stay inside repository: {report_path}")
    elif not resolved.exists():
        errors.append(f"candidate_preflight_report does not exist: {report_path}")


def validate_content_reviews(
    reviews: Any,
    content_index: dict[str, dict[str, Any]],
    gate_decision: str | None,
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    reports: list[dict[str, Any]] = []
    if not isinstance(reviews, list):
        return reports, ["content_reviews must be a list"], warnings

    seen: set[str] = set()
    for index, review in enumerate(reviews):
        if not isinstance(review, dict):
            errors.append(f"content_reviews[{index}] must be an object")
            continue
        content_id = review.get("id")
        display_id = str(content_id) if is_nonempty_string(content_id) else f"content_reviews[{index}]"
        if not is_nonempty_string(content_id):
            errors.append(f"{display_id}: id must be non-empty")
            manifest_entry: dict[str, Any] = {}
        elif content_id not in content_index:
            errors.append(f"{display_id}: id does not exist in source_patch_manifest.contents")
            manifest_entry = {}
        elif content_id in seen:
            errors.append(f"{display_id}: duplicate review id")
            manifest_entry = content_index[str(content_id)]
        else:
            seen.add(str(content_id))
            manifest_entry = content_index[str(content_id)]

        content_type = review.get("content_type")
        if not is_nonempty_string(content_type):
            errors.append(f"{display_id}: content_type must be non-empty")
        elif manifest_entry and content_type != manifest_entry.get("type"):
            errors.append(f"{display_id}: content_type must match source_patch_manifest type")

        decision = review.get("decision")
        if decision not in ALLOWED_ITEM_DECISIONS:
            errors.append(f"{display_id}: decision must be one of {', '.join(sorted(ALLOWED_ITEM_DECISIONS))}")

        low_fields: list[str] = []
        for field in RATING_FIELDS:
            if not validate_rating(review.get(field)):
                errors.append(f"{display_id}: {field} must be an integer from 1 to 5")
            elif int(review[field]) < 4:
                low_fields.append(field)

        if review.get("balance_risk") not in ALLOWED_BALANCE_RISKS:
            errors.append(f"{display_id}: balance_risk must be one of {', '.join(sorted(ALLOWED_BALANCE_RISKS))}")

        notes = review.get("notes")
        if not is_nonempty_string(notes):
            errors.append(f"{display_id}: notes must contain a concrete human observation")
        elif has_placeholder(notes):
            errors.append(f"{display_id}: notes must not contain TODO or placeholder markers")

        required_changes = review.get("required_changes")
        if not isinstance(required_changes, list) or not all(isinstance(item, str) for item in required_changes):
            errors.append(f"{display_id}: required_changes must be a list of strings")
            required_change_count = 0
        else:
            required_change_count = len([item for item in required_changes if item.strip()])
            if has_placeholder(required_changes):
                errors.append(f"{display_id}: required_changes must not contain TODO or placeholder markers")

        if decision in {"revise", "reject"} and required_change_count == 0:
            errors.append(f"{display_id}: {decision} requires at least one required_changes item")
        if gate_decision == "simulate_candidate":
            if decision != "pass":
                errors.append(f"{display_id}: simulate_candidate gate requires every item decision to be pass")
            if low_fields:
                errors.append(f"{display_id}: simulate_candidate gate requires all ratings to be at least 4")
            if review.get("balance_risk") == "high":
                errors.append(f"{display_id}: simulate_candidate gate cannot include high balance_risk")
            if required_change_count:
                errors.append(f"{display_id}: simulate_candidate gate cannot have required_changes")

        reports.append(
            {
                "id": content_id if is_nonempty_string(content_id) else display_id,
                "content_type": content_type,
                "decision": decision,
                "low_rating_count": len(low_fields),
                "required_change_count": required_change_count,
            }
        )

    missing_ids = sorted(set(content_index) - seen)
    if missing_ids:
        errors.append(f"content_reviews missing candidate ids: {', '.join(missing_ids)}")

    return reports, errors, warnings


def build_report(review_path: Path, repo_root: Path) -> dict[str, Any]:
    payload = load_json_object(review_path)
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(payload.get("review_version"), int) or payload["review_version"] <= 0:
        errors.append("review_version must be a positive integer")
    for field in ("candidate_pack_id", "reviewer", "reviewed_at", "summary"):
        if not is_nonempty_string(payload.get(field)):
            errors.append(f"{field} must be non-empty")
        elif has_placeholder(payload.get(field)):
            errors.append(f"{field} must not contain TODO or placeholder markers")

    gate_decision = payload.get("gate_decision")
    if gate_decision in FORBIDDEN_GATE_DECISIONS:
        errors.append(f"forbidden gate_decision `{gate_decision}`")
    elif gate_decision not in ALLOWED_GATE_DECISIONS:
        errors.append(f"gate_decision must be one of {', '.join(sorted(ALLOWED_GATE_DECISIONS))}")

    validate_existing_report(repo_root, payload, errors)
    content_index = load_candidate_index(repo_root, payload, errors)
    content_reports, content_errors, content_warnings = validate_content_reviews(
        payload.get("content_reviews"),
        content_index,
        str(gate_decision) if isinstance(gate_decision, str) else None,
    )
    errors.extend(content_errors)
    warnings.extend(content_warnings)

    batch_risks = string_list(payload.get("batch_risks"))
    next_actions = string_list(payload.get("next_actions"))
    if payload.get("batch_risks") is not None and not isinstance(payload.get("batch_risks"), list):
        errors.append("batch_risks must be a list")
    if payload.get("next_actions") is not None and not isinstance(payload.get("next_actions"), list):
        errors.append("next_actions must be a list")
    if has_placeholder(payload.get("batch_risks")):
        errors.append("batch_risks must not contain TODO or placeholder markers")
    if has_placeholder(payload.get("next_actions")):
        errors.append("next_actions must not contain TODO or placeholder markers")
    if gate_decision == "simulate_candidate" and batch_risks:
        errors.append("simulate_candidate gate cannot list unresolved batch_risks")
    if gate_decision in {"repair", "reject", "needs_more_review"} and not next_actions:
        errors.append(f"{gate_decision} gate requires non-empty next_actions")

    repair_item_count = sum(
        1
        for item in content_reports
        if item["decision"] in {"revise", "reject"} or item["required_change_count"] > 0
    )
    if gate_decision == "repair" and repair_item_count == 0 and not batch_risks:
        errors.append("repair gate requires at least one item issue or batch_risks entry")

    return {
        "report_version": 1,
        "source": relative_repo_path(repo_root, review_path),
        "repo_root": str(repo_root),
        "decision": "content_candidate_design_review_valid" if not errors else "content_candidate_design_review_invalid",
        "gate_decision": gate_decision,
        "content_review_count": len(content_reports),
        "expected_content_count": len(content_index),
        "repair_item_count": repair_item_count,
        "batch_risk_count": len(batch_risks),
        "next_action_count": len(next_actions),
        "errors": errors,
        "warnings": warnings,
        "limitations": [
            "This validator checks content design review completeness only.",
            "It does not run Schema, static budget, simulation, replay, or playtest gates.",
            "A simulate_candidate decision does not promote content into accepted_content or Runtime.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Content Candidate Design Review Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Decision: `{report['decision']}`",
        f"- Gate decision: `{report['gate_decision']}`",
        f"- Contents reviewed: {report['content_review_count']} / {report['expected_content_count']}",
        f"- Repair items: {report['repair_item_count']}",
        f"- Batch risks: {report['batch_risk_count']}",
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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm content candidate design reviews.")
    parser.add_argument("review", type=Path, help="Content candidate design review JSON file")
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
    return 0 if report["decision"] == "content_candidate_design_review_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
