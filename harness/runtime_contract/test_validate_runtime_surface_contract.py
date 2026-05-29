#!/usr/bin/env python3
"""Regression tests for Runtime surface contract validation.

Run with:
    python3 harness/runtime_contract/test_validate_runtime_surface_contract.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
VALIDATOR = SCRIPT_DIR / "validate_runtime_surface_contract.py"
CONTRACT = SCRIPT_DIR / "runtime_surface_contract_v0.json"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_runtime_surface_contract import build_report, load_json_object  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


class RuntimeSurfaceContractValidatorTests(unittest.TestCase):
    def test_template_contract_passes(self) -> None:
        report = build_report(CONTRACT, REPO_ROOT)

        self.assertEqual(report["decision"], "runtime_surface_contract_valid")
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["key_binding_count"], 25)

    def test_missing_cli_flag_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contract = load_json_object(CONTRACT)
            contract["required_cli_flags"].append("--missing-runtime-flag")
            path = Path(temp_dir) / "contract.json"
            write_json(path, contract)

            report = build_report(path, REPO_ROOT)

            self.assertEqual(report["decision"], "runtime_surface_contract_invalid")
            self.assertTrue(any("--missing-runtime-flag" in error for error in report["errors"]))

    def test_missing_struct_field_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contract = load_json_object(CONTRACT)
            contract["required_structs"][0]["required_fields"].append("missing_runtime_field")
            path = Path(temp_dir) / "contract.json"
            write_json(path, contract)

            report = build_report(path, REPO_ROOT)

            self.assertEqual(report["decision"], "runtime_surface_contract_invalid")
            self.assertTrue(any("missing_runtime_field" in error for error in report["errors"]))

    def test_missing_panel_fragment_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contract = load_json_object(CONTRACT)
            contract["required_source_fragments"].append("不存在的设置页面文案")
            path = Path(temp_dir) / "contract.json"
            write_json(path, contract)

            report = build_report(path, REPO_ROOT)

            self.assertEqual(report["decision"], "runtime_surface_contract_invalid")
            self.assertTrue(any("不存在的设置页面文案" in error for error in report["errors"]))

    def test_privacy_defaults_must_remain_false(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contract = load_json_object(CONTRACT)
            contract["default_privacy_settings"]["telemetry_upload_enabled"] = True
            path = Path(temp_dir) / "contract.json"
            write_json(path, contract)

            report = build_report(path, REPO_ROOT)

            self.assertEqual(report["decision"], "runtime_surface_contract_invalid")
            self.assertTrue(any("default_privacy_settings.telemetry_upload_enabled" in error for error in report["errors"]))

    def test_cli_writes_report_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = Path(temp_dir) / "runtime_surface_contract.json"
            markdown_path = Path(temp_dir) / "summary.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(CONTRACT),
                    "--repo-root",
                    str(REPO_ROOT),
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
                "runtime_surface_contract_valid",
            )
            self.assertIn("Runtime Surface Contract Validation", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
