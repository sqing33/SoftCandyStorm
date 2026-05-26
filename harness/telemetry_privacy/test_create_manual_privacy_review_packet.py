#!/usr/bin/env python3
"""Regression tests for manual privacy review packet generation.

Run with:
    python3 harness/telemetry_privacy/test_create_manual_privacy_review_packet.py
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
PACKET = SCRIPT_DIR / "create_manual_privacy_review_packet.py"

sys.path.insert(0, str(SCRIPT_DIR))

from create_manual_privacy_review_packet import build_packet  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def make_fixture(root: Path) -> Path:
    policy = root / "harness/telemetry_privacy/policy.json"
    runtime = root / "harness/telemetry_privacy/runtime_contract.json"
    save = root / "harness/save_contract/save_state.json"
    review = root / "harness/telemetry_privacy/manual_privacy_review_template.json"
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
            "allowed_event_fields": ["timestamp", "run_id"],
            "prohibited_fields": ["email", "ip_address"],
            "storage": {"retention_days": 30},
        },
    )
    write_json(
        runtime,
        {
            "contract_id": "fixture-runtime-privacy",
            "ui_controls": [
                {
                    "id": "telemetry_upload_toggle",
                    "setting": "telemetry_upload_enabled",
                    "default_enabled": False,
                    "requires_explicit_consent": True,
                }
            ],
            "data_action_controls": [
                {
                    "id": "delete_local_telemetry",
                    "action": "delete_local_data",
                    "visible": True,
                }
            ],
            "privacy_notice": {
                "short_text": "默认只保存在本机。",
                "required_topics": ["default_off", "delete_export"],
            },
        },
    )
    write_json(save, {"contract_id": "save-state-v0"})
    write_json(
        review,
        {
            "review_version": 1,
            "review_id": "<manual-privacy-review-id>",
            "policy_path": str(policy.relative_to(root)),
            "runtime_privacy_contract_path": str(runtime.relative_to(root)),
            "save_contract_path": str(save.relative_to(root)),
            "policy_validation_report": "harness/reports/policy/summary.md",
            "runtime_contract_validation_report": "harness/reports/runtime/summary.md",
            "gate_decision": "needs_more_review",
            "summary": "TODO",
            "checks": [
                {
                    "id": "default_off",
                    "decision": "needs_more_review",
                    "notes": "TODO: confirm default off.",
                    "required_changes": ["TODO"],
                },
                {
                    "id": "explicit_consent",
                    "decision": "needs_more_review",
                    "notes": "TODO: confirm consent.",
                    "required_changes": ["TODO"],
                },
            ],
        },
    )
    return review


class ManualPrivacyReviewPacketTests(unittest.TestCase):
    def test_build_packet_summarizes_policy_contract_and_checks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            review = make_fixture(root)

            packet = build_packet(review, root)

            self.assertEqual(packet["policy_id"], "fixture-policy")
            self.assertEqual(packet["upload_default_enabled"], False)
            self.assertEqual(packet["check_count"], 2)
            self.assertEqual(packet["draft_todo_check_count"], 2)
            self.assertIn("email", packet["prohibited_fields"])

    def test_cli_writes_markdown_packet(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            review = make_fixture(root)
            out = root / "privacy_packet.md"

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
            self.assertIn("Manual Privacy Review Packet", text)
            self.assertIn("default_off", text)
            self.assertIn("draft_todo", text)
            self.assertIn("It does not provide legal advice", text)


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
