#!/usr/bin/env python3
"""Regression tests for first-demo readiness validation.

Run with:
    python3 tools/test_validate_demo_readiness.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
VALIDATOR = SCRIPT_DIR / "validate_demo_readiness.py"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_demo_readiness import build_report  # noqa: E402


class DemoReadinessValidatorTests(unittest.TestCase):
    def test_current_repo_is_honestly_not_ready(self) -> None:
        report = build_report(
            REPO_ROOT,
            REPO_ROOT / "content/base_demo",
            REPO_ROOT / "harness/generated_candidates/2026-05-26_phase4_roster_gap_full_pack",
        )

        self.assertEqual(report["decision"], "demo_not_ready")
        self.assertEqual(report["errors"], [])
        gates = {gate["id"]: gate for gate in report["gates"]}
        self.assertEqual(gates["formal_content_pack"]["status"], "blocked")
        self.assertEqual(gates["candidate_content_pack"]["status"], "pass")
        self.assertEqual(gates["manual_playtest"]["status"], "waiting")
        self.assertEqual(gates["release_state"]["status"], "blocked")

    def test_missing_candidate_path_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report = build_report(
                REPO_ROOT,
                REPO_ROOT / "content/base_demo",
                Path(temp_dir) / "missing_candidate",
            )

            self.assertEqual(report["decision"], "demo_readiness_invalid")
            self.assertTrue(any("content_dir does not exist" in error for error in report["errors"]))

    def test_cli_allow_not_ready_writes_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = Path(temp_dir) / "demo_readiness.json"
            markdown_path = Path(temp_dir) / "summary.md"
            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--repo-root",
                    str(REPO_ROOT),
                    "--report",
                    str(report_path),
                    "--markdown",
                    str(markdown_path),
                    "--allow-not-ready",
                ],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["decision"], "demo_not_ready")
            self.assertIn("Demo Readiness Audit", markdown_path.read_text(encoding="utf-8"))

    def test_cli_without_allow_not_ready_fails(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), "--repo-root", str(REPO_ROOT)],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
