#!/usr/bin/env python3
"""Regression tests for analyze_route_recovery_traces.py."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from analyze_route_recovery_traces import build_report, bucket_for_time, pressure_tags


def write_trace(path: Path) -> None:
    payload = {
        "record_type": "policy_trace",
        "episode": {
            "seed": 62300,
            "map_id": "soda-creek",
            "terminal_kind": "defeat",
        },
        "steps": [
            {
                "step": 1,
                "tick": 1,
                "time_seconds": 12.5,
                "action": 3,
                "reward": -0.1,
                "health": 60.0,
                "level": 2,
                "kills": 10,
                "reward_breakdown": {"route_recovery": -0.004},
                "diagnostics": {
                    "boundary": {"min_distance": 0.0, "edge_risk": 1.0},
                    "enemy_pressure_risk": 0.9,
                    "hazard_pressure_risk": 0.0,
                    "boss_pressure_risk": 0.0,
                    "low_health_risk": 0.2,
                    "safety_risk_score": 0.7,
                    "nearest_enemy": {
                        "enemy_id": "test-gummy",
                        "behavior": "chase",
                        "hitbox_distance": 0.0,
                        "threat": 40.0,
                    },
                },
                "action_score": {
                    "top_actions": [
                        {"action": "3", "score": 0.8},
                        {"action": "7", "score": 0.1},
                    ]
                },
            },
            {
                "step": 2,
                "tick": 2,
                "time_seconds": 62.0,
                "action": 7,
                "reward_breakdown": {"route_recovery": 0.002},
                "diagnostics": {"boundary": {"edge_risk": 0.0}},
            },
        ],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


class RouteRecoveryTraceAnalysisTests(unittest.TestCase):
    def test_time_buckets(self) -> None:
        self.assertEqual(bucket_for_time(12.0), "opening_lt_60")
        self.assertEqual(bucket_for_time(60.0), "mid_60_to_180")
        self.assertEqual(bucket_for_time(180.0), "late_180_to_300")
        self.assertEqual(bucket_for_time(300.0), "post_300")

    def test_pressure_tags_include_major_context(self) -> None:
        tags = pressure_tags(
            {
                "boundary": {"edge_risk": 1.0},
                "enemy_pressure_risk": 0.8,
                "hazard_pressure_risk": 0.5,
                "boss_pressure_risk": 0.3,
                "low_health_risk": 0.7,
            }
        )

        self.assertEqual(
            tags,
            [
                "boundary_edge",
                "enemy_pressure",
                "hazard_pressure",
                "boss_pressure",
                "low_health",
            ],
        )

    def test_build_report_collects_negative_hotspots(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            trace = root / "soda-creek_seed62300_trace.json"
            write_trace(trace)

            report = build_report([root], top=5)

        self.assertEqual(report["decision"], "route_recovery_trace_hotspots_recorded")
        self.assertEqual(report["trace_count"], 1)
        self.assertEqual(report["sample_count"], 2)
        self.assertEqual(report["negative_sample_count"], 1)
        self.assertEqual(report["map_summary"][0]["map_id"], "soda-creek")
        self.assertEqual(report["time_bucket_summary"][0]["time_bucket"], "opening_lt_60")
        self.assertEqual(report["top_hotspots"][0]["pressure_tags"], ["boundary_edge", "enemy_pressure"])
        self.assertEqual(report["top_hotspots"][0]["nearest_enemy"]["enemy_id"], "test-gummy")


if __name__ == "__main__":
    unittest.main()
