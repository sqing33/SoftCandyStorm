#!/usr/bin/env python3
"""Regression tests for the v25 manual playtest launcher."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
LAUNCHER = SCRIPT_DIR / "run_v25_manual_playtest.py"

sys.path.insert(0, str(SCRIPT_DIR))

from run_v25_manual_playtest import (  # noqa: E402
    CONTENT_DIR,
    FORBIDDEN_MANUAL_FLAGS,
    RUNS,
    RUN_BY_ID,
    build_runtime_command,
    validate_manual_command,
)


class V25ManualPlaytestLauncherTests(unittest.TestCase):
    def test_run_matrix_has_required_nine_runs(self) -> None:
        self.assertEqual(
            [run.run_id for run in RUNS],
            [
                "new_001",
                "new_002",
                "new_003",
                "skilled_001",
                "skilled_002",
                "skilled_003",
                "build_001",
                "build_002",
                "build_003",
            ],
        )
        self.assertEqual(len(RUN_BY_ID), 9)

    def test_runtime_command_targets_v25_candidate_without_automation_flags(self) -> None:
        command = build_runtime_command(RUN_BY_ID["build_003"])

        self.assertIn(str(CONTENT_DIR), command)
        self.assertIn("25023", command)
        self.assertIn("harness/telemetry/local/v25_manual_playtest_build_003.json", command)
        for flag in FORBIDDEN_MANUAL_FLAGS:
            self.assertNotIn(flag, command)
        validate_manual_command(command)

    def test_release_command_keeps_manual_runtime_args(self) -> None:
        command = build_runtime_command(RUN_BY_ID["new_001"], release=True)

        self.assertEqual(command[:3], ["cargo", "run", "--release"])
        self.assertIn("-p", command)
        self.assertIn("game_runtime", command)
        validate_manual_command(command)

    def test_dry_run_prints_command_without_launching_runtime(self) -> None:
        result = subprocess.run(
            [sys.executable, str(LAUNCHER), "new_001", "--dry-run"],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("cargo run -p game_runtime", result.stdout)
        self.assertIn("--content-dir", result.stdout)
        self.assertNotIn("--demo-input", result.stdout)
        self.assertNotIn("--simulation-speed", result.stdout)

    def test_list_prints_all_runs(self) -> None:
        result = subprocess.run(
            [sys.executable, str(LAUNCHER), "--list"],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Candidate: 2026-06-02_demo_buildcraft_repair_v25_full_pack", result.stdout)
        self.assertIn("new_001", result.stdout)
        self.assertIn("build_003", result.stdout)


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
