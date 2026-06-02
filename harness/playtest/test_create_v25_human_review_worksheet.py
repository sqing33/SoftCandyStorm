#!/usr/bin/env python3
"""Regression tests for the v25 human review worksheet generator."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
GENERATOR = SCRIPT_DIR / "create_v25_human_review_worksheet.py"

sys.path.insert(0, str(SCRIPT_DIR))

from create_v25_human_review_worksheet import build_markdown  # noqa: E402
from run_v25_manual_playtest import CANDIDATE_ID, CONTENT_HASH, RUNS  # noqa: E402


class V25HumanReviewWorksheetTests(unittest.TestCase):
    def test_markdown_contains_candidate_and_all_runs(self) -> None:
        markdown = build_markdown(REPO_ROOT)

        self.assertIn(CANDIDATE_ID, markdown)
        self.assertIn(CONTENT_HASH, markdown)
        self.assertIn("pudding-turret", markdown)
        for run in RUNS:
            self.assertIn(f"### {run.run_id}", markdown)
            self.assertIn(f"python3 harness/playtest/run_v25_manual_playtest.py {run.run_id}", markdown)

    def test_markdown_warns_against_automated_human_evidence(self) -> None:
        markdown = build_markdown(REPO_ROOT)

        self.assertIn("Human evidence must not use `--demo-input`", markdown)
        self.assertIn("Do not replace human observations with automated demo-input evidence.", markdown)
        self.assertIn("This worksheet is not acceptance evidence by itself", markdown)

    def test_cli_writes_worksheet(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            out = Path(temp_dir) / "worksheet.md"
            result = subprocess.run(
                [sys.executable, str(GENERATOR), "--out", str(out)],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(out.exists())
            text = out.read_text(encoding="utf-8")
            self.assertIn("# v25 Human Review Worksheet", text)
            self.assertIn("## Validation Commands", text)


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
