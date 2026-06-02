#!/usr/bin/env python3
"""Regression tests for the v25 human evidence TODO lister."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
LISTER = SCRIPT_DIR / "list_v25_human_evidence_todos.py"

sys.path.insert(0, str(SCRIPT_DIR))

from list_v25_human_evidence_todos import DESIGN_DRAFT, PLAYTEST_DRAFT, build_report  # noqa: E402
from run_v25_manual_playtest import CANDIDATE_ID, CONTENT_HASH, RUNS  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def complete_design_payload() -> dict:
    return {
        "review_version": 1,
        "candidate_pack_id": CANDIDATE_ID,
        "reviewer": "human reviewer",
        "reviewed_at": "2026-06-02",
        "gate_decision": "simulate_candidate",
        "summary": "Design review complete.",
        "content_reviews": [
            {
                "id": "pudding-turret",
                "content_type": "weapon",
                "decision": "pass",
                "theme_fit": 4,
                "novelty": 4,
                "build_potential": 4,
                "counterplay_clarity": 4,
                "visual_audio_fit": 4,
                "balance_risk": "low",
                "notes": "Concrete design observation.",
                "required_changes": [],
            }
        ],
        "batch_risks": [],
        "next_actions": ["Run formal validation."],
    }


def complete_playtest_payload() -> dict:
    return {
        "candidate_id": CANDIDATE_ID,
        "content_hash": CONTENT_HASH,
        "reviewer": "human reviewer",
        "reviewed_at": "2026-06-02",
        "summary": "Manual playtest complete.",
        "acceptance_decision": "accept_candidate",
        "runs": [
            {
                "run_id": run.run_id,
                "player_skill": run.skill,
                "intent": run.intent,
                "required_observations": ["Concrete observation target."],
                "gate_decision": "playtest_pass",
                "manual_review": {
                    "fun_rating": 4,
                    "clarity_rating": 4,
                    "difficulty_rating": 3,
                    "projectile_readability": 4,
                    "hit_feedback": 4,
                    "xp_pickup_rhythm": 4,
                    "boss_spawn_clarity": 4,
                    "death_reason_clarity": 4,
                    "notes": f"{run.run_id} concrete observation.",
                    "tags": ["fun"],
                    "next_actions": ["Run strict validation."],
                },
            }
            for run in RUNS
        ],
    }


class V25HumanEvidenceTodoTests(unittest.TestCase):
    def test_current_drafts_have_human_todos(self) -> None:
        report = build_report(REPO_ROOT)

        self.assertEqual(report["decision"], "human_evidence_todos_pending")
        self.assertGreater(report["summary"]["design_todo_count"], 0)
        self.assertGreater(report["summary"]["playtest_todo_count"], 0)
        first_run = report["manual_playtest"]["runs"][0]
        self.assertEqual(first_run["run_id"], "new_001")
        self.assertGreater(first_run["todo_count"], 0)

    def test_complete_drafts_are_clear(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_json(root / DESIGN_DRAFT, complete_design_payload())
            write_json(root / PLAYTEST_DRAFT, complete_playtest_payload())

            report = build_report(root)

            self.assertEqual(report["decision"], "human_evidence_todos_clear")
            self.assertEqual(report["summary"]["design_todo_count"], 0)
            self.assertEqual(report["summary"]["playtest_todo_count"], 0)

    def test_cli_allows_current_todos_when_requested(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            out = Path(temp_dir) / "todos.json"
            summary = Path(temp_dir) / "summary.md"
            result = subprocess.run(
                [
                    sys.executable,
                    str(LISTER),
                    "--allow-todos",
                    "--report",
                    str(out),
                    "--markdown",
                    str(summary),
                ],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(payload["decision"], "human_evidence_todos_pending")
            self.assertIn("# v25 Human Evidence TODOs", summary.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
