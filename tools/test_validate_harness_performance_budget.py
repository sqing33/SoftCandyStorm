#!/usr/bin/env python3
"""Regression tests for Harness performance budget validation.

Run with:
    python3 tools/test_validate_harness_performance_budget.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "tools" / "validate_harness_performance_budget.py"

sys.path.insert(0, str(REPO_ROOT / "tools"))

from validate_harness_performance_budget import build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def valid_metrics() -> dict:
    return {
        "kind": "bot_matrix",
        "bots": [
            {
                "bot": "kite",
                "map_id": "frosting-grassland",
                "seed_start": 12345,
                "seeds": 2,
                "seconds": 600.0,
                "tick_rate": 30,
                "victories": 1,
                "win_rate": 0.5,
                "gate_status": "pass",
                "average_duration_seconds": 450.0,
                "average_level": 12.0,
                "average_kills": 800.0,
                "max_enemy_count": 34,
                "runs": [
                    {
                        "seed": 12345,
                        "terminal": "victory",
                        "duration_seconds": 600.008,
                        "level": 16,
                        "kills": 1200,
                        "damage_taken": 10.0,
                        "max_enemy_count": 34,
                    },
                    {
                        "seed": 12346,
                        "terminal": "defeat",
                        "duration_seconds": 300.0,
                        "level": 8,
                        "kills": 400,
                        "damage_taken": 120.0,
                        "max_enemy_count": 20,
                    },
                ],
            }
        ],
    }


class HarnessPerformanceBudgetValidatorTests(unittest.TestCase):
    def test_valid_metrics_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            metrics_path = Path(temp_dir) / "metrics.json"
            write_json(metrics_path, valid_metrics())

            report = build_report(metrics_path)

            self.assertEqual(report["decision"], "harness_performance_budget_valid")
            self.assertEqual(report["errors"], [])
            self.assertEqual(report["summary"]["run_count"], 2)
            self.assertEqual(report["summary"]["observed_max_enemy_count"], 34)

    def test_enemy_ceiling_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            metrics = valid_metrics()
            metrics["bots"][0]["max_enemy_count"] = 141
            metrics["bots"][0]["runs"][0]["max_enemy_count"] = 141
            metrics_path = Path(temp_dir) / "metrics.json"
            write_json(metrics_path, metrics)

            report = build_report(metrics_path)

            self.assertEqual(report["decision"], "harness_performance_budget_invalid")
            self.assertTrue(any("exceeds headless ceiling" in error for error in report["errors"]))

    def test_nonfinite_value_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            metrics = valid_metrics()
            metrics["bots"][0]["runs"][0]["damage_taken"] = float("nan")
            metrics_path = Path(temp_dir) / "metrics.json"
            write_json(metrics_path, metrics)

            report = build_report(metrics_path)

            self.assertEqual(report["decision"], "harness_performance_budget_invalid")
            self.assertTrue(any("damage_taken" in error for error in report["errors"]))

    def test_bool_numeric_value_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            metrics = valid_metrics()
            metrics["bots"][0]["runs"][0]["damage_taken"] = True
            metrics_path = Path(temp_dir) / "metrics.json"
            write_json(metrics_path, metrics)

            report = build_report(metrics_path)

            self.assertEqual(report["decision"], "harness_performance_budget_invalid")
            self.assertTrue(any("damage_taken" in error for error in report["errors"]))

    def test_non_terminal_or_overlong_run_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            metrics = valid_metrics()
            metrics["bots"][0]["runs"][0]["terminal"] = "not_terminal"
            metrics["bots"][0]["runs"][0]["duration_seconds"] = 700.0
            metrics_path = Path(temp_dir) / "metrics.json"
            write_json(metrics_path, metrics)

            report = build_report(metrics_path)

            self.assertEqual(report["decision"], "harness_performance_budget_invalid")
            self.assertTrue(any("terminal" in error for error in report["errors"]))
            self.assertTrue(any("duration_seconds" in error for error in report["errors"]))

    def test_cli_writes_report_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            metrics_path = root / "metrics.json"
            report_path = root / "report.json"
            markdown_path = root / "summary.md"
            write_json(metrics_path, valid_metrics())

            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(metrics_path),
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
                "harness_performance_budget_valid",
            )
            self.assertIn("Harness Performance Budget Validation", markdown_path.read_text(encoding="utf-8"))

    def test_cli_writes_invalid_report_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            metrics_path = root / "metrics.json"
            report_path = root / "report.json"
            markdown_path = root / "summary.md"
            write_json(metrics_path, {"kind": "bot_matrix", "bots": ["not-an-object"]})

            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(metrics_path),
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

            self.assertEqual(result.returncode, 1)
            self.assertEqual(
                json.loads(report_path.read_text(encoding="utf-8"))["decision"],
                "harness_performance_budget_invalid",
            )
            self.assertIn("bots[0]: must be an object", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
