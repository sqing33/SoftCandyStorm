#!/usr/bin/env python3
"""Regression tests for export_route_recovery_samples.py."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from export_route_recovery_samples import build_report


def write_trace(path: Path, *, include_observation: bool = True) -> None:
    step = {
        "step": 30,
        "tick": 30,
        "time_seconds": 1.0,
        "action": 3,
        "reward": -0.1,
        "health": 110.0,
        "level": 1,
        "kills": 2,
        "reward_breakdown": {"route_recovery": -0.004},
        "action_score": {
            "kind": "probability",
            "top_actions": [
                {"action": "3", "score": 0.8},
                {"action": "7", "score": 0.15},
                {"action": "0", "score": 0.05},
            ],
        },
        "diagnostics": {
            "boundary": {
                "left_distance": 2600.0,
                "right_distance": 0.0,
                "bottom_distance": 800.0,
                "top_distance": 900.0,
                "min_distance": 0.0,
                "edge_risk": 1.0,
            },
            "enemy_pressure_risk": 0.7,
            "hazard_pressure_risk": 0.0,
            "boss_pressure_risk": 0.0,
            "low_health_risk": 0.0,
        },
    }
    if include_observation:
        step["observation_version"] = 2
        step["observation_len"] = 3
        step["observation"] = [0.1, 0.2, 0.3]
    payload = {
        "record_type": "policy_episode_trace",
        "episode": {"seed": 62300, "map_id": "soda-creek"},
        "steps": [step],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


class RouteRecoverySampleExportTests(unittest.TestCase):
    def test_exports_boundary_hotspot_with_observation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            trace = root / "soda-creek_seed62300_trace.json"
            samples = root / "samples.jsonl"
            write_trace(trace)

            report = build_report(
                [root],
                samples_out=samples,
                edge_distance=32.0,
                route_recovery_threshold=0.0,
                min_boundary_edge_risk=0.75,
            )

            rows = [json.loads(line) for line in samples.read_text().splitlines()]

        self.assertEqual(report["decision"], "route_recovery_samples_exported")
        self.assertEqual(report["sample_count"], 1)
        self.assertEqual(rows[0]["target_source"], "route_recovery_trace_hotspot")
        self.assertEqual(rows[0]["original_action"], 3)
        self.assertEqual(rows[0]["target_action"], 7)
        self.assertEqual(rows[0]["observation_len"], 3)

    def test_skips_hotspot_without_observation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            trace = root / "soda-creek_seed62300_trace.json"
            samples = root / "samples.jsonl"
            write_trace(trace, include_observation=False)

            report = build_report(
                [trace],
                samples_out=samples,
                edge_distance=32.0,
                route_recovery_threshold=0.0,
                min_boundary_edge_risk=0.75,
            )
            sample_text = samples.read_text()

        self.assertEqual(report["decision"], "route_recovery_samples_unavailable")
        self.assertEqual(report["missing_observation_count"], 1)
        self.assertEqual(sample_text, "")


if __name__ == "__main__":
    unittest.main()
