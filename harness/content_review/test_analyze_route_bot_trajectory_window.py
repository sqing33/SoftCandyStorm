#!/usr/bin/env python3
"""Regression tests for RouteBot trajectory window diagnostics."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
ANALYZER = SCRIPT_DIR / "analyze_route_bot_trajectory_window.py"

sys.path.insert(0, str(SCRIPT_DIR))

from analyze_route_bot_trajectory_window import build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")


def metrics_payload() -> dict:
    return {
        "kind": "bot_matrix",
        "bots": [
            {
                "bot": "route",
                "runs": [
                    {
                        "seed": 1,
                        "terminal": "victory",
                        "duration_seconds": 300.0,
                        "level": 7,
                        "kills": 540,
                        "damage_taken": 80.0,
                    },
                    {
                        "seed": 2,
                        "terminal": "defeat",
                        "duration_seconds": 220.0,
                        "level": 5,
                        "kills": 330,
                        "damage_taken": 120.0,
                    },
                    {
                        "seed": 3,
                        "terminal": "defeat",
                        "duration_seconds": 120.0,
                        "level": 3,
                        "kills": 100,
                        "damage_taken": 120.0,
                    },
                ],
            }
        ],
    }


def diagnostics(edge: float, enemy: float, safety: float) -> dict:
    return {
        "player_position": {"x": 0.0, "y": 0.0},
        "player_velocity": {"x": 1.0, "y": 0.0},
        "map_size": {"width": 1600.0, "height": 1200.0},
        "boundary": {
            "left_distance": 800.0,
            "right_distance": 800.0,
            "bottom_distance": 600.0,
            "top_distance": 600.0,
            "min_distance": 600.0,
            "edge_risk": edge,
        },
        "nearest_enemy": {
            "enemy_id": "licorice-skipper",
            "behavior": "dash",
            "position": {"x": 48.0, "y": 0.0},
            "velocity": {"x": -1.0, "y": 0.0},
            "center_distance": 48.0,
            "hitbox_distance": 32.0,
            "radius": 16.0,
            "threat": 60.0,
            "health_ratio": 1.0,
            "is_boss": False,
            "is_elite": False,
        },
        "visible_enemy_count": 6,
        "nearby_enemy_count_160": 2,
        "nearby_enemy_count_240": 4,
        "active_hazard_count": 0,
        "low_health_risk": 0.1,
        "enemy_pressure_risk": enemy,
        "hazard_pressure_risk": 0.0,
        "boss_pressure_risk": 0.2,
        "safety_risk_score": safety,
    }


def sample(seed: int, terminal_health: float, edge: float, enemy: float, safety: float) -> dict:
    return {
        "record_type": "sample",
        "seed": seed,
        "map_id": "frosting-grassland",
        "bot": "route",
        "tick": 6300,
        "time_seconds": 210.0,
        "health_ratio": terminal_health,
        "level": 6,
        "kills": 350,
        "action": 3,
        "movement": [1.0, 0.0],
        "diagnostics": diagnostics(edge, enemy, safety),
        "observation": [0.1, 0.2],
    }


class RouteBotTrajectoryWindowAnalyzerTests(unittest.TestCase):
    def test_valid_window_diagnostics_compare_victory_and_defeat(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            trajectory = root / "route.jsonl"
            metrics = root / "metrics.json"
            write_json(metrics, metrics_payload())
            write_jsonl(
                trajectory,
                [
                    {
                        "record_type": "metadata",
                        "dataset_version": "bot-trajectory-v0",
                        "bot": "route",
                        "map_id": "frosting-grassland",
                        "sample_start_seconds": 200.0,
                        "sample_end_seconds": 240.0,
                        "sample_stride": 30,
                        "content_hash": "fnv1a64:test",
                        "content_dir": "harness/generated_candidates/test_pack",
                    },
                    sample(1, 0.8, 0.1, 0.2, 0.15),
                    {
                        "record_type": "episode",
                        "seed": 1,
                        "map_id": "frosting-grassland",
                        "bot": "route",
                        "terminal": "victory",
                    },
                    sample(2, 0.25, 0.2, 0.5, 0.45),
                    {
                        "record_type": "episode",
                        "seed": 2,
                        "map_id": "frosting-grassland",
                        "bot": "route",
                        "terminal": "defeat",
                    },
                ],
            )

            report = build_report(trajectory, metrics)

            self.assertEqual(report["decision"], "route_bot_trajectory_window_valid")
            self.assertEqual(report["victory_seed_count"], 1)
            self.assertEqual(report["defeat_seed_count"], 2)
            self.assertEqual(report["sampled_defeat_seed_count"], 1)
            self.assertEqual(report["missing_window_seeds"], [3])
            self.assertEqual(report["victory_group"]["avg_health_ratio"], 0.8)
            self.assertEqual(report["defeat_group"]["avg_enemy_pressure_risk"], 0.5)

    def test_missing_diagnostics_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            trajectory = root / "route.jsonl"
            metrics = root / "metrics.json"
            write_json(metrics, metrics_payload())
            bad_sample = sample(1, 0.8, 0.1, 0.2, 0.15)
            bad_sample.pop("diagnostics")
            write_jsonl(
                trajectory,
                [
                    bad_sample,
                    {"record_type": "episode", "seed": 1, "bot": "route", "terminal": "victory"},
                ],
            )

            report = build_report(trajectory, metrics)

            self.assertEqual(report["decision"], "route_bot_trajectory_window_invalid")
            self.assertIn("sample records are missing diagnostics", report["errors"])

    def test_cli_writes_report_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            trajectory = root / "route.jsonl"
            metrics = root / "metrics.json"
            report_path = root / "report.json"
            markdown_path = root / "summary.md"
            write_json(metrics, metrics_payload())
            write_jsonl(
                trajectory,
                [
                    sample(1, 0.8, 0.1, 0.2, 0.15),
                    {"record_type": "episode", "seed": 1, "bot": "route", "terminal": "victory"},
                    sample(2, 0.25, 0.2, 0.5, 0.45),
                    {"record_type": "episode", "seed": 2, "bot": "route", "terminal": "defeat"},
                ],
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ANALYZER),
                    str(trajectory),
                    "--metrics",
                    str(metrics),
                    "--report",
                    str(report_path),
                    "--markdown",
                    str(markdown_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                json.loads(report_path.read_text(encoding="utf-8"))["decision"],
                "route_bot_trajectory_window_valid",
            )
            self.assertIn("RouteBot Trajectory Window Diagnostic", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
