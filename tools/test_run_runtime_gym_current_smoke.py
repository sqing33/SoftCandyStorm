#!/usr/bin/env python3
"""Regression tests for Runtime/Gym current smoke reporting.

Run with:
    python3 tools/test_run_runtime_gym_current_smoke.py
"""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from run_runtime_gym_current_smoke import REQUIRED_CHECKS, finalize_report  # noqa: E402


def valid_report() -> dict:
    return {
        "report_version": 1,
        "decision": "runtime_gym_current_smoke_pending",
        "commands": [
            {
                "argv": ["python3", "python/gym_env/smoke_test.py"],
                "expected_returncode": 0,
                "returncode": 0,
            },
            {
                "argv": ["cargo", "run", "-p", "game_runtime", "--", "--demo-input"],
                "expected_returncode": 0,
                "returncode": 0,
            },
        ],
        "checks": [
            {
                "id": check_id,
                "status": "pass",
                "summary": "ok",
            }
            for check_id in sorted(REQUIRED_CHECKS)
        ],
        "errors": [],
    }


class RuntimeGymCurrentSmokeReportTests(unittest.TestCase):
    def test_finalize_report_marks_valid_when_required_checks_pass(self) -> None:
        report = finalize_report(valid_report())

        self.assertEqual(report["decision"], "runtime_gym_current_smoke_valid")
        self.assertEqual(report["errors"], [])

    def test_finalize_report_fails_on_command_returncode_mismatch(self) -> None:
        report = valid_report()
        report["commands"][1]["returncode"] = 1

        finalized = finalize_report(report)

        self.assertEqual(finalized["decision"], "runtime_gym_current_smoke_invalid")
        self.assertTrue(any("returncode mismatch" in error for error in finalized["errors"]))

    def test_finalize_report_fails_when_required_check_missing(self) -> None:
        report = valid_report()
        report["checks"] = [
            copy.deepcopy(check)
            for check in report["checks"]
            if check["id"] != "runtime_performance_capture"
        ]

        finalized = finalize_report(report)

        self.assertEqual(finalized["decision"], "runtime_gym_current_smoke_invalid")
        self.assertTrue(any("runtime_performance_capture" in error for error in finalized["errors"]))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
