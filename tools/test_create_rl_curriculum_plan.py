#!/usr/bin/env python3
"""Regression tests for RL curriculum plan creation."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from create_rl_curriculum_plan import build_plan


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def failure_analysis_payload() -> dict:
    return {
        "report_version": 1,
        "decision": "rl_policy_failure_analysis_recorded",
        "maps": [
            {
                "map_id": "soda-creek",
                "average_failure_survival_seconds": 91.0,
                "policy_dominant_action": {"action": "7", "ratio": 0.39},
                "failure_time_bucket_distribution": {
                    "opening_lt_60": {"count": 2, "ratio": 0.6667},
                    "mid_60_to_180": {"count": 0, "ratio": 0.0},
                    "late_180_to_300": {"count": 1, "ratio": 0.3333},
                    "post_300": {"count": 0, "ratio": 0.0},
                },
            },
            {
                "map_id": "caramel-workshop",
                "average_failure_survival_seconds": 180.0,
                "policy_dominant_action": {"action": "3", "ratio": 0.67},
                "failure_time_bucket_distribution": {
                    "opening_lt_60": {"count": 0, "ratio": 0.0},
                    "mid_60_to_180": {"count": 1, "ratio": 0.3333},
                    "late_180_to_300": {"count": 2, "ratio": 0.6667},
                    "post_300": {"count": 0, "ratio": 0.0},
                },
            },
        ],
    }


class RlCurriculumPlanTests(unittest.TestCase):
    def test_build_plan_creates_ordered_chain_from_failure_buckets(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            analysis_path = Path(temp_dir) / "failure_analysis.json"
            write_json(analysis_path, failure_analysis_payload())

            plan = build_plan(
                analysis_path,
                initial_model="models/start.zip",
                output_dir="reports/curriculum",
                timesteps_per_stage=5000,
                ent_coef=0.02,
                train_map_selection="random",
                validation_seed_start=62000,
            )

            self.assertEqual(plan["decision"], "rl_curriculum_plan_created")
            self.assertEqual(plan["stage_count"], 3)
            self.assertEqual(
                [stage["focus_bucket"] for stage in plan["stages"]],
                ["opening_lt_60", "mid_60_to_180", "late_180_to_300"],
            )
            self.assertEqual(plan["stages"][0]["train_maps"], ["soda-creek"])
            self.assertEqual(plan["stages"][1]["train_maps"], ["caramel-workshop"])
            self.assertEqual(plan["stages"][2]["train_maps"], ["caramel-workshop", "soda-creek"])
            self.assertEqual(plan["stages"][1]["model_in"], plan["stages"][0]["model_out"])
            self.assertIn("--train-seconds 60", plan["stages"][0]["train_command"])
            self.assertIn("--train-seconds 300", plan["stages"][2]["train_command"])


if __name__ == "__main__":
    unittest.main()
