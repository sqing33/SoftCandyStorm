#!/usr/bin/env python3
"""Regression tests for current playable-candidate tools."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
GUIDE_SCRIPT = SCRIPT_DIR / "create_current_playable_content_guide.py"
AUDIT_SCRIPT = SCRIPT_DIR / "audit_current_playable_content_coverage.py"
QUICK_PLAY_SCRIPT = SCRIPT_DIR / "play_current_candidate.py"
TOUR_SCRIPT = SCRIPT_DIR / "run_current_content_tour.py"
MANUAL_DRAFT_SCRIPT = SCRIPT_DIR / "create_current_manual_playtest_review_draft.py"
MANUAL_STATUS_SCRIPT = SCRIPT_DIR / "check_current_manual_playtest_status.py"
WORKSHEET_SCRIPT = SCRIPT_DIR / "create_current_human_review_worksheet.py"

sys.path.insert(0, str(SCRIPT_DIR))

from audit_current_playable_content_coverage import build_audit  # noqa: E402
from create_current_playable_content_guide import build_guide  # noqa: E402
from current_candidate import (  # noqa: E402
    CANDIDATE_ID,
    CONTENT_DIR,
    CONTENT_HASH,
    CONTENT_TOUR_RUNS,
    FORBIDDEN_MANUAL_FLAGS,
    MANUAL_PLAYTEST_RUNS,
    QUICK_PLAY_PRESETS,
)
from check_current_manual_playtest_status import build_report as build_manual_status_report  # noqa: E402
from create_current_human_review_worksheet import build_markdown as build_worksheet_markdown  # noqa: E402
from create_current_manual_playtest_review_draft import DEFAULT_OUT as MANUAL_DRAFT, build_draft  # noqa: E402
from play_current_candidate import PRESET_BY_ID, build_quick_play_command, validate_quick_play_command  # noqa: E402
from run_current_content_tour import RUN_BY_ID, build_tour_command, validate_tour_command  # noqa: E402
from run_current_manual_playtest import (  # noqa: E402
    RUN_BY_ID as MANUAL_RUN_BY_ID,
    build_manual_playtest_command,
    validate_manual_playtest_command,
)


class CurrentPlayableCandidateToolTests(unittest.TestCase):
    def test_guide_targets_v51_candidate_counts(self) -> None:
        guide = build_guide(REPO_ROOT)

        self.assertEqual(guide["decision"], "playable_content_guide_candidate_only")
        self.assertEqual(guide["candidate_id"], CANDIDATE_ID)
        self.assertEqual(guide["content_hash"], CONTENT_HASH)
        self.assertEqual(guide["content_dir"], str(CONTENT_DIR))
        self.assertEqual(guide["summary"]["character_count"], 5)
        self.assertEqual(guide["summary"]["map_count"], 6)
        self.assertEqual(guide["summary"]["weapon_count"], 17)
        self.assertEqual(guide["summary"]["passive_count"], 17)
        self.assertEqual(guide["summary"]["evolution_count"], 17)
        self.assertEqual(guide["summary"]["enemy_count"], 12)
        self.assertEqual(guide["summary"]["boss_count"], 6)
        self.assertEqual(guide["summary"]["target_count_failures"], [])
        self.assertTrue(guide["candidate_state"]["candidate_only"])
        self.assertFalse(guide["candidate_state"]["accepted_content"])
        self.assertFalse(guide["candidate_state"]["runtime_integrated"])

    def test_quick_play_and_tour_cover_current_characters_and_maps(self) -> None:
        self.assertEqual(len(QUICK_PLAY_PRESETS), 6)
        self.assertEqual(len(CONTENT_TOUR_RUNS), 6)
        self.assertEqual(len(MANUAL_PLAYTEST_RUNS), 6)
        self.assertEqual(
            {preset.character_id for preset in QUICK_PLAY_PRESETS},
            {"jar-keeper", "bubble-courier", "cream-knight", "pudding-crafter", "sour-plum-doctor"},
        )
        self.assertEqual(
            {run.map_id for run in CONTENT_TOUR_RUNS},
            {
                "caramel-workshop",
                "cotton-cloud-pasture",
                "cracked-star-jar",
                "frosting-grassland",
                "jelly-platform",
                "soda-creek",
            },
        )
        self.assertEqual(
            {run.character_id for run in MANUAL_PLAYTEST_RUNS},
            {"jar-keeper", "bubble-courier", "cream-knight", "pudding-crafter", "sour-plum-doctor"},
        )
        self.assertEqual(
            {run.map_id for run in MANUAL_PLAYTEST_RUNS},
            {
                "caramel-workshop",
                "cotton-cloud-pasture",
                "cracked-star-jar",
                "frosting-grassland",
                "jelly-platform",
                "soda-creek",
            },
        )

    def test_runtime_commands_target_v51_without_automation_flags(self) -> None:
        quick_command = build_quick_play_command(PRESET_BY_ID["default"])
        tour_command = build_tour_command(RUN_BY_ID["soda_bubble_courier"])
        manual_command = build_manual_playtest_command(MANUAL_RUN_BY_ID["speed_soda_bubble_courier"])

        for command in (quick_command, tour_command, manual_command):
            self.assertIn(str(CONTENT_DIR), command)
            for flag in FORBIDDEN_MANUAL_FLAGS:
                self.assertNotIn(flag, command)
        self.assertIn("harness/telemetry/local/v51_quick_play_default.json", quick_command)
        self.assertIn("harness/telemetry/local/v51_content_tour_soda_bubble_courier.json", tour_command)
        self.assertIn("harness/telemetry/local/v51_manual_playtest_speed_soda_bubble_courier.json", manual_command)
        validate_quick_play_command(quick_command)
        validate_tour_command(tour_command)
        validate_manual_playtest_command(manual_command)

    def test_dry_run_launchers_print_current_candidate_commands(self) -> None:
        quick = subprocess.run(
            [sys.executable, str(QUICK_PLAY_SCRIPT), "--dry-run"],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )
        self.assertEqual(quick.returncode, 0, quick.stderr)
        self.assertIn("cargo run -p game_runtime", quick.stdout)
        self.assertIn("--content-dir harness/generated_candidates/2026-06-04_demo_buildcraft_repair_v51_full_pack", quick.stdout)
        self.assertIn("--character-id jar-keeper", quick.stdout)

        tour = subprocess.run(
            [sys.executable, str(TOUR_SCRIPT), "soda_bubble_courier", "--dry-run"],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )
        self.assertEqual(tour.returncode, 0, tour.stderr)
        self.assertIn("--character-id bubble-courier", tour.stdout)
        self.assertIn("--map-id soda-creek", tour.stdout)

        manual = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "run_current_manual_playtest.py"), "speed_soda_bubble_courier", "--dry-run"],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )
        self.assertEqual(manual.returncode, 0, manual.stderr)
        self.assertIn("--character-id bubble-courier", manual.stdout)
        self.assertIn("--map-id soda-creek", manual.stdout)
        self.assertIn("v51_manual_playtest_speed_soda_bubble_courier.json", manual.stdout)

    def test_audit_reports_current_entrypoint_coverage(self) -> None:
        audit = build_audit(REPO_ROOT)

        self.assertEqual(audit["candidate_id"], CANDIDATE_ID)
        self.assertEqual(audit["content_hash"], CONTENT_HASH)
        self.assertTrue(audit["candidate_state"]["candidate_only"])
        self.assertEqual(audit["summary"]["quick_play_preset_count"], 6)
        self.assertEqual(audit["summary"]["content_tour_run_count"], 6)
        self.assertNotIn("entrypoint_coverage", {item["category"] for item in audit["action_items"]})
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

    def test_guide_and_audit_cli_write_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            guide_report = root / "guide.json"
            guide_markdown = root / "guide.md"
            audit_report = root / "audit.json"
            audit_markdown = root / "audit.md"

            guide_result = subprocess.run(
                [
                    sys.executable,
                    str(GUIDE_SCRIPT),
                    "--report",
                    str(guide_report),
                    "--markdown",
                    str(guide_markdown),
                ],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(guide_result.returncode, 0, guide_result.stderr)
            self.assertEqual(json.loads(guide_report.read_text(encoding="utf-8"))["candidate_id"], CANDIDATE_ID)
            self.assertIn("v51 可玩内容导览", guide_markdown.read_text(encoding="utf-8"))

            audit_result = subprocess.run(
                [
                    sys.executable,
                    str(AUDIT_SCRIPT),
                    "--allow-repair",
                    "--report",
                    str(audit_report),
                    "--markdown",
                    str(audit_markdown),
                ],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(audit_result.returncode, 0, audit_result.stderr)
            self.assertEqual(json.loads(audit_report.read_text(encoding="utf-8"))["candidate_id"], CANDIDATE_ID)
            self.assertIn("v51 可玩内容覆盖审计", audit_markdown.read_text(encoding="utf-8"))

    def test_manual_playtest_draft_and_status_are_current_candidate_only(self) -> None:
        draft = build_draft()

        self.assertEqual(draft["candidate_id"], CANDIDATE_ID)
        self.assertEqual(draft["content_hash"], CONTENT_HASH)
        self.assertEqual(len(draft["runs"]), 6)
        self.assertEqual(draft["acceptance_decision"], "needs_more_runs")
        self.assertTrue(all(run["gate_decision"] == "needs_more_runs" for run in draft["runs"]))
        self.assertTrue(all("TODO" in run["manual_review"]["notes"] for run in draft["runs"]))

    def test_manual_status_detects_missing_reports_and_todo_draft(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            draft = build_draft()
            draft_path = root / MANUAL_DRAFT
            draft_path.parent.mkdir(parents=True, exist_ok=True)
            draft_path.write_text(json.dumps(draft, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

            report = build_manual_status_report(root)

            self.assertEqual(report["decision"], "manual_playtest_incomplete")
            self.assertEqual(report["summary"]["missing_report_count"], 6)
            self.assertTrue(report["summary"]["draft_has_todo"])
            self.assertEqual(report["candidate_id"], CANDIDATE_ID)

    def test_worksheet_contains_current_commands_and_warnings(self) -> None:
        markdown = build_worksheet_markdown(REPO_ROOT)

        self.assertIn(CANDIDATE_ID, markdown)
        self.assertIn(CONTENT_HASH, markdown)
        self.assertIn("frosting-grassland-standard", markdown)
        self.assertIn("人工证据不得使用 `--demo-input`", markdown)
        self.assertIn("Runtime GUI 当前环境如遇 GPU 不可用", markdown)
        for run in MANUAL_PLAYTEST_RUNS:
            self.assertIn(f"### {run.run_id}", markdown)
            self.assertIn(f"python3 harness/playtest/run_current_manual_playtest.py {run.run_id}", markdown)

    def test_manual_review_cli_tools_write_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            draft = root / "draft.json"
            status_report = root / "status.json"
            status_markdown = root / "status.md"
            worksheet = root / "worksheet.md"

            draft_result = subprocess.run(
                [sys.executable, str(MANUAL_DRAFT_SCRIPT), "--out", str(draft)],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(draft_result.returncode, 0, draft_result.stderr)
            self.assertEqual(json.loads(draft.read_text(encoding="utf-8"))["candidate_id"], CANDIDATE_ID)

            status_result = subprocess.run(
                [
                    sys.executable,
                    str(MANUAL_STATUS_SCRIPT),
                    "--allow-incomplete",
                    "--draft",
                    str(draft.relative_to(REPO_ROOT) if draft.is_relative_to(REPO_ROOT) else draft),
                    "--report",
                    str(status_report),
                    "--markdown",
                    str(status_markdown),
                ],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(status_result.returncode, 0, status_result.stderr)
            self.assertEqual(json.loads(status_report.read_text(encoding="utf-8"))["decision"], "manual_playtest_incomplete")
            self.assertIn("# v51 Manual Playtest Status", status_markdown.read_text(encoding="utf-8"))

            worksheet_result = subprocess.run(
                [sys.executable, str(WORKSHEET_SCRIPT), "--out", str(worksheet)],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(worksheet_result.returncode, 0, worksheet_result.stderr)
            self.assertIn("# v51 人工审查表", worksheet.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
