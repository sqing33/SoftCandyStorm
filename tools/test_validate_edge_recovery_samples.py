#!/usr/bin/env python3
"""Regression tests for edge recovery sample validation."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import sys

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from validate_edge_recovery_samples import build_report  # noqa: E402


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def sample_payload(**overrides) -> dict:
    payload = {
        "record_type": "edge_recovery_supervision_sample",
        "schema_version": 1,
        "sample_role": "repair_training_input",
        "target_source": "edge_recovery_filter",
        "seed": 62201,
        "map_id": "soda-creek",
        "step": 1800,
        "tick": 1800,
        "time_seconds": 60.0,
        "observation_version": 2,
        "observation_len": 3,
        "observation": [0.1, 0.2, 0.3],
        "original_action": 7,
        "target_action": 0,
        "target_label": "highest_scored_non_wallward_action",
        "adapter_decision": {
            "mode": "edge_recovery_filter",
            "edge_distance": 32.0,
            "original_action": 7,
            "target_action": 0,
            "score_kind": "probability",
            "original_action_score": 0.9,
            "target_action_score": 0.1,
            "score_margin": -0.8,
            "target_rank": 2,
        },
        "action_scores": {"kind": "probability", "scores": [0.1] * 9},
        "diagnostics": {
            "boundary": {
                "left_distance": 0.0,
                "right_distance": 2400.0,
                "bottom_distance": 900.0,
                "top_distance": 900.0,
            }
        },
        "limitations": [
            "This sample is produced by a hand-written diagnostic adapter.",
            "It is not RL policy acceptance evidence.",
        ],
    }
    payload.update(overrides)
    return payload


class EdgeRecoverySampleValidationTests(unittest.TestCase):
    def test_valid_sample_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "samples.jsonl"
            write_jsonl(path, [sample_payload()])

            report = build_report(path)

            self.assertEqual(report["decision"], "edge_recovery_samples_valid")
            self.assertEqual(report["sample_count"], 1)
            self.assertEqual(report["errors"], [])

    def test_route_recovery_trace_hotspot_source_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "samples.jsonl"
            write_jsonl(
                path,
                [
                    sample_payload(
                        target_source="route_recovery_trace_hotspot",
                        adapter_decision={
                            "mode": "route_recovery_trace_hotspot",
                            "edge_distance": 32.0,
                            "original_action": 7,
                            "target_action": 0,
                        },
                    )
                ],
            )

            report = build_report(path)

            self.assertEqual(report["decision"], "edge_recovery_samples_valid")
            self.assertEqual(report["errors"], [])

    def test_target_still_pushing_edge_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "samples.jsonl"
            write_jsonl(
                path,
                [
                    sample_payload(
                        target_action=7,
                        adapter_decision={
                            "mode": "edge_recovery_filter",
                            "edge_distance": 32.0,
                            "original_action": 7,
                            "target_action": 7,
                        },
                    )
                ],
            )

            report = build_report(path)

            self.assertEqual(report["decision"], "edge_recovery_samples_invalid")
            self.assertTrue(any("target_action" in error for error in report["errors"]))

    def test_observation_length_mismatch_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "samples.jsonl"
            write_jsonl(path, [sample_payload(observation_len=99)])

            report = build_report(path)

            self.assertEqual(report["decision"], "edge_recovery_samples_invalid")
            self.assertTrue(any("observation_len" in error for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()
