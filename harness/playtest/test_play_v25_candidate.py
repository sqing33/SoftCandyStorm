#!/usr/bin/env python3
"""Regression tests for the v25 quick-play launcher."""

from __future__ import annotations

import subprocess
import sys
import unittest
from unittest.mock import patch
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
LAUNCHER = SCRIPT_DIR / "play_v25_candidate.py"

sys.path.insert(0, str(SCRIPT_DIR))

from play_v25_candidate import (  # noqa: E402
    DEFAULT_PRESET_ID,
    PRESET_BY_ID,
    QUICK_PLAY_PRESETS,
    build_summary_command,
    build_quick_play_command,
    list_presets,
    main,
    run_quick_play_and_maybe_summarize,
    validate_quick_play_command,
)
from run_v25_manual_playtest import CONTENT_DIR, FORBIDDEN_MANUAL_FLAGS  # noqa: E402


class V25QuickPlayLauncherTests(unittest.TestCase):
    def test_default_preset_is_beginner_baseline(self) -> None:
        preset = PRESET_BY_ID[DEFAULT_PRESET_ID]

        self.assertEqual(preset.character_id, "jar-keeper")
        self.assertEqual(preset.map_id, "frosting-grassland")
        self.assertEqual(preset.seed, 25301)

    def test_presets_cover_v25_characters_and_maps(self) -> None:
        self.assertEqual(len(QUICK_PLAY_PRESETS), 6)
        self.assertEqual(
            {preset.map_id for preset in QUICK_PLAY_PRESETS},
            {
                "frosting-grassland",
                "soda-creek",
                "cotton-cloud-pasture",
                "caramel-workshop",
                "jelly-platform",
                "cracked-star-jar",
            },
        )
        self.assertEqual(
            {preset.character_id for preset in QUICK_PLAY_PRESETS},
            {
                "jar-keeper",
                "bubble-courier",
                "cream-knight",
                "sour-plum-doctor",
                "pudding-crafter",
            },
        )

    def test_default_command_targets_candidate_without_automation_flags(self) -> None:
        command = build_quick_play_command(PRESET_BY_ID["default"])

        self.assertIn(str(CONTENT_DIR), command)
        self.assertIn("--character-id", command)
        self.assertIn("jar-keeper", command)
        self.assertIn("--map-id", command)
        self.assertIn("frosting-grassland", command)
        self.assertIn("--player-skill", command)
        self.assertIn("quickplay", command)
        self.assertIn("harness/telemetry/local/v25_quick_play_default.json", command)
        for flag in FORBIDDEN_MANUAL_FLAGS:
            self.assertNotIn(flag, command)
        validate_quick_play_command(command)

    def test_no_report_command_keeps_gameplay_args(self) -> None:
        command = build_quick_play_command(PRESET_BY_ID["speed"], report=False)

        self.assertIn("bubble-courier", command)
        self.assertIn("soda-creek", command)
        self.assertNotIn("--playtest-report", command)
        self.assertNotIn("--capture-interval", command)
        validate_quick_play_command(command)

    def test_list_presets_mentions_candidate_only(self) -> None:
        text = list_presets()

        self.assertIn("candidate-only", text)
        self.assertIn("default | 默认新手局", text)
        self.assertIn("final | 终局压力局", text)

    def test_dry_run_without_preset_launches_default(self) -> None:
        result = subprocess.run(
            [sys.executable, str(LAUNCHER), "--dry-run"],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("cargo run -p game_runtime", result.stdout)
        self.assertIn("--character-id jar-keeper", result.stdout)
        self.assertIn("--map-id frosting-grassland", result.stdout)
        self.assertIn("Candidate-only quick play", result.stdout)
        self.assertNotIn("--demo-input", result.stdout)
        self.assertNotIn("--simulation-speed", result.stdout)
        self.assertNotIn("summarize_v25_quick_play_reports.py", result.stdout)

    def test_dry_run_can_select_non_default_preset(self) -> None:
        result = subprocess.run(
            [sys.executable, str(LAUNCHER), "control", "--dry-run", "--no-report"],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--character-id sour-plum-doctor", result.stdout)
        self.assertIn("--map-id caramel-workshop", result.stdout)
        self.assertNotIn("--playtest-report", result.stdout)

    def test_launch_returns_runtime_exit_code(self) -> None:
        with patch("play_v25_candidate.subprocess.run") as run_mock:
            run_mock.return_value = subprocess.CompletedProcess(["cargo"], 3)
            with patch("sys.argv", [str(LAUNCHER), "defense", "--no-report", "--no-summary-after"]):
                returncode = main()

        self.assertEqual(returncode, 3)
        self.assertEqual(run_mock.call_count, 1)

    def test_summary_command_refreshes_quick_play_summary(self) -> None:
        command = build_summary_command()

        self.assertIn("harness/playtest/summarize_v25_quick_play_reports.py", command)
        self.assertIn("--allow-incomplete", command)

    def test_successful_runtime_refreshes_summary_after_run(self) -> None:
        runtime_command = ["cargo", "run", "-p", "game_runtime"]
        with patch("play_v25_candidate.subprocess.run") as run_mock:
            run_mock.side_effect = [
                subprocess.CompletedProcess(runtime_command, 0),
                subprocess.CompletedProcess(build_summary_command(), 0),
            ]

            returncode = run_quick_play_and_maybe_summarize(runtime_command, repo_root=REPO_ROOT)

        self.assertEqual(returncode, 0)
        self.assertEqual(run_mock.call_count, 2)
        self.assertEqual(run_mock.call_args_list[0].args[0], runtime_command)
        self.assertIn("summarize_v25_quick_play_reports.py", " ".join(run_mock.call_args_list[1].args[0]))

    def test_runtime_failure_keeps_runtime_exit_code_after_summary_attempt(self) -> None:
        runtime_command = ["cargo", "run", "-p", "game_runtime"]
        with patch("play_v25_candidate.subprocess.run") as run_mock:
            run_mock.side_effect = [
                subprocess.CompletedProcess(runtime_command, 7),
                subprocess.CompletedProcess(build_summary_command(), 0),
            ]

            returncode = run_quick_play_and_maybe_summarize(runtime_command, repo_root=REPO_ROOT)

        self.assertEqual(returncode, 7)
        self.assertEqual(run_mock.call_count, 2)

    def test_summary_can_be_skipped_for_launcher_recovery(self) -> None:
        runtime_command = ["cargo", "run", "-p", "game_runtime"]
        with patch("play_v25_candidate.subprocess.run") as run_mock:
            run_mock.return_value = subprocess.CompletedProcess(runtime_command, 0)

            returncode = run_quick_play_and_maybe_summarize(
                runtime_command,
                repo_root=REPO_ROOT,
                summarize_after=False,
            )

        self.assertEqual(returncode, 0)
        self.assertEqual(run_mock.call_count, 1)


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
