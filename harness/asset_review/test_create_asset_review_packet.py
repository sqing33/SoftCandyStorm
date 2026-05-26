#!/usr/bin/env python3
"""Regression tests for asset review packet generation.

Run with:
    python3 harness/asset_review/test_create_asset_review_packet.py
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
PACKET = SCRIPT_DIR / "create_asset_review_packet.py"

sys.path.insert(0, str(SCRIPT_DIR))

from create_asset_review_packet import build_packet  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def make_candidate(root: Path) -> Path:
    candidate = root / "asset" / "generated_candidates" / "packet_batch"
    (candidate / "images").mkdir(parents=True, exist_ok=True)
    (candidate / "audio").mkdir(parents=True, exist_ok=True)
    (candidate / "images" / "sprite.png").write_bytes(b"png")
    (candidate / "audio" / "voice.mp3").write_bytes(b"mp3")
    write_json(
        candidate / "metadata" / "manifest.json",
        {
            "batch_id": "packet_batch",
            "generated_at": "2026-05-26",
            "project_rules": {
                "candidate_only": True,
                "accepted_content": False,
                "runtime_integrated": False,
                "required_next_steps": ["manual_asset_review"],
            },
            "assets": [
                {
                    "id": "sprite_fixture",
                    "type": "image",
                    "path": "images/sprite.png",
                    "qa_status": "needs_visual_review",
                    "qa_notes": ["inspect at 32px"],
                },
                {
                    "id": "voice_fixture",
                    "type": "speech",
                    "path": "audio/voice.mp3",
                    "qa_status": "needs_listening_review",
                    "qa_notes": ["listen with music"],
                },
            ],
        },
    )
    return candidate


def make_review(root: Path, candidate: Path) -> Path:
    review_path = root / "harness" / "asset_review" / "drafts" / "packet_review.json"
    write_json(
        review_path,
        {
            "review_version": 1,
            "candidate_batch_id": candidate.name,
            "candidate_batch_path": str(candidate.relative_to(root)),
            "candidate_metadata_report": "harness/reports/packet/summary.md",
            "reviewer": "TODO: human reviewer",
            "reviewed_at": "TODO: YYYY-MM-DD",
            "gate_decision": "needs_more_review",
            "summary": "TODO",
            "asset_reviews": [
                {
                    "id": "sprite_fixture",
                    "decision": "revise",
                    "asset_type": "image",
                    "style_fit": "TODO: 1-5",
                    "allowed_candidate_uses": ["concept_reference"],
                },
                {
                    "id": "voice_fixture",
                    "decision": "revise",
                    "asset_type": "speech",
                    "style_fit": "TODO: 1-5",
                    "allowed_candidate_uses": ["audio_candidate"],
                },
            ],
            "global_risks": ["TODO"],
            "next_actions": ["TODO"],
        },
    )
    return review_path


class AssetReviewPacketTests(unittest.TestCase):
    def test_build_packet_covers_assets_and_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidate = make_candidate(root)
            review = make_review(root, candidate)

            packet = build_packet(
                candidate,
                root,
                "harness/reports/packet/summary.md",
                review,
            )

            self.assertEqual(packet["batch_id"], "packet_batch")
            self.assertEqual(packet["asset_count"], 2)
            self.assertEqual(packet["missing_file_count"], 0)
            self.assertEqual(packet["missing_review_count"], 0)
            self.assertEqual([asset["review_status"] for asset in packet["assets"]], ["draft_todo", "draft_todo"])

    def test_cli_writes_markdown_packet(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidate = make_candidate(root)
            review = make_review(root, candidate)
            out = root / "packet.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(PACKET),
                    str(candidate),
                    "--repo-root",
                    str(root),
                    "--metadata-report",
                    "harness/reports/packet/summary.md",
                    "--review-draft",
                    str(review),
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
            self.assertIn("Asset Candidate Review Packet", text)
            self.assertIn("sprite_fixture", text)
            self.assertIn("voice_fixture", text)
            self.assertIn("draft_todo", text)


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
