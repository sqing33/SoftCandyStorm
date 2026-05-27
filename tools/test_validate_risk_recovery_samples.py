#!/usr/bin/env python3
"""Regression tests for risk recovery sample validation."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from validate_risk_recovery_samples import build_report  # noqa: E402


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def sample_payload(**overrides) -> dict:
    payload = {
        "record_type": "risk_recovery_supervision_sample",
        "schema_version": 1,
        "sample_role": "repair_training_input",
        "target_source": "late_recovery_filter",
        "seed": 62400,
        "map_id": "cracked-star-jar",
        "step": 5400,
        "tick": 5400,
        "time_seconds": 180.0,
        "observation_version": 2,
        "observation_len": 3,
        "observation": [0.6, 0.4, 0.2],
        "original_action": 1,
        "target_action": 3,
        "target_label": "highest_scored_late_safe_action",
        "adapter_decision": {
            "mode": "late_recovery_filter",
            "min_seconds": 180.0,
            "edge_distance": 32.0,
            "thresholds": {
                "hazard": 0.2,
                "boss": 0.05,
                "enemy": 0.05,
                "low_health": 0.25,
                "toward_dot": 0.15,
            },
            "original_action": 1,
            "target_action": 3,
            "risk_reasons": ["wallward_edge"],
            "target_risk_reasons": [],
            "pressure_context": {
                "hazard_pressure_risk": 0.0,
                "boss_pressure_risk": 0.0,
                "enemy_pressure_risk": 0.0,
                "low_health_risk": 0.5,
                "combined_pressure": 0.0,
                "hazard_vector": [0.0, 0.0],
                "boss_vector": [0.0, 0.0],
                "enemy_vector": [100.0, -100.0],
            },
            "score_kind": "probability",
            "original_action_score": 0.8,
            "target_action_score": 0.1,
            "score_margin": -0.7,
            "target_rank": 2,
        },
        "action_scores": {"kind": "probability", "scores": [0.1] * 9},
        "diagnostics": {
            "boundary": {
                "left_distance": 1300.0,
                "right_distance": 1300.0,
                "bottom_distance": 1900.0,
                "top_distance": 0.0,
            }
        },
        "limitations": [
            "This sample is produced by a hand-written diagnostic adapter.",
            "It is not RL policy acceptance evidence.",
        ],
    }
    payload.update(overrides)
    return payload


class RiskRecoverySampleValidationTests(unittest.TestCase):
    def test_valid_wallward_sample_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "samples.jsonl"
            write_jsonl(path, [sample_payload()])

            report = build_report(path)

        self.assertEqual(report["decision"], "risk_recovery_samples_valid")
        self.assertEqual(report["sample_count"], 1)
        self.assertEqual(report["errors"], [])

    def test_risk_reason_mismatch_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "samples.jsonl"
            payload = sample_payload()
            payload["adapter_decision"]["risk_reasons"] = ["toward_hazard"]
            write_jsonl(path, [payload])

            report = build_report(path)

        self.assertEqual(report["decision"], "risk_recovery_samples_invalid")
        self.assertTrue(any("risk_reasons mismatch" in error for error in report["errors"]))

    def test_missing_target_risk_reason_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "samples.jsonl"
            write_jsonl(path, [sample_payload(target_action=2)])

            report = build_report(path)

        self.assertEqual(report["decision"], "risk_recovery_samples_invalid")
        self.assertTrue(any("target_risk_reasons mismatch" in error for error in report["errors"]))

    def test_multiple_files_are_summarized_together(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first = root / "soda.jsonl"
            second = root / "caramel.jsonl"
            write_jsonl(first, [sample_payload(map_id="soda-creek")])
            write_jsonl(second, [sample_payload(map_id="caramel-workshop", seed=62401)])

            report = build_report([first, second])

        self.assertEqual(report["decision"], "risk_recovery_samples_valid")
        self.assertEqual(report["sample_count"], 2)
        self.assertEqual(report["map_ids"], ["caramel-workshop", "soda-creek"])
        self.assertEqual(report["seeds"], [62400, 62401])


if __name__ == "__main__":
    unittest.main()
