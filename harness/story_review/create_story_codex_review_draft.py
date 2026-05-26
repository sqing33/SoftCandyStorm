#!/usr/bin/env python3
"""Create a human-review draft for a story/codex candidate pack.

This script intentionally produces a draft with TODO placeholders. It is not a
manual review and should not be used as acceptance evidence. Its job is to read
a generated story/codex candidate pack and create one review entry per chapter
and codex item so a human reviewer cannot accidentally miss a narrative item.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def relative_repo_path(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(path)


def manifest_path_for_candidate(candidate_pack: Path) -> Path:
    return candidate_pack / "metadata" / "manifest.json"


def read_candidate_items(candidate_pack: Path, subdir: str) -> list[dict[str, Any]]:
    directory = candidate_pack / subdir
    if not directory.exists():
        raise ValueError(f"{candidate_pack} is missing `{subdir}` directory")

    items: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path in sorted(directory.glob("*.json")):
        payload = load_json_object(path)
        item_id = payload.get("id")
        if not is_nonempty_string(item_id):
            raise ValueError(f"{path} missing non-empty id")
        if str(item_id) in seen:
            raise ValueError(f"{path}: duplicate {subdir} id `{item_id}`")
        seen.add(str(item_id))
        items.append(payload)

    if not items:
        raise ValueError(f"{candidate_pack} `{subdir}` directory contains no JSON items")
    return items


def placeholder_chapter_review(chapter: dict[str, Any]) -> dict[str, Any]:
    review: dict[str, Any] = {
        "id": chapter.get("id", "TODO_chapter_id"),
        "decision": "revise",
        "tone_rating": "TODO: 1-5",
        "lore_consistency": "TODO: 1-5",
        "ui_fit": "TODO: 1-5",
        "spoiler_control": "TODO: 1-5",
        "notes": "TODO: human reviewer must record concrete tone, pacing, and UI observations.",
        "required_changes": [
            "TODO: record concrete dialogue, lore, spoiler, or UI-length revision."
        ],
    }
    if is_nonempty_string(chapter.get("title")):
        review["title"] = chapter["title"]
    if is_nonempty_string(chapter.get("theme")):
        review["theme"] = chapter["theme"]
    return review


def placeholder_codex_review(codex: dict[str, Any]) -> dict[str, Any]:
    review: dict[str, Any] = {
        "id": codex.get("id", "TODO_codex_id"),
        "decision": "revise",
        "tone_rating": "TODO: 1-5",
        "lore_consistency": "TODO: 1-5",
        "ui_fit": "TODO: 1-5",
        "unlock_fit": "TODO: 1-5",
        "notes": "TODO: human reviewer must record concrete lore, unlock, and UI observations.",
        "required_changes": [
            "TODO: record concrete entry, unlock hint, tone tag, or UI-length revision."
        ],
    }
    if is_nonempty_string(codex.get("title")):
        review["title"] = codex["title"]
    if is_nonempty_string(codex.get("category")):
        review["category"] = codex["category"]
    return review


def build_draft(
    candidate_pack: Path,
    repo_root: Path,
    candidate_validation_report: str,
    reviewer: str,
    reviewed_at: str,
) -> dict[str, Any]:
    manifest_path = manifest_path_for_candidate(candidate_pack)
    manifest = load_json_object(manifest_path)
    project_rules = manifest.get("project_rules")
    if not isinstance(project_rules, dict):
        raise ValueError(f"{manifest_path} must contain project_rules object")
    if project_rules.get("candidate_only") is not True:
        raise ValueError(f"{manifest_path} project_rules.candidate_only must stay true")
    if project_rules.get("accepted_content") is not False:
        raise ValueError(f"{manifest_path} project_rules.accepted_content must stay false")
    if project_rules.get("runtime_integrated") is not False:
        raise ValueError(f"{manifest_path} project_rules.runtime_integrated must stay false")

    chapters = read_candidate_items(candidate_pack, "chapters")
    codex_entries = read_candidate_items(candidate_pack, "codex")
    batch_id = manifest.get("batch_id") if is_nonempty_string(manifest.get("batch_id")) else candidate_pack.name

    return {
        "review_version": 1,
        "draft_notice": "AUTO-GENERATED DRAFT ONLY. A human reviewer must replace TODO placeholders before validation or promotion.",
        "candidate_pack_id": batch_id,
        "candidate_pack_path": relative_repo_path(repo_root, candidate_pack),
        "candidate_validation_report": candidate_validation_report,
        "reviewer": reviewer,
        "reviewed_at": reviewed_at,
        "gate_decision": "needs_more_review",
        "summary": "TODO: human reviewer must summarize tone, lore consistency, UI fit, spoiler pacing, unlock fit, and final gate decision.",
        "chapter_reviews": [placeholder_chapter_review(chapter) for chapter in chapters],
        "codex_reviews": [placeholder_codex_review(codex) for codex in codex_entries],
        "global_risks": [
            "TODO: list unresolved lore, pacing, UI, localization, spoiler, or unlock risks."
        ],
        "next_actions": [
            "TODO: fill every rating with integer 1-5 and replace notes with concrete human observations.",
            "TODO: run harness/story_review/validate_story_codex_manual_review.py after the draft is fully reviewed.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a draft human-review JSON for a story/codex candidate pack.")
    parser.add_argument("candidate_pack", type=Path, help="Path to harness/generated_candidates/<pack>")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--candidate-validation-report", required=True, help="Existing story/codex validation summary path")
    parser.add_argument("--reviewer", default="TODO: human reviewer", help="Reviewer placeholder")
    parser.add_argument("--reviewed-at", default="TODO: YYYY-MM-DD", help="Review date placeholder")
    parser.add_argument("--out", type=Path, required=True, help="Output review draft JSON path")
    args = parser.parse_args()

    draft = build_draft(
        args.candidate_pack,
        args.repo_root,
        args.candidate_validation_report,
        args.reviewer,
        args.reviewed_at,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(draft, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
