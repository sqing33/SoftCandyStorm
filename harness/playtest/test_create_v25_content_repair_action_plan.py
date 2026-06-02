#!/usr/bin/env python3
"""Regression tests for v25 playable-content repair action plans."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
SCRIPT = SCRIPT_DIR / "create_v25_content_repair_action_plan.py"

sys.path.insert(0, str(SCRIPT_DIR))

from create_v25_content_repair_action_plan import build_plan  # noqa: E402
from play_v25_candidate import QUICK_PLAY_PRESETS  # noqa: E402
from run_v25_content_tour import TOUR_RUNS  # noqa: E402
from run_v25_manual_playtest import CONTENT_DIR, RUNS  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def capture_payload(
    *,
    player_skill: str,
    seed: int,
    map_id: str = "frosting-grassland",
    character_id: str = "jar-keeper",
    terminal_kind: str = "victory",
    duration_seconds: float = 600.0,
    level: int = 6,
    kills: int = 260,
    damage_taken: float = 20.0,
    upgrade_choices: list[str] | None = None,
    average_fps: float = 58.0,
    boss_spawned: int = 1,
) -> dict:
    if upgrade_choices is None:
        upgrade_choices = [
            "rainbow-candy-shot-level-2",
            "cream-clockwork-level-2",
            "pudding-turret-level-2",
        ]
    return {
        "kind": "runtime_playtest_capture",
        "report_version": 1,
        "player_skill": player_skill,
        "input_mode": "manual",
        "simulation_speed": 1.0,
        "auto_exit_after_report": False,
        "content_dir": str(CONTENT_DIR),
        "run_config": {
            "seed": seed,
            "duration_seconds": 600.0,
            "map_id": map_id,
            "character_id": character_id,
        },
        "frame_metrics": {
            "average_fps": average_fps,
            "slow_frame_count_30fps": 0,
            "frame_count": 3600,
        },
        "event_counts": {
            "boss_spawned": boss_spawned,
            "player_damaged": 3,
            "xp_collected": 75,
            "level_up": level,
            "upgrade_offered": len(upgrade_choices),
            "upgrade_chosen": len(upgrade_choices),
            "run_ended": 1,
        },
        "samples": [{"time_seconds": 0.0}, {"time_seconds": 2.0}],
        "final_metrics": {
            "seed": seed,
            "duration_seconds": duration_seconds,
            "terminal": {
                "kind": terminal_kind,
                "time_seconds": duration_seconds,
                "reason": "duration_reached" if terminal_kind == "victory" else "player_defeated",
            },
            "kills": kills,
            "level": level,
            "xp_collected": 160.0,
            "xp_dropped": 190.0,
            "damage_taken": damage_taken,
            "max_enemy_count": 80,
            "max_projectile_count": 20,
            "upgrade_choices": upgrade_choices,
        },
    }


def write_all_valid_reports(root: Path) -> None:
    for preset in QUICK_PLAY_PRESETS:
        write_json(
            root / preset.report_path,
            capture_payload(
                player_skill="quickplay",
                seed=preset.seed,
                map_id=preset.map_id,
                character_id=preset.character_id,
            ),
        )
    for run in TOUR_RUNS:
        write_json(
            root / run.report_path,
            capture_payload(
                player_skill="tour",
                seed=run.seed,
                map_id=run.map_id,
                character_id=run.character_id,
            ),
        )
    for run in RUNS:
        write_json(root / run.report_path, capture_payload(player_skill=run.skill, seed=run.seed))


class V25ContentRepairActionPlanTests(unittest.TestCase):
    def test_current_state_lists_missing_playtest_reports(self) -> None:
        plan = build_plan(REPO_ROOT)

        self.assertEqual(plan["decision"], "v25_content_repair_action_plan_needs_playtest_reports")
        self.assertEqual(plan["summary"]["action_item_count"], 26)
        self.assertEqual(plan["summary"]["missing_report_count"], 21)
        self.assertEqual(plan["summary"]["content_coverage_gap_count"], 5)
        self.assertEqual(plan["summary"]["domain_counts"]["manual_playtest"], 9)
        self.assertEqual(plan["summary"]["domain_counts"]["coverage_audit"], 5)
        self.assertTrue(
            any("play_v25_candidate.py default" in item["command"] for item in plan["action_items"])
        )
        self.assertIn(
            "coverage_character_starter_without_evolution_bubble-courier",
            {item["id"] for item in plan["action_items"]},
        )
        self.assertIn("不批准", " ".join(plan["limitations"]))

    def test_metric_risks_create_repair_triage_items(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            preset = QUICK_PLAY_PRESETS[0]
            write_json(
                root / preset.report_path,
                capture_payload(
                    player_skill="quickplay",
                    seed=preset.seed,
                    map_id=preset.map_id,
                    character_id=preset.character_id,
                    terminal_kind="defeat",
                    duration_seconds=180.0,
                    level=1,
                    kills=25,
                    damage_taken=140.0,
                    upgrade_choices=[],
                    average_fps=50.0,
                    boss_spawned=0,
                ),
            )

            plan = build_plan(root)

            self.assertEqual(plan["decision"], "v25_content_repair_action_plan_needs_repair_triage")
            ids = {item["id"] for item in plan["action_items"]}
            self.assertIn("quick_play_risk_survival_default", ids)
            self.assertIn("quick_play_risk_contact_damage_default", ids)
            self.assertIn("quick_play_risk_runtime_readability_default", ids)

    def test_all_valid_reports_have_no_generated_repair_items(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_all_valid_reports(root)

            plan = build_plan(root)

            self.assertEqual(plan["decision"], "v25_content_repair_action_plan_ready_for_human_review")
            self.assertEqual(plan["summary"]["action_item_count"], 0)
            self.assertEqual(plan["summary"]["missing_report_count"], 0)

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            report_path = root / "out" / "plan.json"
            markdown_path = root / "out" / "summary.md"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--repo-root",
                    str(root),
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
            payload = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["decision"], "v25_content_repair_action_plan_needs_playtest_reports")
            markdown = markdown_path.read_text(encoding="utf-8")
            self.assertIn("# v25 内容修复行动计划", markdown)
            self.assertIn("play_v25_candidate.py default", markdown)


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
