#!/usr/bin/env python3
"""Regression tests for manual platform path review packet generation.

Run with:
    python3 harness/save_contract/test_create_manual_platform_path_review_packet.py
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
PACKET = SCRIPT_DIR / "create_manual_platform_path_review_packet.py"

sys.path.insert(0, str(SCRIPT_DIR))

from create_manual_platform_path_review_packet import build_packet  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def make_fixture(root: Path) -> Path:
    policy = root / "harness/save_contract/platform_save_path_policy_v0.json"
    save_v0 = root / "harness/save_contract/save_state_v0_template.json"
    save_v1 = root / "harness/save_contract/save_state_v1_template.json"
    review = root / "harness/save_contract/manual_platform_path_review_template.json"
    write_json(
        policy,
        {
            "policy_id": "platform-save-path-v0",
            "scope": "local-save-and-runtime-data",
            "status": "contract-only",
            "storage_roots": [
                {
                    "id": "save_files",
                    "purpose": "player_save_state",
                    "logical_path": "platform_user_data/game/saves",
                    "delete_supported": True,
                    "export_supported": True,
                    "cloud_sync_allowed": False,
                }
            ],
            "path_rules": {
                "local_only_by_default": True,
                "no_absolute_paths_in_save": True,
            },
            "prohibited_path_fragments": ["/Users/", "C:\\"],
            "release_requirements": ["platform_path_review"],
            "blockers": ["Runtime does not resolve platform-native save paths"],
            "next_actions": ["complete manual review"],
        },
    )
    write_json(save_v0, {"contract_id": "save-state-v0", "contract_version": 1, "schema_version": "v0"})
    write_json(save_v1, {"contract_id": "save-state-v1", "contract_version": 1, "schema_version": "v1"})
    write_json(
        review,
        {
            "review_version": 1,
            "review_id": "<manual-platform-path-review-id>",
            "path_policy_path": str(policy.relative_to(root)),
            "path_policy_validation_report": "harness/reports/path/summary.md",
            "save_contract_paths": [
                str(save_v0.relative_to(root)),
                str(save_v1.relative_to(root)),
            ],
            "save_contract_validation_reports": [
                "harness/reports/save-v0/summary.md",
                "harness/reports/save-v1/summary.md",
            ],
            "gate_decision": "needs_more_review",
            "summary": "TODO",
            "checks": [
                {
                    "id": "logical_roots",
                    "decision": "needs_more_review",
                    "notes": "TODO: confirm roots.",
                    "required_changes": ["TODO"],
                },
                {
                    "id": "runtime_evidence_limits",
                    "decision": "needs_more_review",
                    "notes": "TODO: confirm evidence limits.",
                    "required_changes": ["TODO"],
                },
            ],
        },
    )
    return review


class ManualPlatformPathReviewPacketTests(unittest.TestCase):
    def test_build_packet_summarizes_policy_contracts_and_checks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            review = make_fixture(root)

            packet = build_packet(review, root)

            self.assertEqual(packet["policy_id"], "platform-save-path-v0")
            self.assertEqual(packet["storage_root_count"], 1)
            self.assertEqual(packet["save_contract_count"], 2)
            self.assertEqual(packet["draft_todo_check_count"], 2)
            self.assertIn("/Users/", packet["prohibited_path_fragments"])

    def test_cli_writes_markdown_packet(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            review = make_fixture(root)
            out = root / "platform_path_packet.md"

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
            self.assertIn("Manual Platform Path Review Packet", text)
            self.assertIn("save_files", text)
            self.assertIn("draft_todo", text)
            self.assertIn("It does not provide legal advice", text)


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
