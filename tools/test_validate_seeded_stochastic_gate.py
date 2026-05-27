#!/usr/bin/env python3
"""Regression tests for seeded stochastic watch validation."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import sys

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from validate_seeded_stochastic_gate import build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def comparison_payload(
    *,
    seconds: float,
    seeds: int,
    action_selection: str = "stochastic",
    action_random_seed: int = 62201,
    win_rate: float = 1.0,
    entropy: float = 0.83,
    dominant_ratio: float = 0.3,
) -> dict:
    maps = []
    for map_id in ("soda-creek", "caramel-workshop", "cracked-star-jar"):
        maps.append(
            {
                "map_id": map_id,
                "policy_win_rate": win_rate,
                "policy_average_survival_seconds": seconds,
                "policy_dominant_action": {
                    "action": "7",
                    "count": 100,
                    "ratio": dominant_ratio,
                },
                "policy_normalized_action_entropy": entropy,
                "rule_bot_win_rates": {"random": 0.5, "kite": 1.0, "tank": 1.0},
                "best_rule_bot_win_rate": 1.0,
                "inner_gate_decision": "comparison_recorded_not_balance_gate",
            }
        )
    return {
        "report_version": 1,
        "status": "compared",
        "action_selection": action_selection,
        "action_random_seed": action_random_seed,
        "map_preset": "high-pressure",
        "seed_start": 62400,
        "seeds": seeds,
        "seconds": seconds,
        "summary": {
            "maps": maps,
            "map_count": len(maps),
            "minimum_policy_win_rate": win_rate,
            "average_policy_win_rate": win_rate,
            "repair_maps": [],
        },
        "findings": [],
        "gate_decision": "multimap_comparison_recorded_not_balance_gate",
    }


class SeededStochasticGateTests(unittest.TestCase):
    def test_ready_pair_passes_watch_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            short = root / "short.json"
            long = root / "long.json"
            write_json(short, comparison_payload(seconds=60.0, seeds=10))
            write_json(long, comparison_payload(seconds=180.0, seeds=3))

            report = build_report(short, long)

            self.assertEqual(report["decision"], "seeded_stochastic_watch_ready")
            self.assertEqual(report["errors"], [])
            self.assertEqual(report["action_random_seed"], 62201)

    def test_deterministic_report_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            short = root / "short.json"
            long = root / "long.json"
            write_json(
                short,
                comparison_payload(
                    seconds=60.0,
                    seeds=10,
                    action_selection="deterministic",
                ),
            )
            write_json(long, comparison_payload(seconds=180.0, seeds=3))

            report = build_report(short, long)

            self.assertEqual(report["decision"], "seeded_stochastic_watch_blocked")
            self.assertTrue(any("action_selection" in error for error in report["errors"]))

    def test_mismatched_action_seed_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            short = root / "short.json"
            long = root / "long.json"
            write_json(short, comparison_payload(seconds=60.0, seeds=10))
            write_json(
                long,
                comparison_payload(seconds=180.0, seeds=3, action_random_seed=7),
            )

            report = build_report(short, long)

            self.assertEqual(report["decision"], "seeded_stochastic_watch_blocked")
            self.assertTrue(any("mismatch" in error for error in report["errors"]))

    def test_low_entropy_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            short = root / "short.json"
            long = root / "long.json"
            write_json(short, comparison_payload(seconds=60.0, seeds=10, entropy=0.4))
            write_json(long, comparison_payload(seconds=180.0, seeds=3))

            report = build_report(short, long)

            self.assertEqual(report["decision"], "seeded_stochastic_watch_blocked")
            self.assertTrue(any("entropy" in error for error in report["errors"]))

    def test_acceptance_wording_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            short = root / "short.json"
            long = root / "long.json"
            payload = comparison_payload(seconds=60.0, seeds=10)
            payload["gate_decision"] = "rl_test_bot_candidate"
            write_json(short, payload)
            write_json(long, comparison_payload(seconds=180.0, seeds=3))

            report = build_report(short, long)

            self.assertEqual(report["decision"], "seeded_stochastic_watch_blocked")
            self.assertTrue(any("too strong" in error for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()
