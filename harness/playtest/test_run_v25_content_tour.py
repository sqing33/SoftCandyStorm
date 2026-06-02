#!/usr/bin/env python3
"""Regression tests for the optional v25 content-tour launcher."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
LAUNCHER = SCRIPT_DIR / "run_v25_content_tour.py"

sys.path.insert(0, str(SCRIPT_DIR))

from run_v25_content_tour import (  # noqa: E402
    RUN_BY_ID,
    TOUR_RUNS,
    build_tour_command,
    first_missing_run,
    status_text,
    validate_tour_command,
)
from run_v25_manual_playtest import CONTENT_DIR, FORBIDDEN_MANUAL_FLAGS  # noqa: E402


class V25ContentTourLauncherTests(unittest.TestCase):
    def test_tour_matrix_covers_all_maps_and_characters(self) -> None:
        self.assertEqual(len(TOUR_RUNS), 6)
        self.assertEqual(
            {run.map_id for run in TOUR_RUNS},
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
            {run.character_id for run in TOUR_RUNS},
            {
                "jar-keeper",
                "bubble-courier",
                "cream-knight",
                "sour-plum-doctor",
                "pudding-crafter",
            },
        )

    def test_tour_command_targets_candidate_map_and_character_without_automation_flags(self) -> None:
        run = RUN_BY_ID["caramel_sour_plum_doctor"]
        command = build_tour_command(run)

        self.assertIn(str(CONTENT_DIR), command)
        self.assertIn("--character-id", command)
        self.assertIn("sour-plum-doctor", command)
        self.assertIn("--map-id", command)
        self.assertIn("caramel-workshop", command)
        self.assertIn("harness/telemetry/local/v25_content_tour_caramel_sour_plum_doctor.json", command)
        for flag in FORBIDDEN_MANUAL_FLAGS:
            self.assertNotIn(flag, command)
        validate_tour_command(command)

    def test_first_missing_run_uses_tour_report_presence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.assertEqual(first_missing_run(root).run_id, TOUR_RUNS[0].run_id)
            for run in TOUR_RUNS[:3]:
                path = root / run.report_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("{}\n", encoding="utf-8")

            self.assertEqual(first_missing_run(root).run_id, TOUR_RUNS[3].run_id)
            self.assertIn("Reports: 3 / 6", status_text(root))

    def test_list_prints_optional_tour_runs(self) -> None:
        result = subprocess.run(
            [sys.executable, str(LAUNCHER), "--list"],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("not acceptance evidence", result.stdout)
        self.assertIn("frosting_jar_keeper", result.stdout)
        self.assertIn("cracked_jar_keeper", result.stdout)

    def test_next_dry_run_launches_first_missing_tour_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for run in TOUR_RUNS[:1]:
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
            self.assertIn("--character-id bubble-courier", result.stdout)
            self.assertIn("--map-id soda-creek", result.stdout)
            self.assertNotIn("--demo-input", result.stdout)
            self.assertNotIn("--simulation-speed", result.stdout)


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
