#!/usr/bin/env python3
"""Regression tests for final asset acceptance validation.

Run with:
    python3 harness/asset_review/test_validate_asset_final_acceptance.py
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
TEMPLATE = SCRIPT_DIR / "asset_final_acceptance_template.json"

sys.path.insert(0, str(SCRIPT_DIR))

from test_validate_asset_acceptance_manifest import (  # noqa: E402
    create_runtime_candidate,
    valid_audio_loudness_review,
    valid_final_acceptance,
    valid_runtime_preview_review,
)
from validate_asset_final_acceptance import build_report, load_json_object  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


class AssetFinalAcceptanceValidatorTests(unittest.TestCase):
    def test_valid_final_acceptance_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            create_runtime_candidate(repo_root)
            valid_runtime_preview_review(repo_root)
            valid_audio_loudness_review(repo_root)
            review = valid_final_acceptance(repo_root)

            report = build_report(review, repo_root)

            self.assertEqual(report["decision"], "asset_final_acceptance_valid")
            self.assertEqual(report["gate_decision"], "accepted_content")
            self.assertEqual(report["runtime_preview_review_decision"], "asset_runtime_preview_review_valid")
            self.assertEqual(report["audio_loudness_review_decision"], "asset_audio_loudness_review_valid")

    def test_template_is_invalid_until_human_fills_placeholders(self) -> None:
        report = build_report(TEMPLATE, REPO_ROOT)

        self.assertEqual(report["decision"], "asset_final_acceptance_invalid")
        self.assertTrue(any("placeholder" in error for error in report["errors"]))
        self.assertTrue(any("runtime_preview_review_file" in error for error in report["errors"]))

    def test_acceptance_cannot_claim_runtime_integration(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            create_runtime_candidate(repo_root)
            valid_runtime_preview_review(repo_root)
            valid_audio_loudness_review(repo_root)
            review = valid_final_acceptance(repo_root)
            payload = load_json_object(review)
            payload["checks"]["runtime_integrated"] = True
            write_json(review, payload)

            report = build_report(review, repo_root)

            self.assertEqual(report["decision"], "asset_final_acceptance_invalid")
            self.assertTrue(any("checks.runtime_integrated" in error for error in report["errors"]))

    def test_acceptance_requires_valid_audio_loudness_review(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            create_runtime_candidate(repo_root)
            valid_runtime_preview_review(repo_root)
            valid_audio_loudness_review(repo_root)
            review = valid_final_acceptance(repo_root)
            audio_review = repo_root / "harness/asset_review/audio_loudness_reviews/fixture-loudness.json"
            payload = load_json_object(audio_review)
            payload["decision"] = "needs_more_review"
            payload["unresolved_issues"] = ["语音和 sting 混音比例仍需重调。"]
            write_json(audio_review, payload)

            report = build_report(review, repo_root)

            self.assertEqual(report["decision"], "asset_final_acceptance_invalid")
            self.assertTrue(
                any("audio_loudness_review_file gate_decision must be audio_loudness_pass" in error for error in report["errors"])
            )


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
