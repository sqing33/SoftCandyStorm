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


def distribution_from_ratios(ratios: dict[str, float]) -> dict:
    return {
        action: {
            "count": int(round(ratio * 1000)),
            "ratio": ratio,
        }
        for action, ratio in ratios.items()
    }


def comparison_payload(
    seconds: float,
    win_rates: dict[str, float],
    survival: dict[str, float] | None = None,
    seed_start: int | None = None,
    seeds: int | None = None,
    action_distributions: dict[str, dict[str, float]] | None = None,
    normalized_entropy: dict[str, float] | None = None,
) -> dict:
    survival = survival or {map_id: seconds for map_id in win_rates}
    normalized_entropy = normalized_entropy or {}
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
    payload = {
        "report_version": 1,
        "status": "compared",
        "seconds": seconds,
        "seed_start": seed_start,
        "seeds": seeds,
        "map_preset": "high-pressure",
        "action_selection": "deterministic",
        "reward_profile": "standard",
        "gate_decision": "multimap_comparison_recorded_not_balance_gate",
        "summary": {
            "maps": maps,
            "map_count": len(maps),
            "minimum_policy_win_rate": min(win_rates.values()),
        },
    }
    if action_distributions is not None:
        payload["maps"] = [
            {
                "map_id": map_id,
                "policy": {
                    "summary": {
                        "action_distribution": distribution_from_ratios(
                            action_distributions[map_id]
                        ),
                        "normalized_action_entropy": normalized_entropy.get(map_id, 0.75),
                    }
                },
            }
            for map_id in win_rates
        ]
    return payload


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

    def test_seed_start_mismatch_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            baseline = root / "baseline_60.json"
            candidate = root / "candidate_60.json"
            write_json(
                baseline,
                comparison_payload(60.0, {"soda-creek": 1.0}, seed_start=62800, seeds=3),
            )
            write_json(
                candidate,
                comparison_payload(60.0, {"soda-creek": 1.0}, seed_start=63100, seeds=3),
            )

            report = build_report({"60s": baseline}, {"60s": candidate})

        self.assertEqual(report["decision"], "policy_window_regression_invalid")
        self.assertTrue(any("seed_start" in error for error in report["errors"]))

    def test_action_ratio_delta_blocks_full_distribution_shift(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            baseline = root / "baseline_60.json"
            candidate = root / "candidate_60.json"
            write_json(
                baseline,
                comparison_payload(
                    60.0,
                    {"caramel-workshop": 1.0},
                    action_distributions={
                        "caramel-workshop": {"0": 0.4, "1": 0.4, "2": 0.2}
                    },
                ),
            )
            write_json(
                candidate,
                comparison_payload(
                    60.0,
                    {"caramel-workshop": 1.0},
                    action_distributions={
                        "caramel-workshop": {"0": 0.4, "1": 0.1, "2": 0.5}
                    },
                ),
            )

            report = build_report(
                {"60s": baseline},
                {"60s": candidate},
                max_action_ratio_increase=0.2,
            )

        self.assertEqual(report["decision"], "policy_window_regression_failed")
        self.assertTrue(any("action 2 ratio increased" in item for item in report["blockers"]))
        action_delta = report["windows"][0]["map_results"][0]["action_distribution_delta"]
        self.assertEqual(action_delta["max_action_ratio_increase"]["action"], "2")

    def test_action_distribution_l1_delta_can_block_broad_churn(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            baseline = root / "baseline_180.json"
            candidate = root / "candidate_180.json"
            write_json(
                baseline,
                comparison_payload(
                    180.0,
                    {"soda-creek": 1.0},
                    action_distributions={"soda-creek": {"0": 0.5, "1": 0.5}},
                ),
            )
            write_json(
                candidate,
                comparison_payload(
                    180.0,
                    {"soda-creek": 1.0},
                    action_distributions={
                        "soda-creek": {"0": 0.35, "1": 0.35, "2": 0.3}
                    },
                ),
            )

            report = build_report(
                {"180s": baseline},
                {"180s": candidate},
                max_action_ratio_increase=0.35,
                max_action_distribution_l1_delta=0.5,
            )

        self.assertEqual(report["decision"], "policy_window_regression_failed")
        self.assertTrue(
            any("action_distribution_l1_delta" in item for item in report["blockers"])
        )

    def test_normalized_entropy_drop_can_block_without_distribution_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            baseline = root / "baseline_300.json"
            candidate = root / "candidate_300.json"
            write_json(
                baseline,
                comparison_payload(
                    300.0,
                    {"cracked-star-jar": 0.0},
                    action_distributions={"cracked-star-jar": {"0": 0.5, "1": 0.5}},
                    normalized_entropy={"cracked-star-jar": 0.8},
                ),
            )
            write_json(
                candidate,
                comparison_payload(
                    300.0,
                    {"cracked-star-jar": 0.0},
                    action_distributions={"cracked-star-jar": {"0": 0.9, "1": 0.1}},
                    normalized_entropy={"cracked-star-jar": 0.55},
                ),
            )

            report = build_report(
                {"300s": baseline},
                {"300s": candidate},
                max_normalized_entropy_drop=0.2,
            )

        self.assertEqual(report["decision"], "policy_window_regression_failed")
        self.assertTrue(
            any("normalized_action_entropy dropped" in item for item in report["blockers"])
        )


if __name__ == "__main__":
    unittest.main()
