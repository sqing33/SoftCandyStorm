#!/usr/bin/env python3
"""Regression tests for the v25 content design-review status checker."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
CHECKER = SCRIPT_DIR / "check_v25_design_review_status.py"

sys.path.insert(0, str(SCRIPT_DIR))

from check_v25_design_review_status import CANDIDATE_ID, CANDIDATE_PATH, DEFAULT_DRAFT, build_report  # noqa: E402


SOURCE_MANIFEST = CANDIDATE_PATH / "metadata" / "source_patch_manifest.json"


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
        "contents": [
            {
                "id": "pudding-turret",
                "type": "weapon",
                "path": "weapons/pudding-turret.json",
            }
        ],
    }


def complete_review_payload() -> dict:
    return {
        "review_version": 1,
        "candidate_pack_id": CANDIDATE_ID,
        "candidate_pack_path": str(CANDIDATE_PATH),
        "source_patch_manifest": str(SOURCE_MANIFEST),
        "candidate_preflight_report": "harness/reports/example/summary.md",
        "reviewer": "human reviewer",
        "reviewed_at": "2026-06-02",
        "gate_decision": "simulate_candidate",
        "summary": "布丁炮台修复方向清晰，可以进入正式设计审查校验。",
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
                "notes": "人工确认该修复只收窄自动安全收益。",
                "required_changes": [],
            }
        ],
        "batch_risks": [],
        "next_actions": ["继续正式设计审查校验。"],
    }


class V25DesignReviewStatusTests(unittest.TestCase):
    def test_current_todo_draft_is_incomplete(self) -> None:
        report = build_report(REPO_ROOT)

        self.assertEqual(report["decision"], "design_review_incomplete")
        self.assertEqual(report["summary"]["expected_content_count"], 1)
        self.assertTrue(report["summary"]["draft_has_placeholder"])
        self.assertIn("pudding-turret", report["placeholder_reviews"])

    def test_complete_draft_is_ready_for_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_json(root / SOURCE_MANIFEST, source_manifest_payload())
            write_json(root / DEFAULT_DRAFT, complete_review_payload())

            report = build_report(root)

            self.assertEqual(report["decision"], "design_review_ready_for_validation")
            self.assertEqual(report["summary"]["reviewed_content_count"], 1)
            self.assertEqual(report["errors"], [])

    def test_cli_allows_current_incomplete_status_when_requested(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            out = Path(temp_dir) / "status.json"
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
            self.assertEqual(payload["decision"], "design_review_incomplete")
            self.assertIn("# v25 Content Design Review Status", summary.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
