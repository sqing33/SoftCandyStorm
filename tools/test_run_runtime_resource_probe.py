#!/usr/bin/env python3
"""Regression tests for Runtime resource probe runner.

Run with:
    python3 tools/test_run_runtime_resource_probe.py
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from run_runtime_resource_probe import build_report, max_rss_bytes_from_usage  # noqa: E402


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


class RuntimeResourceProbeTests(unittest.TestCase):
    def test_probe_passes_when_command_writes_valid_capture(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            capture_path = root / "capture.json"
            writer = root / "writer.py"
            writer.write_text(
                "import json, pathlib\n"
                f"pathlib.Path({str(capture_path)!r}).write_text(json.dumps({valid_capture()!r}))\n",
                encoding="utf-8",
            )

            report = build_report(
                command=[sys.executable, str(writer)],
                capture_path=capture_path,
                profile="smoke",
                max_rss_mib=2048.0,
                cwd=root,
            )

            self.assertEqual(report["decision"], "runtime_resource_probe_valid")
            self.assertEqual(report["returncode"], 0)
            self.assertEqual(report["performance_decision"], "runtime_performance_capture_valid")
            self.assertGreaterEqual(report["resource"]["max_rss_bytes"], 0)

    def test_probe_fails_when_capture_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            capture_path = root / "capture.json"
            bad_capture = valid_capture()
            bad_capture["privacy"]["telemetry_upload_enabled"] = True
            writer = root / "writer.py"
            writer.write_text(
                "import json, pathlib\n"
                f"pathlib.Path({str(capture_path)!r}).write_text(json.dumps({bad_capture!r}))\n",
                encoding="utf-8",
            )

            report = build_report(
                command=[sys.executable, str(writer)],
                capture_path=capture_path,
                profile="smoke",
                max_rss_mib=2048.0,
                cwd=root,
            )

            self.assertEqual(report["decision"], "runtime_resource_probe_invalid")
            self.assertIn("runtime performance capture validation did not pass", report["errors"])

    def test_probe_fails_when_capture_is_not_refreshed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            capture_path = root / "capture.json"
            write_json(capture_path, valid_capture())

            report = build_report(
                command=[sys.executable, "-c", "pass"],
                capture_path=capture_path,
                profile="smoke",
                max_rss_mib=2048.0,
                cwd=root,
            )

            self.assertEqual(report["decision"], "runtime_resource_probe_invalid")
            self.assertIn("capture path was not refreshed by the runtime command", report["errors"])
            self.assertFalse(report["capture_refreshed"])

    def test_max_rss_normalization_is_non_negative(self) -> None:
        import resource

        usage = resource.getrusage(resource.RUSAGE_SELF)
        self.assertGreaterEqual(max_rss_bytes_from_usage(usage), 0)


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
