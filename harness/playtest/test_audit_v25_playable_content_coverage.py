#!/usr/bin/env python3
"""Regression tests for v25 playable-content coverage auditing."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
SCRIPT = SCRIPT_DIR / "audit_v25_playable_content_coverage.py"

sys.path.insert(0, str(SCRIPT_DIR))

from audit_v25_playable_content_coverage import build_audit  # noqa: E402


class V25PlayableContentCoverageAuditTests(unittest.TestCase):
    def test_current_state_flags_content_repair_without_promoting_candidate(self) -> None:
        audit = build_audit(REPO_ROOT)

        self.assertEqual(audit["decision"], "v25_playable_content_coverage_needs_content_repair")
        self.assertTrue(audit["candidate_state"]["candidate_only"])
        self.assertFalse(audit["candidate_state"]["accepted_content"])
        self.assertFalse(audit["candidate_state"]["runtime_integrated"])
        self.assertEqual(audit["summary"]["quick_play_preset_count"], 6)
        self.assertEqual(audit["summary"]["content_tour_run_count"], 6)

    def test_current_state_detects_starter_weapon_evolution_gaps(self) -> None:
        audit = build_audit(REPO_ROOT)
        items = {item["id"]: item for item in audit["action_items"]}

        self.assertIn("character_starter_without_evolution_bubble-courier", items)
        self.assertIn("soda-bubble-pop", items["character_starter_without_evolution_bubble-courier"]["affected_ids"])
        self.assertIn("character_starter_without_evolution_sour-plum-doctor", items)
        self.assertIn("sour-plum-spray", items["character_starter_without_evolution_sour-plum-doctor"]["affected_ids"])

    def test_current_state_entrypoints_cover_all_characters_and_maps(self) -> None:
        audit = build_audit(REPO_ROOT)
        categories = {item["category"] for item in audit["action_items"]}

        self.assertNotIn("entrypoint_coverage", categories)
        self.assertEqual(
            audit["coverage"]["quick_play_characters"],
            ["bubble-courier", "cream-knight", "jar-keeper", "pudding-crafter", "sour-plum-doctor"],
        )
        self.assertEqual(
            audit["coverage"]["content_tour_maps"],
            [
                "caramel-workshop",
                "cotton-cloud-pasture",
                "cracked-star-jar",
                "frosting-grassland",
                "jelly-platform",
                "soda-creek",
            ],
        )

    def test_cli_writes_json_and_markdown_with_allow_repair(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = Path(temp_dir) / "coverage.json"
            markdown_path = Path(temp_dir) / "summary.md"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--allow-repair",
                    "--report",
                    str(report_path),
                    "--markdown",
                    str(markdown_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["decision"], "v25_playable_content_coverage_needs_content_repair")
            markdown = markdown_path.read_text(encoding="utf-8")
            self.assertIn("# v25 可玩内容覆盖审计", markdown)
            self.assertIn("character_starter_without_evolution", markdown)


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
