#!/usr/bin/env python3
"""Regression tests for policy fixed-window no-regression validation."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from validate_policy_window_regression import build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def comparison_payload(seconds: float, win_rates: dict[str, float], survival: dict[str, float] | None = None) -> dict:
    survival = survival or {map_id: seconds for map_id in win_rates}
    maps = []
    for map_id, win_rate in win_rates.items():
        maps.append(
            {
                "map_id": map_id,
                "policy_win_rate": win_rate,
                "policy_average_survival_seconds": survival.get(map_id, seconds),
                "policy_dominant_action": {"action": "7", "count": 100, "ratio": 0.4},
                "policy_normalized_action_entropy": 0.5,
            }
        )
    return {
        "report_version": 1,
        "status": "compared",
        "seconds": seconds,
        "map_preset": "high-pressure",
        "gate_decision": "multimap_comparison_recorded_not_balance_gate",
        "summary": {
            "maps": maps,
            "map_count": len(maps),
            "minimum_policy_win_rate": min(win_rates.values()),
        },
    }


class PolicyWindowRegressionTests(unittest.TestCase):
    def test_candidate_matching_baseline_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            baseline = root / "baseline_60.json"
            candidate = root / "candidate_60.json"
            payload = comparison_payload(
                60.0,
                {"soda-creek": 1.0, "caramel-workshop": 1.0, "cracked-star-jar": 1.0},
            )
            write_json(baseline, payload)
            write_json(candidate, payload)

            report = build_report({"60s": baseline}, {"60s": candidate})

        self.assertEqual(report["decision"], "policy_window_regression_passed")
        self.assertEqual(report["blockers"], [])

    def test_win_rate_drop_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            baseline = root / "baseline_60.json"
            candidate = root / "candidate_60.json"
            write_json(
                baseline,
                comparison_payload(
                    60.0,
                    {"soda-creek": 1.0, "caramel-workshop": 1.0, "cracked-star-jar": 1.0},
                ),
            )
            write_json(
                candidate,
                comparison_payload(
                    60.0,
                    {"soda-creek": 0.3333, "caramel-workshop": 1.0, "cracked-star-jar": 1.0},
                ),
            )

            report = build_report({"60s": baseline}, {"60s": candidate})

        self.assertEqual(report["decision"], "policy_window_regression_failed")
        self.assertTrue(any("soda-creek" in blocker for blocker in report["blockers"]))

    def test_survival_drop_fails_even_when_win_rate_matches(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            baseline = root / "baseline_300.json"
            candidate = root / "candidate_300.json"
            write_json(
                baseline,
                comparison_payload(
                    300.0,
                    {"soda-creek": 0.0},
                    {"soda-creek": 230.0},
                ),
            )
            write_json(
                candidate,
                comparison_payload(
                    300.0,
                    {"soda-creek": 0.0},
                    {"soda-creek": 101.0},
                ),
            )

            report = build_report(
                {"300s": baseline},
                {"300s": candidate},
                max_survival_drop_seconds=5.0,
            )

        self.assertEqual(report["decision"], "policy_window_regression_failed")
        self.assertTrue(any("average_survival_seconds" in blocker for blocker in report["blockers"]))

    def test_missing_window_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            baseline = root / "baseline_60.json"
            write_json(baseline, comparison_payload(60.0, {"soda-creek": 1.0}))

            report = build_report({"60s": baseline}, {})

        self.assertEqual(report["decision"], "policy_window_regression_invalid")
        self.assertTrue(any("candidate window" in error for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()
