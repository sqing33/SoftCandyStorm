#!/usr/bin/env python3
"""Regression tests for final asset acceptance review packet generation.

Run with:
    python3 harness/asset_review/test_create_asset_acceptance_review_packet.py
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
PACKET = SCRIPT_DIR / "create_asset_acceptance_review_packet.py"
TEMPLATE = SCRIPT_DIR / "asset_acceptance_manifest_template.json"

sys.path.insert(0, str(SCRIPT_DIR))

from create_asset_acceptance_review_packet import build_packet  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def make_ready_manifest(root: Path) -> Path:
    write_json(
        root / "harness/asset_review/runtime_candidates/batch/runtime_candidate_manifest.json",
        {"decision": "asset_runtime_candidate_manifest_valid"},
    )
    write_json(
        root / "harness/asset_review/runtime_preview_reviews/batch-preview.json",
        {"review_type": "asset_runtime_preview_review", "decision": "runtime_preview_pass"},
    )
    write_json(
        root / "harness/asset_review/audio_loudness_reviews/batch-loudness.json",
        {"review_type": "asset_audio_loudness_review", "decision": "audio_loudness_pass"},
    )
    write_json(
        root / "harness/asset_review/final_acceptance/batch-final.json",
        {"review_type": "asset_final_acceptance", "decision": "accepted_content"},
    )
    manifest = root / "harness/asset_review/accepted/batch/acceptance_manifest.json"
    write_json(
        manifest,
        {
            "manifest_version": 1,
            "manifest_contract_id": "asset-acceptance-manifest-v0",
            "stage": "asset_acceptance",
            "candidate_batch_id": "batch",
            "accepted_at": "2026-05-26T00:00:00Z",
            "source_runtime_candidate_manifest": "harness/asset_review/runtime_candidates/batch/runtime_candidate_manifest.json",
            "runtime_preview_review_file": "harness/asset_review/runtime_preview_reviews/batch-preview.json",
            "audio_loudness_review_file": "harness/asset_review/audio_loudness_reviews/batch-loudness.json",
            "final_human_acceptance_file": "harness/asset_review/final_acceptance/batch-final.json",
            "asset_count": 1,
            "accepted_assets": [
                {
                    "id": "player_sprite",
                    "type": "image",
                    "accepted_use": "runtime_asset",
                    "source_path": "images/player.png",
                }
            ],
            "rules": {
                "accepted_content": True,
                "runtime_integrated": False,
                "release_ready": False,
                "requires_runtime_candidate_manifest": True,
                "requires_runtime_preview": True,
                "requires_audio_loudness_review": True,
                "requires_final_human_acceptance": True,
                "generated_candidate_direct_acceptance_allowed": False,
            },
        },
    )
    return manifest


class AssetAcceptanceReviewPacketTests(unittest.TestCase):
    def test_template_packet_reports_missing_human_evidence(self) -> None:
        packet = build_packet(TEMPLATE, REPO_ROOT)

        self.assertEqual(packet["decision"], "asset_acceptance_review_packet_needs_evidence")
        self.assertEqual(packet["placeholder_evidence_count"], 4)
        self.assertEqual(packet["existing_evidence_count"], 0)
        self.assertTrue(any(item["field"] == "runtime_preview_review_file" for item in packet["evidence"]))
        self.assertTrue(any(asset["status"] == "placeholder" for asset in packet["accepted_assets"]))

    def test_ready_manifest_packet_can_move_to_validator(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = make_ready_manifest(root)

            packet = build_packet(manifest, root)

            self.assertEqual(packet["decision"], "asset_acceptance_review_packet_ready_for_validation")
            self.assertEqual(packet["existing_evidence_count"], 4)
            self.assertEqual(packet["placeholder_asset_count"], 0)

    def test_cli_writes_markdown_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            out_dir = Path(temp_dir)
            report = out_dir / "packet.json"
            markdown = out_dir / "packet.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(PACKET),
                    str(TEMPLATE),
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
            self.assertEqual(payload["decision"], "asset_acceptance_review_packet_needs_evidence")
            text = markdown.read_text(encoding="utf-8")
            self.assertIn("Asset Acceptance Review Packet", text)
            self.assertIn("runtime_preview_review_file", text)
            self.assertIn("audio_loudness_review_file", text)


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
