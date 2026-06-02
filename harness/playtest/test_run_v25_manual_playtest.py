#!/usr/bin/env python3
"""Regression tests for the v25 manual playtest launcher."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
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
    build_summary_command,
    build_runtime_command,
    first_missing_run,
    run_playtest_and_maybe_summarize,
    status_text,
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
        self.assertNotIn("summarize_v25_manual_playtest_reports.py", result.stdout)

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

    def test_first_missing_run_uses_local_report_presence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            self.assertEqual(first_missing_run(root).run_id, "new_001")
            for run in RUNS[:2]:
                path = root / run.report_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("{}\n", encoding="utf-8")

            self.assertEqual(first_missing_run(root).run_id, "new_003")
            self.assertIn("Reports: 2 / 9", status_text(root))

    def test_next_dry_run_launches_first_missing_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for run in RUNS[:2]:
                path = root / run.report_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("{}\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(LAUNCHER), "--repo-root", str(root), "--next", "--dry-run"],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("--seed 25003", result.stdout)
            self.assertIn("v25_manual_playtest_new_003.json", result.stdout)
            self.assertNotIn("--demo-input", result.stdout)

    def test_status_prints_next_missing_run(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [sys.executable, str(LAUNCHER), "--repo-root", temp_dir, "--status"],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Reports: 0 / 9", result.stdout)
            self.assertIn("Next run: new_001", result.stdout)

    def test_summary_command_uses_objective_summary_tool(self) -> None:
        command = build_summary_command()

        self.assertIn("summarize_v25_manual_playtest_reports.py", " ".join(command))
        self.assertIn("--allow-incomplete", command)

    def test_successful_runtime_refreshes_summary_after_run(self) -> None:
        runtime_command = ["cargo", "run", "-p", "game_runtime"]
        with patch("run_v25_manual_playtest.subprocess.run") as run_mock:
            run_mock.side_effect = [
                subprocess.CompletedProcess(runtime_command, 0),
                subprocess.CompletedProcess(build_summary_command(), 0),
            ]

            returncode = run_playtest_and_maybe_summarize(runtime_command, repo_root=REPO_ROOT)

        self.assertEqual(returncode, 0)
        self.assertEqual(run_mock.call_count, 2)
        self.assertEqual(run_mock.call_args_list[0].args[0], runtime_command)
        self.assertIn("summarize_v25_manual_playtest_reports.py", " ".join(run_mock.call_args_list[1].args[0]))

    def test_runtime_failure_keeps_runtime_exit_code_after_summary_attempt(self) -> None:
        runtime_command = ["cargo", "run", "-p", "game_runtime"]
        with patch("run_v25_manual_playtest.subprocess.run") as run_mock:
            run_mock.side_effect = [
                subprocess.CompletedProcess(runtime_command, 7),
                subprocess.CompletedProcess(build_summary_command(), 0),
            ]

            returncode = run_playtest_and_maybe_summarize(runtime_command, repo_root=REPO_ROOT)

        self.assertEqual(returncode, 7)
        self.assertEqual(run_mock.call_count, 2)

    def test_summary_can_be_skipped_for_launcher_recovery(self) -> None:
        runtime_command = ["cargo", "run", "-p", "game_runtime"]
        with patch("run_v25_manual_playtest.subprocess.run") as run_mock:
            run_mock.return_value = subprocess.CompletedProcess(runtime_command, 0)

            returncode = run_playtest_and_maybe_summarize(
                runtime_command,
                repo_root=REPO_ROOT,
                summarize_after=False,
            )

        self.assertEqual(returncode, 0)
        self.assertEqual(run_mock.call_count, 1)


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
