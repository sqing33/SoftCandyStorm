#!/usr/bin/env python3
"""Regression tests for partial generated content candidate validation.

Run with:
    python3 tools/test_validate_content_candidates.py
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
VALIDATOR = SCRIPT_DIR / "validate_content_candidates.py"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_content_candidates import build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def make_candidate(root: Path, *, duplicate_id: bool = False, runtime_integrated: bool = False) -> Path:
    candidate_dir = root / "2026-05-26_fixture_candidate"
    passive_id = "big-candy-jar" if duplicate_id else "honey-heart"
    write_json(
        candidate_dir / "metadata" / "manifest.json",
        {
            "batch_id": candidate_dir.name,
            "generated_at": "2026-05-26",
            "source_docs": ["docs/10_AI内容生成流水线.md", "docs/13_内容数据Schema设计.md"],
            "project_rules": {
                "candidate_only": True,
                "accepted_content": False,
                "runtime_integrated": runtime_integrated,
                "required_next_steps": ["schema validation", "static budget review", "human review"],
            },
        },
    )
    (candidate_dir / "README.md").write_text("# Fixture Candidate\n", encoding="utf-8")
    write_json(
        candidate_dir / "weapons" / "sugar-drum.json",
        {
            "id": "sugar-drum",
            "name": "糖鼓",
            "version": 1,
            "rarity": "common",
            "type": "burst",
            "tags": ["burst", "aoe", "rhythm"],
            "description": "按节拍敲出小范围糖波。",
            "targeting": {"mode": "self_centered", "range": 180},
            "base_stats": {
                "damage": 20,
                "cooldown_ms": 780,
                "projectile_speed": 0,
                "projectile_count": 1,
                "pierce": 0,
                "area_radius": 54,
                "duration_ms": 120,
            },
            "scaling": {
                "max_level": 5,
                "damage_per_level": 5,
                "cooldown_multiplier_per_level": 0.93,
                "range_per_level": 6,
                "area_per_level": 3,
                "projectile_count_bonus_levels": [4],
            },
            "balance_budget": {
                "role": "aoe-clear",
                "single_target_dps": 26,
                "group_dps": 54,
                "performance_cost": "medium",
            },
            "visual_description": "圆形糖鼓敲出粉色糖波。",
            "sfx_description": "轻快鼓点和糖屑弹跳声。",
            "unlock": {"type": "discover"},
        },
    )
    write_json(
        candidate_dir / "passives" / f"{passive_id}.json",
        {
            "id": passive_id,
            "name": "蜂蜜糖心",
            "version": 1,
            "rarity": "common",
            "tags": ["recovery", "defense"],
            "description": "缓慢恢复生命。",
            "stat_modifiers": [{"stat": "regen_per_second", "mode": "add", "value_per_level": 0.25}],
            "max_level": 5,
            "visual_description": "发光蜂蜜心形糖。",
            "sfx_description": "温暖糖浆滴落声。",
            "unlock": {"type": "discover"},
        },
    )
    write_json(
        candidate_dir / "evolutions" / "sugar-drum-crescendo.json",
        {
            "id": "sugar-drum-crescendo",
            "name": "糖鼓终曲",
            "version": 1,
            "rarity": "epic",
            "tags": ["burst", "aoe", "evolution"],
            "description": "糖鼓进化为连续扩散的终曲糖波。",
            "requirements": {
                "weapon": {"id": "sugar-drum", "min_level": 5},
                "passive": {"id": passive_id, "min_level": 3},
                "trigger": "boss_chest",
            },
            "replaces_weapon": "sugar-drum",
            "weapon_definition": {
                "type": "burst",
                "targeting": {"mode": "self_centered", "range": 260},
                "base_stats": {"damage": 48, "cooldown_ms": 920, "projectile_count": 3, "area_radius": 92},
            },
            "visual_description": "多圈糖波像节拍一样向外扩散。",
            "sfx_description": "层叠糖鼓终曲声。",
            "unlock": {"type": "discover"},
        },
    )
    write_json(
        candidate_dir / "enemies" / "licorice-skipper.json",
        {
            "id": "licorice-skipper",
            "name": "甘草跳跳",
            "version": 1,
            "family": "licorice",
            "rarity": "common",
            "tags": ["jump", "disruptor"],
            "description": "会短距离跳跃切入路线的甘草糖敌人。",
            "stats": {
                "health": 34,
                "move_speed": 72,
                "contact_damage_per_second": 5.5,
                "radius": 14,
                "xp_value": 4,
                "score_value": 12,
            },
            "behavior": {"type": "jump", "parameters": {"cooldown_seconds": 3.2}},
            "spawn_budget": {"threat": 1.7, "performance_cost": 1.1},
            "counterplay": "跳跃前会压低身体，横向移动可以躲开落点。",
            "visual_description": "细长甘草糖卷成弹簧状，顶部有糖粉。",
            "death_effect": "弹成几段小甘草糖。",
            "sfx_description": "有弹性的 twang 声。",
            "unlock": {"type": "discover"},
        },
    )
    write_json(
        candidate_dir / "waves" / "frosting-grassland-standard.json",
        {
            "id": "frosting-grassland-standard",
            "name": "糖霜草地候选波次",
            "version": 1,
            "map_id": "frosting-grassland",
            "duration_seconds": 600,
            "segments": [
                {
                    "start_second": 0,
                    "end_second": 90,
                    "spawn_interval_ms": 1250,
                    "spawn_count": 1,
                    "max_alive": 35,
                    "enemy_pool": [{"enemy_id": "bouncy-gummy", "weight": 1.0}],
                },
                {
                    "start_second": 90,
                    "end_second": 210,
                    "spawn_interval_ms": 1000,
                    "spawn_count": 2,
                    "max_alive": 50,
                    "enemy_pool": [{"enemy_id": "licorice-skipper", "weight": 0.2}, {"enemy_id": "bouncy-gummy", "weight": 0.8}],
                },
            ],
            "boss_events": [{"time_second": 210, "boss_id": "runaway-sugar-mixer"}],
            "pressure_budget": {"early": "low", "middle": "medium", "late": "high"},
        },
    )
    return candidate_dir


class ContentCandidateValidatorTests(unittest.TestCase):
    def test_valid_partial_candidate_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "generated_candidate_patches"
            candidate = make_candidate(root)
            report = build_report(candidate, base_content_dir=Path("content/base_demo"), allow_overrides=True)

            self.assertEqual(report["decision"], "content_candidates_valid")
            self.assertEqual(report["candidate_count"], 1)
            self.assertEqual(report["content_count"], 5)

    def test_duplicate_base_id_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "generated_candidate_patches"
            candidate = make_candidate(root, duplicate_id=True)
            report = build_report(candidate, base_content_dir=Path("content/base_demo"), allow_overrides=False)

            self.assertEqual(report["decision"], "content_candidates_invalid")
            self.assertTrue(any("duplicates base content id" in error for error in report["errors"]))

    def test_runtime_integrated_candidate_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "generated_candidate_patches"
            candidate = make_candidate(root, runtime_integrated=True)
            report = build_report(candidate, base_content_dir=Path("content/base_demo"), allow_overrides=False)

            self.assertEqual(report["decision"], "content_candidates_invalid")
            self.assertTrue(any("runtime_integrated" in error for error in report["errors"]))

    def test_cli_writes_report_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "generated_candidate_patches"
            candidate = make_candidate(root)
            report_path = Path(temp_dir) / "report.json"
            markdown_path = Path(temp_dir) / "summary.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(candidate),
                    "--base-content-dir",
                    "content/base_demo",
                    "--allow-overrides",
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
            self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["decision"], "content_candidates_valid")
            self.assertIn("Content Candidate Validation", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
