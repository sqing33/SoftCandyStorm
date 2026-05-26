#!/usr/bin/env python3
"""Validate human review records for story/codex candidate packs.

This tool checks review evidence completeness only. It does not judge writing
quality by itself and it never promotes generated candidates into accepted
content.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ALLOWED_GATE_DECISIONS = {"repair", "ui_candidate", "reject", "needs_more_review"}
FORBIDDEN_GATE_DECISIONS = {"accepted_content", "runtime_integrated", "release_ready", "accept_content"}
ALLOWED_ITEM_DECISIONS = {"pass", "revise", "reject"}
CHAPTER_RATING_FIELDS = ["tone_rating", "lore_consistency", "ui_fit", "spoiler_control"]
CODEX_RATING_FIELDS = ["tone_rating", "lore_consistency", "ui_fit", "unlock_fit"]


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


def resolve_repo_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def is_inside_repo(repo_root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return False
    return True


def read_ids(candidate_dir: Path, subdir: str, errors: list[str]) -> set[str]:
    ids: set[str] = set()
    directory = candidate_dir / subdir
    if not directory.exists():
        errors.append(f"candidate pack missing `{subdir}` directory")
        return ids
    for path in sorted(directory.glob("*.json")):
        try:
            payload = load_json_object(path)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            errors.append(f"{subdir}/{path.name} is invalid JSON: {error}")
            continue
        item_id = payload.get("id")
        if not is_nonempty_string(item_id):
            errors.append(f"{subdir}/{path.name} missing non-empty id")
            continue
        ids.add(str(item_id))
    if not ids:
        errors.append(f"candidate pack `{subdir}` directory contains no reviewable items")
    return ids


def load_candidate_index(
    repo_root: Path,
    payload: dict[str, Any],
    errors: list[str],
) -> tuple[set[str], set[str]]:
    candidate_path = payload.get("candidate_pack_path")
    if not is_nonempty_string(candidate_path):
        errors.append("candidate_pack_path must be non-empty")
        return set(), set()

    resolved = resolve_repo_path(repo_root, str(candidate_path))
    if not is_inside_repo(repo_root, resolved):
        errors.append(f"candidate_pack_path must stay inside repository: {candidate_path}")
        return set(), set()
    if not resolved.exists():
        errors.append(f"candidate_pack_path does not exist: {candidate_path}")
        return set(), set()

    candidate_id = payload.get("candidate_pack_id")
    if is_nonempty_string(candidate_id) and resolved.name != candidate_id:
        errors.append("candidate_pack_id must match candidate_pack_path directory name")

    manifest_path = resolved / "metadata" / "manifest.json"
    if not manifest_path.exists():
        errors.append("candidate pack missing metadata/manifest.json")
    else:
        try:
            manifest = load_json_object(manifest_path)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            errors.append(f"candidate pack manifest is invalid: {error}")
        else:
            project_rules = manifest.get("project_rules")
            if not isinstance(project_rules, dict):
                errors.append("candidate manifest project_rules must be an object")
            else:
                if project_rules.get("candidate_only") is not True:
                    errors.append("candidate manifest project_rules.candidate_only must stay true")
                if project_rules.get("accepted_content") is not False:
                    errors.append("candidate manifest project_rules.accepted_content must stay false")
                if project_rules.get("runtime_integrated") is not False:
                    errors.append("candidate manifest project_rules.runtime_integrated must stay false")

    return read_ids(resolved, "chapters", errors), read_ids(resolved, "codex", errors)


def validate_existing_report(repo_root: Path, payload: dict[str, Any], errors: list[str]) -> None:
    report_path = payload.get("candidate_validation_report")
    if not is_nonempty_string(report_path):
        errors.append("candidate_validation_report must be non-empty")
        return
    resolved = resolve_repo_path(repo_root, str(report_path))
    if not is_inside_repo(repo_root, resolved):
        errors.append(f"candidate_validation_report must stay inside repository: {report_path}")
    elif not resolved.exists():
        errors.append(f"candidate_validation_report does not exist: {report_path}")


def validate_review_collection(
    label: str,
    reviews: Any,
    expected_ids: set[str],
    rating_fields: list[str],
    gate_decision: str | None,
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    reports: list[dict[str, Any]] = []
    if not isinstance(reviews, list):
        return reports, [f"{label}_reviews must be a list"], warnings

    seen: set[str] = set()
    for index, review in enumerate(reviews):
        if not isinstance(review, dict):
            errors.append(f"{label}_reviews[{index}] must be an object")
            continue
        item_id = review.get("id")
        display_id = str(item_id) if is_nonempty_string(item_id) else f"{label}_reviews[{index}]"
        if not is_nonempty_string(item_id):
            errors.append(f"{display_id}: id must be non-empty")
        elif item_id not in expected_ids:
            errors.append(f"{display_id}: id does not exist in candidate pack")
        elif item_id in seen:
            errors.append(f"{display_id}: duplicate review id")
        else:
            seen.add(str(item_id))

        decision = review.get("decision")
        if decision not in ALLOWED_ITEM_DECISIONS:
            errors.append(f"{display_id}: decision must be one of {', '.join(sorted(ALLOWED_ITEM_DECISIONS))}")

        low_fields: list[str] = []
        for field in rating_fields:
            if not validate_rating(review.get(field)):
                errors.append(f"{display_id}: {field} must be an integer from 1 to 5")
            elif int(review[field]) < 4:
                low_fields.append(field)

        if not is_nonempty_string(review.get("notes")):
            errors.append(f"{display_id}: notes must contain a concrete human observation")

        required_changes = review.get("required_changes")
        if not isinstance(required_changes, list) or not all(isinstance(item, str) for item in required_changes):
            errors.append(f"{display_id}: required_changes must be a list of strings")
            required_change_count = 0
        else:
            required_change_count = len([item for item in required_changes if item.strip()])

        if decision in {"revise", "reject"} and required_change_count == 0:
            errors.append(f"{display_id}: {decision} requires at least one required_changes item")
        if low_fields and decision == "pass":
            warnings.append(f"{display_id}: pass decision has ratings below 4 for {', '.join(low_fields)}")
        if gate_decision == "ui_candidate":
            if decision != "pass":
                errors.append(f"{display_id}: ui_candidate gate requires every item decision to be pass")
            if low_fields:
                errors.append(f"{display_id}: ui_candidate gate requires all ratings to be at least 4")
            if required_change_count:
                errors.append(f"{display_id}: ui_candidate gate cannot have required_changes")

        reports.append(
            {
                "id": item_id if is_nonempty_string(item_id) else display_id,
                "decision": decision,
                "low_rating_count": len(low_fields),
                "required_change_count": required_change_count,
            }
        )

    missing_ids = sorted(expected_ids - seen)
    if missing_ids:
        errors.append(f"{label}_reviews missing candidate ids: {', '.join(missing_ids)}")

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

    gate_decision = payload.get("gate_decision")
    if gate_decision in FORBIDDEN_GATE_DECISIONS:
        errors.append(f"forbidden gate_decision `{gate_decision}`")
    elif gate_decision not in ALLOWED_GATE_DECISIONS:
        errors.append(f"gate_decision must be one of {', '.join(sorted(ALLOWED_GATE_DECISIONS))}")

    validate_existing_report(repo_root, payload, errors)
    chapter_ids, codex_ids = load_candidate_index(repo_root, payload, errors)

    chapter_reports, chapter_errors, chapter_warnings = validate_review_collection(
        "chapter",
        payload.get("chapter_reviews"),
        chapter_ids,
        CHAPTER_RATING_FIELDS,
        str(gate_decision) if isinstance(gate_decision, str) else None,
    )
    codex_reports, codex_errors, codex_warnings = validate_review_collection(
        "codex",
        payload.get("codex_reviews"),
        codex_ids,
        CODEX_RATING_FIELDS,
        str(gate_decision) if isinstance(gate_decision, str) else None,
    )
    errors.extend(chapter_errors)
    errors.extend(codex_errors)
    warnings.extend(chapter_warnings)
    warnings.extend(codex_warnings)

    global_risks = string_list(payload.get("global_risks"))
    next_actions = string_list(payload.get("next_actions"))
    if payload.get("global_risks") is not None and not isinstance(payload.get("global_risks"), list):
        errors.append("global_risks must be a list")
    if payload.get("next_actions") is not None and not isinstance(payload.get("next_actions"), list):
        errors.append("next_actions must be a list")
    if gate_decision == "ui_candidate" and global_risks:
        errors.append("ui_candidate gate cannot list unresolved global_risks")
    if gate_decision in {"repair", "reject", "needs_more_review"} and not next_actions:
        errors.append(f"{gate_decision} gate requires non-empty next_actions")

    repair_item_count = sum(
        1
        for item in chapter_reports + codex_reports
        if item["decision"] in {"revise", "reject"} or item["required_change_count"] > 0
    )
    if gate_decision == "repair" and repair_item_count == 0 and not global_risks:
        errors.append("repair gate requires at least one item issue or global_risks entry")

    return {
        "report_version": 1,
        "source": str(review_path),
        "repo_root": str(repo_root),
        "decision": "story_codex_manual_review_valid" if not errors else "story_codex_manual_review_invalid",
        "gate_decision": gate_decision,
        "chapter_review_count": len(chapter_reports),
        "expected_chapter_count": len(chapter_ids),
        "codex_review_count": len(codex_reports),
        "expected_codex_count": len(codex_ids),
        "repair_item_count": repair_item_count,
        "global_risk_count": len(global_risks),
        "next_action_count": len(next_actions),
        "errors": errors,
        "warnings": warnings,
        "limitations": [
            "This validator checks manual review record completeness only.",
            "It cannot judge writing quality, emotional tone, translation quality, or UI feel.",
            "A ui_candidate decision does not promote content into accepted_content or Runtime.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Story Codex Manual Review Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Decision: `{report['decision']}`",
        f"- Gate decision: `{report['gate_decision']}`",
        f"- Chapters reviewed: {report['chapter_review_count']} / {report['expected_chapter_count']}",
        f"- Codex reviewed: {report['codex_review_count']} / {report['expected_codex_count']}",
        f"- Repair items: {report['repair_item_count']}",
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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm story/codex manual review records.")
    parser.add_argument("review", type=Path, help="Story/codex manual review JSON file")
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
    return 0 if report["decision"] == "story_codex_manual_review_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
