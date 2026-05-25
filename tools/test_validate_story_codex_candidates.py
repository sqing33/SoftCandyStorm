#!/usr/bin/env python3
"""Regression tests for story/codex candidate validation.

Run with:
    python3 tools/test_validate_story_codex_candidates.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
VALIDATOR = SCRIPT_DIR / "validate_story_codex_candidates.py"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_story_codex_candidates import build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def make_base_content(root: Path) -> Path:
    base_dir = root / "content" / "base_demo"
    for category, item_id in (
        ("maps", "frosting-grassland"),
        ("bosses", "runaway-sugar-mixer"),
        ("characters", "jar-keeper"),
        ("enemies", "bouncy-gummy"),
    ):
        write_json(base_dir / category / f"{item_id}.json", {"id": item_id, "name": item_id})
    return base_dir


def make_candidate(
    root: Path,
    *,
    missing_unlock: bool = False,
    runtime_integrated: bool = False,
    forbidden_term: bool = False,
    bad_reference: bool = False,
) -> Path:
    candidate_dir = root / "2026-05-26_story_fixture"
    write_json(
        candidate_dir / "metadata" / "manifest.json",
        {
            "batch_id": candidate_dir.name,
            "candidate_kind": "story_codex_seed_pack",
            "generated_at": "2026-05-26",
            "source_docs": [
                "docs/03_世界观与剧情大纲.md",
                "docs/10_AI内容生成流水线.md",
                "docs/18_完整游戏流程与局外成长.md",
            ],
            "base_content_dir": "content/base_demo",
            "content_counts": {
                "chapters": 1,
                "codex_entries": 2,
            },
            "project_rules": {
                "candidate_only": True,
                "accepted_content": False,
                "runtime_integrated": runtime_integrated,
                "required_next_steps": [
                    "validate_story_codex_candidates",
                    "manual_lore_review",
                ],
            },
        },
    )
    (candidate_dir / "README.md").write_text("# Story Fixture\n", encoding="utf-8")
    write_json(
        candidate_dir / "chapters" / "frosting-grassland.json",
        {
            "id": "frosting-grassland",
            "title": "第一章：糖霜草地",
            "map_id": "unknown-map" if bad_reference else "frosting-grassland",
            "boss_id": "runaway-sugar-mixer",
            "theme": "混乱刚刚开始",
            "unlock_summary": "默认解锁，守护员第一次巡逻糖霜草地。",
            "pre_run_lines": [
                "糖霜草地今天太安静了。",
                "如果软糖怪追过来，就先把它们请回糖罐里。",
            ],
            "boss_intro_line": "那台搅糖机不是生气，它只是停不下来。",
            "completion_summary": "主角找回第一片糖罐星碎片，也确认风暴不是普通天气。",
            "codex_unlocks": ["world-sugar-jar-stars"] if missing_unlock else [
                "world-sugar-jar-stars",
                "enemy-bouncy-gummy",
            ],
        },
    )
    entry_text = "每颗糖罐星都装着一天的快乐。"
    if forbidden_term:
        entry_text = "这段故事突然变成 horror blood zombie。"
    write_json(
        candidate_dir / "codex" / "world-sugar-jar-stars.json",
        {
            "id": "world-sugar-jar-stars",
            "category": "world",
            "title": "糖罐星",
            "related_ids": ["frosting-grassland"],
            "unlock_hint": "找回第一片糖罐星碎片。",
            "entry": entry_text,
            "tone_tags": ["cute", "lore"],
        },
    )
    write_json(
        candidate_dir / "codex" / "enemy-bouncy-gummy.json",
        {
            "id": "enemy-bouncy-gummy",
            "category": "enemy",
            "title": "蹦蹦软糖",
            "related_ids": ["bouncy-gummy"],
            "unlock_hint": "第一次遇见蹦蹦软糖。",
            "entry": "最常见的风暴软糖，只是不知道该把多出来的开心往哪里放。",
            "tone_tags": ["enemy", "basic"],
        },
    )
    return candidate_dir


class StoryCodexCandidateValidatorTests(unittest.TestCase):
    def test_valid_story_codex_candidate_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            base_dir = make_base_content(root)
            candidate = make_candidate(root)
            report = build_report(candidate, base_content_dir=base_dir)

            self.assertEqual(report["decision"], "story_codex_candidates_valid")
            self.assertEqual(report["candidate_count"], 1)
            self.assertEqual(report["chapter_count"], 1)
            self.assertEqual(report["codex_entry_count"], 2)

    def test_missing_codex_unlock_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            base_dir = make_base_content(root)
            candidate = make_candidate(root, missing_unlock=True)
            (candidate / "codex" / "world-sugar-jar-stars.json").unlink()
            report = build_report(candidate, base_content_dir=base_dir)

            self.assertEqual(report["decision"], "story_codex_candidates_invalid")
            self.assertTrue(any("codex_unlock" in error for error in report["errors"]))
            self.assertTrue(any("manifest expects 2 codex entries" in error for error in report["errors"]))

    def test_runtime_integrated_candidate_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            base_dir = make_base_content(root)
            candidate = make_candidate(root, runtime_integrated=True)
            report = build_report(candidate, base_content_dir=base_dir)

            self.assertEqual(report["decision"], "story_codex_candidates_invalid")
            self.assertTrue(any("runtime_integrated" in error for error in report["errors"]))

    def test_bad_base_reference_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            base_dir = make_base_content(root)
            candidate = make_candidate(root, bad_reference=True)
            report = build_report(candidate, base_content_dir=base_dir)

            self.assertEqual(report["decision"], "story_codex_candidates_invalid")
            self.assertTrue(any("map_id `unknown-map`" in error for error in report["errors"]))

    def test_forbidden_terms_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            base_dir = make_base_content(root)
            candidate = make_candidate(root, forbidden_term=True)
            report = build_report(candidate, base_content_dir=base_dir)

            self.assertEqual(report["decision"], "story_codex_candidates_invalid")
            self.assertTrue(any("forbidden theme term" in error for error in report["errors"]))

    def test_cli_writes_report_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            base_dir = make_base_content(root)
            candidate = make_candidate(root)
            report_path = root / "story_report.json"
            markdown_path = root / "summary.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(candidate),
                    "--base-content-dir",
                    str(base_dir),
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
            self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["decision"], "story_codex_candidates_valid")
            self.assertIn("Story Codex Candidate Validation", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
