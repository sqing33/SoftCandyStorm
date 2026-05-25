#!/usr/bin/env python3
"""Regression tests for Phase 4 roster target validation.

Run with:
    python3 tools/test_validate_phase4_roster_targets.py
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
VALIDATOR = SCRIPT_DIR / "validate_phase4_roster_targets.py"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_phase4_roster_targets import CATEGORY_REQUIRED_FIELDS, COUNT_TARGETS, EXPECTED_IDS, build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def make_payload(category: str, item_id: str) -> dict:
    payload = {"id": item_id}
    for field in CATEGORY_REQUIRED_FIELDS[category]:
        if field == "name":
            payload[field] = item_id
        elif field == "version":
            payload[field] = 1
        elif field in {"base_stats", "targeting", "scaling", "balance_budget", "requirements", "weapon_definition", "stats", "behavior", "spawn_budget", "size", "spawn_rules", "pressure_budget"}:
            payload[field] = {"fixture": True}
        elif field in {"initial_loadout"}:
            payload[field] = {"weapons": ["rainbow-candy-shot"], "passives": ["big-candy-jar"]}
        elif field in {"stat_modifiers", "phases", "segments", "boss_events"}:
            payload[field] = [{"fixture": True}]
        elif field == "map_id":
            payload[field] = "frosting-grassland"
        elif field == "duration_seconds":
            payload[field] = 600
        elif field == "replaces_weapon":
            payload[field] = "rainbow-candy-shot"
        elif field == "type":
            payload[field] = "projectile"
        elif field == "max_level":
            payload[field] = 5
        else:
            payload[field] = f"{field} for {item_id}"

    if category == "evolutions":
        payload["requirements"] = {
            "weapon": {"id": "rainbow-candy-shot", "min_level": 5},
            "passive": {"id": "big-candy-jar", "min_level": 3},
        }
    if category == "waves":
        payload["segments"] = [{"enemy_pool": [{"enemy_id": "bouncy-gummy", "weight": 1.0}]}]
        payload["boss_events"] = [{"boss_id": "runaway-sugar-mixer", "time_second": 60}]
    return payload


def make_valid_pack(root: Path) -> Path:
    pack = root / "content_pack"
    for category, ids in EXPECTED_IDS.items():
        all_ids = set(ids)
        index = 0
        while len(all_ids) < COUNT_TARGETS[category]:
            all_ids.add(f"extra-{category}-{index}")
            index += 1
        for item_id in sorted(all_ids):
            write_json(pack / category / f"{item_id}.json", make_payload(category, item_id))
    return pack


class Phase4RosterTargetValidatorTests(unittest.TestCase):
    def test_valid_pack_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pack = make_valid_pack(Path(temp_dir))

            report = build_report(pack)

            self.assertEqual(report["decision"], "phase4_roster_targets_valid")
            self.assertFalse(report["errors"])

    def test_missing_docs_roster_id_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pack = make_valid_pack(Path(temp_dir))
            (pack / "characters" / "jar-keeper.json").unlink()

            report = build_report(pack)

            self.assertEqual(report["decision"], "phase4_roster_targets_invalid")
            self.assertTrue(any("jar-keeper" in error for error in report["errors"]))

    def test_below_phase4_count_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pack = make_valid_pack(Path(temp_dir))
            for path in sorted((pack / "passives").glob("extra-passives-*.json")):
                path.unlink()

            report = build_report(pack)

            self.assertEqual(report["decision"], "phase4_roster_targets_invalid")
            self.assertTrue(any("passives count" in error for error in report["errors"]))

    def test_unknown_wave_reference_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pack = make_valid_pack(Path(temp_dir))
            wave_path = pack / "waves" / "frosting-grassland-standard.json"
            payload = json.loads(wave_path.read_text(encoding="utf-8"))
            payload["segments"][0]["enemy_pool"][0]["enemy_id"] = "missing-enemy"
            write_json(wave_path, payload)

            report = build_report(pack)

            self.assertEqual(report["decision"], "phase4_roster_targets_invalid")
            self.assertTrue(any("missing-enemy" in error for error in report["errors"]))

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
            self.assertEqual(
                json.loads(report_path.read_text(encoding="utf-8"))["decision"],
                "phase4_roster_targets_valid",
            )
            self.assertIn("Phase 4 Roster Target Validation", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
