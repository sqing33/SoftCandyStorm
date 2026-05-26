#!/usr/bin/env python3
"""Regression tests for story/codex final acceptance manifest validation.

Run with:
    python3 harness/story_review/test_validate_story_codex_acceptance_manifest.py
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
TEMPLATE = SCRIPT_DIR / "story_codex_acceptance_manifest_template.json"

sys.path.insert(0, str(SCRIPT_DIR))

from promote_story_codex_ui_candidate import promote_story_codex_ui_candidate  # noqa: E402
from validate_story_codex_acceptance_manifest import build_report, load_json_object  # noqa: E402


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


def create_ui_candidate(repo_root: Path) -> Path:
    create_candidate_pack(repo_root)
    review = valid_ui_review(repo_root)
    out_dir = repo_root / "harness/story_review/ui_candidates"
    promote_story_codex_ui_candidate(review, repo_root, out_dir)
    return out_dir / "story-pack/ui_candidate_manifest.json"


def valid_runtime_ui_review(repo_root: Path, ui_manifest: Path) -> Path:
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


def valid_final_acceptance(repo_root: Path) -> Path:
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


def valid_acceptance_manifest(repo_root: Path, ui_manifest: Path) -> Path:
    valid_runtime_ui_review(repo_root, ui_manifest)
    valid_final_acceptance(repo_root)
    manifest = repo_root / "harness/story_review/accepted/story-pack/acceptance_manifest.json"
    write_json(
        manifest,
        {
            "manifest_version": 1,
            "manifest_contract_id": "story-codex-acceptance-manifest-v0",
            "stage": "story_codex_acceptance",
            "candidate_pack_id": "story-pack",
            "accepted_at": "2026-05-26T00:00:00Z",
            "source_ui_candidate_manifest": "harness/story_review/ui_candidates/story-pack/ui_candidate_manifest.json",
            "runtime_ui_review_file": "harness/story_review/runtime_ui_reviews/story-pack-runtime-ui.json",
            "final_human_acceptance_file": "harness/story_review/final_acceptance/story-pack-final.json",
            "chapter_count": 1,
            "codex_entry_count": 1,
            "rules": {
                "accepted_content": True,
                "runtime_integrated": False,
                "release_ready": False,
                "requires_ui_candidate_manifest": True,
                "requires_runtime_ui_review": True,
                "requires_final_human_acceptance": True,
                "generated_candidate_direct_acceptance_allowed": False,
            },
        },
    )
    return manifest


class StoryCodexAcceptanceManifestValidatorTests(unittest.TestCase):
    def test_valid_acceptance_manifest_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            ui_manifest = create_ui_candidate(repo_root)
            manifest = valid_acceptance_manifest(repo_root, ui_manifest)

            report = build_report(manifest, repo_root)

            self.assertEqual(report["decision"], "story_codex_acceptance_manifest_valid")
            self.assertEqual(report["ui_candidate_manifest_decision"], "story_codex_ui_candidate_manifest_valid")
            self.assertEqual(report["runtime_ui_review_decision"], "runtime_ui_review_pass")
            self.assertEqual(report["final_acceptance_decision"], "accepted_content")

    def test_template_is_invalid_without_human_evidence(self) -> None:
        report = build_report(TEMPLATE, REPO_ROOT)

        self.assertEqual(report["decision"], "story_codex_acceptance_manifest_invalid")
        self.assertTrue(any("placeholder" in error for error in report["errors"]))
        self.assertTrue(any("runtime_ui_review_file" in error for error in report["errors"]))
        self.assertTrue(any("final_human_acceptance_file" in error for error in report["errors"]))

    def test_rejects_runtime_integrated_claim(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            ui_manifest = create_ui_candidate(repo_root)
            manifest = valid_acceptance_manifest(repo_root, ui_manifest)
            payload = load_json_object(manifest)
            payload["rules"]["runtime_integrated"] = True
            write_json(manifest, payload)

            report = build_report(manifest, repo_root)

            self.assertEqual(report["decision"], "story_codex_acceptance_manifest_invalid")
            self.assertTrue(any("rules.runtime_integrated" in error for error in report["errors"]))

    def test_rejects_unpassed_runtime_ui_review(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            ui_manifest = create_ui_candidate(repo_root)
            manifest = valid_acceptance_manifest(repo_root, ui_manifest)
            runtime_review = repo_root / "harness/story_review/runtime_ui_reviews/story-pack-runtime-ui.json"
            payload = load_json_object(runtime_review)
            payload["decision"] = "needs_more_review"
            write_json(runtime_review, payload)

            report = build_report(manifest, repo_root)

            self.assertEqual(report["decision"], "story_codex_acceptance_manifest_invalid")
            self.assertTrue(any("runtime_ui_review_file.decision" in error for error in report["errors"]))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
