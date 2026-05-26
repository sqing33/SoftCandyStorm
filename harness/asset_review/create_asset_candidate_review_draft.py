#!/usr/bin/env python3
"""Create a human-review draft for an asset candidate batch.

This script intentionally produces a draft with TODO placeholders. It is not a
manual review and should not be used as acceptance evidence. Its job is to read
an asset candidate manifest and create one review entry per asset so a human
reviewer cannot accidentally miss an image, speech, music, or SFX candidate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


AUDIO_TYPES = {"audio", "speech", "music", "sfx", "voice"}
IMAGE_TYPES = {"image", "sprite", "ui", "icon", "background"}


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


def manifest_path_for_candidate(candidate_batch: Path) -> Path:
    return candidate_batch / "metadata" / "manifest.json"


def allowed_uses_for_type(asset_type: str | None) -> list[str]:
    if asset_type in AUDIO_TYPES:
        return ["audio_candidate"]
    if asset_type in IMAGE_TYPES:
        return ["concept_reference"]
    return ["concept_reference"]


def placeholder_review(asset: dict[str, Any]) -> dict[str, Any]:
    asset_type = asset.get("type") if is_nonempty_string(asset.get("type")) else "unknown"
    common: dict[str, Any] = {
        "id": asset.get("id", "TODO_asset_id"),
        "decision": "revise",
        "asset_type": asset_type,
        "style_fit": "TODO: 1-5",
        "gameplay_readability": "TODO: 1-5",
        "provenance_confidence": "TODO: 1-5",
        "technical_readiness": "TODO: 1-5",
        "allowed_candidate_uses": allowed_uses_for_type(str(asset_type)),
        "notes": "TODO: human reviewer must record concrete observation before validation.",
        "required_changes": [
            "TODO: record concrete revision, cleanup, loudness, crop, or rejection reason."
        ],
    }
    if asset_type in AUDIO_TYPES:
        common.update(
            {
                "audio_clarity": "TODO: 1-5",
                "loudness_readiness": "TODO: 1-5",
                "duration_fit": "TODO: 1-5",
            }
        )
    elif asset_type in IMAGE_TYPES:
        common.update(
            {
                "small_size_readability": "TODO: 1-5",
                "alpha_edge_quality": "TODO: 1-5",
            }
        )
    else:
        common.update(
            {
                "small_size_readability": "TODO: 1-5 if visual",
                "alpha_edge_quality": "TODO: 1-5 if visual",
                "audio_clarity": "TODO: 1-5 if audio",
                "loudness_readiness": "TODO: 1-5 if audio",
                "duration_fit": "TODO: 1-5 if audio",
            }
        )
    return common


def build_draft(
    candidate_batch: Path,
    repo_root: Path,
    metadata_report: str,
    reviewer: str,
    reviewed_at: str,
) -> dict[str, Any]:
    manifest_path = manifest_path_for_candidate(candidate_batch)
    manifest = load_json_object(manifest_path)
    assets = manifest.get("assets")
    if not isinstance(assets, list) or not assets:
        raise ValueError(f"{manifest_path} must contain a non-empty assets array")

    asset_reviews: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, asset in enumerate(assets):
        if not isinstance(asset, dict):
            raise ValueError(f"{manifest_path}: assets[{index}] must be an object")
        asset_id = asset.get("id")
        if not is_nonempty_string(asset_id):
            raise ValueError(f"{manifest_path}: assets[{index}] missing id")
        if str(asset_id) in seen:
            raise ValueError(f"{manifest_path}: duplicate asset id `{asset_id}`")
        seen.add(str(asset_id))
        asset_reviews.append(placeholder_review(asset))

    batch_id = manifest.get("batch_id") if is_nonempty_string(manifest.get("batch_id")) else candidate_batch.name
    return {
        "review_version": 1,
        "draft_notice": "AUTO-GENERATED DRAFT ONLY. A human reviewer must replace TODO placeholders before validation or promotion.",
        "candidate_batch_id": batch_id,
        "candidate_batch_path": relative_repo_path(repo_root, candidate_batch),
        "candidate_metadata_report": metadata_report,
        "reviewer": reviewer,
        "reviewed_at": reviewed_at,
        "gate_decision": "needs_more_review",
        "summary": "TODO: human reviewer must summarize style, readability, provenance, technical readiness, and final gate decision.",
        "asset_reviews": asset_reviews,
        "global_risks": [
            "TODO: list unresolved style, legal, provenance, readability, audio, or Runtime risks."
        ],
        "next_actions": [
            "TODO: fill every rating with integer 1-5 and replace notes with concrete human observations.",
            "TODO: run harness/asset_review/validate_asset_candidate_manual_review.py after the draft is fully reviewed.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a draft human-review JSON for an asset candidate batch.")
    parser.add_argument("candidate_batch", type=Path, help="Path to asset/generated_candidates/<batch>")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--metadata-report", required=True, help="Existing metadata validation summary path")
    parser.add_argument("--reviewer", default="TODO: human reviewer", help="Reviewer placeholder")
    parser.add_argument("--reviewed-at", default="TODO: YYYY-MM-DD", help="Review date placeholder")
    parser.add_argument("--out", type=Path, required=True, help="Output review draft JSON path")
    args = parser.parse_args()

    draft = build_draft(
        args.candidate_batch,
        args.repo_root,
        args.metadata_report,
        args.reviewer,
        args.reviewed_at,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(draft, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
