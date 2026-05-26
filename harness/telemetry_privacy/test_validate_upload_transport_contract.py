#!/usr/bin/env python3
"""Regression tests for telemetry upload transport contract validation.

Run with:
    python3 harness/telemetry_privacy/test_validate_upload_transport_contract.py
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
VALIDATOR = SCRIPT_DIR / "validate_upload_transport_contract.py"
CONTRACT = SCRIPT_DIR / "upload_transport_contract_v0.json"
POLICY = SCRIPT_DIR / "telemetry_privacy_policy_template.json"
RUNTIME_CONTRACT = SCRIPT_DIR / "runtime_privacy_settings_contract_v0.json"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_upload_transport_contract import build_report, load_json_object  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


class UploadTransportContractValidatorTests(unittest.TestCase):
    def test_template_contract_passes_with_policy_and_runtime_contract(self) -> None:
        report = build_report(CONTRACT, POLICY, RUNTIME_CONTRACT)

        self.assertEqual(report["decision"], "upload_transport_contract_valid")
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["implementation_status"], "planned")
        self.assertEqual(report["bound_policy_decision"], "telemetry_privacy_policy_valid")
        self.assertEqual(report["bound_runtime_contract_decision"], "runtime_privacy_settings_contract_valid")

    def test_upload_enabled_requires_safe_endpoint_and_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contract = load_json_object(CONTRACT)
            contract["transport"]["upload_enabled"] = True
            contract["transport"]["default_enabled"] = True
            contract["transport"]["endpoint"] = "http://example.invalid/telemetry"
            path = Path(temp_dir) / "contract.json"
            write_json(path, contract)

            report = build_report(path, POLICY, RUNTIME_CONTRACT)

            self.assertEqual(report["decision"], "upload_transport_contract_invalid")
            self.assertTrue(any("transport.upload_enabled" in error for error in report["errors"]))
            self.assertTrue(any("transport.default_enabled" in error for error in report["errors"]))
            self.assertTrue(any("transport.endpoint must be https" in error for error in report["errors"]))

    def test_payload_fields_must_stay_inside_policy(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contract = load_json_object(CONTRACT)
            contract["payload"]["event_fields"].extend(["email", "raw_replay_action_stream", "custom_metric"])
            path = Path(temp_dir) / "contract.json"
            write_json(path, contract)

            report = build_report(path, POLICY, RUNTIME_CONTRACT)

            self.assertEqual(report["decision"], "upload_transport_contract_invalid")
            self.assertTrue(any("disallowed field `email`" in error for error in report["errors"]))
            self.assertTrue(any("outside telemetry policy" in error for error in report["errors"]))
            self.assertTrue(any("overlap prohibited_fields" in error for error in report["errors"]))

    def test_raw_replay_and_crash_payloads_stay_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contract = load_json_object(CONTRACT)
            contract["raw_replay"]["payload_allowed"] = True
            contract["raw_replay"]["separate_consent_required"] = False
            contract["crash_reports"]["includes_file_paths"] = True
            path = Path(temp_dir) / "contract.json"
            write_json(path, contract)

            report = build_report(path, POLICY, RUNTIME_CONTRACT)

            self.assertEqual(report["decision"], "upload_transport_contract_invalid")
            self.assertTrue(any("raw_replay.payload_allowed" in error for error in report["errors"]))
            self.assertTrue(any("raw_replay.separate_consent_required" in error for error in report["errors"]))
            self.assertTrue(any("crash_reports.includes_file_paths" in error for error in report["errors"]))

    def test_queue_retention_cannot_exceed_policy(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contract = load_json_object(CONTRACT)
            contract["queue"]["retention_days"] = 90
            path = Path(temp_dir) / "contract.json"
            write_json(path, contract)

            report = build_report(path, POLICY, RUNTIME_CONTRACT)

            self.assertEqual(report["decision"], "upload_transport_contract_invalid")
            self.assertTrue(any("queue.retention_days" in error for error in report["errors"]))

    def test_release_requirements_and_limitations_are_required(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contract = load_json_object(CONTRACT)
            contract["release_requirements"] = ["telemetry_privacy_policy"]
            contract["limitations"] = ["does_not_prove_runtime_upload_transport"]
            path = Path(temp_dir) / "contract.json"
            write_json(path, contract)

            report = build_report(path, POLICY, RUNTIME_CONTRACT)

            self.assertEqual(report["decision"], "upload_transport_contract_invalid")
            self.assertTrue(any("release_requirements missing" in error for error in report["errors"]))
            self.assertTrue(any("limitations missing" in error for error in report["errors"]))

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
                    "--runtime-contract",
                    str(RUNTIME_CONTRACT),
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
                "upload_transport_contract_valid",
            )
            self.assertIn("Upload Transport Contract Validation", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
