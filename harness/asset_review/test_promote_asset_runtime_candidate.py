#!/usr/bin/env python3
"""Regression tests for asset Runtime candidate promotion.

Run with:
    python3 harness/asset_review/test_promote_asset_runtime_candidate.py
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from promote_asset_runtime_candidate import promote_asset_runtime_candidate


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


class AssetRuntimeCandidatePromotionTests(unittest.TestCase):
    def test_promotes_valid_asset_candidate_without_integrating_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            create_candidate_batch(repo_root)
            review = valid_asset_review(repo_root)
            out_dir = repo_root / "harness/asset_review/runtime_candidates"

            report = promote_asset_runtime_candidate(review, repo_root, out_dir)
            manifest = json.loads(
                (out_dir / "fixture_asset_batch/runtime_candidate_manifest.json").read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(report["decision"], "asset_runtime_candidate_promoted")
            self.assertEqual(report["asset_count"], 2)
            self.assertFalse(manifest["rules"]["accepted_content"])
            self.assertFalse(manifest["rules"]["runtime_integrated"])
            self.assertFalse(manifest["rules"]["release_ready"])
            self.assertEqual(
                manifest["assets"][0]["allowed_candidate_uses"],
                ["runtime_preview_candidate"],
            )
            self.assertTrue((out_dir / "fixture_asset_batch/manual_review.json").exists())

    def test_rejects_non_asset_candidate_review(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            create_candidate_batch(repo_root)
            review = valid_asset_review(repo_root)
            payload = json.loads(review.read_text(encoding="utf-8"))
            payload["gate_decision"] = "repair"
            payload["asset_reviews"][0]["decision"] = "revise"
            payload["asset_reviews"][0]["style_fit"] = 3
            payload["asset_reviews"][0]["required_changes"] = ["清理透明边缘后重新审查。"]
            payload["global_risks"] = ["玩家图标边缘仍需修复。"]
            payload["next_actions"] = ["修复后重新审查。"]
            write_json(review, payload)

            with self.assertRaisesRegex(ValueError, "gate_decision"):
                promote_asset_runtime_candidate(
                    review,
                    repo_root,
                    repo_root / "harness/asset_review/runtime_candidates",
                )

    def test_refuses_to_overwrite_existing_runtime_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            create_candidate_batch(repo_root)
            review = valid_asset_review(repo_root)
            out_dir = repo_root / "harness/asset_review/runtime_candidates"

            promote_asset_runtime_candidate(review, repo_root, out_dir)

            with self.assertRaises(FileExistsError):
                promote_asset_runtime_candidate(review, repo_root, out_dir)


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
