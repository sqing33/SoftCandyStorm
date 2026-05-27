#!/usr/bin/env python3
"""Regression tests for RL policy failure analysis."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from analyze_rl_policy_failures import build_report


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def episode(seed: int, time_seconds: float, terminal_kind: str) -> dict:
    return {
        "seed": seed,
        "time_seconds": time_seconds,
        "terminal_kind": terminal_kind,
        "terminal_reason": "duration_reached" if terminal_kind == "victory" else "player_health_depleted",
        "level": 3,
        "kills": 42,
        "damage_taken": 12.5 if terminal_kind == "victory" else 120.0,
        "action_counts": {
            "0": 0,
            "1": 10,
            "2": 0,
            "3": 20,
        },
        "reward_breakdown": {
            "total": 1.0 if terminal_kind == "victory" else -2.0,
        },
    }


def comparison_payload() -> dict:
    return {
        "report_version": 1,
        "status": "compared",
        "algorithm": "ppo",
        "model_path": "fixture.zip",
        "map_preset": "high-pressure",
        "seconds": 300,
        "seed_start": 100,
        "seeds": 3,
        "gate_decision": "multimap_comparison_recorded_needs_policy_repair",
        "findings": [{"id": "zero_policy_win_rate"}],
        "maps": [
            {
                "map_id": "soda-creek",
                "gate_decision": "comparison_recorded_not_balance_gate",
                "policy": {
                    "episodes": [
                        episode(100, 20.0, "defeat"),
                        episode(101, 90.0, "defeat"),
                        episode(102, 220.0, "defeat"),
                    ],
                    "summary": {
                        "win_rate": 0.0,
                        "average_survival_seconds": 110.0,
                        "normalized_action_entropy": 0.5,
                        "action_distribution": {
                            "0": {"count": 0, "ratio": 0.0},
                            "1": {"count": 30, "ratio": 0.3333},
                            "2": {"count": 0, "ratio": 0.0},
                            "3": {"count": 60, "ratio": 0.6667},
                        },
                        "reward_breakdown_average": {"total": -2.0},
                    },
                },
            },
            {
                "map_id": "cracked-star-jar",
                "gate_decision": "comparison_recorded_not_balance_gate",
                "policy": {
                    "episodes": [
                        episode(100, 300.0, "victory"),
                        episode(101, 210.0, "defeat"),
                    ],
                    "summary": {
                        "win_rate": 0.5,
                        "average_survival_seconds": 255.0,
                        "normalized_action_entropy": 0.8,
                        "action_distribution": {
                            "1": {"count": 10, "ratio": 0.25},
                            "7": {"count": 30, "ratio": 0.75},
                        },
                        "reward_breakdown_average": {"total": 1.0},
                    },
                },
            },
        ],
    }


class RlPolicyFailureAnalysisTests(unittest.TestCase):
    def test_build_report_buckets_failures_by_map_and_time(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "comparison.json"
            write_json(path, comparison_payload())

            report = build_report(path)

            self.assertEqual(report["decision"], "rl_policy_failure_analysis_recorded")
            self.assertEqual(report["total_failures"], 4)
            self.assertEqual(report["repair_maps"], ["soda-creek", "cracked-star-jar"])
            soda = report["maps"][0]
            self.assertEqual(soda["failure_count"], 3)
            self.assertEqual(soda["failure_time_bucket_distribution"]["opening_lt_60"]["count"], 1)
            self.assertEqual(soda["failure_time_bucket_distribution"]["mid_60_to_180"]["count"], 1)
            self.assertEqual(soda["failure_time_bucket_distribution"]["late_180_to_300"]["count"], 1)
            self.assertEqual(soda["policy_dominant_action"]["action"], "3")

    def test_build_report_accepts_single_policy_evaluation(self) -> None:
        payload = {
            "report_version": 1,
            "status": "evaluated",
            "algorithm": "behavior_clone",
            "model_path": "fixture.pt",
            "seconds": 180,
            "seed_start": 62400,
            "seeds": 2,
            "gate_decision": "evaluation_recorded_not_policy_gate",
            "policy": {
                "map_id": "soda-creek",
                "gate_decision": "evaluation_recorded_not_policy_gate",
                "episodes": [
                    episode(62400, 22.5, "defeat"),
                    episode(62401, 180.0, "victory"),
                ],
                "summary": {
                    "win_rate": 0.5,
                    "average_survival_seconds": 101.25,
                    "normalized_action_entropy": 0.6,
                    "action_distribution": {
                        "1": {"count": 10, "ratio": 0.25},
                        "3": {"count": 30, "ratio": 0.75},
                    },
                    "reward_breakdown_average": {"total": -0.5},
                },
            },
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "evaluation.json"
            write_json(path, payload)

            report = build_report(path)

        self.assertEqual(report["decision"], "rl_policy_failure_analysis_recorded")
        self.assertEqual(report["map_count"], 1)
        self.assertEqual(report["total_failures"], 1)
        self.assertEqual(report["repair_maps"], ["soda-creek"])
        self.assertEqual(report["maps"][0]["map_id"], "soda-creek")
        self.assertEqual(report["maps"][0]["failure_time_bucket_distribution"]["opening_lt_60"]["count"], 1)


if __name__ == "__main__":
    unittest.main()
