#!/usr/bin/env python3
"""Regression tests for story/codex review draft generation.

Run with:
    python3 harness/story_review/test_create_story_codex_review_draft.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
GENERATOR = SCRIPT_DIR / "create_story_codex_review_draft.py"

sys.path.insert(0, str(SCRIPT_DIR))

from create_story_codex_review_draft import build_draft  # noqa: E402
from validate_story_codex_manual_review import build_report as build_manual_review_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def make_candidate(root: Path) -> Path:
    candidate = root / "harness" / "generated_candidates" / "fixture_story_pack"
    write_json(
        candidate / "metadata" / "manifest.json",
        {
            "batch_id": "fixture_story_pack",
            "candidate_kind": "story_codex_seed_pack",
            "generated_at": "2026-05-26",
            "project_rules": {
                "candidate_only": True,
                "accepted_content": False,
                "runtime_integrated": False,
                "required_next_steps": ["manual_lore_review"],
            },
            "content_counts": {
                "chapters": 2,
                "codex_entries": 2,
            },
        },
    )
    write_json(
        candidate / "chapters" / "frosting-grassland.json",
        {
            "id": "frosting-grassland",
            "title": "第一章：糖霜草地",
            "theme": "混乱刚刚开始",
        },
    )
    write_json(
        candidate / "chapters" / "soda-creek.json",
        {
            "id": "soda-creek",
            "title": "第二章：汽水溪谷",
            "theme": "被压住的情绪开始冒泡",
        },
    )
    write_json(
        candidate / "codex" / "world-sugar-jar-stars.json",
        {
            "id": "world-sugar-jar-stars",
            "category": "world",
            "title": "糖罐星",
        },
    )
    write_json(
        candidate / "codex" / "character-jar-keeper.json",
        {
            "id": "character-jar-keeper",
            "category": "character",
            "title": "糖罐守护员",
        },
    )
    return candidate


def make_validation_report(root: Path) -> Path:
    report = root / "harness" / "reports" / "fixture_story_validation" / "summary.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("# Fixture Story Validation\n", encoding="utf-8")
    return report


class StoryCodexReviewDraftTests(unittest.TestCase):
    def test_build_draft_covers_every_chapter_and_codex_item(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidate = make_candidate(root)

            draft = build_draft(
                candidate,
                root,
                "harness/reports/fixture_story_validation/summary.md",
                "TODO: human reviewer",
                "TODO: YYYY-MM-DD",
            )

            self.assertEqual(draft["candidate_pack_id"], "fixture_story_pack")
            self.assertIn("AUTO-GENERATED DRAFT ONLY", draft["draft_notice"])
            self.assertEqual(
                [item["id"] for item in draft["chapter_reviews"]],
                ["frosting-grassland", "soda-creek"],
            )
            self.assertEqual(
                [item["id"] for item in draft["codex_reviews"]],
                ["character-jar-keeper", "world-sugar-jar-stars"],
            )
            self.assertEqual(draft["gate_decision"], "needs_more_review")
            self.assertIn("TODO", str(draft["chapter_reviews"][0]["tone_rating"]))
            self.assertEqual(draft["codex_reviews"][0]["category"], "character")

    def test_cli_writes_draft_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidate = make_candidate(root)
            out = root / "draft.json"

            result = subprocess.run(
                [
                    sys.executable,
                    str(GENERATOR),
                    str(candidate),
                    "--repo-root",
                    str(root),
                    "--candidate-validation-report",
                    "harness/reports/fixture_story_validation/summary.md",
                    "--out",
                    str(out),
                ],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(len(payload["chapter_reviews"]), 2)
            self.assertEqual(len(payload["codex_reviews"]), 2)
            self.assertEqual(payload["gate_decision"], "needs_more_review")

    def test_draft_is_not_valid_manual_review_until_human_fills_todo(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidate = make_candidate(root)
            report_path = make_validation_report(root)
            draft = build_draft(
                candidate,
                root,
                str(report_path.relative_to(root)),
                "TODO: human reviewer",
                "TODO: YYYY-MM-DD",
            )
            draft_path = root / "harness" / "story_review" / "draft.json"
            write_json(draft_path, draft)

            report = build_manual_review_report(draft_path, root)

            self.assertEqual(report["decision"], "story_codex_manual_review_invalid")
            self.assertTrue(any("tone_rating must be an integer" in error for error in report["errors"]))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
