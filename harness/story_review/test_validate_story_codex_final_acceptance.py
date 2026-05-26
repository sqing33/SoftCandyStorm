#!/usr/bin/env python3
"""Regression tests for story/codex final acceptance validation.

Run with:
    python3 harness/story_review/test_validate_story_codex_final_acceptance.py
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
TEMPLATE = SCRIPT_DIR / "story_codex_final_acceptance_template.json"

sys.path.insert(0, str(SCRIPT_DIR))

from test_validate_story_codex_runtime_ui_review import valid_runtime_ui_review  # noqa: E402
from validate_story_codex_final_acceptance import build_report, load_json_object  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def valid_final_acceptance(repo_root: Path) -> Path:
    valid_runtime_ui_review(repo_root)
    path = repo_root / "harness/story_review/final_acceptance/story-pack-final.json"
    write_json(
        path,
        {
            "review_version": 1,
            "review_type": "story_codex_final_acceptance",
            "candidate_pack_id": "story-pack",
            "source_ui_candidate_manifest": "harness/story_review/ui_candidates/story-pack/ui_candidate_manifest.json",
            "runtime_ui_review_file": "harness/story_review/runtime_ui_reviews/story-pack-runtime-ui.json",
            "reviewer": "final-human-reviewer",
            "reviewed_at": "2026-05-26",
            "decision": "accepted_content",
            "summary": "最终人工接受该批剧情和图鉴文本进入 accepted story/codex 内容池。",
            "checks": {
                "accepts_story_codex_text": True,
                "accepted_content_only_after_reviews": True,
                "release_ready": False,
                "runtime_integrated": False,
            },
            "concrete_observations": [
                "章节短句没有破坏糖果风语气。",
                "图鉴条目解锁节奏和当前章节推进匹配。",
            ],
            "unresolved_issues": [],
        },
    )
    return path


class StoryCodexFinalAcceptanceValidatorTests(unittest.TestCase):
    def test_valid_final_acceptance_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            review = valid_final_acceptance(repo_root)

            report = build_report(review, repo_root)

            self.assertEqual(report["decision"], "story_codex_final_acceptance_valid")
            self.assertEqual(report["gate_decision"], "accepted_content")
            self.assertEqual(report["runtime_ui_review_decision"], "story_codex_runtime_ui_review_valid")

    def test_template_is_invalid_until_human_fills_placeholders(self) -> None:
        report = build_report(TEMPLATE, REPO_ROOT)

        self.assertEqual(report["decision"], "story_codex_final_acceptance_invalid")
        self.assertTrue(any("placeholder" in error for error in report["errors"]))
        self.assertTrue(any("runtime_ui_review_file" in error for error in report["errors"]))

    def test_acceptance_cannot_claim_release_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            review = valid_final_acceptance(repo_root)
            payload = load_json_object(review)
            payload["checks"]["release_ready"] = True
            write_json(review, payload)

            report = build_report(review, repo_root)

            self.assertEqual(report["decision"], "story_codex_final_acceptance_invalid")
            self.assertTrue(any("checks.release_ready" in error for error in report["errors"]))

    def test_acceptance_requires_valid_runtime_ui_review(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            review = valid_final_acceptance(repo_root)
            runtime_review = repo_root / "harness/story_review/runtime_ui_reviews/story-pack-runtime-ui.json"
            runtime_payload = load_json_object(runtime_review)
            runtime_payload["decision"] = "needs_more_review"
            runtime_payload["unresolved_issues"] = ["F3 文案仍需缩短。"]
            write_json(runtime_review, runtime_payload)

            report = build_report(review, repo_root)

            self.assertEqual(report["decision"], "story_codex_final_acceptance_invalid")
            self.assertTrue(
                any("runtime_ui_review_file gate_decision must be runtime_ui_review_pass" in error for error in report["errors"])
            )


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
