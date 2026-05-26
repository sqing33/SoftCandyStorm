#!/usr/bin/env python3
"""Regression tests for asset candidate review draft generation.

Run with:
    python3 harness/asset_review/test_create_asset_candidate_review_draft.py
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
GENERATOR = SCRIPT_DIR / "create_asset_candidate_review_draft.py"

sys.path.insert(0, str(SCRIPT_DIR))

from create_asset_candidate_review_draft import build_draft  # noqa: E402
from validate_asset_candidate_manual_review import build_report as build_manual_review_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def make_candidate(root: Path) -> Path:
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
                    "id": "map_background_fixture",
                    "type": "image",
                    "path": "images/map.jpg",
                    "qa_status": "needs_visual_review",
                    "qa_notes": ["fixture"],
                },
                {
                    "id": "boss_voice_fixture",
                    "type": "speech",
                    "path": "audio/boss.mp3",
                    "qa_status": "needs_review",
                    "qa_notes": ["fixture"],
                },
                {
                    "id": "boss_sting_fixture",
                    "type": "music",
                    "path": "music/boss.mp3",
                    "qa_status": "needs_listening_review",
                    "qa_notes": ["fixture"],
                },
            ],
        },
    )
    return candidate


def make_metadata_report(root: Path) -> Path:
    report = root / "harness" / "reports" / "fixture_asset_validation" / "summary.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("# Fixture Asset Validation\n", encoding="utf-8")
    return report


class AssetCandidateReviewDraftTests(unittest.TestCase):
    def test_build_draft_covers_every_manifest_asset(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidate = make_candidate(root)

            draft = build_draft(
                candidate,
                root,
                "harness/reports/fixture_asset_validation/summary.md",
                "TODO: human reviewer",
                "TODO: YYYY-MM-DD",
            )

            self.assertEqual(draft["candidate_batch_id"], "fixture_asset_batch")
            self.assertIn("AUTO-GENERATED DRAFT ONLY", draft["draft_notice"])
            self.assertEqual(
                [item["id"] for item in draft["asset_reviews"]],
                ["map_background_fixture", "boss_voice_fixture", "boss_sting_fixture"],
            )
            self.assertEqual(draft["asset_reviews"][0]["allowed_candidate_uses"], ["concept_reference"])
            self.assertEqual(draft["asset_reviews"][1]["allowed_candidate_uses"], ["audio_candidate"])
            self.assertIn("TODO", str(draft["asset_reviews"][0]["style_fit"]))

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
                    "--metadata-report",
                    "harness/reports/fixture_asset_validation/summary.md",
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
            self.assertEqual(len(payload["asset_reviews"]), 3)
            self.assertEqual(payload["gate_decision"], "needs_more_review")

    def test_draft_is_not_valid_manual_review_until_human_fills_todo(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidate = make_candidate(root)
            report_path = make_metadata_report(root)
            draft = build_draft(
                candidate,
                root,
                str(report_path.relative_to(root)),
                "TODO: human reviewer",
                "TODO: YYYY-MM-DD",
            )
            draft_path = root / "harness" / "asset_review" / "draft.json"
            write_json(draft_path, draft)

            report = build_manual_review_report(draft_path, root)

            self.assertEqual(report["decision"], "asset_candidate_manual_review_invalid")
            self.assertTrue(any("style_fit must be an integer" in error for error in report["errors"]))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
