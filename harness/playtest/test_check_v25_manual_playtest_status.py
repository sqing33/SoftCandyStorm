#!/usr/bin/env python3
"""Regression tests for the v25 manual playtest status checker."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
CHECKER = SCRIPT_DIR / "check_v25_manual_playtest_status.py"

sys.path.insert(0, str(SCRIPT_DIR))

from check_v25_manual_playtest_status import DEFAULT_DRAFT, build_report  # noqa: E402
from run_v25_manual_playtest import CANDIDATE_ID, CONTENT_HASH, RUNS  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def complete_review_payload() -> dict:
    return {
        "candidate_id": CANDIDATE_ID,
        "content_hash": CONTENT_HASH,
        "reviewer": "human reviewer",
        "reviewed_at": "2026-06-02",
        "summary": "九局试玩记录完整。",
        "acceptance_decision": "accept_candidate",
        "runs": [
            {
                "run_id": run.run_id,
                "gate_decision": "playtest_pass",
                "manual_review": {
                    "fun_rating": 4,
                    "clarity_rating": 4,
                    "difficulty_rating": 3,
                    "projectile_readability": 4,
                    "hit_feedback": 4,
                    "xp_pickup_rhythm": 4,
                    "boss_spawn_clarity": 4,
                    "death_reason_clarity": 4,
                    "notes": f"{run.run_id} 有具体人工观察。",
                    "tags": ["fun"],
                    "next_actions": ["继续 strict acceptance 校验。"],
                },
            }
            for run in RUNS
        ],
    }


class V25ManualPlaytestStatusTests(unittest.TestCase):
    def test_missing_reports_and_todo_draft_are_incomplete(self) -> None:
        report = build_report(REPO_ROOT)

        self.assertEqual(report["decision"], "manual_playtest_incomplete")
        self.assertEqual(report["summary"]["missing_report_count"], 9)
        self.assertTrue(report["summary"]["draft_has_todo"])

    def test_complete_local_evidence_is_ready_for_strict_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_json(root / DEFAULT_DRAFT, complete_review_payload())
            for run in RUNS:
                write_json(root / run.report_path, {"run_id": run.run_id})

            report = build_report(root)

            self.assertEqual(report["decision"], "manual_playtest_ready_for_strict_validation")
            self.assertEqual(report["summary"]["existing_report_count"], 9)
            self.assertFalse(report["summary"]["draft_has_todo"])
            self.assertEqual(report["errors"], [])

    def test_cli_allows_current_incomplete_status_when_requested(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            out = Path(temp_dir) / "status.json"
            summary = Path(temp_dir) / "summary.md"
            result = subprocess.run(
                [
                    sys.executable,
                    str(CHECKER),
                    "--allow-incomplete",
                    "--report",
                    str(out),
                    "--markdown",
                    str(summary),
                ],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(payload["decision"], "manual_playtest_incomplete")
            self.assertIn("# v25 Manual Playtest Status", summary.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
