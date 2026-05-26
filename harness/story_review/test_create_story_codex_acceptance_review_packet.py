#!/usr/bin/env python3
"""Regression tests for final story/codex acceptance review packet generation.

Run with:
    python3 harness/story_review/test_create_story_codex_acceptance_review_packet.py
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
PACKET = SCRIPT_DIR / "create_story_codex_acceptance_review_packet.py"
TEMPLATE = SCRIPT_DIR / "story_codex_acceptance_manifest_template.json"

sys.path.insert(0, str(SCRIPT_DIR))

from create_story_codex_acceptance_review_packet import build_packet  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def make_ready_manifest(root: Path) -> Path:
    write_json(
        root / "harness/story_review/ui_candidates/story-pack/ui_candidate_manifest.json",
        {"decision": "story_codex_ui_candidate_manifest_valid"},
    )
    write_json(
        root / "harness/story_review/runtime_ui_reviews/story-pack-runtime-ui.json",
        {"review_type": "story_codex_runtime_ui_review", "decision": "runtime_ui_review_pass"},
    )
    write_json(
        root / "harness/story_review/final_acceptance/story-pack-final.json",
        {"review_type": "story_codex_final_acceptance", "decision": "accepted_content"},
    )
    manifest = root / "harness/story_review/accepted/story-pack/acceptance_manifest.json"
    write_json(
        manifest,
        {
            "manifest_version": 1,
            "manifest_contract_id": "story-codex-acceptance-manifest-v0",
            "stage": "story_codex_acceptance",
            "candidate_pack_id": "story-pack",
            "accepted_at": "2026-05-26T00:00:00Z",
            "source_ui_candidate_manifest": "harness/story_review/ui_candidates/story-pack/ui_candidate_manifest.json",
            "runtime_ui_review_file": "harness/story_review/runtime_ui_reviews/story-pack-runtime-ui.json",
            "final_human_acceptance_file": "harness/story_review/final_acceptance/story-pack-final.json",
            "chapter_count": 6,
            "codex_entry_count": 26,
            "rules": {
                "accepted_content": True,
                "runtime_integrated": False,
                "release_ready": False,
                "requires_ui_candidate_manifest": True,
                "requires_runtime_ui_review": True,
                "requires_final_human_acceptance": True,
                "generated_candidate_direct_acceptance_allowed": False,
            },
        },
    )
    return manifest


class StoryCodexAcceptanceReviewPacketTests(unittest.TestCase):
    def test_template_packet_reports_missing_human_evidence(self) -> None:
        packet = build_packet(TEMPLATE, REPO_ROOT)

        self.assertEqual(packet["decision"], "story_codex_acceptance_review_packet_needs_evidence")
        self.assertEqual(packet["placeholder_evidence_count"], 3)
        self.assertEqual(packet["existing_evidence_count"], 0)
        self.assertEqual(packet["placeholder_manifest_field_count"], 1)
        self.assertTrue(any(item["field"] == "runtime_ui_review_file" for item in packet["evidence"]))
        self.assertTrue(any(item["field"] == "final_human_acceptance_file" for item in packet["evidence"]))

    def test_ready_manifest_packet_can_move_to_validator(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = make_ready_manifest(root)

            packet = build_packet(manifest, root)

            self.assertEqual(packet["decision"], "story_codex_acceptance_review_packet_ready_for_validation")
            self.assertEqual(packet["existing_evidence_count"], 3)
            self.assertEqual(packet["placeholder_manifest_field_count"], 0)

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
            self.assertEqual(payload["decision"], "story_codex_acceptance_review_packet_needs_evidence")
            text = markdown.read_text(encoding="utf-8")
            self.assertIn("Story Codex Acceptance Review Packet", text)
            self.assertIn("runtime_ui_review_file", text)
            self.assertIn("final_human_acceptance_file", text)


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
