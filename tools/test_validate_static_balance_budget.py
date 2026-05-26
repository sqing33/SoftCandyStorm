#!/usr/bin/env python3
"""Regression tests for static balance budget validation.

Run with:
    python3 tools/test_validate_static_balance_budget.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "tools" / "validate_static_balance_budget.py"

sys.path.insert(0, str(REPO_ROOT / "tools"))

from validate_static_balance_budget import build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def make_valid_pack(root: Path) -> Path:
    pack = root / "content" / "fixture_pack"
    write_json(
        pack / "weapons" / "rainbow-candy-shot.json",
        {
            "id": "rainbow-candy-shot",
            "base_stats": {
                "damage": 12,
                "cooldown_ms": 600,
                "projectile_count": 1,
                "area_radius": 12,
            },
            "balance_budget": {
                "role": "starter",
                "single_target_dps": 20,
                "group_dps": 14,
                "performance_cost": "low",
            },
        },
    )
    write_json(
        pack / "enemies" / "bouncy-gummy.json",
        {
            "id": "bouncy-gummy",
            "stats": {
                "health": 18,
                "move_speed": 60,
                "contact_damage_per_second": 4.5,
                "xp_value": 2,
            },
            "spawn_budget": {
                "threat": 1.0,
                "performance_cost": 1.0,
            },
        },
    )
    write_json(
        pack / "bosses" / "runaway-sugar-mixer.json",
        {
            "id": "runaway-sugar-mixer",
            "stats": {
                "health": 900,
                "move_speed": 38,
                "contact_damage_per_second": 20,
                "xp_value": 80,
            },
        },
    )
    write_json(
        pack / "waves" / "frosting-grassland-standard.json",
        {
            "id": "frosting-grassland-standard",
            "segments": [
                {
                    "start_second": 0,
                    "end_second": 90,
                    "spawn_interval_ms": 1250,
                    "spawn_count": 1,
                    "max_alive": 35,
                    "enemy_pool": [{"enemy_id": "bouncy-gummy", "weight": 1.0}],
                }
            ],
        },
    )
    return pack


class StaticBalanceBudgetValidatorTests(unittest.TestCase):
    def test_valid_fixture_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pack = make_valid_pack(Path(temp_dir))
            report = build_report(pack)

            self.assertEqual(report["decision"], "static_balance_budget_valid")
            self.assertEqual(report["errors"], [])

    def test_weapon_dps_outside_budget_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pack = make_valid_pack(Path(temp_dir))
            weapon_path = pack / "weapons" / "rainbow-candy-shot.json"
            weapon = json.loads(weapon_path.read_text(encoding="utf-8"))
            weapon["base_stats"]["damage"] = 40
            write_json(weapon_path, weapon)

            report = build_report(pack)

            self.assertEqual(report["decision"], "static_balance_budget_invalid")
            self.assertTrue(any("weapon `rainbow-candy-shot` failed static budget" in error for error in report["errors"]))

    def test_enemy_speed_damage_pressure_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pack = make_valid_pack(Path(temp_dir))
            enemy_path = pack / "enemies" / "bouncy-gummy.json"
            enemy = json.loads(enemy_path.read_text(encoding="utf-8"))
            enemy["stats"]["move_speed"] = 100
            enemy["stats"]["contact_damage_per_second"] = 9
            write_json(enemy_path, enemy)

            report = build_report(pack)

            self.assertEqual(report["decision"], "static_balance_budget_invalid")
            self.assertTrue(any("speed_damage_pressure" in error for error in report["errors"]))

    def test_wave_pressure_and_unknown_enemy_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pack = make_valid_pack(Path(temp_dir))
            wave_path = pack / "waves" / "frosting-grassland-standard.json"
            wave = json.loads(wave_path.read_text(encoding="utf-8"))
            wave["segments"][0]["spawn_count"] = 10
            wave["segments"][0]["enemy_pool"].append({"enemy_id": "missing-enemy", "weight": 1.0})
            write_json(wave_path, wave)

            report = build_report(pack)

            self.assertEqual(report["decision"], "static_balance_budget_invalid")
            self.assertTrue(any("unknown enemy" in error for error in report["errors"]))

    def test_cli_writes_report_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            pack = make_valid_pack(root)
            report_path = root / "report.json"
            markdown_path = root / "summary.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(pack),
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
            self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["decision"], "static_balance_budget_valid")
            self.assertIn("Static Balance Budget Validation", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
