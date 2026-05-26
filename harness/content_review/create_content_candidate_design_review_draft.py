#!/usr/bin/env python3
"""Create a human-review draft for content candidate design review.

The draft intentionally contains TODO placeholders. It is not acceptance
evidence. Its job is to read a materialized generated content pack and create
one design-review entry per new item listed in source_patch_manifest.contents.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


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


def source_patch_manifest_path(candidate_pack: Path) -> Path:
    return candidate_pack / "metadata" / "source_patch_manifest.json"


def content_path_for_entry(candidate_pack: Path, entry: dict[str, Any]) -> Path:
    entry_path = entry.get("path")
    if is_nonempty_string(entry_path):
        return candidate_pack / str(entry_path)
    content_type = entry.get("type")
    content_id = entry.get("id")
    category = TYPE_TO_CATEGORY.get(str(content_type))
    if category is None or not is_nonempty_string(content_id):
        raise ValueError("content entry must include a supported type and id")
    return candidate_pack / category / f"{content_id}.json"


def placeholder_review(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": entry.get("id", "TODO_content_id"),
        "content_type": entry.get("type", "unknown"),
        "decision": "revise",
        "theme_fit": "TODO: 1-5",
        "novelty": "TODO: 1-5",
        "build_potential": "TODO: 1-5",
        "counterplay_clarity": "TODO: 1-5",
        "visual_audio_fit": "TODO: 1-5",
        "balance_risk": "TODO: low|medium|high",
        "notes": "TODO: human reviewer must record concrete design observation before validation.",
        "required_changes": [
            "TODO: record concrete revision, simulation concern, acceptance blocker, or rejection reason."
        ],
    }


def build_draft(
    candidate_pack: Path,
    repo_root: Path,
    preflight_report: str,
    reviewer: str,
    reviewed_at: str,
) -> dict[str, Any]:
    manifest = load_json_object(manifest_path_for_candidate(candidate_pack))
    source_manifest = load_json_object(source_patch_manifest_path(candidate_pack))
    contents = source_manifest.get("contents")
    if not isinstance(contents, list) or not contents:
        raise ValueError("source_patch_manifest.contents must be a non-empty list")

    content_reviews: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, entry in enumerate(contents):
        if not isinstance(entry, dict):
            raise ValueError(f"source_patch_manifest.contents[{index}] must be an object")
        content_id = entry.get("id")
        if not is_nonempty_string(content_id):
            raise ValueError(f"source_patch_manifest.contents[{index}] missing id")
        if str(content_id) in seen:
            raise ValueError(f"source_patch_manifest duplicate content id `{content_id}`")
        seen.add(str(content_id))
        content_path = content_path_for_entry(candidate_pack, entry)
        if not content_path.exists():
            raise ValueError(f"candidate pack missing content file for `{content_id}`: {content_path}")
        content_reviews.append(placeholder_review(entry))

    batch_id = manifest.get("batch_id") if is_nonempty_string(manifest.get("batch_id")) else candidate_pack.name
    return {
        "review_version": 1,
        "draft_notice": "AUTO-GENERATED DRAFT ONLY. A human reviewer must replace TODO placeholders before validation.",
        "candidate_pack_id": batch_id,
        "candidate_pack_path": relative_repo_path(repo_root, candidate_pack),
        "source_patch_manifest": relative_repo_path(repo_root, source_patch_manifest_path(candidate_pack)),
        "candidate_preflight_report": preflight_report,
        "reviewer": reviewer,
        "reviewed_at": reviewed_at,
        "gate_decision": "needs_more_review",
        "summary": "TODO: human reviewer must summarize theme fit, novelty, counterplay, readability, risks, and next gate.",
        "content_reviews": content_reviews,
        "batch_risks": [
            "TODO: list unresolved design, balance, theme, readability, or production risks."
        ],
        "next_actions": [
            "TODO: fill every rating with integer 1-5 and replace notes with concrete human observations.",
            "TODO: run harness/content_review/validate_content_candidate_design_review.py after the draft is fully reviewed.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a draft human design review for a content candidate pack.")
    parser.add_argument("candidate_pack", type=Path, help="Path to harness/generated_candidates/<full-pack>")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--preflight-report", required=True, help="Existing materialized content preflight summary path")
    parser.add_argument("--reviewer", default="TODO: human reviewer", help="Reviewer placeholder")
    parser.add_argument("--reviewed-at", default="TODO: YYYY-MM-DD", help="Review date placeholder")
    parser.add_argument("--out", type=Path, required=True, help="Output review draft JSON path")
    args = parser.parse_args()

    draft = build_draft(
        args.candidate_pack,
        args.repo_root,
        args.preflight_report,
        args.reviewer,
        args.reviewed_at,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(draft, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
