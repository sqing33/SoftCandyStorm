#!/usr/bin/env python3
"""Tests for target seed policy preflight validation."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from validate_policy_target_seed_preflight import build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def comparison_payload(episode: dict, *, seconds: float = 60.0) -> dict:
    map_id = episode["map_id"]
    return {
        "report_version": 1,
        "status": "compared",
        "seconds": seconds,
        "gate_decision": "multimap_comparison_recorded_not_balance_gate",
        "action_selection": "deterministic",
        "reward_profile": "opening-boundary-escape",
        "maps": [
            {
                "map_id": map_id,
                "policy": {
                    "status": "evaluated",
                    "episodes": [episode],
                    "summary": {
                        "win_rate": 1.0 if episode["terminal_kind"] == "victory" else 0.0,
                    },
                },
            }
        ],
    }


def top_level_evaluation_payload(episode: dict, *, seconds: float = 300.0) -> dict:
    return {
        "report_version": 1,
        "status": "evaluated",
        "seconds": seconds,
        "map_id": episode["map_id"],
        "gate_decision": "evaluation_recorded_not_policy_gate",
        "action_selection": "deterministic",
        "reward_profile": "standard",
        "episodes": [episode],
        "summary": {
            "win_rate": 1.0 if episode["terminal_kind"] == "victory" else 0.0,
        },
    }


class PolicyTargetSeedPreflightTests(unittest.TestCase):
    def test_target_window_survival_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "comparison.json"
            write_json(
                path,
                comparison_payload(
                    {
                        "map_id": "soda-creek",
                        "seed": 63402,
                        "time_seconds": 60.0327,
                        "terminal_kind": "victory",
                        "terminal_reason": "duration_reached",
                        "action_counts": {"7": 120, "1": 80},
                    }
                ),
            )

            report = build_report(
                path,
                [("soda-creek", 63402)],
                require_window_survival=True,
                require_non_defeat=True,
                min_action_ratios=[("7", 0.5)],
            )

        self.assertEqual(report["decision"], "policy_target_seed_preflight_passed")
        self.assertEqual(report["blockers"], [])
        self.assertEqual(report["target_results"][0]["action_ratios"]["7"], 0.6)

    def test_top_level_evaluation_episodes_are_supported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "evaluation.json"
            write_json(
                path,
                top_level_evaluation_payload(
                    {
                        "map_id": "caramel-workshop",
                        "seed": 63407,
                        "time_seconds": 300.015,
                        "terminal_kind": "victory",
                        "terminal_reason": "duration_reached",
                        "action_counts": {"3": 100, "5": 75, "7": 25},
                    }
                ),
            )

            report = build_report(
                path,
                [("caramel-workshop", 63407)],
                require_window_survival=True,
                max_action_ratios=[("5", 0.5)],
            )

        self.assertEqual(report["decision"], "policy_target_seed_preflight_passed")
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["blockers"], [])
        self.assertEqual(report["target_results"][0]["action_ratios"]["5"], 0.375)

    def test_target_defeat_before_window_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "comparison.json"
            write_json(
                path,
                comparison_payload(
                    {
                        "map_id": "soda-creek",
                        "seed": 63402,
                        "time_seconds": 45.233,
                        "terminal_kind": "defeat",
                        "terminal_reason": "player_health_depleted",
                        "action_counts": {"8": 571, "2": 472, "1": 305},
                    }
                ),
            )

            report = build_report(
                path,
                [("soda-creek", 63402)],
                require_window_survival=True,
                require_non_defeat=True,
            )

        self.assertEqual(report["decision"], "policy_target_seed_preflight_failed")
        self.assertTrue(any("did not reach window" in item for item in report["blockers"]))
        self.assertTrue(any("terminal_kind `defeat` is not `victory`" in item for item in report["blockers"]))

    def test_action_ratio_bounds_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "comparison.json"
            write_json(
                path,
                comparison_payload(
                    {
                        "map_id": "soda-creek",
                        "seed": 63402,
                        "time_seconds": 60.0,
                        "terminal_kind": "victory",
                        "terminal_reason": "duration_reached",
                        "action_counts": {"1": 90, "7": 10},
                    }
                ),
            )

            report = build_report(
                path,
                [("soda-creek", 63402)],
                min_action_ratios=[("7", 0.2)],
                max_action_ratios=[("1", 0.5)],
            )

        self.assertEqual(report["decision"], "policy_target_seed_preflight_failed")
        self.assertTrue(any("action 7 ratio" in item for item in report["blockers"]))
        self.assertTrue(any("action 1 ratio" in item for item in report["blockers"]))

    def test_missing_target_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "comparison.json"
            write_json(
                path,
                comparison_payload(
                    {
                        "map_id": "soda-creek",
                        "seed": 63400,
                        "time_seconds": 60.0,
                        "terminal_kind": "victory",
                        "terminal_reason": "duration_reached",
                        "action_counts": {"7": 100},
                    }
                ),
            )

            report = build_report(path, [("soda-creek", 63402)])

        self.assertEqual(report["decision"], "policy_target_seed_preflight_failed")
        self.assertTrue(any("target episode missing" in item for item in report["blockers"]))


if __name__ == "__main__":
    unittest.main()
