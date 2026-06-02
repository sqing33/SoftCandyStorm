#!/usr/bin/env python3
"""Regression tests for the v25 playable content guide generator."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
GENERATOR = SCRIPT_DIR / "create_v25_playable_content_guide.py"

sys.path.insert(0, str(SCRIPT_DIR))

from create_v25_playable_content_guide import build_guide, write_markdown  # noqa: E402
from run_v25_manual_playtest import CANDIDATE_ID, CONTENT_HASH  # noqa: E402


class V25PlayableContentGuideTests(unittest.TestCase):
    def test_current_v25_pack_summarizes_playable_counts(self) -> None:
        guide = build_guide(REPO_ROOT)

        self.assertEqual(guide["decision"], "playable_content_guide_candidate_only")
        self.assertEqual(guide["candidate_id"], CANDIDATE_ID)
        self.assertEqual(guide["content_hash"], CONTENT_HASH)
        self.assertEqual(guide["summary"]["character_count"], 5)
        self.assertEqual(guide["summary"]["map_count"], 6)
        self.assertEqual(guide["summary"]["weapon_count"], 17)
        self.assertEqual(guide["summary"]["passive_count"], 17)
        self.assertEqual(guide["summary"]["evolution_count"], 13)
        self.assertEqual(guide["summary"]["enemy_count"], 12)
        self.assertEqual(guide["summary"]["boss_count"], 6)
        self.assertEqual(guide["summary"]["target_count_failures"], [])

    def test_build_routes_include_demo_buildcraft_pairs(self) -> None:
        guide = build_guide(REPO_ROOT)
        route_by_id = {route["id"]: route for route in guide["build_routes"]}

        self.assertIn("sugar-drum-crescendo", route_by_id)
        self.assertEqual(route_by_id["sugar-drum-crescendo"]["weapon_id"], "sugar-drum")
        self.assertEqual(route_by_id["sugar-drum-crescendo"]["passive_id"], "rhythm-ribbon")
        self.assertIn("pudding-bastion", route_by_id)
        self.assertEqual(route_by_id["pudding-bastion"]["weapon_id"], "pudding-turret")

    def test_guide_marks_candidate_as_not_accepted(self) -> None:
        guide = build_guide(REPO_ROOT)

        self.assertTrue(guide["candidate_state"]["candidate_only"])
        self.assertFalse(guide["candidate_state"]["accepted_content"])
        self.assertFalse(guide["candidate_state"]["runtime_integrated"])
        self.assertIn("design_review_incomplete", guide["human_review_blockers"])

    def test_guide_includes_optional_content_tour_runs(self) -> None:
        guide = build_guide(REPO_ROOT)

        self.assertEqual(len(guide["content_tour_runs"]), 6)
        self.assertIn("python3 harness/playtest/run_v25_content_tour.py --next", guide["content_tour_entrypoints"])
        self.assertIn(
            "python3 harness/playtest/summarize_v25_content_tour_reports.py --allow-incomplete",
            guide["content_tour_entrypoints"],
        )
        run_by_id = {run["run_id"]: run for run in guide["content_tour_runs"]}
        self.assertEqual(run_by_id["soda_bubble_courier"]["character_id"], "bubble-courier")
        self.assertEqual(run_by_id["soda_bubble_courier"]["map_id"], "soda-creek")
        self.assertIn("--character-id bubble-courier", run_by_id["soda_bubble_courier"]["runtime_command"])

    def test_markdown_contains_human_playtest_entrypoints(self) -> None:
        guide = build_guide(REPO_ROOT)
        with tempfile.TemporaryDirectory() as temp_dir:
            markdown = Path(temp_dir) / "summary.md"
            write_markdown(guide, markdown)

            text = markdown.read_text(encoding="utf-8")
            self.assertIn("# v25 可玩内容导览", text)
            self.assertIn("糖鼓终曲", text)
            self.assertIn("python3 harness/playtest/run_v25_manual_playtest.py --next", text)
            self.assertIn("python3 harness/playtest/run_v25_content_tour.py --next", text)
            self.assertIn("summarize_v25_content_tour_reports.py", text)
            self.assertIn("Accepted content: `False`", text)

    def test_cli_writes_report_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            report = root / "guide.json"
            markdown = root / "summary.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(GENERATOR),
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
            self.assertEqual(payload["decision"], "playable_content_guide_candidate_only")
            self.assertIn("v25 可玩内容导览", markdown.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
