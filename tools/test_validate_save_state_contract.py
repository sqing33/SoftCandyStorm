#!/usr/bin/env python3
"""Regression tests for save-state contract validation.

Run with:
    python3 tools/test_validate_save_state_contract.py
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
VALIDATOR = SCRIPT_DIR / "validate_save_state_contract.py"
TEMPLATE = REPO_ROOT / "harness" / "save_contract" / "save_state_v0_template.json"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_save_state_contract import build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_template() -> dict:
    return json.loads(TEMPLATE.read_text(encoding="utf-8"))


class SaveStateContractValidatorTests(unittest.TestCase):
    def test_template_passes(self) -> None:
        report = build_report(TEMPLATE)

        self.assertEqual(report["decision"], "save_state_contract_valid")
        self.assertEqual(report["errors"], [])

    def test_upload_defaults_fail_when_enabled(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = load_template()
            payload["settings"]["telemetry_upload_enabled"] = True
            path = Path(temp_dir) / "save.json"
            write_json(path, payload)

            report = build_report(path)

            self.assertEqual(report["decision"], "save_state_contract_invalid")
            self.assertTrue(any("telemetry_upload_enabled" in error for error in report["errors"]))

    def test_missing_delete_control_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = load_template()
            payload["data_controls"]["delete_save_available"] = False
            path = Path(temp_dir) / "save.json"
            write_json(path, payload)

            report = build_report(path)

            self.assertEqual(report["decision"], "save_state_contract_invalid")
            self.assertTrue(any("delete_save_available" in error for error in report["errors"]))

    def test_negative_codex_count_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = load_template()
            payload["meta_progress"]["codex"]["characters"]["jar-keeper"]["seen_count"] = -1
            path = Path(temp_dir) / "save.json"
            write_json(path, payload)

            report = build_report(path)

            self.assertEqual(report["decision"], "save_state_contract_invalid")
            self.assertTrue(any("seen_count" in error for error in report["errors"]))

    def test_forbidden_key_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = copy.deepcopy(load_template())
            payload["profile"] = {"email": "player@example.test"}
            path = Path(temp_dir) / "save.json"
            write_json(path, payload)

            report = build_report(path)

            self.assertEqual(report["decision"], "save_state_contract_invalid")
            self.assertTrue(any("forbidden" in error for error in report["errors"]))

    def test_cli_writes_report_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = Path(temp_dir) / "report.json"
            markdown_path = Path(temp_dir) / "summary.md"
            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(TEMPLATE),
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
            self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["decision"], "save_state_contract_valid")
            self.assertIn("Save State Contract Validation", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
