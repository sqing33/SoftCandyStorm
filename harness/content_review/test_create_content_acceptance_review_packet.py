#!/usr/bin/env python3
"""Regression tests for final content acceptance review packet generation.

Run with:
    python3 harness/content_review/test_create_content_acceptance_review_packet.py
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
PACKET = SCRIPT_DIR / "create_content_acceptance_review_packet.py"
PHASE4_PACK = REPO_ROOT / "harness/generated_candidates/2026-05-26_phase4_roster_gap_full_pack"

sys.path.insert(0, str(SCRIPT_DIR))

from create_content_acceptance_review_packet import build_packet, default_evidence_paths  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_ready_pack(root: Path) -> tuple[Path, dict[str, str]]:
    candidate_pack = root / "harness/generated_candidates/ready-content-pack"
    project_rules = {
        "candidate_only": True,
        "accepted_content": False,
        "runtime_integrated": False,
    }
    write_json(
        candidate_pack / "metadata/manifest.json",
        {
            "batch_id": "ready-content-pack",
            "candidate_kind": "full_content_pack",
            "project_rules": project_rules,
        },
    )
    write_json(
        candidate_pack / "metadata/source_patch_manifest.json",
        {
            "batch_id": "ready-content-pack",
            "project_rules": project_rules,
            "contents": [
                {
                    "id": "ready-passive",
                    "type": "passive",
                    "role": "fixture",
                    "path": "passives/ready-passive.json",
                    "balance_budget": {
                        "risk": "low",
                        "gate_focus": "fixture gate",
                    },
                }
            ],
        },
    )
    write_json(
        candidate_pack / "passives/ready-passive.json",
        {
            "id": "ready-passive",
            "name": "Ready Passive",
            "tags": ["fixture", "defense"],
        },
    )

    write_text(root / "harness/reports/preflight/summary.md", "# preflight\n")
    write_text(root / "harness/reports/static-budget/summary.md", "# static budget\n")
    write_text(root / "harness/reports/design-packet/summary.md", "# design packet\n")
    write_json(
        root / "harness/content_review/reviews/ready-design-review.json",
        {
            "decision": "validated",
            "gate_decision": "simulate_candidate",
            "content_reviews": [{"id": "ready-passive", "decision": "simulate_candidate"}],
        },
    )
    write_json(
        root / "harness/reports/demo-ready/demo_readiness.json",
        {"decision": "demo_ready"},
    )
    write_json(
        root / "harness/playtest/reviews/ready-manual-playtest.json",
        {
            "acceptance_decision": "accept_candidate",
            "runs": [{"run_id": "new_001", "scores": {"fun": 4}}],
        },
    )
    write_json(
        root / "harness/reports/lockfile/accepted_content_lockfile.json",
        {"decision": "accepted_content_lockfile_valid"},
    )

    evidence = {
        "candidate_preflight_report": "harness/reports/preflight/summary.md",
        "static_budget_report": "harness/reports/static-budget/summary.md",
        "design_review_draft": "harness/content_review/reviews/ready-design-review.json",
        "design_review_packet": "harness/reports/design-packet/summary.md",
        "demo_readiness_report": "harness/reports/demo-ready/demo_readiness.json",
        "manual_playtest_draft": "harness/playtest/reviews/ready-manual-playtest.json",
        "accepted_content_lockfile_report": "harness/reports/lockfile/accepted_content_lockfile.json",
    }
    return candidate_pack, evidence


class ContentAcceptanceReviewPacketTests(unittest.TestCase):
    def test_phase4_packet_reports_missing_acceptance_evidence(self) -> None:
        packet = build_packet(PHASE4_PACK, REPO_ROOT, default_evidence_paths())

        self.assertEqual(packet["decision"], "content_acceptance_review_packet_needs_evidence")
        self.assertEqual(packet["existing_evidence_count"], 7)
        self.assertEqual(packet["content_count"], 8)
        self.assertEqual(packet["type_counts"], {"enemy": 4, "passive": 4})
        self.assertEqual(packet["design_review_status"]["status"], "draft_todo")
        self.assertEqual(packet["manual_playtest_status"]["status"], "draft_todo")
        self.assertEqual(packet["demo_readiness_decision"], "demo_not_ready")
        self.assertEqual(packet["accepted_content_lockfile_decision"], "accepted_content_lockfile_blocked")
        self.assertTrue(any("manual playtest has not accepted" in item for item in packet["blockers"]))

    def test_ready_pack_can_move_to_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidate_pack, evidence = make_ready_pack(root)

            packet = build_packet(candidate_pack, root, evidence)

            self.assertEqual(packet["decision"], "content_acceptance_review_packet_ready_for_validation")
            self.assertEqual(packet["existing_evidence_count"], 7)
            self.assertEqual(packet["blockers"], [])
            self.assertEqual(packet["errors"], [])

    def test_cli_writes_markdown_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            out_dir = Path(temp_dir)
            report = out_dir / "content_acceptance_review_packet.json"
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
            self.assertEqual(payload["decision"], "content_acceptance_review_packet_needs_evidence")
            text = markdown.read_text(encoding="utf-8")
            self.assertIn("Content Acceptance Review Packet", text)
            self.assertIn("manual_playtest_draft", text)
            self.assertIn("accepted_content_lockfile_report", text)


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
