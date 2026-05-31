#!/usr/bin/env python3
"""Tests for RL lane repair action-plan generation."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from create_rl_lane_repair_action_plan import build_report  # noqa: E402


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def inventory_payload() -> dict[str, Any]:
    return {
        "lanes": [
            {
                "label": "retention63405",
                "split_status": "failed",
                "reuse_decision": "trace_diagnostic_recorded_boundary_path_retention_lane",
            }
        ]
    }


def trace_payload() -> dict[str, Any]:
    return {
        "matched_seed_comparison": [
            {
                "seed": 63405,
                "time_delta_seconds": -75.8496,
                "first_divergent_action": {
                    "time_seconds": 13.0001,
                    "left_action": "3",
                    "right_action": "7",
                },
                "per_label": {
                    "a_parent": {
                        "episode_time_seconds": 214.5169,
                        "first_boundary_enemy_pressure_step": {"time_seconds": 100.9988},
                        "first_low_health_step": {"time_seconds": 214.0168},
                    },
                    "b_candidate": {
                        "episode_time_seconds": 138.6673,
                        "first_boundary_enemy_pressure_step": {"time_seconds": 45.9996},
                        "first_low_health_step": {"time_seconds": 138.0005},
                    },
                },
            }
        ]
    }


def hotspot_payload() -> dict[str, Any]:
    return {
        "sample_count": 356,
        "negative_sample_count": 248,
        "negative_sample_ratio": 0.6966,
        "time_bucket_summary": [
            {"time_bucket": "opening_lt_60", "hotspot_count": 67, "action_counts": {"7": 46}},
            {"time_bucket": "mid_60_to_180", "hotspot_count": 156, "action_counts": {"5": 59}},
            {"time_bucket": "late_180_to_300", "hotspot_count": 25, "action_counts": {"5": 17}},
        ],
        "pressure_summary": [
            {"pressure_tag": "boundary_edge", "hotspot_count": 236, "action_counts": {"5": 76}},
            {"pressure_tag": "hazard_pressure", "hotspot_count": 33, "action_counts": {"7": 8}},
            {"pressure_tag": "low_health", "hotspot_count": 2, "action_counts": {"8": 1}},
        ],
    }


class RlLaneRepairActionPlanTests(unittest.TestCase):
    def test_classifies_seed63405_as_opening_mid_boundary_lane(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            inventory = root / "inventory.json"
            trace = root / "trace.json"
            hotspots = root / "hotspots.json"
            write_json(inventory, inventory_payload())
            write_json(trace, trace_payload())
            write_json(hotspots, hotspot_payload())

            report = build_report(
                lane_inventory=inventory,
                trace_comparison=trace,
                route_hotspots=hotspots,
                lane_label="retention63405",
                parent_label="a_parent",
                candidate_label="b_candidate",
                target_seed=63405,
            )

        self.assertEqual(report["decision"], "rl_lane_repair_action_plan_ready")
        self.assertEqual(
            report["diagnosis"]["classification"],
            "opening_mid_boundary_path_retention",
        )
        self.assertTrue(report["diagnosis"]["not_pure_late_low_health"])
        self.assertEqual(report["metrics"]["episode_time_delta_seconds"], -75.8496)
        self.assertEqual(report["metrics"]["high_pressure_delta_seconds"], -54.9992)
        self.assertIn(
            "60s/caramel-workshop window target preflight must pass",
            report["action_plan"]["required_gates"],
        )
        self.assertIn(
            "pure late low-health continuation",
            report["action_plan"]["disallowed_next_steps"],
        )

    def test_missing_lane_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            inventory = root / "inventory.json"
            trace = root / "trace.json"
            hotspots = root / "hotspots.json"
            write_json(inventory, inventory_payload())
            write_json(trace, trace_payload())
            write_json(hotspots, hotspot_payload())

            report = build_report(
                lane_inventory=inventory,
                trace_comparison=trace,
                route_hotspots=hotspots,
                lane_label="missing",
                parent_label="a_parent",
                candidate_label="b_candidate",
                target_seed=63405,
            )

        self.assertEqual(report["decision"], "rl_lane_repair_action_plan_invalid")
        self.assertIn("lane `missing` not found in lane inventory", report["errors"])

    def test_late_heavy_hotspots_do_not_claim_boundary_lane(self) -> None:
        payload = hotspot_payload()
        payload["time_bucket_summary"] = [
            {"time_bucket": "opening_lt_60", "hotspot_count": 5, "action_counts": {"7": 5}},
            {"time_bucket": "mid_60_to_180", "hotspot_count": 15, "action_counts": {"5": 15}},
            {"time_bucket": "late_180_to_300", "hotspot_count": 228, "action_counts": {"8": 228}},
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            inventory = root / "inventory.json"
            trace = root / "trace.json"
            hotspots = root / "hotspots.json"
            write_json(inventory, inventory_payload())
            write_json(trace, trace_payload())
            write_json(hotspots, payload)

            report = build_report(
                lane_inventory=inventory,
                trace_comparison=trace,
                route_hotspots=hotspots,
                lane_label="retention63405",
                parent_label="a_parent",
                candidate_label="b_candidate",
                target_seed=63405,
            )

        self.assertEqual(report["decision"], "rl_lane_repair_action_plan_ready")
        self.assertEqual(report["diagnosis"]["classification"], "late_retention_candidate")
        self.assertFalse(report["diagnosis"]["not_pure_late_low_health"])


if __name__ == "__main__":
    unittest.main()
