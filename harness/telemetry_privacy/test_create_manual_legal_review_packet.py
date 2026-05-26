#!/usr/bin/env python3
"""Regression tests for manual legal review packet generation.

Run with:
    python3 harness/telemetry_privacy/test_create_manual_legal_review_packet.py
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
PACKET = SCRIPT_DIR / "create_manual_legal_review_packet.py"

sys.path.insert(0, str(SCRIPT_DIR))

from create_manual_legal_review_packet import build_packet  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def make_fixture(root: Path) -> Path:
    policy = root / "harness/telemetry_privacy/policy.json"
    runtime = root / "harness/telemetry_privacy/runtime_contract.json"
    save = root / "harness/save_contract/save_state.json"
    upload = root / "harness/telemetry_privacy/upload_contract.json"
    manual_privacy_report = root / "harness/reports/privacy/manual_privacy_review.json"
    manual_platform_report = root / "harness/reports/platform/manual_platform_path_review.json"
    review = root / "harness/telemetry_privacy/manual_legal_review_template.json"

    write_json(
        policy,
        {
            "policy_id": "fixture-policy",
            "scope": "development-local",
            "upload": {
                "enabled": False,
                "default_enabled": False,
                "requires_explicit_consent": True,
            },
            "raw_replay_upload": {
                "default_enabled": False,
                "requires_explicit_consent": True,
            },
            "crash_reports": {
                "default_enabled": False,
                "requires_explicit_consent": True,
            },
            "allowed_event_fields": ["timestamp", "run_id"],
            "prohibited_fields": ["email", "ip_address", "absolute_path"],
            "storage": {"retention_days": 30},
        },
    )
    write_json(runtime, {"contract_id": "fixture-runtime-privacy"})
    write_json(save, {"contract_id": "save-state-v0"})
    write_json(
        upload,
        {
            "contract_id": "upload-transport-v0",
            "implementation_status": "planned",
            "transport_mode": "none",
            "release_requirements": ["manual_privacy_review", "manual_legal_review"],
        },
    )
    write_json(manual_privacy_report, {"decision": "manual_privacy_review_valid"})
    write_json(manual_platform_report, {"decision": "manual_platform_path_review_valid"})
    write_json(
        review,
        {
            "review_version": 1,
            "review_id": "<manual-legal-review-id>",
            "policy_path": str(policy.relative_to(root)),
            "runtime_privacy_contract_path": str(runtime.relative_to(root)),
            "save_contract_path": str(save.relative_to(root)),
            "upload_transport_contract_path": str(upload.relative_to(root)),
            "policy_validation_report": "harness/reports/policy/summary.md",
            "runtime_contract_validation_report": "harness/reports/runtime/summary.md",
            "upload_transport_validation_report": "harness/reports/upload/summary.md",
            "manual_privacy_review_report": str(manual_privacy_report.relative_to(root)),
            "manual_platform_path_review_report": str(manual_platform_report.relative_to(root)),
            "reviewer": "<human legal reviewer>",
            "reviewer_role": "<legal_or_compliance>",
            "reviewed_at": "YYYY-MM-DD",
            "jurisdiction_scope": ["TODO: prototype_local"],
            "gate_decision": "needs_more_review",
            "summary": "TODO",
            "checks": [
                {
                    "id": "privacy_notice_claims",
                    "decision": "needs_more_review",
                    "notes": "TODO: confirm notice claims.",
                    "required_changes": ["TODO"],
                },
                {
                    "id": "upload_transport_status",
                    "decision": "needs_more_review",
                    "notes": "TODO: confirm transport status.",
                    "required_changes": ["TODO"],
                },
            ],
        },
    )
    return review


class ManualLegalReviewPacketTests(unittest.TestCase):
    def test_build_packet_summarizes_evidence_and_checks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            review = make_fixture(root)

            packet = build_packet(review, root)

            self.assertEqual(packet["policy_id"], "fixture-policy")
            self.assertEqual(packet["upload_implementation_status"], "planned")
            self.assertEqual(packet["check_count"], 2)
            self.assertEqual(packet["draft_todo_check_count"], 2)
            self.assertEqual(packet["report_refs"]["manual_privacy_review_report"]["decision"], "manual_privacy_review_valid")
            self.assertEqual(packet["report_refs"]["manual_platform_path_review_report"]["decision"], "manual_platform_path_review_valid")

    def test_cli_writes_markdown_packet(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            review = make_fixture(root)
            out = root / "legal_packet.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(PACKET),
                    "--review-template",
                    str(review),
                    "--repo-root",
                    str(root),
                    "--out",
                    str(out),
                ],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            text = out.read_text(encoding="utf-8")
            self.assertIn("Manual Legal Review Packet", text)
            self.assertIn("privacy_notice_claims", text)
            self.assertIn("draft_todo", text)
            self.assertIn("It does not provide legal advice", text)


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
