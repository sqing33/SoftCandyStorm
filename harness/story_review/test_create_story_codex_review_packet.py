#!/usr/bin/env python3
"""Regression tests for story/codex review packet generation.

Run with:
    python3 harness/story_review/test_create_story_codex_review_packet.py
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
PACKET = SCRIPT_DIR / "create_story_codex_review_packet.py"

sys.path.insert(0, str(SCRIPT_DIR))

from create_story_codex_review_packet import build_packet  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def make_candidate(root: Path) -> Path:
    candidate = root / "harness" / "generated_candidates" / "packet_story_pack"
    write_json(
        candidate / "metadata" / "manifest.json",
        {
            "batch_id": "packet_story_pack",
            "candidate_kind": "story_codex_seed_pack",
            "generated_at": "2026-05-26",
            "project_rules": {
                "candidate_only": True,
                "accepted_content": False,
                "runtime_integrated": False,
                "required_next_steps": ["manual_lore_review"],
            },
        },
    )
    write_json(
        candidate / "chapters" / "frosting-grassland.json",
        {
            "id": "frosting-grassland",
            "title": "第一章：糖霜草地",
            "map_id": "frosting-grassland",
            "boss_id": "runaway-sugar-mixer",
            "theme": "混乱刚刚开始",
            "pre_run_lines": ["糖霜草地今天太安静了。"],
            "codex_unlocks": ["world-sugar-jar-stars"],
        },
    )
    write_json(
        candidate / "codex" / "character-jar-keeper.json",
        {
            "id": "character-jar-keeper",
            "category": "character",
            "title": "糖罐守护员",
            "related_ids": ["jar-keeper"],
            "unlock_hint": "默认角色。",
            "entry": "见习守护员原本只负责擦星星。",
            "tone_tags": ["character", "gentle-humor"],
        },
    )
    return candidate


def make_review(root: Path, candidate: Path) -> Path:
    review = root / "harness" / "story_review" / "drafts" / "packet_story_review.json"
    write_json(
        review,
        {
            "review_version": 1,
            "candidate_pack_id": candidate.name,
            "candidate_pack_path": str(candidate.relative_to(root)),
            "candidate_validation_report": "harness/reports/story/summary.md",
            "reviewer": "TODO: human reviewer",
            "reviewed_at": "TODO: YYYY-MM-DD",
            "gate_decision": "needs_more_review",
            "summary": "TODO",
            "chapter_reviews": [
                {
                    "id": "frosting-grassland",
                    "decision": "revise",
                    "tone_rating": "TODO: 1-5",
                }
            ],
            "codex_reviews": [
                {
                    "id": "character-jar-keeper",
                    "decision": "revise",
                    "tone_rating": "TODO: 1-5",
                }
            ],
            "global_risks": ["TODO"],
            "next_actions": ["TODO"],
        },
    )
    return review


class StoryCodexReviewPacketTests(unittest.TestCase):
    def test_build_packet_covers_chapter_and_codex_entries(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidate = make_candidate(root)
            review = make_review(root, candidate)

            packet = build_packet(
                candidate,
                root,
                "harness/reports/story/summary.md",
                review,
            )

            self.assertEqual(packet["pack_id"], "packet_story_pack")
            self.assertEqual(packet["chapter_count"], 1)
            self.assertEqual(packet["codex_count"], 1)
            self.assertEqual(packet["missing_chapter_review_count"], 0)
            self.assertEqual(packet["missing_codex_review_count"], 0)
            self.assertEqual(packet["chapters"][0]["review_status"], "draft_todo")
            self.assertEqual(packet["codex_entries"][0]["review_status"], "draft_todo")

    def test_cli_writes_markdown_packet(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidate = make_candidate(root)
            review = make_review(root, candidate)
            out = root / "story_packet.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(PACKET),
                    str(candidate),
                    "--repo-root",
                    str(root),
                    "--candidate-validation-report",
                    "harness/reports/story/summary.md",
                    "--review-draft",
                    str(review),
                    "--out",
                    str(out),
                ],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            text = out.read_text(encoding="utf-8")
            self.assertIn("Story Codex Review Packet", text)
            self.assertIn("frosting-grassland", text)
            self.assertIn("character-jar-keeper", text)
            self.assertIn("draft_todo", text)


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
