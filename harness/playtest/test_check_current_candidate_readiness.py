#!/usr/bin/env python3
"""Regression tests for the current candidate readiness summary."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
CHECKER = SCRIPT_DIR / "check_current_candidate_readiness.py"
CONTENT_REVIEW_DIR = SCRIPT_DIR.parent / "content_review"

sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(CONTENT_REVIEW_DIR))

from check_current_candidate_readiness import build_report  # noqa: E402
from check_current_design_review_status import DEFAULT_DRAFT as DESIGN_DRAFT  # noqa: E402
from check_current_manual_playtest_status import DEFAULT_DRAFT as PLAYTEST_DRAFT  # noqa: E402
from current_candidate import CANDIDATE_ID, CONTENT_DIR, CONTENT_HASH, MANUAL_PLAYTEST_RUNS  # noqa: E402


SOURCE_MANIFEST = CONTENT_DIR / "metadata" / "source_patch_manifest.json"


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def source_manifest_payload() -> dict:
    return {
        "project_rules": {
            "candidate_only": True,
            "accepted_content": False,
            "runtime_integrated": False,
        },
        "contents": [{"id": "route-memory-caramel-ring", "type": "event"}],
    }


def complete_design_review_payload() -> dict:
    return {
        "review_version": 1,
        "candidate_pack_id": CANDIDATE_ID,
        "candidate_pack_path": str(CONTENT_DIR),
        "source_patch_manifest": str(SOURCE_MANIFEST),
        "candidate_preflight_report": "harness/reports/example/summary.md",
        "reviewer": "human reviewer",
        "reviewed_at": "2026-06-05",
        "gate_decision": "simulate_candidate",
        "summary": "人工确认 v61 新增事件可以进入后续校验。",
        "content_reviews": [
            {
                "id": "route-memory-caramel-ring",
                "content_type": "event",
                "decision": "pass",
                "theme_fit": 4,
                "novelty": 4,
                "build_potential": 3,
                "counterplay_clarity": 4,
                "visual_audio_fit": 4,
                "balance_risk": "low",
                "notes": "焦糖旧路环印提示明确，风险集中在 210 秒后地图压力。",
                "required_changes": [],
            }
        ],
        "batch_risks": [],
        "next_actions": ["运行正式设计审查校验。"],
    }


def complete_playtest_review_payload() -> dict:
    return {
        "candidate_id": CANDIDATE_ID,
        "content_hash": CONTENT_HASH,
        "reviewer": "human reviewer",
        "reviewed_at": "2026-06-05",
        "summary": "六局人工试玩记录完整。",
        "acceptance_decision": "accept_candidate",
        "runs": [
            {
                "run_id": run.run_id,
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
                    "notes": f"{run.run_id} 有具体人工观察。",
                    "tags": ["fun"],
                    "next_actions": ["继续 strict acceptance 校验。"],
                },
            }
            for run in MANUAL_PLAYTEST_RUNS
        ],
    }


class CurrentCandidateReadinessTests(unittest.TestCase):
    def test_current_state_waits_for_human_evidence(self) -> None:
        report = build_report(REPO_ROOT)

        self.assertEqual(report["decision"], "candidate_waiting_for_human_evidence")
        self.assertIn("design_review_incomplete", report["blockers"])
        self.assertIn("manual_playtest_incomplete", report["blockers"])
        self.assertEqual(
            report["summary"]["next_manual_command"],
            "python3 harness/playtest/run_current_manual_playtest.py new_frosting_jar_keeper",
        )

    def test_complete_local_evidence_is_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_json(root / SOURCE_MANIFEST, source_manifest_payload())
            write_json(root / DESIGN_DRAFT, complete_design_review_payload())
            write_json(root / PLAYTEST_DRAFT, complete_playtest_review_payload())
            for run in MANUAL_PLAYTEST_RUNS:
                write_json(root / run.report_path, {"run_id": run.run_id})

            report = build_report(root)

            self.assertEqual(report["decision"], "candidate_ready_for_human_validation")
            self.assertEqual(report["blockers"], [])
            self.assertIsNone(report["summary"]["next_manual_command"])

    def test_cli_allows_current_incomplete_status_when_requested(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            out = Path(temp_dir) / "readiness.json"
            summary = Path(temp_dir) / "summary.md"
            result = subprocess.run(
                [
                    sys.executable,
                    str(CHECKER),
                    "--allow-incomplete",
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
            self.assertEqual(payload["decision"], "candidate_waiting_for_human_evidence")
            markdown = summary.read_text(encoding="utf-8")
            self.assertIn("# v61 Candidate Readiness", markdown)
            self.assertIn("## Next Manual Command", markdown)


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
