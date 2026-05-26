#!/usr/bin/env python3
"""Regression tests for manual playtest review draft generation.

Run with:
    python3 harness/playtest/test_create_manual_playtest_review_draft.py
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
GENERATOR = SCRIPT_DIR / "create_manual_playtest_review_draft.py"
TEMPLATE = SCRIPT_DIR / "runtime_manual_review_template.json"

sys.path.insert(0, str(SCRIPT_DIR))

from create_manual_playtest_review_draft import build_draft  # noqa: E402
from validate_manual_review import REQUIRED_RUN_IDS, build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


class ManualPlaytestReviewDraftTests(unittest.TestCase):
    def test_build_draft_covers_every_required_run(self) -> None:
        draft = build_draft(
            TEMPLATE,
            "TODO: candidate id",
            "TODO: content hash",
            "TODO: human reviewer",
            "TODO: YYYY-MM-DD",
        )

        self.assertIn("AUTO-GENERATED DRAFT ONLY", draft["draft_notice"])
        self.assertEqual(draft["acceptance_decision"], "needs_more_runs")
        self.assertEqual([run["run_id"] for run in draft["runs"]], REQUIRED_RUN_IDS)
        self.assertTrue(all(run["gate_decision"] == "needs_more_runs" for run in draft["runs"]))
        self.assertIn("TODO", str(draft["runs"][0]["manual_review"]["fun_rating"]))
        self.assertIn("是否理解移动", draft["runs"][0]["required_observations"])

    def test_cli_writes_draft_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            out = Path(temp_dir) / "draft.json"

            result = subprocess.run(
                [
                    sys.executable,
                    str(GENERATOR),
                    "--template",
                    str(TEMPLATE),
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
            self.assertEqual(len(payload["runs"]), len(REQUIRED_RUN_IDS))
            self.assertEqual(payload["acceptance_decision"], "needs_more_runs")

    def test_draft_is_not_valid_manual_review_until_human_fills_todo(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            draft = build_draft(
                TEMPLATE,
                "TODO: candidate id",
                "TODO: content hash",
                "TODO: human reviewer",
                "TODO: YYYY-MM-DD",
            )
            draft_path = root / "harness" / "playtest" / "draft.json"
            write_json(draft_path, draft)

            report = build_report(draft_path, draft, strict_acceptance=True)

            self.assertEqual(report["decision"], "manual_review_invalid")
            self.assertTrue(any("fun_rating" in error for error in report["errors"]))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
