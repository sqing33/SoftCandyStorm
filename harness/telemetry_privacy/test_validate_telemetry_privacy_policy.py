#!/usr/bin/env python3
"""Regression tests for telemetry privacy policy validation.

Run with:
    python3 harness/telemetry_privacy/test_validate_telemetry_privacy_policy.py
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
VALIDATOR = SCRIPT_DIR / "validate_telemetry_privacy_policy.py"
TEMPLATE = SCRIPT_DIR / "telemetry_privacy_policy_template.json"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_telemetry_privacy_policy import build_report, load_json_object  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


class TelemetryPrivacyPolicyValidatorTests(unittest.TestCase):
    def test_template_policy_passes(self) -> None:
        report = build_report(TEMPLATE)

        self.assertEqual(report["decision"], "telemetry_privacy_policy_valid")
        self.assertEqual(report["errors"], [])

    def test_upload_requires_explicit_consent_and_endpoint(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            policy = load_json_object(TEMPLATE)
            policy["upload"]["enabled"] = True
            policy["upload"]["requires_explicit_consent"] = False
            policy["upload"]["endpoint"] = ""
            path = Path(temp_dir) / "policy.json"
            write_json(path, policy)
            report = build_report(path)

            self.assertEqual(report["decision"], "telemetry_privacy_policy_invalid")
            self.assertTrue(any("requires_explicit_consent" in error for error in report["errors"]))
            self.assertTrue(any("upload.endpoint" in error for error in report["errors"]))

    def test_allowed_event_fields_reject_personal_data(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            policy = load_json_object(TEMPLATE)
            policy["allowed_event_fields"].extend(["email", "file_path", "raw_replay_action_stream"])
            path = Path(temp_dir) / "policy.json"
            write_json(path, policy)
            report = build_report(path)

            self.assertEqual(report["decision"], "telemetry_privacy_policy_invalid")
            self.assertTrue(any("allowed_event_fields contains disallowed field `email`" in error for error in report["errors"]))
            self.assertTrue(any("overlap prohibited_fields" in error for error in report["errors"]))

    def test_missing_player_controls_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            policy = load_json_object(TEMPLATE)
            policy["player_controls"]["disable_upload"] = False
            del policy["player_controls"]["delete_local_data"]
            path = Path(temp_dir) / "policy.json"
            write_json(path, policy)
            report = build_report(path)

            self.assertEqual(report["decision"], "telemetry_privacy_policy_invalid")
            self.assertTrue(any("player_controls.disable_upload" in error for error in report["errors"]))
            self.assertTrue(any("player_controls.delete_local_data" in error for error in report["errors"]))

    def test_retention_range_is_checked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            policy = load_json_object(TEMPLATE)
            policy["storage"]["retention_days"] = 365
            path = Path(temp_dir) / "policy.json"
            write_json(path, policy)
            report = build_report(path)

            self.assertEqual(report["decision"], "telemetry_privacy_policy_invalid")
            self.assertTrue(any("retention_days" in error for error in report["errors"]))

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
            self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["decision"], "telemetry_privacy_policy_valid")
            self.assertIn("Telemetry Privacy Policy Validation", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
