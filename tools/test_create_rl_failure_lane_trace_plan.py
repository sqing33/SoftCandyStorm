#!/usr/bin/env python3
"""Tests for RL failure-lane trace plan generation."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from create_rl_failure_lane_trace_plan import build_report  # noqa: E402


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sample_failure_analysis() -> dict[str, Any]:
    return {
        "report_version": 1,
        "decision": "rl_policy_failure_analysis_recorded",
        "model_path": "reports/model.zip",
        "seconds": 300.0,
        "maps": [
            {
                "map_id": "caramel-workshop",
                "failure_lanes": {
                    "late_terminal_survival_conversion": {
                        "lane_id": "late_terminal_survival_conversion",
                        "count": 3,
                        "ratio": 0.75,
                        "time_buckets": ["late_180_to_300"],
                        "seeds": [63400, 63402, 63403],
                    },
                    "opening_repair": {
                        "lane_id": "opening_repair",
                        "count": 1,
                        "ratio": 0.25,
                        "time_buckets": ["opening_lt_60"],
                        "seeds": [63401],
                    },
                },
                "failures": [
                    {
                        "seed": 63400,
                        "time_seconds": 214.65,
                        "time_bucket": "late_180_to_300",
                        "dominant_action": {"action": "8"},
                    },
                    {
                        "seed": 63401,
                        "time_seconds": 40.1,
                        "time_bucket": "opening_lt_60",
                        "dominant_action": {"action": "5"},
                    },
                    {
                        "seed": 63402,
                        "time_seconds": 220.0,
                        "time_bucket": "late_180_to_300",
                        "dominant_action": {"action": "5"},
                    },
                    {
                        "seed": 63403,
                        "time_seconds": 225.8,
                        "time_bucket": "late_180_to_300",
                        "dominant_action": {"action": "5"},
                    },
                ],
            }
        ],
    }


class RlFailureLaneTracePlanTests(unittest.TestCase):
    def test_builds_separate_opening_and_late_trace_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "failure_analysis.json"
            write_json(source, sample_failure_analysis())

            report = build_report(source, Path("reports/traces"))

        self.assertEqual(report["decision"], "rl_failure_lane_trace_plan_ready")
        self.assertEqual(report["lane_ids"], ["late_terminal_survival_conversion", "opening_repair"])
        tasks = {task["lane_id"]: task for task in report["tasks"]}
        opening = tasks["opening_repair"]
        self.assertEqual(opening["task_type"], "opening_trace_preflight")
        self.assertEqual(opening["trace_window_seconds"], {"start": 0.0, "end": 60.0})
        self.assertEqual(opening["evaluation_range"]["seed_start"], 63401)
        self.assertEqual(opening["evaluation_range"]["eval_episodes"], 1)

        late = tasks["late_terminal_survival_conversion"]
        self.assertEqual(late["task_type"], "late_terminal_trace_preflight")
        self.assertEqual(late["evaluation_range"]["seed_start"], 63400)
        self.assertEqual(late["evaluation_range"]["eval_episodes"], 4)
        self.assertEqual(late["evaluation_range"]["extra_scan_seeds"], [63401])
        self.assertEqual(late["trace_window_seconds"], {"start": 180.0, "end": 240.8})
        self.assertEqual(late["dominant_action_counts"], {"5": 2, "8": 1})
        self.assertEqual(late["dispatch_window_seconds"], {"start": 209.65, "end": 240.8})
        self.assertIn("--trace-include-observation", late["suggested_train_sb3_args"])

    def test_missing_failure_lanes_is_invalid(self) -> None:
        payload = sample_failure_analysis()
        payload["maps"][0].pop("failure_lanes")
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "failure_analysis.json"
            write_json(source, payload)

            report = build_report(source, Path("reports/traces"))

        self.assertEqual(report["decision"], "rl_failure_lane_trace_plan_invalid")
        self.assertIn("failure analysis contains no map-level failure_lanes", report["errors"])

    def test_invalid_json_shape_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "failure_analysis.json"
            write_json(source, [])

            report = build_report(source, Path("reports/traces"))

        self.assertEqual(report["decision"], "rl_failure_lane_trace_plan_invalid")
        self.assertTrue(any("must contain a JSON object" in error for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()
