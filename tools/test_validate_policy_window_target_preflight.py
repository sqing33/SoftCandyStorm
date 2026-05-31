#!/usr/bin/env python3
"""Tests for policy window target preflight validation."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from validate_policy_window_target_preflight import build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def comparison_payload(
    *,
    win_rate: float = 0.6667,
    average_survival_seconds: float = 58.5,
    normalized_action_entropy: float = 0.55,
    dominant_ratio: float = 0.45,
) -> dict:
    return {
        "status": "compared",
        "seconds": 60.0,
        "seed_start": 63400,
        "seeds": 3,
        "map_preset": "high-pressure",
        "action_selection": "deterministic",
        "maps": [
            {
                "map_id": "caramel-workshop",
                "policy": {
                    "summary": {
                        "episodes": 3,
                        "win_rate": win_rate,
                        "average_survival_seconds": average_survival_seconds,
                        "normalized_action_entropy": normalized_action_entropy,
                        "action_distribution": {
                            "0": {"count": 10, "ratio": dominant_ratio},
                            "1": {"count": 5, "ratio": round(1.0 - dominant_ratio, 4)},
                        },
                    }
                },
            }
        ],
    }


class PolicyWindowTargetPreflightTests(unittest.TestCase):
    def test_target_passes_thresholds(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "comparison.json"
            write_json(path, comparison_payload())

            report = build_report(
                path,
                label="60s-caramel",
                map_id="caramel-workshop",
                min_win_rate=0.6667,
                min_average_survival_seconds=55.0,
                min_normalized_action_entropy=0.5,
                max_dominant_action_ratio=0.6,
                expected_seconds=60.0,
                expected_seed_start=63400,
                expected_seeds=3,
                expected_map_preset="high-pressure",
                expected_action_selection="deterministic",
            )

        self.assertEqual(report["decision"], "policy_window_target_preflight_passed")
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["blockers"], [])

    def test_low_win_rate_and_survival_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "comparison.json"
            write_json(path, comparison_payload(win_rate=0.3333, average_survival_seconds=49.2))

            report = build_report(
                path,
                label="60s-caramel",
                map_id="caramel-workshop",
                min_win_rate=0.6667,
                min_average_survival_seconds=55.0,
            )

        self.assertEqual(report["decision"], "policy_window_target_preflight_failed")
        self.assertTrue(any("win_rate" in blocker for blocker in report["blockers"]))
        self.assertTrue(any("average_survival_seconds" in blocker for blocker in report["blockers"]))

    def test_context_mismatch_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "comparison.json"
            write_json(path, comparison_payload())

            report = build_report(
                path,
                label="60s-caramel",
                map_id="caramel-workshop",
                min_win_rate=0.5,
                expected_seconds=180.0,
            )

        self.assertEqual(report["decision"], "policy_window_target_preflight_invalid")
        self.assertTrue(any("context seconds" in error for error in report["errors"]))

    def test_missing_map_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "comparison.json"
            write_json(path, comparison_payload())

            report = build_report(
                path,
                label="60s-soda",
                map_id="soda-creek",
                min_win_rate=0.5,
            )

        self.assertEqual(report["decision"], "policy_window_target_preflight_invalid")
        self.assertTrue(any("soda-creek" in error for error in report["errors"]))

    def test_requires_at_least_one_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "comparison.json"
            write_json(path, comparison_payload())

            report = build_report(path, label="60s-caramel", map_id="caramel-workshop")

        self.assertEqual(report["decision"], "policy_window_target_preflight_invalid")
        self.assertTrue(any("threshold" in error for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()
