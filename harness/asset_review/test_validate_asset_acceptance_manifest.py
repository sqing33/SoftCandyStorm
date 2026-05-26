#!/usr/bin/env python3
"""Regression tests for final asset acceptance manifest validation.

Run with:
    python3 harness/asset_review/test_validate_asset_acceptance_manifest.py
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
TEMPLATE = SCRIPT_DIR / "asset_acceptance_manifest_template.json"

sys.path.insert(0, str(SCRIPT_DIR))

from promote_asset_runtime_candidate import promote_asset_runtime_candidate  # noqa: E402
from validate_asset_acceptance_manifest import build_report, load_json_object  # noqa: E402


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


def create_runtime_candidate(repo_root: Path) -> Path:
    create_candidate_batch(repo_root)
    review = valid_asset_review(repo_root)
    out_dir = repo_root / "harness/asset_review/runtime_candidates"
    promote_asset_runtime_candidate(review, repo_root, out_dir)
    return out_dir / "fixture_asset_batch/runtime_candidate_manifest.json"


def valid_runtime_preview_review(repo_root: Path) -> Path:
    path = repo_root / "harness/asset_review/runtime_preview_reviews/fixture-preview.json"
    write_json(
        path,
        {
            "review_version": 1,
            "review_type": "asset_runtime_preview_review",
            "candidate_batch_id": "fixture_asset_batch",
            "source_runtime_candidate_manifest": "harness/asset_review/runtime_candidates/fixture_asset_batch/runtime_candidate_manifest.json",
            "reviewer": "runtime-human-reviewer",
            "reviewed_at": "2026-05-26",
            "decision": "runtime_preview_pass",
            "summary": "Runtime 预览中图像和音频候选均可识别，未声明正式集成。",
            "checks": {
                "all_assets_visible_or_audible": True,
                "small_size_readable": True,
                "no_placeholder_leak": True,
                "no_runtime_integration_claim": True,
            },
            "concrete_observations": [
                "玩家图标在 64px 预览中仍能辨认轮廓。",
                "升级语音预览能在混音前单独听清。",
            ],
            "unresolved_issues": [],
        },
    )
    return path


def valid_audio_loudness_review(repo_root: Path) -> Path:
    path = repo_root / "harness/asset_review/audio_loudness_reviews/fixture-loudness.json"
    write_json(
        path,
        {
            "review_version": 1,
            "review_type": "asset_audio_loudness_review",
            "candidate_batch_id": "fixture_asset_batch",
            "source_runtime_candidate_manifest": "harness/asset_review/runtime_candidates/fixture_asset_batch/runtime_candidate_manifest.json",
            "reviewer": "audio-human-reviewer",
            "reviewed_at": "2026-05-26",
            "decision": "audio_loudness_pass",
            "summary": "语音清晰，无削波，响度适合进入接受候选。",
            "checks": {
                "dialogue_clear_if_present": True,
                "loudness_review_passed": True,
                "no_clipping": True,
                "loop_or_duration_fit": True,
            },
            "concrete_observations": [
                "升级语音峰值未削波。",
                "音频长度适合升级反馈，不会遮挡战斗提示。",
            ],
            "unresolved_issues": [],
        },
    )
    return path


def valid_final_acceptance(repo_root: Path) -> Path:
    path = repo_root / "harness/asset_review/final_acceptance/fixture-final.json"
    write_json(
        path,
        {
            "review_version": 1,
            "review_type": "asset_final_acceptance",
            "candidate_batch_id": "fixture_asset_batch",
            "source_runtime_candidate_manifest": "harness/asset_review/runtime_candidates/fixture_asset_batch/runtime_candidate_manifest.json",
            "reviewer": "final-human-reviewer",
            "reviewed_at": "2026-05-26",
            "decision": "accepted_content",
            "summary": "最终人工接受该批素材进入 accepted asset 内容池。",
            "checks": {
                "accepts_asset_batch": True,
                "accepted_content_only_after_reviews": True,
                "release_ready": False,
                "runtime_integrated": False,
            },
            "concrete_observations": [
                "图片和音频均保留了来源与后处理记录。",
                "本次接受只代表素材内容接受，不代表 Runtime 已使用这些文件。",
            ],
            "unresolved_issues": [],
        },
    )
    return path


def valid_acceptance_manifest(repo_root: Path, runtime_manifest: Path) -> Path:
    valid_runtime_preview_review(repo_root)
    valid_audio_loudness_review(repo_root)
    valid_final_acceptance(repo_root)
    manifest = repo_root / "harness/asset_review/accepted/fixture_asset_batch/acceptance_manifest.json"
    write_json(
        manifest,
        {
            "manifest_version": 1,
            "manifest_contract_id": "asset-acceptance-manifest-v0",
            "stage": "asset_acceptance",
            "candidate_batch_id": "fixture_asset_batch",
            "accepted_at": "2026-05-26T00:00:00Z",
            "source_runtime_candidate_manifest": "harness/asset_review/runtime_candidates/fixture_asset_batch/runtime_candidate_manifest.json",
            "runtime_preview_review_file": "harness/asset_review/runtime_preview_reviews/fixture-preview.json",
            "audio_loudness_review_file": "harness/asset_review/audio_loudness_reviews/fixture-loudness.json",
            "final_human_acceptance_file": "harness/asset_review/final_acceptance/fixture-final.json",
            "asset_count": 2,
            "accepted_assets": [
                {
                    "id": "player_sprite_fixture",
                    "type": "image",
                    "accepted_use": "runtime_asset",
                    "source_path": "images/player.png",
                },
                {
                    "id": "level_up_voice_fixture",
                    "type": "speech",
                    "accepted_use": "runtime_audio",
                    "source_path": "audio/level_up.mp3",
                },
            ],
            "rules": {
                "accepted_content": True,
                "runtime_integrated": False,
                "release_ready": False,
                "requires_runtime_candidate_manifest": True,
                "requires_runtime_preview": True,
                "requires_audio_loudness_review": True,
                "requires_final_human_acceptance": True,
                "generated_candidate_direct_acceptance_allowed": False,
            },
        },
    )
    return manifest


class AssetAcceptanceManifestValidatorTests(unittest.TestCase):
    def test_valid_acceptance_manifest_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            runtime_manifest = create_runtime_candidate(repo_root)
            manifest = valid_acceptance_manifest(repo_root, runtime_manifest)

            report = build_report(manifest, repo_root)

            self.assertEqual(report["decision"], "asset_acceptance_manifest_valid")
            self.assertEqual(report["runtime_candidate_manifest_decision"], "asset_runtime_candidate_manifest_valid")
            self.assertEqual(report["runtime_preview_review_decision"], "runtime_preview_pass")
            self.assertEqual(report["audio_loudness_review_decision"], "audio_loudness_pass")
            self.assertEqual(report["final_acceptance_decision"], "accepted_content")
            self.assertEqual(report["validated_asset_count"], 2)

    def test_template_is_invalid_without_human_evidence(self) -> None:
        report = build_report(TEMPLATE, REPO_ROOT)

        self.assertEqual(report["decision"], "asset_acceptance_manifest_invalid")
        self.assertTrue(any("placeholder" in error for error in report["errors"]))
        self.assertTrue(any("runtime_preview_review_file" in error for error in report["errors"]))
        self.assertTrue(any("final_human_acceptance_file" in error for error in report["errors"]))

    def test_rejects_release_ready_claim(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            runtime_manifest = create_runtime_candidate(repo_root)
            manifest = valid_acceptance_manifest(repo_root, runtime_manifest)
            payload = load_json_object(manifest)
            payload["rules"]["release_ready"] = True
            write_json(manifest, payload)

            report = build_report(manifest, repo_root)

            self.assertEqual(report["decision"], "asset_acceptance_manifest_invalid")
            self.assertTrue(any("rules.release_ready" in error for error in report["errors"]))

    def test_rejects_unpassed_loudness_review(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            runtime_manifest = create_runtime_candidate(repo_root)
            manifest = valid_acceptance_manifest(repo_root, runtime_manifest)
            loudness_review = repo_root / "harness/asset_review/audio_loudness_reviews/fixture-loudness.json"
            payload = load_json_object(loudness_review)
            payload["decision"] = "needs_more_review"
            write_json(loudness_review, payload)

            report = build_report(manifest, repo_root)

            self.assertEqual(report["decision"], "asset_acceptance_manifest_invalid")
            self.assertTrue(any("audio_loudness_review_file.decision" in error for error in report["errors"]))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
