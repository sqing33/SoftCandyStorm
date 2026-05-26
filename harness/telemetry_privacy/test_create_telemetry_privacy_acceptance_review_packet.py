#!/usr/bin/env python3
"""Regression tests for telemetry/privacy acceptance packet generation.

Run with:
    python3 harness/telemetry_privacy/test_create_telemetry_privacy_acceptance_review_packet.py
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
PACKET = SCRIPT_DIR / "create_telemetry_privacy_acceptance_review_packet.py"

sys.path.insert(0, str(SCRIPT_DIR))

from create_telemetry_privacy_acceptance_review_packet import build_packet, default_evidence_paths  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


PRIVACY_CHECKS = [
    "default_off",
    "explicit_consent",
    "raw_replay_separate_consent",
    "prohibited_fields",
    "delete_export_controls",
    "privacy_notice_text",
    "retention_and_storage",
    "runtime_evidence_limits",
]
PLATFORM_CHECKS = [
    "logical_roots",
    "no_host_absolute_paths",
    "delete_scope",
    "export_scope",
    "migration_original_retention",
    "cloud_sync_policy",
    "runtime_evidence_limits",
]
LEGAL_CHECKS = [
    "privacy_notice_claims",
    "consent_and_default_off",
    "prohibited_data_fields",
    "raw_replay_and_crash_reports",
    "retention_delete_export",
    "platform_path_and_local_data_scope",
    "upload_transport_status",
    "jurisdiction_and_store_requirements",
    "release_evidence_limits",
]


def passed_review(check_ids: list[str]) -> dict:
    return {
        "review_version": 1,
        "review_id": "fixture-review",
        "reviewer": "human-reviewer-fixture",
        "reviewed_at": "2026-05-26",
        "gate_decision": "pass",
        "summary": "Fixture review with concrete human observations.",
        "checks": [
            {
                "id": check_id,
                "decision": "pass",
                "notes": f"{check_id} has been checked by a human fixture.",
                "required_changes": [],
            }
            for check_id in check_ids
        ],
    }


def make_ready_tree(root: Path) -> dict[str, str]:
    write_json(root / "harness/reports/policy/policy.json", {"decision": "telemetry_privacy_policy_valid"})
    write_json(root / "harness/reports/runtime/runtime.json", {"decision": "runtime_privacy_settings_contract_valid"})
    write_json(
        root / "harness/reports/upload/upload.json",
        {
            "decision": "upload_transport_contract_valid",
            "implementation_status": "implemented",
            "transport_mode": "local-test",
        },
    )
    write_json(root / "harness/reports/save-path/save_path.json", {"decision": "save_path_policy_valid"})
    write_json(root / "harness/telemetry_privacy/manual_privacy_review.json", passed_review(PRIVACY_CHECKS))
    write_text(root / "harness/reports/privacy-packet/summary.md", "# privacy packet\n")
    write_json(root / "harness/reports/privacy/manual_privacy_review.json", {"decision": "manual_privacy_review_valid"})
    write_json(root / "harness/save_contract/manual_platform_path_review.json", passed_review(PLATFORM_CHECKS))
    write_text(root / "harness/reports/platform-packet/summary.md", "# platform packet\n")
    write_json(root / "harness/reports/platform/manual_platform_path_review.json", {"decision": "manual_platform_path_review_valid"})
    write_json(root / "harness/telemetry_privacy/manual_legal_review.json", passed_review(LEGAL_CHECKS))
    write_text(root / "harness/reports/legal-packet/summary.md", "# legal packet\n")
    write_json(root / "harness/reports/legal/manual_legal_review.json", {"decision": "manual_legal_review_valid"})
    write_json(
        root / "harness/release/current_local_rc_evidence.json",
        {
            "gates": [
                {
                    "id": "telemetry_privacy",
                    "status": "pass",
                    "summary": "Fixture telemetry privacy gate passed.",
                    "evidence_paths": ["harness/reports/privacy/manual_privacy_review.json"],
                    "synthetic": False,
                }
            ]
        },
    )
    return {
        "policy_validation_report": "harness/reports/policy/policy.json",
        "runtime_contract_validation_report": "harness/reports/runtime/runtime.json",
        "upload_transport_validation_report": "harness/reports/upload/upload.json",
        "save_path_policy_report": "harness/reports/save-path/save_path.json",
        "manual_privacy_review_template": "harness/telemetry_privacy/manual_privacy_review.json",
        "manual_privacy_review_packet": "harness/reports/privacy-packet/summary.md",
        "manual_privacy_review_validation_report": "harness/reports/privacy/manual_privacy_review.json",
        "manual_platform_path_review_template": "harness/save_contract/manual_platform_path_review.json",
        "manual_platform_path_review_packet": "harness/reports/platform-packet/summary.md",
        "manual_platform_path_review_validation_report": "harness/reports/platform/manual_platform_path_review.json",
        "manual_legal_review_template": "harness/telemetry_privacy/manual_legal_review.json",
        "manual_legal_review_packet": "harness/reports/legal-packet/summary.md",
        "manual_legal_review_validation_report": "harness/reports/legal/manual_legal_review.json",
        "release_candidate_evidence": "harness/release/current_local_rc_evidence.json",
    }


class TelemetryPrivacyAcceptanceReviewPacketTests(unittest.TestCase):
    def test_current_local_packet_reports_missing_human_evidence(self) -> None:
        packet = build_packet(REPO_ROOT, default_evidence_paths())

        self.assertEqual(packet["decision"], "telemetry_privacy_acceptance_review_packet_needs_evidence")
        self.assertEqual(packet["manual_review_sources"]["privacy"]["status"], "draft_todo")
        self.assertEqual(packet["manual_review_sources"]["platform_path"]["status"], "draft_todo")
        self.assertEqual(packet["manual_review_sources"]["legal"]["status"], "draft_todo")
        self.assertEqual(packet["release_candidate_telemetry_privacy_gate"]["status"], "waiting")
        self.assertTrue(any("manual review source still contains TODO" in blocker for blocker in packet["blockers"]))
        self.assertTrue(any("implementation_status" in blocker for blocker in packet["blockers"]))

    def test_ready_tree_can_support_release_gate_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            evidence = make_ready_tree(root)

            packet = build_packet(root, evidence)

            self.assertEqual(packet["decision"], "telemetry_privacy_acceptance_review_packet_ready_for_release_gate")
            self.assertEqual(packet["blockers"], [])
            self.assertEqual(packet["errors"], [])

    def test_cli_writes_markdown_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            out_dir = Path(temp_dir)
            report = out_dir / "telemetry_privacy_acceptance_review_packet.json"
            markdown = out_dir / "summary.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(PACKET),
                    "--repo-root",
                    str(REPO_ROOT),
                    "--report",
                    str(report),
                    "--markdown",
                    str(markdown),
                ],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(payload["decision"], "telemetry_privacy_acceptance_review_packet_needs_evidence")
            text = markdown.read_text(encoding="utf-8")
            self.assertIn("Telemetry Privacy Acceptance Review Packet", text)
            self.assertIn("manual_privacy_review_validation_report", text)
            self.assertIn("RC telemetry_privacy gate", text)


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
