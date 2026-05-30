#!/usr/bin/env python3
"""Regression tests for fixed-window RL action plan creation."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from create_rl_fixed_window_action_plan import build_plan, parse_validation_windows  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def analysis_payload(seconds: int, maps: list[dict]) -> dict:
    return {
        "report_version": 1,
        "decision": "rl_policy_failure_analysis_recorded",
        "gate_decision": "multimap_comparison_recorded_needs_policy_repair",
        "seconds": seconds,
        "maps": maps,
    }


def map_payload(
    map_id: str,
    *,
    opening: int = 0,
    mid: int = 0,
    late: int = 0,
    win_rate: float = 0.0,
) -> dict:
    total = max(1, opening + mid + late)
    return {
        "map_id": map_id,
        "failure_count": opening + mid + late,
        "win_rate": win_rate,
        "average_failure_survival_seconds": 91.0,
        "policy_dominant_action": {"action": "7", "ratio": 0.42},
        "failure_time_bucket_distribution": {
            "opening_lt_60": {"count": opening, "ratio": opening / total},
            "mid_60_to_180": {"count": mid, "ratio": mid / total},
            "late_180_to_300": {"count": late, "ratio": late / total},
            "post_300": {"count": 0, "ratio": 0.0},
        },
    }


class RlFixedWindowActionPlanTests(unittest.TestCase):
    def test_build_plan_combines_windows_into_ordered_repair_stages(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            analysis_60 = root / "failure_60.json"
            analysis_300 = root / "failure_300.json"
            write_json(
                analysis_60,
                analysis_payload(
                    60,
                    [
                        map_payload("soda-creek", opening=1, win_rate=0.6667),
                        map_payload("caramel-workshop", win_rate=1.0),
                    ],
                ),
            )
            write_json(
                analysis_300,
                analysis_payload(
                    300,
                    [
                        map_payload("soda-creek", mid=1),
                        map_payload("cracked-star-jar", late=2),
                    ],
                ),
            )

            plan = build_plan(
                [("60s", analysis_60), ("300s", analysis_300)],
                initial_model="reports/start.zip",
                output_dir="reports/fixed_window_plan/stages",
                timesteps_per_stage=256,
                reward_profile="late-route-recovery",
                train_map_selection="random",
                validation_seed_start=63300,
                validation_windows=[60, 180, 300],
            )

            self.assertEqual(plan["decision"], "rl_fixed_window_action_plan_ready")
            self.assertEqual(plan["stage_count"], 3)
            self.assertEqual(plan["failure_group_count"], 3)
            self.assertEqual(plan["total_failure_count"], 4)
            self.assertEqual(
                [stage["focus_bucket"] for stage in plan["stages"]],
                ["opening_lt_60", "mid_60_to_180", "late_180_to_300"],
            )
            self.assertEqual(plan["stages"][0]["train_maps"], ["soda-creek"])
            self.assertEqual(plan["stages"][1]["train_maps"], ["soda-creek"])
            self.assertEqual(plan["stages"][2]["train_maps"], ["cracked-star-jar"])
            self.assertEqual(plan["stages"][0]["source_windows"], [60])
            self.assertEqual(plan["stages"][1]["source_windows"], [300])
            self.assertEqual(plan["stages"][2]["total_failure_count"], 2)
            self.assertEqual(plan["stages"][1]["model_in"], plan["stages"][0]["model_out"])
            self.assertIn("--train-seconds 60", plan["stages"][0]["train_command"])
            self.assertIn("--train-seconds 300", plan["stages"][2]["train_command"])
            self.assertEqual(len(plan["stages"][0]["compare_commands"]), 3)
            self.assertIn("comparison_300s.json", plan["stages"][0]["compare_commands"][2])

    def test_parse_validation_windows_rejects_empty_values(self) -> None:
        with self.assertRaises(ValueError):
            parse_validation_windows(" , ")


if __name__ == "__main__":
    unittest.main(verbosity=2)
