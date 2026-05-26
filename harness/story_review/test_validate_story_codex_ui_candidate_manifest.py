#!/usr/bin/env python3
"""Regression tests for story/codex UI candidate manifest validation.

Run with:
    python3 harness/story_review/test_validate_story_codex_ui_candidate_manifest.py
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
TEMPLATE = SCRIPT_DIR / "story_codex_ui_candidate_manifest_template.json"

sys.path.insert(0, str(SCRIPT_DIR))

from promote_story_codex_ui_candidate import promote_story_codex_ui_candidate  # noqa: E402
from validate_story_codex_ui_candidate_manifest import build_report, load_json_object  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def create_candidate_pack(repo_root: Path) -> Path:
    candidate = repo_root / "harness/generated_candidates/story-pack"
    write_json(
        candidate / "metadata/manifest.json",
        {
            "batch_id": "story-pack",
            "candidate_kind": "story_codex_seed_pack",
            "generated_at": "2026-05-26",
            "project_rules": {
                "candidate_only": True,
                "accepted_content": False,
                "runtime_integrated": False,
            },
        },
    )
    write_json(candidate / "chapters/frosting-grassland.json", {"id": "frosting-grassland"})
    write_json(candidate / "codex/character-jar-keeper.json", {"id": "character-jar-keeper"})
    write_text(repo_root / "harness/reports/story/summary.md", "# valid\n")
    return candidate


def valid_ui_review(repo_root: Path) -> Path:
    review_path = repo_root / "harness/story_review/reviews/story-pack-review.json"
    write_json(
        review_path,
        {
            "review_version": 1,
            "candidate_pack_id": "story-pack",
            "candidate_pack_path": "harness/generated_candidates/story-pack",
            "candidate_validation_report": "harness/reports/story/summary.md",
            "reviewer": "human-reviewer",
            "reviewed_at": "2026-05-26",
            "gate_decision": "ui_candidate",
            "summary": "人工审校确认语气、设定和 UI 长度均可进入 UI 候选。",
            "chapter_reviews": [
                {
                    "id": "frosting-grassland",
                    "decision": "pass",
                    "tone_rating": 4,
                    "lore_consistency": 5,
                    "ui_fit": 4,
                    "spoiler_control": 4,
                    "notes": "章节语气轻快，信息量适合局外 UI。",
                    "required_changes": [],
                }
            ],
            "codex_reviews": [
                {
                    "id": "character-jar-keeper",
                    "decision": "pass",
                    "tone_rating": 4,
                    "lore_consistency": 5,
                    "ui_fit": 4,
                    "unlock_fit": 4,
                    "notes": "图鉴条目和解锁节奏匹配。",
                    "required_changes": [],
                }
            ],
            "global_risks": [],
            "next_actions": [],
        },
    )
    return review_path


class StoryCodexUiCandidateManifestValidatorTests(unittest.TestCase):
    def test_promoted_manifest_validates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            create_candidate_pack(repo_root)
            review = valid_ui_review(repo_root)
            out_dir = repo_root / "harness/story_review/ui_candidates"
            promote_story_codex_ui_candidate(review, repo_root, out_dir)

            manifest = out_dir / "story-pack/ui_candidate_manifest.json"
            report = build_report(manifest, repo_root)

            self.assertEqual(report["decision"], "story_codex_ui_candidate_manifest_valid")
            self.assertEqual(report["manual_gate_decision"], "ui_candidate")
            self.assertEqual(report["chapter_count"], 1)
            self.assertEqual(report["codex_entry_count"], 1)

    def test_template_is_invalid_until_human_review_exists(self) -> None:
        report = build_report(TEMPLATE, REPO_ROOT)

        self.assertEqual(report["decision"], "story_codex_ui_candidate_manifest_invalid")
        self.assertTrue(any("placeholder" in error for error in report["errors"]))
        self.assertTrue(any("manual_review_file" in error for error in report["errors"]))

    def test_rejects_manifest_that_claims_accepted_content(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            create_candidate_pack(repo_root)
            review = valid_ui_review(repo_root)
            out_dir = repo_root / "harness/story_review/ui_candidates"
            promote_story_codex_ui_candidate(review, repo_root, out_dir)
            manifest = out_dir / "story-pack/ui_candidate_manifest.json"
            payload = load_json_object(manifest)
            payload["rules"]["accepted_content"] = True
            write_json(manifest, payload)

            report = build_report(manifest, repo_root)

            self.assertEqual(report["decision"], "story_codex_ui_candidate_manifest_invalid")
            self.assertTrue(any("rules.accepted_content" in error for error in report["errors"]))

    def test_counts_must_match_candidate_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            create_candidate_pack(repo_root)
            review = valid_ui_review(repo_root)
            out_dir = repo_root / "harness/story_review/ui_candidates"
            promote_story_codex_ui_candidate(review, repo_root, out_dir)
            manifest = out_dir / "story-pack/ui_candidate_manifest.json"
            payload = load_json_object(manifest)
            payload["chapter_count"] = 99
            write_json(manifest, payload)

            report = build_report(manifest, repo_root)

            self.assertEqual(report["decision"], "story_codex_ui_candidate_manifest_invalid")
            self.assertTrue(any("chapter_count" in error for error in report["errors"]))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
