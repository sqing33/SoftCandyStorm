#!/usr/bin/env python3
"""Regression tests for asset candidate manual review validation.

Run with:
    python3 harness/asset_review/test_validate_asset_candidate_manual_review.py
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
VALIDATOR = SCRIPT_DIR / "validate_asset_candidate_manual_review.py"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_asset_candidate_manual_review import build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def make_candidate(root: Path) -> tuple[Path, Path]:
    candidate = root / "asset" / "generated_candidates" / "fixture_asset_batch"
    write_json(
        candidate / "metadata" / "manifest.json",
        {
            "batch_id": "fixture_asset_batch",
            "generated_at": "2026-05-26",
            "project_rules": {
                "candidate_only": True,
                "accepted_content": False,
                "runtime_integrated": False,
                "required_next_steps": ["manual_asset_review"],
            },
            "assets": [
                {
                    "id": "player_sprite_fixture",
                    "type": "image",
                    "path": "images/player.png",
                    "qa_status": "repair",
                    "qa_notes": ["fixture"],
                },
                {
                    "id": "level_up_voice_fixture",
                    "type": "speech",
                    "path": "audio/level_up.mp3",
                    "qa_status": "needs_review",
                    "qa_notes": ["fixture"],
                },
            ],
        },
    )
    (candidate / "images").mkdir(parents=True, exist_ok=True)
    (candidate / "audio").mkdir(parents=True, exist_ok=True)
    (candidate / "images" / "player.png").write_bytes(b"png")
    (candidate / "audio" / "level_up.mp3").write_bytes(b"mp3")

    report = root / "harness" / "reports" / "fixture_asset_validation" / "summary.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("# Fixture Asset Validation\n", encoding="utf-8")
    return candidate, report


def make_review(root: Path, candidate: Path, report: Path, *, gate_decision: str = "asset_candidate") -> Path:
    if gate_decision == "asset_candidate":
        image_rating = 4
        audio_rating = 4
        image_decision = "pass"
        audio_decision = "pass"
        image_changes: list[str] = []
        audio_changes: list[str] = []
        global_risks: list[str] = []
    else:
        image_rating = 3
        audio_rating = 4
        image_decision = "revise"
        audio_decision = "pass"
        image_changes = ["清理边缘残留并重新生成 32px 预览。"]
        audio_changes = []
        global_risks = ["玩家图标小尺寸边缘仍需复核。"]

    review = root / "harness" / "asset_review" / "fixture_review.json"
    write_json(
        review,
        {
            "review_version": 1,
            "candidate_batch_id": candidate.name,
            "candidate_batch_path": str(candidate.relative_to(root)),
            "candidate_metadata_report": str(report.relative_to(root)),
            "reviewer": "fixture reviewer",
            "reviewed_at": "2026-05-26",
            "gate_decision": gate_decision,
            "summary": "人工素材审查 fixture，用于验证字段完整性。",
            "asset_reviews": [
                {
                    "id": "player_sprite_fixture",
                    "decision": image_decision,
                    "asset_type": "image",
                    "style_fit": image_rating,
                    "gameplay_readability": image_rating,
                    "provenance_confidence": image_rating,
                    "technical_readiness": image_rating,
                    "small_size_readability": image_rating,
                    "alpha_edge_quality": image_rating,
                    "allowed_candidate_uses": ["runtime_candidate"],
                    "notes": "玩家图标风格可爱，小尺寸轮廓清楚。",
                    "required_changes": image_changes,
                },
                {
                    "id": "level_up_voice_fixture",
                    "decision": audio_decision,
                    "asset_type": "speech",
                    "style_fit": audio_rating,
                    "gameplay_readability": audio_rating,
                    "provenance_confidence": audio_rating,
                    "technical_readiness": audio_rating,
                    "audio_clarity": audio_rating,
                    "loudness_readiness": audio_rating,
                    "duration_fit": audio_rating,
                    "allowed_candidate_uses": ["audio_candidate"],
                    "notes": "语音短促清楚，适合作为升级提示候选。",
                    "required_changes": audio_changes,
                },
            ],
            "global_risks": global_risks,
            "next_actions": ["继续小尺寸预览和 Runtime smoke 前复核。"],
        },
    )
    return review


class AssetCandidateManualReviewValidatorTests(unittest.TestCase):
    def test_valid_asset_candidate_review_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidate, report_path = make_candidate(root)
            review = make_review(root, candidate, report_path)
            report = build_report(review, repo_root=root)

            self.assertEqual(report["decision"], "asset_candidate_manual_review_valid")
            self.assertEqual(report["asset_review_count"], 2)
            self.assertEqual(report["expected_asset_count"], 2)

    def test_repair_review_passes_with_required_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidate, report_path = make_candidate(root)
            review = make_review(root, candidate, report_path, gate_decision="repair")
            report = build_report(review, repo_root=root)

            self.assertEqual(report["decision"], "asset_candidate_manual_review_valid")
            self.assertEqual(report["repair_item_count"], 1)
            self.assertEqual(report["global_risk_count"], 1)

    def test_asset_candidate_rejects_low_rating(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidate, report_path = make_candidate(root)
            review = make_review(root, candidate, report_path)
            payload = json.loads(review.read_text(encoding="utf-8"))
            payload["asset_reviews"][0]["small_size_readability"] = 3
            write_json(review, payload)
            report = build_report(review, repo_root=root)

            self.assertEqual(report["decision"], "asset_candidate_manual_review_invalid")
            self.assertTrue(any("asset_candidate gate requires all ratings" in error for error in report["errors"]))

    def test_missing_asset_review_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidate, report_path = make_candidate(root)
            review = make_review(root, candidate, report_path)
            payload = json.loads(review.read_text(encoding="utf-8"))
            payload["asset_reviews"] = payload["asset_reviews"][:1]
            write_json(review, payload)
            report = build_report(review, repo_root=root)

            self.assertEqual(report["decision"], "asset_candidate_manual_review_invalid")
            self.assertTrue(any("missing candidate asset ids" in error for error in report["errors"]))

    def test_forbidden_gate_decision_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidate, report_path = make_candidate(root)
            review = make_review(root, candidate, report_path)
            payload = json.loads(review.read_text(encoding="utf-8"))
            payload["gate_decision"] = "runtime_integrated"
            write_json(review, payload)
            report = build_report(review, repo_root=root)

            self.assertEqual(report["decision"], "asset_candidate_manual_review_invalid")
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
            self.assertEqual(json.loads(output_report.read_text(encoding="utf-8"))["decision"], "asset_candidate_manual_review_valid")
            self.assertIn("Asset Candidate Manual Review Validation", markdown.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
