#!/usr/bin/env python3
"""Regression tests for story/codex Runtime UI review validation.

Run with:
    python3 harness/story_review/test_validate_story_codex_runtime_ui_review.py
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
TEMPLATE = SCRIPT_DIR / "story_codex_runtime_ui_review_template.json"

sys.path.insert(0, str(SCRIPT_DIR))

from promote_story_codex_ui_candidate import promote_story_codex_ui_candidate  # noqa: E402
from validate_story_codex_runtime_ui_review import build_report, load_json_object  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def create_candidate_pack(repo_root: Path) -> None:
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


def create_ui_candidate(repo_root: Path) -> Path:
    create_candidate_pack(repo_root)
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
    out_dir = repo_root / "harness/story_review/ui_candidates"
    promote_story_codex_ui_candidate(review_path, repo_root, out_dir)
    return out_dir / "story-pack/ui_candidate_manifest.json"


def valid_runtime_ui_review(repo_root: Path) -> Path:
    create_ui_candidate(repo_root)
    path = repo_root / "harness/story_review/runtime_ui_reviews/story-pack-runtime-ui.json"
    write_json(
        path,
        {
            "review_version": 1,
            "review_type": "story_codex_runtime_ui_review",
            "candidate_pack_id": "story-pack",
            "source_ui_candidate_manifest": "harness/story_review/ui_candidates/story-pack/ui_candidate_manifest.json",
            "reviewer": "runtime-human-reviewer",
            "reviewed_at": "2026-05-26",
            "decision": "runtime_ui_review_pass",
            "summary": "F3 状态入口可读，未加载候选正文。",
            "checks": {
                "f3_entry_visible": True,
                "no_generated_candidate_text_loaded": True,
                "no_runtime_integration_claim": True,
                "layout_readable": True,
            },
            "concrete_observations": [
                "候选包 id、章节数和图鉴条目数可以在状态区读清。",
                "界面文本明确写出仍需 Runtime UI review 和最终人工接受。",
            ],
            "unresolved_issues": [],
        },
    )
    return path


class StoryCodexRuntimeUiReviewValidatorTests(unittest.TestCase):
    def test_valid_runtime_ui_review_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            review = valid_runtime_ui_review(repo_root)

            report = build_report(review, repo_root)

            self.assertEqual(report["decision"], "story_codex_runtime_ui_review_valid")
            self.assertEqual(report["gate_decision"], "runtime_ui_review_pass")
            self.assertEqual(report["ui_candidate_manifest_decision"], "story_codex_ui_candidate_manifest_valid")

    def test_template_is_invalid_until_human_fills_placeholders(self) -> None:
        report = build_report(TEMPLATE, REPO_ROOT)

        self.assertEqual(report["decision"], "story_codex_runtime_ui_review_invalid")
        self.assertTrue(any("placeholder" in error for error in report["errors"]))
        self.assertTrue(any("source_ui_candidate_manifest" in error for error in report["errors"]))

    def test_pass_requires_all_checks_true(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            review = valid_runtime_ui_review(repo_root)
            payload = load_json_object(review)
            payload["checks"]["layout_readable"] = False
            write_json(review, payload)

            report = build_report(review, repo_root)

            self.assertEqual(report["decision"], "story_codex_runtime_ui_review_invalid")
            self.assertTrue(any("checks.layout_readable" in error for error in report["errors"]))

    def test_pass_rejects_unresolved_issues(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            review = valid_runtime_ui_review(repo_root)
            payload = load_json_object(review)
            payload["unresolved_issues"] = ["F3 文案仍需缩短。"]
            write_json(review, payload)

            report = build_report(review, repo_root)

            self.assertEqual(report["decision"], "story_codex_runtime_ui_review_invalid")
            self.assertTrue(any("unresolved_issues" in error for error in report["errors"]))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
