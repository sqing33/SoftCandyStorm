#!/usr/bin/env python3
"""Regression tests for RL repair probe gate validation."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from validate_rl_repair_probe_gate import build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def training_payload(gate_decision: str = "trained_needs_rule_bot_comparison") -> dict:
    return {
        "status": "trained",
        "gate_decision": gate_decision,
        "model_path": "reports/model.zip",
        "reward_profile": "late-route-recovery",
    }


def alignment_payload(*, blockers: list[str] | None = None) -> dict:
    blockers = blockers or []
    return {
        "decision": (
            "behavior_clone_anchor_alignment_failed"
            if blockers
            else "behavior_clone_anchor_alignment_within_thresholds"
        ),
        "gate_decision": (
            "behavior_clone_anchor_alignment_failed"
            if blockers
            else "behavior_clone_anchor_alignment_within_thresholds"
        ),
        "overall": {"mean_kl": 0.12, "argmax_agreement": 0.88},
        "blockers": blockers,
    }


def regression_payload(*, blockers: list[str] | None = None) -> dict:
    blockers = blockers or []
    return {
        "decision": (
            "policy_window_regression_failed"
            if blockers
            else "policy_window_regression_passed"
        ),
        "gate_decision": (
            "policy_window_regression_failed"
            if blockers
            else "policy_window_regression_passed"
        ),
        "errors": [],
        "blockers": blockers,
    }


class RlRepairProbeGateTests(unittest.TestCase):
    def test_clean_bundle_passes_for_limited_followup(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            training = root / "training.json"
            alignment = root / "alignment.json"
            regression = root / "regression.json"
            write_json(training, training_payload())
            write_json(alignment, alignment_payload())
            write_json(regression, regression_payload())

            report = build_report(
                training_report=training,
                anchor_alignment=alignment,
                window_regressions=[regression],
            )

        self.assertEqual(report["decision"], "rl_repair_probe_gate_passed_for_limited_followup")
        self.assertEqual(report["blockers"], [])
        self.assertEqual(report["errors"], [])

    def test_anchor_alignment_blocker_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            training = root / "training.json"
            alignment = root / "alignment.json"
            regression = root / "regression.json"
            write_json(training, training_payload())
            write_json(alignment, alignment_payload(blockers=["overall mean_kl too high"]))
            write_json(regression, regression_payload())

            report = build_report(
                training_report=training,
                anchor_alignment=alignment,
                window_regressions=[regression],
            )

        self.assertEqual(report["decision"], "rl_repair_probe_gate_failed")
        self.assertTrue(any("mean_kl" in blocker for blocker in report["blockers"]))

    def test_window_regression_blocker_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            training = root / "training.json"
            regression = root / "regression.json"
            write_json(training, training_payload())
            write_json(regression, regression_payload(blockers=["300/soda: survival dropped"]))

            report = build_report(
                training_report=training,
                window_regressions=[regression],
            )

        self.assertEqual(report["decision"], "rl_repair_probe_gate_failed")
        self.assertTrue(any("survival dropped" in blocker for blocker in report["blockers"]))

    def test_required_multibaseline_regressions_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            training = root / "training.json"
            e30_regression = root / "e30_regression.json"
            parent_regression = root / "parent_regression.json"
            write_json(training, training_payload())
            write_json(e30_regression, regression_payload())
            write_json(parent_regression, regression_payload())

            report = build_report(
                training_report=training,
                window_regressions=[],
                required_window_regressions=[
                    ("e30", e30_regression),
                    ("parent", parent_regression),
                ],
            )

        self.assertEqual(report["decision"], "rl_repair_probe_gate_passed_for_limited_followup")
        self.assertEqual(report["window_regression_requirement"], "required_labeled_baselines")
        self.assertEqual(report["required_window_regression_labels"], ["e30", "parent"])
        self.assertTrue(all(item["required"] for item in report["window_regressions"]))

    def test_required_parent_regression_blocker_fails_with_label(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            training = root / "training.json"
            e30_regression = root / "e30_regression.json"
            parent_regression = root / "parent_regression.json"
            write_json(training, training_payload())
            write_json(e30_regression, regression_payload())
            write_json(parent_regression, regression_payload(blockers=["300/caramel: survival dropped"]))

            report = build_report(
                training_report=training,
                window_regressions=[],
                required_window_regressions=[
                    ("e30", e30_regression),
                    ("parent", parent_regression),
                ],
            )

        self.assertEqual(report["decision"], "rl_repair_probe_gate_failed")
        self.assertTrue(
            any("parent" in blocker and "survival dropped" in blocker for blocker in report["blockers"])
        )

    def test_duplicate_window_regression_labels_are_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            training = root / "training.json"
            first = root / "first.json"
            second = root / "second.json"
            write_json(training, training_payload())
            write_json(first, regression_payload())
            write_json(second, regression_payload())

            report = build_report(
                training_report=training,
                window_regressions=[("baseline", first)],
                required_window_regressions=[("baseline", second)],
            )

        self.assertEqual(report["decision"], "rl_repair_probe_gate_invalid")
        self.assertTrue(any("duplicate label" in error for error in report["errors"]))

    def test_forbidden_candidate_wording_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            training = root / "training.json"
            regression = root / "regression.json"
            write_json(training, training_payload("rl_test_bot_candidate"))
            write_json(regression, regression_payload())

            report = build_report(
                training_report=training,
                window_regressions=[regression],
            )

        self.assertEqual(report["decision"], "rl_repair_probe_gate_invalid")
        self.assertTrue(any("overclaims" in error for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()
