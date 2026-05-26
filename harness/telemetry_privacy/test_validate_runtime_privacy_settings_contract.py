#!/usr/bin/env python3
"""Regression tests for Runtime privacy settings contract validation.

Run with:
    python3 harness/telemetry_privacy/test_validate_runtime_privacy_settings_contract.py
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
VALIDATOR = SCRIPT_DIR / "validate_runtime_privacy_settings_contract.py"
CONTRACT = SCRIPT_DIR / "runtime_privacy_settings_contract_v0.json"
POLICY = SCRIPT_DIR / "telemetry_privacy_policy_template.json"
SAVE_CONTRACT = REPO_ROOT / "harness" / "save_contract" / "save_state_v0_template.json"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_runtime_privacy_settings_contract import build_report, load_json_object  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


class RuntimePrivacySettingsContractValidatorTests(unittest.TestCase):
    def test_template_contract_passes_with_policy_and_save_contract(self) -> None:
        report = build_report(CONTRACT, POLICY, SAVE_CONTRACT)

        self.assertEqual(report["decision"], "runtime_privacy_settings_contract_valid")
        self.assertEqual(report["errors"], [])

    def test_missing_required_toggle_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contract = load_json_object(CONTRACT)
            contract["ui_controls"] = [
                control
                for control in contract["ui_controls"]
                if control["setting"] != "raw_replay_upload_enabled"
            ]
            path = Path(temp_dir) / "contract.json"
            write_json(path, contract)

            report = build_report(path, POLICY, SAVE_CONTRACT)

            self.assertEqual(report["decision"], "runtime_privacy_settings_contract_invalid")
            self.assertTrue(any("raw_replay_upload_enabled" in error for error in report["errors"]))

    def test_toggle_defaults_and_consent_are_checked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contract = load_json_object(CONTRACT)
            contract["ui_controls"][0]["default_enabled"] = True
            contract["ui_controls"][0]["requires_explicit_consent"] = False
            contract["settings_bindings"]["telemetry_upload_enabled"] = True
            path = Path(temp_dir) / "contract.json"
            write_json(path, contract)

            report = build_report(path, POLICY, SAVE_CONTRACT)

            self.assertEqual(report["decision"], "runtime_privacy_settings_contract_invalid")
            self.assertTrue(any("default_enabled" in error for error in report["errors"]))
            self.assertTrue(any("requires_explicit_consent" in error for error in report["errors"]))
            self.assertTrue(any("settings_bindings.telemetry_upload_enabled" in error for error in report["errors"]))

    def test_raw_replay_requires_separate_notice_topic(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contract = load_json_object(CONTRACT)
            for control in contract["ui_controls"]:
                if control["setting"] == "raw_replay_upload_enabled":
                    control["notice_topics"] = ["default_off"]
            path = Path(temp_dir) / "contract.json"
            write_json(path, contract)

            report = build_report(path, POLICY, SAVE_CONTRACT)

            self.assertEqual(report["decision"], "runtime_privacy_settings_contract_invalid")
            self.assertTrue(any("raw_replay_separate_consent" in error for error in report["errors"]))

    def test_data_actions_require_delete_export_and_notice(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contract = load_json_object(CONTRACT)
            contract["data_action_controls"] = [
                {
                    "id": "delete_local_telemetry",
                    "label": "删除本地遥测与 Replay 数据",
                    "action": "delete_local_data",
                    "visible": True,
                    "confirmation_required": False,
                    "destructive": False,
                }
            ]
            path = Path(temp_dir) / "contract.json"
            write_json(path, contract)

            report = build_report(path, POLICY, SAVE_CONTRACT)

            self.assertEqual(report["decision"], "runtime_privacy_settings_contract_invalid")
            self.assertTrue(any("confirmation_required" in error for error in report["errors"]))
            self.assertTrue(any("export_local_data" in error for error in report["errors"]))
            self.assertTrue(any("open_privacy_notice" in error for error in report["errors"]))

    def test_notice_topics_and_disallowed_claims_are_checked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contract = load_json_object(CONTRACT)
            contract["privacy_notice"]["short_text"] = "遥测 always on，无法关闭。"
            contract["privacy_notice"]["required_topics"] = ["purposes"]
            del contract["privacy_notice"]["purpose_labels"]["balance"]
            path = Path(temp_dir) / "contract.json"
            write_json(path, contract)

            report = build_report(path, POLICY, SAVE_CONTRACT)

            self.assertEqual(report["decision"], "runtime_privacy_settings_contract_invalid")
            self.assertTrue(any("disallowed claim" in error for error in report["errors"]))
            self.assertTrue(any("required_topics missing" in error for error in report["errors"]))
            self.assertTrue(any("purpose_labels missing" in error for error in report["errors"]))

    def test_save_contract_binding_is_checked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            save_contract = load_json_object(SAVE_CONTRACT)
            save_contract["settings"]["raw_replay_upload_enabled"] = True
            path = Path(temp_dir) / "save_contract.json"
            write_json(path, save_contract)

            report = build_report(CONTRACT, POLICY, path)

            self.assertEqual(report["decision"], "runtime_privacy_settings_contract_invalid")
            self.assertTrue(any("save contract settings.raw_replay_upload_enabled" in error for error in report["errors"]))

    def test_cli_writes_report_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = Path(temp_dir) / "report.json"
            markdown_path = Path(temp_dir) / "summary.md"
            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(CONTRACT),
                    "--policy",
                    str(POLICY),
                    "--save-contract",
                    str(SAVE_CONTRACT),
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
                "runtime_privacy_settings_contract_valid",
            )
            self.assertIn("Runtime Privacy Settings Contract Validation", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
