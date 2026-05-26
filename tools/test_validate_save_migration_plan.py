#!/usr/bin/env python3
"""Regression tests for save migration plan validation.

Run with:
    python3 tools/test_validate_save_migration_plan.py
"""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
VALIDATOR = SCRIPT_DIR / "validate_save_migration_plan.py"
PLAN = REPO_ROOT / "harness" / "save_contract" / "save_migration_plan_v0_to_v1.json"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_save_migration_plan import build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_plan() -> dict:
    return json.loads(PLAN.read_text(encoding="utf-8"))


class SaveMigrationPlanValidatorTests(unittest.TestCase):
    def test_current_plan_is_valid_planned_migration(self) -> None:
        report = build_report(PLAN, REPO_ROOT)

        self.assertEqual(report["decision"], "save_migration_plan_planned")
        self.assertEqual(report["errors"], [])
        self.assertGreater(report["blocker_count"], 0)

    def test_missing_privacy_invariant_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = copy.deepcopy(load_plan())
            payload["privacy_invariants"]["telemetry_upload_enabled"] = True
            path = Path(temp_dir) / "plan.json"
            write_json(path, payload)

            report = build_report(path, REPO_ROOT)

            self.assertEqual(report["decision"], "save_migration_plan_invalid")
            self.assertTrue(any("telemetry_upload_enabled" in error for error in report["errors"]))

    def test_missing_meta_progress_preserve_mapping_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = copy.deepcopy(load_plan())
            payload["field_mappings"] = [
                item for item in payload["field_mappings"] if item["source"] != "meta_progress"
            ]
            path = Path(temp_dir) / "plan.json"
            write_json(path, payload)

            report = build_report(path, REPO_ROOT)

            self.assertEqual(report["decision"], "save_migration_plan_invalid")
            self.assertTrue(any("preserve meta_progress" in error for error in report["errors"]))

    def test_missing_failure_policy_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = copy.deepcopy(load_plan())
            payload["failure_policy"]["on_partial_write"] = "best_effort"
            path = Path(temp_dir) / "plan.json"
            write_json(path, payload)

            report = build_report(path, REPO_ROOT)

            self.assertEqual(report["decision"], "save_migration_plan_invalid")
            self.assertTrue(any("on_partial_write" in error for error in report["errors"]))

    def test_same_target_contract_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = copy.deepcopy(load_plan())
            payload["target_contract_id"] = "save-state-v0"
            path = Path(temp_dir) / "plan.json"
            write_json(path, payload)

            report = build_report(path, REPO_ROOT)

            self.assertEqual(report["decision"], "save_migration_plan_invalid")
            self.assertTrue(any("target_contract_id must differ" in error for error in report["errors"]))

    def test_invalid_source_schema_version_fails_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = copy.deepcopy(load_plan())
            payload["source_schema_version"] = "1"
            path = Path(temp_dir) / "plan.json"
            write_json(path, payload)

            report = build_report(path, REPO_ROOT)

            self.assertEqual(report["decision"], "save_migration_plan_invalid")
            self.assertTrue(any("source_schema_version must be 1" in error for error in report["errors"]))

    def test_target_template_must_match_target_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = copy.deepcopy(load_plan())
            payload["target_contract_id"] = "save-state-v2"
            path = Path(temp_dir) / "plan.json"
            write_json(path, payload)

            report = build_report(path, REPO_ROOT)

            self.assertEqual(report["decision"], "save_migration_plan_invalid")
            self.assertTrue(any("target_template contract_id" in error for error in report["errors"]))

    def test_target_template_must_exist(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = copy.deepcopy(load_plan())
            payload["target_template"] = "harness/save_contract/missing_save_state_v1_template.json"
            path = Path(temp_dir) / "plan.json"
            write_json(path, payload)

            report = build_report(path, REPO_ROOT)

            self.assertEqual(report["decision"], "save_migration_plan_invalid")
            self.assertTrue(any("target_template does not exist" in error for error in report["errors"]))

    def test_cli_allow_planned_writes_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = Path(temp_dir) / "report.json"
            markdown_path = Path(temp_dir) / "summary.md"
            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(PLAN),
                    "--repo-root",
                    str(REPO_ROOT),
                    "--report",
                    str(report_path),
                    "--markdown",
                    str(markdown_path),
                    "--allow-planned",
                ],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                json.loads(report_path.read_text(encoding="utf-8"))["decision"],
                "save_migration_plan_planned",
            )
            self.assertIn("Save Migration Plan Validation", markdown_path.read_text(encoding="utf-8"))

    def test_cli_without_allow_planned_fails(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), str(PLAN), "--repo-root", str(REPO_ROOT)],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
