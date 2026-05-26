#!/usr/bin/env python3
"""Regression tests for Runtime performance capture validation.

Run with:
    python3 tools/test_validate_runtime_performance_capture.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "tools" / "validate_runtime_performance_capture.py"

sys.path.insert(0, str(REPO_ROOT / "tools"))

from validate_runtime_performance_capture import build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def valid_capture() -> dict:
    return {
        "kind": "runtime_playtest_capture",
        "report_version": 1,
        "player_skill": "machine-smoke",
        "input_mode": "demo",
        "simulation_speed": 6.0,
        "auto_exit_after_report": True,
        "run_number": 1,
        "content_dir": "content/base_demo",
        "run_config": {
            "seed": 12345,
            "map_id": "frosting-grassland",
            "character_id": "jar-keeper",
            "difficulty": "normal",
            "duration_seconds": 60.0,
            "tick_rate": 30,
            "ruleset_version": "prototype",
            "content_pack_ids": ["base-demo"],
            "starting_weapons": ["rainbow-candy-shot"],
            "starting_passives": [],
        },
        "frame_metrics": {
            "frame_count": 120,
            "total_frame_seconds": 2.0,
            "average_frame_seconds": 1.0 / 60.0,
            "average_fps": 60.0,
            "min_frame_seconds": 0.010,
            "max_frame_seconds": 0.025,
            "worst_frame_fps": 40.0,
            "slow_frame_count_45fps": 2,
            "slow_frame_count_30fps": 0,
        },
        "event_counts": {
            "enemy_spawned": 20,
            "boss_spawned": 1,
            "boss_phase_changed": 1,
            "boss_ability_used": 1,
            "weapon_fired": 100,
            "enemy_hit": 80,
            "enemy_killed": 15,
            "xp_dropped": 15,
            "xp_collected": 12,
            "level_up": 2,
            "upgrade_offered": 2,
            "upgrade_chosen": 2,
            "player_damaged": 1,
            "content_event_triggered": 1,
            "run_ended": 1,
        },
        "samples": [
            {
                "time_seconds": 0.0,
                "health": 120.0,
                "max_health": 120.0,
                "level": 1,
                "xp": 0.0,
                "xp_to_next_level": 10.0,
                "kills": 0,
                "visible_enemies": 0,
                "visible_pickups": 0,
                "visible_projectiles": 0,
                "active_hazards": 0,
                "active_effects": 0,
                "upgrade_options": 0,
                "last_event_kind": "system",
            },
            {
                "time_seconds": 60.0,
                "health": 80.0,
                "max_health": 120.0,
                "level": 3,
                "xp": 5.0,
                "xp_to_next_level": 20.0,
                "kills": 15,
                "visible_enemies": 18,
                "visible_pickups": 4,
                "visible_projectiles": 8,
                "active_hazards": 1,
                "active_effects": 12,
                "upgrade_options": 0,
                "last_event_kind": "terminal",
            },
        ],
        "final_metrics": {
            "seed": 12345,
            "tick_rate": 30,
            "duration_seconds": 60.0,
            "terminal": {
                "kind": "victory",
                "time_seconds": 60.0,
                "reason": "duration target reached",
                "final_level": 3,
                "kills": 15,
            },
            "kills": 15,
            "level": 3,
            "xp_collected": 60.0,
            "xp_dropped": 70.0,
            "damage_dealt_by_weapon": 300.0,
            "damage_taken": 40.0,
            "max_enemy_count": 20,
            "max_projectile_count": 10,
            "upgrade_choices": ["rainbow-candy-shot-level-2"],
        },
        "privacy": {
            "telemetry_upload_enabled": False,
            "raw_replay_upload_enabled": False,
            "crash_report_upload_enabled": False,
            "local_capture_only": True,
            "upload_transport": "not_implemented",
        },
        "manual_review": {
            "fun_rating": None,
            "clarity_rating": None,
            "difficulty_rating": None,
            "projectile_readability": None,
            "hit_feedback": None,
            "xp_pickup_rhythm": None,
            "boss_spawn_clarity": None,
            "death_reason_clarity": None,
            "notes": "TODO",
            "tags": [],
            "next_actions": [],
        },
    }


class RuntimePerformanceCaptureValidatorTests(unittest.TestCase):
    def test_valid_capture_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            capture_path = Path(temp_dir) / "capture.json"
            write_json(capture_path, valid_capture())

            report = build_report(capture_path)

            self.assertEqual(report["decision"], "runtime_performance_capture_valid")
            self.assertEqual(report["errors"], [])
            self.assertEqual(report["summary"]["samples"]["max_visible_enemies"], 18)
            self.assertAlmostEqual(report["summary"]["frame_metrics"]["average_fps"], 60.0)

    def test_low_average_fps_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            capture = valid_capture()
            capture["frame_metrics"]["frame_count"] = 50
            capture["frame_metrics"]["total_frame_seconds"] = 2.0
            capture["frame_metrics"]["average_frame_seconds"] = 0.04
            capture["frame_metrics"]["average_fps"] = 25.0
            capture_path = Path(temp_dir) / "capture.json"
            write_json(capture_path, capture)

            report = build_report(capture_path)

            self.assertEqual(report["decision"], "runtime_performance_capture_invalid")
            self.assertTrue(any("average_fps" in error for error in report["errors"]))

    def test_entity_ceiling_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            capture = valid_capture()
            capture["samples"][1]["visible_enemies"] = 141
            capture["final_metrics"]["max_enemy_count"] = 141
            capture_path = Path(temp_dir) / "capture.json"
            write_json(capture_path, capture)

            report = build_report(capture_path)

            self.assertEqual(report["decision"], "runtime_performance_capture_invalid")
            self.assertTrue(any("visible_enemies" in error for error in report["errors"]))
            self.assertTrue(any("max_enemy_count" in error for error in report["errors"]))

    def test_missing_terminal_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            capture = valid_capture()
            capture["final_metrics"]["terminal"] = None
            capture_path = Path(temp_dir) / "capture.json"
            write_json(capture_path, capture)

            report = build_report(capture_path)

            self.assertEqual(report["decision"], "runtime_performance_capture_invalid")
            self.assertTrue(any("terminal" in error for error in report["errors"]))

    def test_privacy_upload_enabled_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            capture = valid_capture()
            capture["privacy"]["telemetry_upload_enabled"] = True
            capture_path = Path(temp_dir) / "capture.json"
            write_json(capture_path, capture)

            report = build_report(capture_path)

            self.assertEqual(report["decision"], "runtime_performance_capture_invalid")
            self.assertTrue(any("telemetry_upload_enabled" in error for error in report["errors"]))

    def test_cli_writes_report_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            capture_path = root / "capture.json"
            report_path = root / "report.json"
            markdown_path = root / "summary.md"
            write_json(capture_path, valid_capture())

            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(capture_path),
                    "--report",
                    str(report_path),
                    "--markdown",
                    str(markdown_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                json.loads(report_path.read_text(encoding="utf-8"))["decision"],
                "runtime_performance_capture_valid",
            )
            self.assertIn("Runtime Performance Capture Validation", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
