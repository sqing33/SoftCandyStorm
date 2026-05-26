#!/usr/bin/env python3
"""Regression tests for manual playtest acceptance review packet generation.

Run with:
    python3 harness/playtest/test_create_manual_playtest_acceptance_review_packet.py
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
PACKET = SCRIPT_DIR / "create_manual_playtest_acceptance_review_packet.py"

sys.path.insert(0, str(SCRIPT_DIR))

from create_manual_playtest_acceptance_review_packet import build_packet, default_evidence_paths  # noqa: E402


REQUIRED_RUN_IDS = [
    "new_001",
    "new_002",
    "new_003",
    "skilled_001",
    "skilled_002",
    "skilled_003",
    "build_001",
    "build_002",
    "build_003",
]


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_ready_review() -> dict:
    return {
        "candidate_id": "ready-playtest-candidate",
        "content_hash": "fnv1a64:0123456789abcdef",
        "reviewer": "human-reviewer-fixture",
        "reviewed_at": "2026-05-26",
        "summary": "Fixture human review complete enough for handoff.",
        "acceptance_decision": "accept_candidate",
        "runs": [
            {
                "run_id": run_id,
                "gate_decision": "playtest_pass",
                "manual_review": {
                    "fun_rating": 4,
                    "clarity_rating": 4,
                    "difficulty_rating": 4,
                    "projectile_readability": 4,
                    "hit_feedback": 4,
                    "xp_pickup_rhythm": 4,
                    "boss_spawn_clarity": 4,
                    "death_reason_clarity": 4,
                    "notes": f"Concrete human observation for {run_id}.",
                    "tags": ["fun"],
                    "next_actions": ["Keep this run in the acceptance evidence set."],
                },
            }
            for run_id in REQUIRED_RUN_IDS
        ],
    }


def make_ready_tree(root: Path) -> dict[str, str]:
    write_json(root / "harness/playtest/runtime_manual_review_template.json", {"runs": []})
    write_json(root / "harness/playtest/reviews/ready-review.json", make_ready_review())
    write_text(root / "harness/reports/manual-review-packet/summary.md", "# packet\n")
    write_json(
        root / "harness/reports/manual-review-validation/manual_review_validation.json",
        {
            "decision": "manual_review_valid",
            "strict_acceptance": True,
            "run_count": 9,
            "errors": [],
            "warnings": [],
        },
    )
    write_json(
        root / "harness/release/current_local_rc_evidence.json",
        {
            "gates": [
                {
                    "id": "manual_playtest",
                    "status": "pass",
                    "summary": "Fixture manual playtest passed.",
                    "evidence_paths": ["harness/playtest/reviews/ready-review.json"],
                    "synthetic": False,
                }
            ]
        },
    )
    write_json(
        root / "harness/reports/content-acceptance/content_acceptance_review_packet.json",
        {"decision": "content_acceptance_review_packet_ready_for_validation"},
    )
    write_json(
        root / "harness/reports/lockfile/accepted_content_lockfile.json",
        {"decision": "accepted_content_lockfile_valid"},
    )
    return {
        "manual_review_template": "harness/playtest/runtime_manual_review_template.json",
        "manual_review_source": "harness/playtest/reviews/ready-review.json",
        "manual_review_packet": "harness/reports/manual-review-packet/summary.md",
        "strict_validation_report": "harness/reports/manual-review-validation/manual_review_validation.json",
        "release_candidate_evidence": "harness/release/current_local_rc_evidence.json",
        "content_acceptance_review_packet": "harness/reports/content-acceptance/content_acceptance_review_packet.json",
        "accepted_content_lockfile_report": "harness/reports/lockfile/accepted_content_lockfile.json",
    }


class ManualPlaytestAcceptanceReviewPacketTests(unittest.TestCase):
    def test_current_local_packet_reports_missing_human_evidence(self) -> None:
        packet = build_packet(REPO_ROOT, default_evidence_paths())

        self.assertEqual(packet["decision"], "manual_playtest_acceptance_review_packet_needs_evidence")
        self.assertEqual(packet["manual_review_status"]["status"], "draft_todo")
        self.assertEqual(packet["manual_review_status"]["acceptance_decision"], "needs_more_runs")
        self.assertEqual(packet["release_candidate_manual_playtest_gate"]["status"], "waiting")
        self.assertTrue(any("TODO placeholders" in blocker for blocker in packet["blockers"]))
        self.assertTrue(any("manual_playtest gate" in blocker for blocker in packet["blockers"]))

    def test_ready_review_can_move_to_content_lock_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            evidence = make_ready_tree(root)

            packet = build_packet(root, evidence)

            self.assertEqual(packet["decision"], "manual_playtest_acceptance_review_packet_ready_for_content_lock")
            self.assertEqual(packet["manual_review_status"]["completed_run_count"], 9)
            self.assertEqual(packet["strict_validation_status"]["decision"], "manual_review_valid")
            self.assertEqual(packet["blockers"], [])
            self.assertEqual(packet["errors"], [])

    def test_cli_writes_markdown_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            out_dir = Path(temp_dir)
            report = out_dir / "manual_playtest_acceptance_review_packet.json"
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
            self.assertEqual(payload["decision"], "manual_playtest_acceptance_review_packet_needs_evidence")
            text = markdown.read_text(encoding="utf-8")
            self.assertIn("Manual Playtest Acceptance Review Packet", text)
            self.assertIn("manual_review_source", text)
            self.assertIn("RC manual playtest gate", text)


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
