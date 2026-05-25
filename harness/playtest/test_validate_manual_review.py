#!/usr/bin/env python3
"""Regression tests for the manual playtest review validator.

Run with:
    python3 harness/playtest/test_validate_manual_review.py
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
VALID_FIXTURE = SCRIPT_DIR / "fixtures" / "manual_review_valid.json"
INVALID_FIXTURE = SCRIPT_DIR / "fixtures" / "manual_review_missing_fields.json"
VALIDATOR = SCRIPT_DIR / "validate_manual_review.py"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_manual_review import build_report, load_json  # noqa: E402


class ManualReviewValidatorTests(unittest.TestCase):
    def test_valid_fixture_passes_strict_acceptance(self) -> None:
        payload = load_json(VALID_FIXTURE)
        report = build_report(VALID_FIXTURE, payload, strict_acceptance=True)

        self.assertEqual(report["decision"], "manual_review_valid")
        self.assertEqual(report["run_count"], 9)
        self.assertEqual(report["errors"], [])

    def test_missing_fields_fixture_fails_strict_acceptance(self) -> None:
        payload = load_json(INVALID_FIXTURE)
        report = build_report(INVALID_FIXTURE, payload, strict_acceptance=True)

        self.assertEqual(report["decision"], "manual_review_invalid")
        self.assertTrue(any("missing required run ids" in error for error in report["errors"]))
        self.assertTrue(any("forbidden gate_decision" in error for error in report["errors"]))
        self.assertTrue(any("accept_candidate requires content_hash" in error for error in report["errors"]))
        self.assertTrue(any("missing manual_review object" in error for error in report["errors"]))

    def test_cli_writes_report_and_markdown_for_valid_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = Path(temp_dir) / "report.json"
            markdown_path = Path(temp_dir) / "summary.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(VALID_FIXTURE),
                    "--strict-acceptance",
                    "--report",
                    str(report_path),
                    "--markdown",
                    str(markdown_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(report_path.exists())
            self.assertTrue(markdown_path.exists())
            self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["decision"], "manual_review_valid")
            self.assertIn("Manual Playtest Review Validation", markdown_path.read_text(encoding="utf-8"))

    def test_cli_returns_nonzero_for_invalid_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = Path(temp_dir) / "report.json"

            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(INVALID_FIXTURE),
                    "--strict-acceptance",
                    "--report",
                    str(report_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["decision"], "manual_review_invalid")


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
