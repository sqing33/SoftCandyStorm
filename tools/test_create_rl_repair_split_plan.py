#!/usr/bin/env python3
"""Tests for RL repair split-plan generation."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from create_rl_repair_split_plan import build_plan  # noqa: E402


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sample_gate_payload() -> dict[str, Any]:
    return {
        "decision": "rl_repair_probe_gate_failed",
        "gate_decision": "rl_repair_probe_gate_failed",
        "blockers": [
            "parent/window_regression: 300s/caramel action delta too high",
            "opening63402/target_seed_preflight: defeat before 60s",
            "opening63402/target_seed_preflight: terminal_kind is defeat",
            "short60/window_target_preflight: win_rate below threshold",
            "unscoped/manual-review: inspect training report wording",
        ],
        "target_seed_preflights": [
            {
                "label": "target63407",
                "path": "reports/target_seed_preflight_seed63407.json",
                "required": True,
                "decision": "policy_target_seed_preflight_passed",
                "blocker_count": 0,
                "error_count": 0,
            },
            {
                "label": "opening63402",
                "path": "reports/target_seed_preflight_seed63402_opening.json",
                "required": True,
                "decision": "policy_target_seed_preflight_failed",
                "blocker_count": 2,
                "error_count": 0,
            },
        ],
        "window_regressions": [
            {
                "label": "parent",
                "path": "reports/window_regression_high_pressure_vs_parent.json",
                "required": True,
                "decision": "policy_window_regression_failed",
                "blocker_count": 1,
                "error_count": 0,
            }
        ],
        "window_target_preflights": [
            {
                "label": "short60",
                "path": "reports/window_target_preflight_60s_caramel.json",
                "required": True,
                "decision": "policy_window_target_preflight_failed",
                "blocker_count": 1,
                "error_count": 0,
            }
        ],
        "policy_adapter_scopes": [
            {
                "label": "scope",
                "path": "reports/policy_adapter_scope.json",
                "required": True,
                "decision": "policy_adapter_scope_passed",
                "blocker_count": 0,
                "error_count": 0,
            }
        ],
    }


class RlRepairSplitPlanTests(unittest.TestCase):
    def test_groups_blockers_by_repair_lane(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "repair_gate.json"
            write_json(path, sample_gate_payload())

            report = build_plan(path)

        self.assertEqual(report["decision"], "rl_repair_split_plan_ready")
        self.assertEqual(report["failed_lanes"], ["opening63402", "short60", "parent"])
        self.assertEqual(report["passed_lanes"], ["target63407", "scope"])
        lanes = {lane["label"]: lane for lane in report["lanes"]}
        self.assertEqual(lanes["opening63402"]["blocker_count"], 2)
        self.assertEqual(len(lanes["opening63402"]["blockers"]), 2)
        self.assertEqual(lanes["target63407"]["status"], "passed")
        self.assertEqual(
            report["unassigned_blockers"],
            ["unscoped/manual-review: inspect training report wording"],
        )

    def test_invalid_top_level_json_shape_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "repair_gate.json"
            write_json(path, [])

            report = build_plan(path)

        self.assertEqual(report["decision"], "rl_repair_split_plan_invalid")
        self.assertTrue(any("must contain a JSON object" in error for error in report["errors"]))

    def test_invalid_section_shape_is_reported(self) -> None:
        payload = sample_gate_payload()
        payload["target_seed_preflights"] = {"label": "target63407"}
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "repair_gate.json"
            write_json(path, payload)

            report = build_plan(path)

        self.assertEqual(report["decision"], "rl_repair_split_plan_invalid")
        self.assertIn("target_seed_preflights must be a list when present", report["errors"])

    def test_lane_errors_mark_plan_invalid(self) -> None:
        payload = sample_gate_payload()
        payload["policy_adapter_scopes"][0]["decision"] = "policy_adapter_scope_invalid"
        payload["policy_adapter_scopes"][0]["error_count"] = 1
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "repair_gate.json"
            write_json(path, payload)

            report = build_plan(path)

        self.assertEqual(report["decision"], "rl_repair_split_plan_invalid")
        self.assertEqual(report["invalid_lanes"], ["scope"])

    def test_bad_count_fields_are_reported_without_crashing(self) -> None:
        payload = sample_gate_payload()
        payload["target_seed_preflights"][1]["blocker_count"] = "many"
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "repair_gate.json"
            write_json(path, payload)

            report = build_plan(path)

        self.assertEqual(report["decision"], "rl_repair_split_plan_invalid")
        self.assertIn("opening63402: blocker_count must be a non-negative integer", report["errors"])


if __name__ == "__main__":
    unittest.main()
