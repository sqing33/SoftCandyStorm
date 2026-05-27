#!/usr/bin/env python3
"""Regression tests for RL policy acceptance validation.

Run with:
    python3 tools/test_validate_rl_policy_acceptance.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
VALIDATOR = SCRIPT_DIR / "validate_rl_policy_acceptance.py"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_rl_policy_acceptance import build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str = "fixture\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def comparison_payload(*, seconds: float, min_win_rate: float = 1.0, best_rule_bot: float = 0.9) -> dict:
    maps = []
    for map_id in ("soda-creek", "caramel-workshop", "cracked-star-jar"):
        maps.append(
            {
                "map_id": map_id,
                "policy_win_rate": min_win_rate,
                "policy_average_survival_seconds": seconds,
                "policy_dominant_action": {"action": "3", "count": 120, "ratio": 0.24},
                "policy_normalized_action_entropy": 0.88,
                "rule_bot_win_rates": {"random": 0.0, "kite": best_rule_bot, "tank": 0.5},
                "best_rule_bot_win_rate": best_rule_bot,
                "inner_gate_decision": "comparison_recorded_not_balance_gate",
            }
        )
    return {
        "report_version": 1,
        "status": "compared",
        "phase": "rl_phase_1_movement_survival",
        "algorithm": "behavior_clone",
        "model_path": "python/train/models/fixture.pt",
        "map_preset": "high-pressure",
        "seconds": seconds,
        "maps": [{"map_id": item["map_id"]} for item in maps],
        "summary": {
            "maps": maps,
            "map_count": 3,
            "minimum_policy_win_rate": min_win_rate,
            "average_policy_win_rate": min_win_rate,
            "repair_maps": [],
        },
        "findings": [],
        "gate_decision": "multimap_comparison_recorded_not_balance_gate",
    }


def make_ready_manifest(root: Path) -> Path:
    write_text(root / "python" / "train" / "models" / "fixture.pt")
    write_json(root / "python" / "train" / "models" / "fixture_metadata.json", {"policy_id": "fixture"})
    write_json(
        root / "reports" / "training.json",
        {
            "status": "trained",
            "gate_decision": "training_recorded_requires_acceptance_gate",
            "model_path": "python/train/models/fixture.pt",
        },
    )
    write_json(root / "reports" / "short.json", comparison_payload(seconds=60.0, min_win_rate=1.0))
    write_json(root / "reports" / "long.json", comparison_payload(seconds=300.0, min_win_rate=1.0))
    write_json(root / "reports" / "local_binary.json", {"decision": "local_binary_launch_ok"})
    manifest = root / "python" / "train" / "rl_policy_acceptance_fixture.json"
    write_json(
        manifest,
        {
            "report_version": 1,
            "generated_at": "2026-05-26",
            "policy_id": "fixture_policy",
            "policy_type": "behavior_clone",
            "policy_phase": "rl_phase_1_movement_survival",
            "summary": "Fixture ready policy.",
            "model_path": "python/train/models/fixture.pt",
            "model_metadata_path": "python/train/models/fixture_metadata.json",
            "training_report_path": "reports/training.json",
            "short_eval_report_path": "reports/short.json",
            "long_eval_report_path": "reports/long.json",
            "rule_bot_comparison_report_path": "reports/long.json",
            "local_binary_diagnostic_report_path": "reports/local_binary.json",
            "failure_case_paths": [],
            "unresolved_failure_case_paths": [],
            "acceptance_criteria": {
                "required_map_preset": "high-pressure",
                "min_map_count": 3,
                "min_short_seconds": 60,
                "min_long_seconds": 300,
                "min_normalized_action_entropy": 0.5,
                "max_dominant_action_ratio": 0.7,
                "min_short_policy_win_rate": 1.0,
                "min_long_policy_win_rate": 1.0,
                "must_match_best_rule_bot": True,
            },
            "gate_decision": "rl_test_bot_candidate",
        },
    )
    return manifest


class RlPolicyAcceptanceValidatorTests(unittest.TestCase):
    def test_ready_fixture_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = make_ready_manifest(root)

            report = build_report(manifest, root)

            self.assertEqual(report["decision"], "rl_policy_acceptance_ready")
            self.assertEqual(report["errors"], [])
            self.assertEqual(report["blockers"], [])

    def test_repository_template_is_blocked_not_ready(self) -> None:
        manifest = REPO_ROOT / "python" / "train" / "rl_policy_acceptance_template.json"

        report = build_report(manifest, REPO_ROOT)

        self.assertEqual(report["decision"], "rl_policy_acceptance_not_ready")
        self.assertIn(report["gate_decision"], {"blocked_by_local_binary_launch", "repair"})
        self.assertTrue(report["blockers"])

    def test_local_binary_blocked_cannot_pass_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = make_ready_manifest(root)
            write_json(root / "reports" / "local_binary.json", {"decision": "local_binary_launch_blocked"})

            report = build_report(manifest, root)

            self.assertEqual(report["decision"], "rl_policy_acceptance_not_ready")
            self.assertTrue(any("local_binary_diagnostic" in error for error in report["errors"]))

    def test_missing_long_eval_prevents_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = make_ready_manifest(root)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["long_eval_report_path"] = None
            write_json(manifest, payload)

            report = build_report(manifest, root)

            self.assertEqual(report["decision"], "rl_policy_acceptance_not_ready")
            self.assertTrue(any("long_eval_report_path" in error for error in report["errors"]))

    def test_stochastic_eval_reports_cannot_pass_acceptance(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = make_ready_manifest(root)
            for name in ("short", "long"):
                report_path = root / "reports" / f"{name}.json"
                payload = json.loads(report_path.read_text(encoding="utf-8"))
                payload["action_selection"] = "stochastic"
                payload["action_random_seed"] = 62201
                write_json(report_path, payload)

            report = build_report(manifest, root)

            self.assertEqual(report["decision"], "rl_policy_acceptance_not_ready")
            self.assertTrue(any("watch evidence only" in error for error in report["errors"]))

    def test_unresolved_failure_case_prevents_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = make_ready_manifest(root)
            write_json(root / "harness" / "failed_cases" / "fail_001.json", {"case_id": "fail_001"})
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["failure_case_paths"] = ["harness/failed_cases/fail_001.json"]
            payload["unresolved_failure_case_paths"] = ["harness/failed_cases/fail_001.json"]
            write_json(manifest, payload)

            report = build_report(manifest, root)

            self.assertEqual(report["decision"], "rl_policy_acceptance_not_ready")
            self.assertTrue(any("unresolved_failure_case_paths" in error for error in report["errors"]))

    def test_forbidden_gate_decision_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = make_ready_manifest(root)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["gate_decision"] = "release_ready"
            write_json(manifest, payload)

            report = build_report(manifest, root)

            self.assertEqual(report["decision"], "rl_policy_acceptance_not_ready")
            self.assertTrue(any("forbidden" in error for error in report["errors"]))

    def test_cli_writes_not_ready_report_with_allow_flag(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = make_ready_manifest(root)
            write_json(root / "reports" / "local_binary.json", {"decision": "local_binary_launch_blocked"})
            report_path = root / "report.json"
            markdown_path = root / "summary.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(manifest),
                    "--repo-root",
                    str(root),
                    "--report",
                    str(report_path),
                    "--markdown",
                    str(markdown_path),
                    "--allow-not-ready",
                ],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                json.loads(report_path.read_text(encoding="utf-8"))["decision"],
                "rl_policy_acceptance_not_ready",
            )
            self.assertIn("RL Policy Acceptance Validation", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
