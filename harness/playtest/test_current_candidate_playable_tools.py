#!/usr/bin/env python3
"""Regression tests for current playable-candidate tools."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
GUIDE_SCRIPT = SCRIPT_DIR / "create_current_playable_content_guide.py"
AUDIT_SCRIPT = SCRIPT_DIR / "audit_current_playable_content_coverage.py"
QUICK_PLAY_SCRIPT = SCRIPT_DIR / "play_current_candidate.py"
TOUR_SCRIPT = SCRIPT_DIR / "run_current_content_tour.py"

sys.path.insert(0, str(SCRIPT_DIR))

from audit_current_playable_content_coverage import build_audit  # noqa: E402
from create_current_playable_content_guide import build_guide  # noqa: E402
from current_candidate import (  # noqa: E402
    CANDIDATE_ID,
    CONTENT_DIR,
    CONTENT_HASH,
    CONTENT_TOUR_RUNS,
    FORBIDDEN_MANUAL_FLAGS,
    QUICK_PLAY_PRESETS,
)
from play_current_candidate import PRESET_BY_ID, build_quick_play_command, validate_quick_play_command  # noqa: E402
from run_current_content_tour import RUN_BY_ID, build_tour_command, validate_tour_command  # noqa: E402


class CurrentPlayableCandidateToolTests(unittest.TestCase):
    def test_guide_targets_v51_candidate_counts(self) -> None:
        guide = build_guide(REPO_ROOT)

        self.assertEqual(guide["decision"], "playable_content_guide_candidate_only")
        self.assertEqual(guide["candidate_id"], CANDIDATE_ID)
        self.assertEqual(guide["content_hash"], CONTENT_HASH)
        self.assertEqual(guide["content_dir"], str(CONTENT_DIR))
        self.assertEqual(guide["summary"]["character_count"], 5)
        self.assertEqual(guide["summary"]["map_count"], 6)
        self.assertEqual(guide["summary"]["weapon_count"], 17)
        self.assertEqual(guide["summary"]["passive_count"], 17)
        self.assertEqual(guide["summary"]["evolution_count"], 17)
        self.assertEqual(guide["summary"]["enemy_count"], 12)
        self.assertEqual(guide["summary"]["boss_count"], 6)
        self.assertEqual(guide["summary"]["target_count_failures"], [])
        self.assertTrue(guide["candidate_state"]["candidate_only"])
        self.assertFalse(guide["candidate_state"]["accepted_content"])
        self.assertFalse(guide["candidate_state"]["runtime_integrated"])

    def test_quick_play_and_tour_cover_current_characters_and_maps(self) -> None:
        self.assertEqual(len(QUICK_PLAY_PRESETS), 6)
        self.assertEqual(len(CONTENT_TOUR_RUNS), 6)
        self.assertEqual(
            {preset.character_id for preset in QUICK_PLAY_PRESETS},
            {"jar-keeper", "bubble-courier", "cream-knight", "pudding-crafter", "sour-plum-doctor"},
        )
        self.assertEqual(
            {run.map_id for run in CONTENT_TOUR_RUNS},
            {
                "caramel-workshop",
                "cotton-cloud-pasture",
                "cracked-star-jar",
                "frosting-grassland",
                "jelly-platform",
                "soda-creek",
            },
        )

    def test_runtime_commands_target_v51_without_automation_flags(self) -> None:
        quick_command = build_quick_play_command(PRESET_BY_ID["default"])
        tour_command = build_tour_command(RUN_BY_ID["soda_bubble_courier"])

        for command in (quick_command, tour_command):
            self.assertIn(str(CONTENT_DIR), command)
            for flag in FORBIDDEN_MANUAL_FLAGS:
                self.assertNotIn(flag, command)
        self.assertIn("harness/telemetry/local/v51_quick_play_default.json", quick_command)
        self.assertIn("harness/telemetry/local/v51_content_tour_soda_bubble_courier.json", tour_command)
        validate_quick_play_command(quick_command)
        validate_tour_command(tour_command)

    def test_dry_run_launchers_print_current_candidate_commands(self) -> None:
        quick = subprocess.run(
            [sys.executable, str(QUICK_PLAY_SCRIPT), "--dry-run"],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )
        self.assertEqual(quick.returncode, 0, quick.stderr)
        self.assertIn("cargo run -p game_runtime", quick.stdout)
        self.assertIn("--content-dir harness/generated_candidates/2026-06-04_demo_buildcraft_repair_v51_full_pack", quick.stdout)
        self.assertIn("--character-id jar-keeper", quick.stdout)

        tour = subprocess.run(
            [sys.executable, str(TOUR_SCRIPT), "soda_bubble_courier", "--dry-run"],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )
        self.assertEqual(tour.returncode, 0, tour.stderr)
        self.assertIn("--character-id bubble-courier", tour.stdout)
        self.assertIn("--map-id soda-creek", tour.stdout)

    def test_audit_reports_current_entrypoint_coverage(self) -> None:
        audit = build_audit(REPO_ROOT)

        self.assertEqual(audit["candidate_id"], CANDIDATE_ID)
        self.assertEqual(audit["content_hash"], CONTENT_HASH)
        self.assertTrue(audit["candidate_state"]["candidate_only"])
        self.assertEqual(audit["summary"]["quick_play_preset_count"], 6)
        self.assertEqual(audit["summary"]["content_tour_run_count"], 6)
        self.assertNotIn("entrypoint_coverage", {item["category"] for item in audit["action_items"]})
        self.assertEqual(
            audit["coverage"]["quick_play_characters"],
            ["bubble-courier", "cream-knight", "jar-keeper", "pudding-crafter", "sour-plum-doctor"],
        )
        self.assertEqual(
            audit["coverage"]["content_tour_maps"],
            [
                "caramel-workshop",
                "cotton-cloud-pasture",
                "cracked-star-jar",
                "frosting-grassland",
                "jelly-platform",
                "soda-creek",
            ],
        )

    def test_guide_and_audit_cli_write_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            guide_report = root / "guide.json"
            guide_markdown = root / "guide.md"
            audit_report = root / "audit.json"
            audit_markdown = root / "audit.md"

            guide_result = subprocess.run(
                [
                    sys.executable,
                    str(GUIDE_SCRIPT),
                    "--report",
                    str(guide_report),
                    "--markdown",
                    str(guide_markdown),
                ],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(guide_result.returncode, 0, guide_result.stderr)
            self.assertEqual(json.loads(guide_report.read_text(encoding="utf-8"))["candidate_id"], CANDIDATE_ID)
            self.assertIn("v51 可玩内容导览", guide_markdown.read_text(encoding="utf-8"))

            audit_result = subprocess.run(
                [
                    sys.executable,
                    str(AUDIT_SCRIPT),
                    "--allow-repair",
                    "--report",
                    str(audit_report),
                    "--markdown",
                    str(audit_markdown),
                ],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(audit_result.returncode, 0, audit_result.stderr)
            self.assertEqual(json.loads(audit_report.read_text(encoding="utf-8"))["candidate_id"], CANDIDATE_ID)
            self.assertIn("v51 可玩内容覆盖审计", audit_markdown.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
