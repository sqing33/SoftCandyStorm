#!/usr/bin/env python3
"""Tests for RL failure-lane repair preflight generation."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from create_rl_failure_lane_repair_preflight import build_report  # noqa: E402


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sample_trace_summary() -> dict[str, Any]:
    return {
        "report_version": 1,
        "decision": "rl_failure_lane_trace_diagnostics_recorded",
        "source_trace_plan": "reports/trace_plan.json",
        "source_failure_analysis": "reports/failure_analysis.json",
        "map_id": "caramel-workshop",
        "lanes": [
            {
                "lane": "opening_repair",
                "seeds": [63402],
                "candidate_comparison": "reports/opening/candidate_comparison.json",
                "route_hotspots": "reports/opening/route_hotspots.json",
                "hotspot_summary": {
                    "trace_count": 1,
                    "sample_count": 82,
                    "negative_sample_count": 51,
                    "negative_sample_ratio": 0.622,
                    "time_bucket_hotspots": {"opening_lt_60": 51},
                    "pressure_hotspots": {"boundary_edge": 47},
                    "action_counts": {"5": 39, "4": 10, "2": 2},
                },
            },
            {
                "lane": "late_terminal_survival_conversion",
                "seeds": [63400, 63401, 63403],
                "extra_scan_seeds": [63402],
                "candidate_comparison": "reports/late/candidate_comparison.json",
                "route_hotspots_late_seeds_only": "reports/late/route_hotspots_late_seeds_only.json",
                "route_hotspots_all_scanned_seeds": "reports/late/route_hotspots.json",
                "hotspot_summary": {
                    "trace_count": 3,
                    "sample_count": 900,
                    "negative_sample_count": 600,
                    "negative_sample_ratio": 0.6667,
                    "time_bucket_hotspots": {
                        "opening_lt_60": 100,
                        "mid_60_to_180": 350,
                        "late_180_to_300": 150,
                    },
                    "pressure_hotspots": {"boundary_edge": 550, "low_health": 25},
                    "action_counts": {"5": 210, "7": 160, "1": 100},
                },
            },
        ],
    }


class RlFailureLaneRepairPreflightTests(unittest.TestCase):
    def test_builds_required_preflights_for_opening_and_late_lanes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "trace_summary.json"
            write_json(source, sample_trace_summary())

            report = build_report(source)

        self.assertEqual(report["decision"], "rl_failure_lane_repair_preflight_ready")
        lanes = {lane["lane"]: lane for lane in report["preflight_lanes"]}
        opening = lanes["opening_repair"]
        self.assertEqual(opening["classification"], "opening_boundary_action_lock")
        self.assertEqual(opening["dominant_action"], "5")
        self.assertEqual(opening["trace_quality"]["negative_sample_count"], 51)
        self.assertEqual(opening["required_preflights"][0]["seed"], 63402)

        late = lanes["late_terminal_survival_conversion"]
        self.assertEqual(late["classification"], "terminal_conversion_with_opening_mid_route_debt")
        self.assertEqual(late["repair_shape"], "path-retention-preserving terminal conversion")
        self.assertEqual(late["dominant_action"], "5")
        self.assertEqual(late["required_preflights"][0]["eval_episodes"], 10)
        self.assertIn("terminal branch that ignores 60-180s path retention debt", late["blocked_patterns"])

    def test_missing_lanes_is_invalid(self) -> None:
        payload = sample_trace_summary()
        payload["lanes"] = [payload["lanes"][0]]
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "trace_summary.json"
            write_json(source, payload)

            report = build_report(source)

        self.assertEqual(report["decision"], "rl_failure_lane_repair_preflight_invalid")
        self.assertIn("missing late_terminal_survival_conversion lane", report["errors"])

    def test_invalid_json_shape_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "trace_summary.json"
            write_json(source, [])

            report = build_report(source)

        self.assertEqual(report["decision"], "rl_failure_lane_repair_preflight_invalid")
        self.assertTrue(any("must contain a JSON object" in error for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()
