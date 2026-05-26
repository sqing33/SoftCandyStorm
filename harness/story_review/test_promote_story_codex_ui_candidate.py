#!/usr/bin/env python3
"""Regression tests for story/codex UI candidate promotion.

Run with:
    python3 harness/story_review/test_promote_story_codex_ui_candidate.py
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from promote_story_codex_ui_candidate import promote_story_codex_ui_candidate


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


class StoryCodexUiCandidatePromotionTests(unittest.TestCase):
    def test_promotes_valid_ui_candidate_without_accepting_content(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            create_candidate_pack(repo_root)
            review = valid_ui_review(repo_root)
            out_dir = repo_root / "harness/story_review/ui_candidates"

            report = promote_story_codex_ui_candidate(review, repo_root, out_dir)
            manifest = json.loads(
                (out_dir / "story-pack/ui_candidate_manifest.json").read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(report["decision"], "story_codex_ui_candidate_promoted")
            self.assertEqual(report["chapter_count"], 1)
            self.assertEqual(report["codex_entry_count"], 1)
            self.assertFalse(manifest["rules"]["accepted_content"])
            self.assertFalse(manifest["rules"]["runtime_integrated"])
            self.assertTrue((out_dir / "story-pack/manual_review.json").exists())

    def test_rejects_non_ui_candidate_review(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            create_candidate_pack(repo_root)
            review = valid_ui_review(repo_root)
            payload = json.loads(review.read_text(encoding="utf-8"))
            payload["gate_decision"] = "repair"
            payload["chapter_reviews"][0]["decision"] = "revise"
            payload["chapter_reviews"][0]["tone_rating"] = 3
            payload["chapter_reviews"][0]["required_changes"] = ["缩短章节导语"]
            payload["global_risks"] = ["章节导语略长"]
            payload["next_actions"] = ["修订后重新审校"]
            write_json(review, payload)

            with self.assertRaisesRegex(ValueError, "gate_decision"):
                promote_story_codex_ui_candidate(
                    review,
                    repo_root,
                    repo_root / "harness/story_review/ui_candidates",
                )

    def test_refuses_to_overwrite_existing_ui_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            create_candidate_pack(repo_root)
            review = valid_ui_review(repo_root)
            out_dir = repo_root / "harness/story_review/ui_candidates"

            promote_story_codex_ui_candidate(review, repo_root, out_dir)

            with self.assertRaises(FileExistsError):
                promote_story_codex_ui_candidate(review, repo_root, out_dir)


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
