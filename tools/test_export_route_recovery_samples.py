#!/usr/bin/env python3
"""Regression tests for export_route_recovery_samples.py."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from export_route_recovery_samples import build_report


def write_trace(path: Path, *, include_observation: bool = True, time_seconds: float = 1.0) -> None:
    step = {
        "step": 30,
        "tick": 30,
        "time_seconds": time_seconds,
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
        self.assertEqual(rows[0]["health_ratio"], 0.2)

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

    def test_time_window_filters_hotspots(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            early = root / "early_trace.json"
            late = root / "late_trace.json"
            samples = root / "samples.jsonl"
            write_trace(early, time_seconds=10.0)
            write_trace(late, time_seconds=25.0)

            report = build_report(
                [root],
                samples_out=samples,
                edge_distance=32.0,
                route_recovery_threshold=0.0,
                min_boundary_edge_risk=0.75,
                min_seconds=20.0,
                max_seconds=30.0,
            )
            rows = [json.loads(line) for line in samples.read_text().splitlines()]

        self.assertEqual(report["decision"], "route_recovery_samples_exported")
        self.assertEqual(report["outside_time_window_count"], 1)
        self.assertEqual(report["sample_count"], 1)
        self.assertEqual(rows[0]["time_seconds"], 25.0)

    def test_phase_duration_conditioning_rewrites_progress(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            trace = root / "late_trace.json"
            samples = root / "samples.jsonl"
            write_trace(trace, time_seconds=25.0)

            report = build_report(
                [root],
                samples_out=samples,
                edge_distance=32.0,
                route_recovery_threshold=0.0,
                min_boundary_edge_risk=0.75,
                phase_duration_seconds=300.0,
            )
            rows = [json.loads(line) for line in samples.read_text().splitlines()]

        self.assertEqual(report["decision"], "route_recovery_samples_exported")
        self.assertEqual(report["phase_duration_seconds"], 300.0)
        self.assertAlmostEqual(rows[0]["observation"][0], 25.0 / 300.0)

    def test_min_health_ratio_filters_low_health_samples(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            trace = root / "low_health_trace.json"
            samples = root / "samples.jsonl"
            write_trace(trace)

            report = build_report(
                [trace],
                samples_out=samples,
                edge_distance=32.0,
                route_recovery_threshold=0.0,
                min_boundary_edge_risk=0.75,
                min_health_ratio=0.25,
            )
            sample_text = samples.read_text()

        self.assertEqual(report["decision"], "route_recovery_samples_unavailable")
        self.assertEqual(report["low_health_filtered_count"], 1)
        self.assertEqual(report["sample_count"], 0)
        self.assertEqual(sample_text, "")

    def test_original_action_filter_keeps_only_requested_actions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            trace = root / "soda-creek_seed62300_trace.json"
            samples = root / "samples.jsonl"
            write_trace(trace)

            report = build_report(
                [trace],
                samples_out=samples,
                edge_distance=32.0,
                route_recovery_threshold=0.0,
                min_boundary_edge_risk=0.75,
                original_actions={1},
            )
            sample_text = samples.read_text()

        self.assertEqual(report["decision"], "route_recovery_samples_unavailable")
        self.assertEqual(report["original_action_filtered_count"], 1)
        self.assertEqual(report["sample_count"], 0)
        self.assertEqual(sample_text, "")


if __name__ == "__main__":
    unittest.main()
