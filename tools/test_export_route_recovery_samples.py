#!/usr/bin/env python3
"""Regression tests for export_route_recovery_samples.py."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from export_route_recovery_samples import build_report


def write_trace(
    path: Path,
    *,
    include_observation: bool = True,
    time_seconds: float = 1.0,
    map_id: str = "soda-creek",
    action: int = 3,
    route_recovery: float = -0.004,
    health_ratio: float = 0.2,
    low_health_risk: float = 0.0,
    enemy_pressure_risk: float = 0.7,
    hazard_pressure_risk: float = 0.0,
    boss_pressure_risk: float = 0.0,
    boundary: dict | None = None,
    top_actions: list[dict] | None = None,
) -> None:
    if boundary is None:
        boundary = {
            "left_distance": 2600.0,
            "right_distance": 0.0,
            "bottom_distance": 800.0,
            "top_distance": 900.0,
            "min_distance": 0.0,
            "edge_risk": 1.0,
        }
    if top_actions is None:
        top_actions = [
            {"action": "3", "score": 0.8},
            {"action": "7", "score": 0.15},
            {"action": "0", "score": 0.05},
        ]
    step = {
        "step": 30,
        "tick": 30,
        "time_seconds": time_seconds,
        "action": action,
        "reward": -0.1,
        "health": 110.0,
        "level": 1,
        "kills": 2,
        "reward_breakdown": {"route_recovery": route_recovery},
        "action_score": {
            "kind": "probability",
            "top_actions": top_actions,
        },
        "diagnostics": {
            "boundary": boundary,
            "enemy_pressure_risk": enemy_pressure_risk,
            "hazard_pressure_risk": hazard_pressure_risk,
            "boss_pressure_risk": boss_pressure_risk,
            "low_health_risk": low_health_risk,
        },
    }
    if include_observation:
        step["observation_version"] = 2
        step["observation_len"] = 3
        step["observation"] = [0.1, health_ratio, 0.3]
    payload = {
        "record_type": "policy_episode_trace",
        "episode": {"seed": 62300, "map_id": map_id},
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

    def test_max_health_ratio_filters_high_health_samples(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            trace = root / "high_health_trace.json"
            samples = root / "samples.jsonl"
            write_trace(trace, health_ratio=0.8)

            report = build_report(
                [trace],
                samples_out=samples,
                edge_distance=32.0,
                route_recovery_threshold=0.0,
                min_boundary_edge_risk=0.75,
                max_health_ratio=0.5,
            )
            sample_text = samples.read_text()

        self.assertEqual(report["decision"], "route_recovery_samples_unavailable")
        self.assertEqual(report["high_health_filtered_count"], 1)
        self.assertEqual(report["sample_count"], 0)
        self.assertEqual(sample_text, "")

    def test_pressure_filters_keep_matching_diagnostics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kept = root / "kept_trace.json"
            skipped = root / "skipped_trace.json"
            samples = root / "samples.jsonl"
            write_trace(
                kept,
                low_health_risk=0.8,
                hazard_pressure_risk=0.6,
                boss_pressure_risk=0.4,
            )
            write_trace(
                skipped,
                low_health_risk=0.2,
                hazard_pressure_risk=0.1,
                boss_pressure_risk=0.0,
            )

            report = build_report(
                [root],
                samples_out=samples,
                edge_distance=32.0,
                route_recovery_threshold=0.0,
                min_boundary_edge_risk=0.75,
                min_low_health_risk=0.6,
                min_hazard_pressure_risk=0.4,
                min_boss_pressure_risk=0.25,
            )
            rows = [json.loads(line) for line in samples.read_text().splitlines()]

        self.assertEqual(report["decision"], "route_recovery_samples_exported")
        self.assertEqual(report["pressure_filtered_count"], 1)
        self.assertEqual(report["low_health_risk_filtered_count"], 1)
        self.assertEqual(report["hazard_pressure_filtered_count"], 1)
        self.assertEqual(report["boss_pressure_filtered_count"], 1)
        self.assertEqual(report["sample_count"], 1)
        self.assertIn("low_health", rows[0]["adapter_decision"]["pressure_tags"])
        self.assertIn("hazard_pressure", rows[0]["adapter_decision"]["pressure_tags"])
        self.assertIn("boss_pressure", rows[0]["adapter_decision"]["pressure_tags"])

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

    def test_map_filter_keeps_requested_episode_map(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kept = root / "cracked-star-jar_seed62300_trace.json"
            skipped = root / "soda-creek_seed62300_trace.json"
            samples = root / "samples.jsonl"
            write_trace(kept, map_id="cracked-star-jar")
            write_trace(skipped, map_id="soda-creek")

            report = build_report(
                [root],
                samples_out=samples,
                edge_distance=32.0,
                route_recovery_threshold=0.0,
                min_boundary_edge_risk=0.75,
                map_ids={"cracked-star-jar"},
            )
            rows = [json.loads(line) for line in samples.read_text().splitlines()]

        self.assertEqual(report["decision"], "route_recovery_samples_exported")
        self.assertEqual(report["map_filtered_trace_count"], 1)
        self.assertEqual(report["map_ids"], ["cracked-star-jar"])
        self.assertEqual(report["sample_count"], 1)
        self.assertEqual(rows[0]["map_id"], "cracked-star-jar")

    def test_enemy_pressure_filter_keeps_only_high_pressure_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kept = root / "kept_trace.json"
            skipped = root / "skipped_trace.json"
            samples = root / "samples.jsonl"
            write_trace(kept, enemy_pressure_risk=0.8)
            write_trace(skipped, enemy_pressure_risk=0.2)

            report = build_report(
                [root],
                samples_out=samples,
                edge_distance=32.0,
                route_recovery_threshold=0.0,
                min_boundary_edge_risk=0.75,
                min_enemy_pressure_risk=0.6,
            )
            rows = [json.loads(line) for line in samples.read_text().splitlines()]

        self.assertEqual(report["decision"], "route_recovery_samples_exported")
        self.assertEqual(report["enemy_pressure_filtered_count"], 1)
        self.assertEqual(report["sample_count"], 1)
        self.assertEqual(rows[0]["diagnostics"]["enemy_pressure_risk"], 0.8)

    def test_preferred_targets_can_cycle_success_actions_for_guard_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = root / "first_trace.json"
            second = root / "second_trace.json"
            samples = root / "samples.jsonl"
            bottom_edge = {
                "left_distance": 2400.0,
                "right_distance": 2400.0,
                "bottom_distance": 0.0,
                "top_distance": 1800.0,
                "min_distance": 0.0,
                "edge_risk": 1.0,
            }
            wallward_top_actions = [
                {"action": "5", "score": 0.78},
                {"action": "6", "score": 0.12},
                {"action": "4", "score": 0.07},
            ]
            write_trace(
                first,
                action=5,
                route_recovery=0.001,
                boundary=bottom_edge,
                top_actions=wallward_top_actions,
            )
            write_trace(
                second,
                action=5,
                route_recovery=0.001,
                boundary=bottom_edge,
                top_actions=wallward_top_actions,
            )

            report = build_report(
                [root],
                samples_out=samples,
                edge_distance=32.0,
                route_recovery_threshold=0.0,
                route_recovery_filter="any",
                min_boundary_edge_risk=0.75,
                min_enemy_pressure_risk=0.6,
                original_actions={5},
                preferred_target_actions=[7, 3],
                preferred_target_selection="cycle",
            )
            rows = [json.loads(line) for line in samples.read_text().splitlines()]

        self.assertEqual(report["decision"], "route_recovery_samples_exported")
        self.assertEqual(report["route_recovery_filter"], "any")
        self.assertEqual(report["route_recovery_match_count"], 2)
        self.assertEqual(report["target_action_distribution"], {"7": 1, "3": 1})
        self.assertEqual([row["target_action"] for row in rows], [7, 3])
        self.assertEqual(rows[0]["target_label"], "preferred_non_wallward_action")


if __name__ == "__main__":
    unittest.main()
