#!/usr/bin/env python3
"""Regression tests for asset Runtime candidate manifest validation.

Run with:
    python3 harness/asset_review/test_validate_asset_runtime_candidate_manifest.py
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
TEMPLATE = SCRIPT_DIR / "asset_runtime_candidate_manifest_template.json"

sys.path.insert(0, str(SCRIPT_DIR))

from promote_asset_runtime_candidate import promote_asset_runtime_candidate  # noqa: E402
from validate_asset_runtime_candidate_manifest import build_report, load_json_object  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def create_candidate_batch(repo_root: Path) -> Path:
    candidate = repo_root / "asset/generated_candidates/fixture_asset_batch"
    write_json(
        candidate / "metadata/manifest.json",
        {
            "batch_id": "fixture_asset_batch",
            "generated_at": "2026-05-26",
            "project_rules": {
                "candidate_only": True,
                "accepted_content": False,
                "runtime_integrated": False,
            },
            "assets": [
                {
                    "id": "player_sprite_fixture",
                    "type": "image",
                    "path": "images/player.png",
                    "qa_status": "needs_visual_review",
                },
                {
                    "id": "level_up_voice_fixture",
                    "type": "speech",
                    "path": "audio/level_up.mp3",
                    "qa_status": "needs_listening_review",
                },
            ],
        },
    )
    (candidate / "images").mkdir(parents=True, exist_ok=True)
    (candidate / "audio").mkdir(parents=True, exist_ok=True)
    (candidate / "images/player.png").write_bytes(b"png")
    (candidate / "audio/level_up.mp3").write_bytes(b"mp3")
    report = repo_root / "harness/reports/assets/summary.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("# Asset metadata validation\n", encoding="utf-8")
    return candidate


def valid_asset_review(repo_root: Path) -> Path:
    review_path = repo_root / "harness/asset_review/reviews/fixture_asset_review.json"
    write_json(
        review_path,
        {
            "review_version": 1,
            "candidate_batch_id": "fixture_asset_batch",
            "candidate_batch_path": "asset/generated_candidates/fixture_asset_batch",
            "candidate_metadata_report": "harness/reports/assets/summary.md",
            "reviewer": "human-reviewer",
            "reviewed_at": "2026-05-26",
            "gate_decision": "asset_candidate",
            "summary": "人工素材审查确认风格、可读性、来源和技术准备度可进入 Runtime 候选。",
            "asset_reviews": [
                {
                    "id": "player_sprite_fixture",
                    "decision": "pass",
                    "asset_type": "image",
                    "style_fit": 4,
                    "gameplay_readability": 4,
                    "provenance_confidence": 4,
                    "technical_readiness": 4,
                    "small_size_readability": 4,
                    "alpha_edge_quality": 4,
                    "allowed_candidate_uses": ["runtime_preview_candidate"],
                    "notes": "玩家图标轮廓清晰，候选阶段适合进入 Runtime 预览。",
                    "required_changes": [],
                },
                {
                    "id": "level_up_voice_fixture",
                    "decision": "pass",
                    "asset_type": "speech",
                    "style_fit": 4,
                    "gameplay_readability": 4,
                    "provenance_confidence": 4,
                    "technical_readiness": 4,
                    "audio_clarity": 4,
                    "loudness_readiness": 4,
                    "duration_fit": 4,
                    "allowed_candidate_uses": ["audio_preview_candidate"],
                    "notes": "升级语音短促清楚，候选阶段适合进入听感预览。",
                    "required_changes": [],
                },
            ],
            "global_risks": [],
            "next_actions": [],
        },
    )
    return review_path


class AssetRuntimeCandidateManifestValidatorTests(unittest.TestCase):
    def test_promoted_manifest_validates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            create_candidate_batch(repo_root)
            review = valid_asset_review(repo_root)
            out_dir = repo_root / "harness/asset_review/runtime_candidates"
            promote_asset_runtime_candidate(review, repo_root, out_dir)

            manifest = out_dir / "fixture_asset_batch/runtime_candidate_manifest.json"
            report = build_report(manifest, repo_root)

            self.assertEqual(report["decision"], "asset_runtime_candidate_manifest_valid")
            self.assertEqual(report["manual_gate_decision"], "asset_candidate")
            self.assertEqual(report["asset_count"], 2)
            self.assertEqual(report["validated_asset_count"], 2)

    def test_template_is_invalid_until_human_review_exists(self) -> None:
        report = build_report(TEMPLATE, REPO_ROOT)

        self.assertEqual(report["decision"], "asset_runtime_candidate_manifest_invalid")
        self.assertTrue(any("placeholder" in error for error in report["errors"]))
        self.assertTrue(any("manual_review_file" in error for error in report["errors"]))

    def test_rejects_manifest_that_claims_release_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            create_candidate_batch(repo_root)
            review = valid_asset_review(repo_root)
            out_dir = repo_root / "harness/asset_review/runtime_candidates"
            promote_asset_runtime_candidate(review, repo_root, out_dir)
            manifest = out_dir / "fixture_asset_batch/runtime_candidate_manifest.json"
            payload = load_json_object(manifest)
            payload["rules"]["release_ready"] = True
            write_json(manifest, payload)

            report = build_report(manifest, repo_root)

            self.assertEqual(report["decision"], "asset_runtime_candidate_manifest_invalid")
            self.assertTrue(any("rules.release_ready" in error for error in report["errors"]))

    def test_asset_count_must_match_source_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            create_candidate_batch(repo_root)
            review = valid_asset_review(repo_root)
            out_dir = repo_root / "harness/asset_review/runtime_candidates"
            promote_asset_runtime_candidate(review, repo_root, out_dir)
            manifest = out_dir / "fixture_asset_batch/runtime_candidate_manifest.json"
            payload = load_json_object(manifest)
            payload["asset_count"] = 99
            write_json(manifest, payload)

            report = build_report(manifest, repo_root)

            self.assertEqual(report["decision"], "asset_runtime_candidate_manifest_invalid")
            self.assertTrue(any("asset_count" in error for error in report["errors"]))

    def test_asset_metadata_must_match_source_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            create_candidate_batch(repo_root)
            review = valid_asset_review(repo_root)
            out_dir = repo_root / "harness/asset_review/runtime_candidates"
            promote_asset_runtime_candidate(review, repo_root, out_dir)
            manifest = out_dir / "fixture_asset_batch/runtime_candidate_manifest.json"
            payload = load_json_object(manifest)
            payload["assets"][0]["qa_status"] = "accepted"
            write_json(manifest, payload)

            report = build_report(manifest, repo_root)

            self.assertEqual(report["decision"], "asset_runtime_candidate_manifest_invalid")
            self.assertTrue(any("qa_status" in error for error in report["errors"]))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
