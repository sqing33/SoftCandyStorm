#!/usr/bin/env python3
"""Regression tests for story/codex manual review validation.

Run with:
    python3 harness/story_review/test_validate_story_codex_manual_review.py
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
VALIDATOR = SCRIPT_DIR / "validate_story_codex_manual_review.py"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_story_codex_manual_review import build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def make_candidate(root: Path) -> tuple[Path, Path]:
    candidate = root / "harness" / "generated_candidates" / "fixture_story_pack"
    write_json(
        candidate / "metadata" / "manifest.json",
        {
            "batch_id": "fixture_story_pack",
            "candidate_kind": "story_codex_seed_pack",
            "project_rules": {
                "candidate_only": True,
                "accepted_content": False,
                "runtime_integrated": False,
            },
        },
    )
    write_json(candidate / "chapters" / "frosting-grassland.json", {"id": "frosting-grassland"})
    write_json(candidate / "codex" / "world-sugar-jar-stars.json", {"id": "world-sugar-jar-stars"})
    report = root / "harness" / "reports" / "fixture_story_validation" / "summary.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("# Fixture Story Validation\n", encoding="utf-8")
    return candidate, report


def make_review(root: Path, candidate: Path, report: Path, *, gate_decision: str = "ui_candidate") -> Path:
    if gate_decision == "ui_candidate":
        chapter_decision = "pass"
        codex_decision = "pass"
        required_changes: list[str] = []
        global_risks: list[str] = []
        next_actions = ["准备 future story/codex UI 接入候选。"]
        rating = 4
    else:
        chapter_decision = "revise"
        codex_decision = "pass"
        required_changes = ["缩短局前第二句，避免 UI 挤压。"]
        global_risks = ["第一章信息量略重。"]
        next_actions = ["由叙事 Agent 修改第一章局前短句。"]
        rating = 3

    review = root / "harness" / "story_review" / "fixture_review.json"
    write_json(
        review,
        {
            "review_version": 1,
            "candidate_pack_id": candidate.name,
            "candidate_pack_path": str(candidate.relative_to(root)),
            "candidate_validation_report": str(report.relative_to(root)),
            "reviewer": "fixture reviewer",
            "reviewed_at": "2026-05-26",
            "gate_decision": gate_decision,
            "summary": "人工审校记录 fixture，用于验证字段完整性。",
            "chapter_reviews": [
                {
                    "id": "frosting-grassland",
                    "decision": chapter_decision,
                    "tone_rating": rating,
                    "lore_consistency": rating,
                    "ui_fit": rating,
                    "spoiler_control": rating,
                    "notes": "章节短句语气清楚，和糖霜草地主题一致。",
                    "required_changes": required_changes,
                }
            ],
            "codex_reviews": [
                {
                    "id": "world-sugar-jar-stars",
                    "decision": codex_decision,
                    "tone_rating": 4,
                    "lore_consistency": 4,
                    "ui_fit": 4,
                    "unlock_fit": 4,
                    "notes": "图鉴解锁点和第一章碎片目标一致。",
                    "required_changes": [],
                }
            ],
            "global_risks": global_risks,
            "next_actions": next_actions,
        },
    )
    return review


class StoryCodexManualReviewValidatorTests(unittest.TestCase):
    def test_valid_ui_candidate_review_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidate, report_path = make_candidate(root)
            review = make_review(root, candidate, report_path)
            report = build_report(review, repo_root=root)

            self.assertEqual(report["decision"], "story_codex_manual_review_valid")
            self.assertEqual(report["chapter_review_count"], 1)
            self.assertEqual(report["codex_review_count"], 1)

    def test_repair_review_passes_with_required_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidate, report_path = make_candidate(root)
            review = make_review(root, candidate, report_path, gate_decision="repair")
            report = build_report(review, repo_root=root)

            self.assertEqual(report["decision"], "story_codex_manual_review_valid")
            self.assertEqual(report["repair_item_count"], 1)
            self.assertEqual(report["global_risk_count"], 1)

    def test_ui_candidate_rejects_required_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidate, report_path = make_candidate(root)
            review = make_review(root, candidate, report_path)
            payload = json.loads(review.read_text(encoding="utf-8"))
            payload["chapter_reviews"][0]["required_changes"] = ["还要改"]
            write_json(review, payload)
            report = build_report(review, repo_root=root)

            self.assertEqual(report["decision"], "story_codex_manual_review_invalid")
            self.assertTrue(any("ui_candidate gate cannot have required_changes" in error for error in report["errors"]))

    def test_missing_candidate_review_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidate, report_path = make_candidate(root)
            review = make_review(root, candidate, report_path)
            payload = json.loads(review.read_text(encoding="utf-8"))
            payload["codex_reviews"] = []
            write_json(review, payload)
            report = build_report(review, repo_root=root)

            self.assertEqual(report["decision"], "story_codex_manual_review_invalid")
            self.assertTrue(any("codex_reviews missing candidate ids" in error for error in report["errors"]))

    def test_forbidden_gate_decision_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidate, report_path = make_candidate(root)
            review = make_review(root, candidate, report_path)
            payload = json.loads(review.read_text(encoding="utf-8"))
            payload["gate_decision"] = "accepted_content"
            write_json(review, payload)
            report = build_report(review, repo_root=root)

            self.assertEqual(report["decision"], "story_codex_manual_review_invalid")
            self.assertTrue(any("forbidden gate_decision" in error for error in report["errors"]))

    def test_cli_writes_report_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidate, report_path = make_candidate(root)
            review = make_review(root, candidate, report_path)
            output_report = root / "review_report.json"
            markdown = root / "summary.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(review),
                    "--repo-root",
                    str(root),
                    "--report",
                    str(output_report),
                    "--markdown",
                    str(markdown),
                ],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(output_report.read_text(encoding="utf-8"))["decision"], "story_codex_manual_review_valid")
            self.assertIn("Story Codex Manual Review Validation", markdown.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
