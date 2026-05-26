#!/usr/bin/env python3
"""Regression tests for manual playtest review packet generation.

Run with:
    python3 harness/playtest/test_create_manual_playtest_review_packet.py
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
PACKET = SCRIPT_DIR / "create_manual_playtest_review_packet.py"

sys.path.insert(0, str(SCRIPT_DIR))

from create_manual_playtest_review_packet import build_packet  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def make_template(root: Path) -> Path:
    template = root / "harness/playtest/runtime_manual_review_template.json"
    write_json(
        template,
        {
            "review_pack_version": 1,
            "minimum_run_count": 2,
            "runs": [
                {
                    "run_id": "new_001",
                    "player_skill": "new",
                    "intent": "不看说明直接开始",
                    "required_observations": ["是否理解移动"],
                },
                {
                    "run_id": "build_001",
                    "player_skill": "build",
                    "intent": "远程投射物优先",
                    "required_observations": ["projectile 可读性"],
                },
            ],
            "manual_review_fields": {
                "fun_rating": None,
                "projectile_readability": None,
                "notes": "",
                "tags": [],
                "next_actions": [],
            },
            "allowed_tags": ["fun", "visual-clarity"],
            "allowed_gate_decisions": ["repair", "playtest_pass", "needs_more_runs"],
        },
    )
    return template


def make_draft(root: Path) -> Path:
    draft = root / "harness/playtest/drafts/review_draft.json"
    write_json(
        draft,
        {
            "review_pack_version": 1,
            "candidate_id": "fixture-runtime",
            "content_hash": "TODO: content hash",
            "reviewer": "TODO: human reviewer",
            "reviewed_at": "TODO: YYYY-MM-DD",
            "summary": "TODO",
            "acceptance_decision": "needs_more_runs",
            "runs": [
                {
                    "run_id": "new_001",
                    "player_skill": "new",
                    "intent": "不看说明直接开始",
                    "gate_decision": "needs_more_runs",
                    "manual_review": {
                        "fun_rating": "TODO: 1-5",
                        "projectile_readability": "TODO: 1-5",
                        "notes": "TODO: observation",
                        "tags": ["TODO: tag"],
                        "next_actions": ["TODO: action"],
                    },
                },
                {
                    "run_id": "build_001",
                    "player_skill": "build",
                    "intent": "远程投射物优先",
                    "gate_decision": "needs_more_runs",
                    "manual_review": {
                        "fun_rating": "TODO: 1-5",
                        "projectile_readability": "TODO: 1-5",
                        "notes": "TODO: observation",
                        "tags": ["TODO: tag"],
                        "next_actions": ["TODO: action"],
                    },
                },
            ],
        },
    )
    return draft


class ManualPlaytestReviewPacketTests(unittest.TestCase):
    def test_build_packet_covers_template_runs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            template = make_template(root)
            draft = make_draft(root)

            packet = build_packet(template, draft, root)

            self.assertEqual(packet["candidate_id"], "fixture-runtime")
            self.assertEqual(packet["run_count"], 2)
            self.assertEqual(packet["missing_draft_run_count"], 0)
            self.assertEqual([run["review_status"] for run in packet["runs"]], ["draft_todo", "draft_todo"])
            self.assertIn("projectile_readability", packet["rating_fields"])

    def test_cli_writes_markdown_packet(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            template = make_template(root)
            draft = make_draft(root)
            out = root / "manual_review_packet.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(PACKET),
                    "--template",
                    str(template),
                    "--draft",
                    str(draft),
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
            self.assertIn("Manual Playtest Review Packet", text)
            self.assertIn("new_001", text)
            self.assertIn("build_001", text)
            self.assertIn("draft_todo", text)
            self.assertIn("It does not run Runtime", text)


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
