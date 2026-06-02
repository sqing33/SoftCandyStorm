#!/usr/bin/env python3
"""Regression tests for v25 manual playtest objective report summaries."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
SCRIPT = SCRIPT_DIR / "summarize_v25_manual_playtest_reports.py"

sys.path.insert(0, str(SCRIPT_DIR))

from run_v25_manual_playtest import CONTENT_DIR, RUNS  # noqa: E402
from summarize_v25_manual_playtest_reports import build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def capture_payload(run, *, input_mode: str = "manual", simulation_speed: float = 1.0) -> dict:
    return {
        "kind": "runtime_playtest_capture",
        "report_version": 1,
        "player_skill": run.skill,
        "input_mode": input_mode,
        "simulation_speed": simulation_speed,
        "auto_exit_after_report": False,
        "content_dir": str(CONTENT_DIR),
        "run_config": {
            "seed": run.seed,
            "duration_seconds": 600.0,
            "map_id": "frosting-grassland",
            "character_id": "jar-keeper",
        },
        "frame_metrics": {
            "average_fps": 58.5,
            "slow_frame_count_30fps": 0,
            "frame_count": 3600,
        },
        "event_counts": {
            "boss_spawned": 1,
            "player_damaged": 2,
            "xp_collected": 80,
            "level_up": 5,
            "upgrade_offered": 5,
            "upgrade_chosen": 5,
            "run_ended": 1,
        },
        "samples": [{"time_seconds": 0.0}, {"time_seconds": 2.0}],
        "final_metrics": {
            "seed": run.seed,
            "duration_seconds": 600.0,
            "terminal": {"kind": "victory", "time_seconds": 600.0, "reason": "duration_reached"},
            "kills": 300,
            "level": 6,
            "xp_collected": 180.0,
            "xp_dropped": 210.0,
            "damage_taken": 12.0,
            "max_enemy_count": 80,
            "max_projectile_count": 20,
            "upgrade_choices": ["rainbow-candy-shot-level-2", "pudding-turret-level-2"],
        },
    }


class V25ManualReportSummaryTests(unittest.TestCase):
    def test_current_state_has_no_reports(self) -> None:
        report = build_report(REPO_ROOT)

        self.assertEqual(report["decision"], "manual_report_summary_no_reports")
        self.assertEqual(report["summary"]["existing_report_count"], 0)
        self.assertEqual(report["summary"]["missing_report_count"], 9)

    def test_valid_single_report_is_partial_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            run = RUNS[0]
            write_json(root / run.report_path, capture_payload(run))

            report = build_report(root)

            self.assertEqual(report["decision"], "manual_report_summary_partial")
            self.assertEqual(report["summary"]["existing_report_count"], 1)
            self.assertEqual(report["summary"]["attention_count"], 0)
            first = report["runs"][0]
            self.assertEqual(first["objective_metrics"]["kills"], 300)
            self.assertEqual(first["objective_metrics"]["upgrade_choice_count"], 2)

    def test_demo_report_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            run = RUNS[0]
            write_json(root / run.report_path, capture_payload(run, input_mode="demo", simulation_speed=8.0))

            report = build_report(root)

            self.assertEqual(report["decision"], "manual_report_summary_needs_attention")
            self.assertGreaterEqual(report["summary"]["attention_count"], 2)
            self.assertIn("input_mode is demo", "\n".join(report["attention_items"]))

    def test_cli_writes_report_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            out = Path(temp_dir) / "summary.json"
            markdown = Path(temp_dir) / "summary.md"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--allow-incomplete",
                    "--report",
                    str(out),
                    "--markdown",
                    str(markdown),
                ],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(payload["decision"], "manual_report_summary_no_reports")
            self.assertIn("# v25 人工试玩报告客观摘要", markdown.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
