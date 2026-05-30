#!/usr/bin/env python3

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from compare_policy_episode_traces import build_report


def write_trace(path: Path, seed: int, terminal: str, actions: list[int]) -> None:
    steps = []
    for index, action in enumerate(actions, start=1):
        steps.append(
            {
                "step": index,
                "time_seconds": float(index),
                "action": action,
                "health": 100.0 - index,
                "reward_breakdown": {"route_recovery": -0.001 if action == 5 else 0.0},
                "diagnostics": {
                    "boundary": {"min_distance": 0.0, "edge_risk": 1.0},
                    "enemy_pressure_risk": 1.0 if action == 5 else 0.0,
                    "low_health_risk": 0.0,
                    "nearest_enemy": {"hitbox_distance": 0.0},
                },
                "action_score": {
                    "kind": "probability",
                    "top_actions": [
                        {"action": str(action), "score": 0.8},
                        {"action": "7", "score": 0.1},
                    ],
                },
            }
        )
    payload = {
        "record_type": "policy_episode_trace",
        "episode": {
            "seed": seed,
            "map_id": "soda-creek",
            "terminal_kind": terminal,
            "terminal_reason": "duration_reached" if terminal == "victory" else "player_health_depleted",
            "time_seconds": float(len(actions)),
        },
        "sample_count": len(steps),
        "steps": steps,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


class ComparePolicyEpisodeTracesTests(unittest.TestCase):
    def test_target_seed_compares_against_success_average(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            root = Path(raw_root)
            base = root / "base"
            candidate = root / "candidate"
            write_trace(base / "soda-creek_seed1_trace.json", 1, "victory", [7, 7, 3])
            write_trace(base / "soda-creek_seed3_trace.json", 3, "defeat", [4, 4, 4])
            write_trace(candidate / "soda-creek_seed1_trace.json", 1, "victory", [7, 7, 3])
            write_trace(candidate / "soda-creek_seed3_trace.json", 3, "defeat", [5, 5, 5])

            report = build_report(
                [
                    f"base={base}",
                    f"candidate={candidate}",
                ],
                target_seed=3,
            )

        self.assertEqual(report["decision"], "policy_episode_trace_comparison_recorded")
        candidate_target = report["target_seed_analysis"]["candidate"]
        self.assertIn("7", candidate_target["missing_success_actions"])
        self.assertIn("5", candidate_target["excess_target_actions"])
        seed3 = next(row for row in report["matched_seed_comparison"] if row["seed"] == 3)
        self.assertEqual(
            seed3["first_divergent_action"],
            {
                "step": 1,
                "time_seconds": 1.0,
                "left_action": "4",
                "right_action": "5",
            },
        )


if __name__ == "__main__":
    unittest.main()
