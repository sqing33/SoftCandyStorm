#!/usr/bin/env python3
"""Regression tests for save path policy validation.

Run with:
    python3 tools/test_validate_save_path_policy.py
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
VALIDATOR = SCRIPT_DIR / "validate_save_path_policy.py"
POLICY = REPO_ROOT / "harness" / "save_contract" / "platform_save_path_policy_v0.json"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_save_path_policy import build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_policy() -> dict:
    return json.loads(POLICY.read_text(encoding="utf-8"))


class SavePathPolicyValidatorTests(unittest.TestCase):
    def test_current_policy_passes(self) -> None:
        report = build_report(POLICY)

        self.assertEqual(report["decision"], "save_path_policy_valid")
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["storage_root_count"], 5)
        self.assertGreater(report["blocker_count"], 0)

    def test_absolute_path_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = copy.deepcopy(load_policy())
            payload["storage_roots"][0]["logical_path"] = "/Users/player/save"
            path = Path(temp_dir) / "policy.json"
            write_json(path, payload)

            report = build_report(path)

            self.assertEqual(report["decision"], "save_path_policy_invalid")
            self.assertTrue(any("logical relative path" in error for error in report["errors"]))

    def test_missing_required_root_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = copy.deepcopy(load_policy())
            payload["storage_roots"] = [
                root for root in payload["storage_roots"] if root["id"] != "local_replay"
            ]
            path = Path(temp_dir) / "policy.json"
            write_json(path, payload)

            report = build_report(path)

            self.assertEqual(report["decision"], "save_path_policy_invalid")
            self.assertTrue(any("local_replay" in error for error in report["errors"]))

    def test_cloud_sync_requires_review(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = copy.deepcopy(load_policy())
            payload["storage_roots"][0]["cloud_sync_allowed"] = True
            path = Path(temp_dir) / "policy.json"
            write_json(path, payload)

            report = build_report(path)

            self.assertEqual(report["decision"], "save_path_policy_invalid")
            self.assertTrue(any("cloud_sync_allowed" in error for error in report["errors"]))

    def test_path_rules_are_required(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = copy.deepcopy(load_policy())
            payload["path_rules"]["delete_scope_must_be_configured_roots"] = False
            path = Path(temp_dir) / "policy.json"
            write_json(path, payload)

            report = build_report(path)

            self.assertEqual(report["decision"], "save_path_policy_invalid")
            self.assertTrue(any("delete_scope_must_be_configured_roots" in error for error in report["errors"]))

    def test_cli_writes_report_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = Path(temp_dir) / "report.json"
            markdown_path = Path(temp_dir) / "summary.md"
            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(POLICY),
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
                "save_path_policy_valid",
            )
            self.assertIn("Save Path Policy Validation", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
