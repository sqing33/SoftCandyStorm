#!/usr/bin/env python3
"""Regression tests for SB3 handoff-state diagnostics."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from analyze_sb3_handoff_states import (  # noqa: E402
    build_report,
    compare_handoff_samples,
    load_trace_samples,
)


class ContextPolicy:
    def __init__(self, pre_scores: list[float], post_scores: list[float]):
        self.pre_scores = pre_scores
        self.post_scores = post_scores
        self.contexts: list[dict] = []
        self.map_ids: list[str] = []
        self.reset_count = 0
        self.time_seconds = 0.0

    def reset(self) -> None:
        self.reset_count += 1

    def set_map_id(self, map_id: str) -> None:
        self.map_ids.append(map_id)

    def set_step_context(self, info: dict) -> None:
        self.contexts.append(info)
        self.time_seconds = float(info.get("time_seconds", 0.0))

    def action_scores(self, observation: list[float]) -> dict:
        scores = self.pre_scores if self.time_seconds < 180.0 else self.post_scores
        return {
            "kind": "probability",
            "scores": scores,
        }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def trace_payload() -> dict:
    return {
        "record_type": "policy_episode_trace",
        "episode": {
            "seed": 63101,
            "map_id": "cracked-star-jar",
            "terminal_kind": "defeat",
            "time_seconds": 230.0,
        },
        "steps": [
            {
                "step": 1,
                "time_seconds": 120.0,
                "action": 0,
                "health": 96.0,
                "observation": [0.1, 0.2],
                "diagnostics": {
                    "enemy_pressure_risk": 0.1,
                    "boundary": {"min_distance": 40.0},
                },
            },
            {
                "step": 2,
                "time_seconds": 179.5,
                "action": 0,
                "health": 50.0,
                "observation": [0.3, 0.4],
                "diagnostics": {
                    "enemy_pressure_risk": 0.7,
                    "boundary": {"min_distance": 4.0},
                },
            },
            {
                "step": 3,
                "time_seconds": 181.0,
                "action": 1,
                "health": 45.0,
                "observation": [0.5, 0.6],
                "diagnostics": {
                    "enemy_pressure_risk": 0.8,
                    "boundary": {"min_distance": 2.0},
                },
            },
        ],
    }


class Sb3HandoffStateDiagnosticTests(unittest.TestCase):
    def test_load_trace_samples_filters_by_time_and_requires_observation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "trace.json"
            write_json(path, trace_payload())

            samples = load_trace_samples(
                [path],
                map_id="cracked-star-jar",
                start_seconds=170.0,
                end_seconds=200.0,
            )

        self.assertEqual([sample["step"] for sample in samples], [2, 3])
        self.assertEqual(samples[0]["episode_outcome"], "defeat")
        self.assertEqual(samples[1]["diagnostics"]["boundary"]["min_distance"], 2.0)

    def test_compare_handoff_samples_groups_pre_and_post_split(self) -> None:
        base = ContextPolicy([0.9, 0.1], [0.8, 0.2])
        late = ContextPolicy([0.85, 0.15], [0.1, 0.9])
        samples = [
            {
                "trace_path": "trace",
                "seed": 7,
                "map_id": "cracked-star-jar",
                "episode_outcome": "defeat",
                "step": 1,
                "time_seconds": 179.5,
                "health": 50.0,
                "action": 0,
                "observation": [0.3, 0.4],
                "diagnostics": {"boundary": {"min_distance": 4.0}},
            },
            {
                "trace_path": "trace",
                "seed": 7,
                "map_id": "cracked-star-jar",
                "episode_outcome": "defeat",
                "step": 2,
                "time_seconds": 181.0,
                "health": 45.0,
                "action": 1,
                "observation": [0.5, 0.6],
                "diagnostics": {"boundary": {"min_distance": 2.0}},
            },
        ]

        report = compare_handoff_samples(
            samples,
            base,
            late,
            action_count=2,
            split_seconds=180.0,
        )

        self.assertEqual(base.reset_count, 1)
        self.assertEqual(late.map_ids, ["cracked-star-jar"])
        self.assertEqual(report["sample_count"], 2)
        self.assertEqual(report["by_window"]["pre_split"]["argmax_agreement"], 1.0)
        self.assertEqual(report["by_window"]["post_split"]["argmax_agreement"], 0.0)
        self.assertEqual(report["overall"]["trace_matches_base_argmax"], 0.5)
        self.assertEqual(report["overall"]["trace_matches_late_argmax"], 1.0)
        self.assertEqual(report["by_episode_outcome"]["defeat"]["sample_count"], 2)

    def test_build_report_wraps_trace_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "cracked-star-jar_seed63101_trace.json"
            write_json(path, trace_payload())
            base = ContextPolicy([0.9, 0.1], [0.8, 0.2])
            late = ContextPolicy([0.85, 0.15], [0.1, 0.9])

            report = build_report(
                [path],
                base,
                late,
                base_model_path="base.zip",
                late_model_path="late.zip",
                action_count=2,
                split_seconds=180.0,
                window_before_seconds=5.0,
                window_after_seconds=5.0,
                map_id="cracked-star-jar",
            )

        self.assertEqual(report["decision"], "sb3_handoff_state_distribution_recorded")
        self.assertEqual(report["trace_count"], 1)
        self.assertEqual(report["sample_count"], 2)
        self.assertEqual(report["window"]["start_seconds"], 175.0)
        self.assertEqual(report["window"]["end_seconds"], 185.0)


if __name__ == "__main__":
    unittest.main()
