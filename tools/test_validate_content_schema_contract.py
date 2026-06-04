#!/usr/bin/env python3
"""Regression tests for content schema contract validation.

Run with:
    python3 tools/test_validate_content_schema_contract.py
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
VALIDATOR = SCRIPT_DIR / "validate_content_schema_contract.py"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_content_schema_contract import CONTENT_CATEGORIES, build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def make_schema_fixture(root: Path) -> Path:
    schema_dir = root / "schemas"
    categories = {category: f"{category}.schema.json" for category in CONTENT_CATEGORIES}
    write_json(
        schema_dir / "manifest.json",
        {
            "schema_version": 1,
            "draft": "https://json-schema.org/draft/2020-12/schema",
            "categories": categories,
        },
    )
    for category in CONTENT_CATEGORIES:
        write_json(
            schema_dir / f"{category}.schema.json",
            {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
                "additionalProperties": True,
                "required": ["id", "name", "version"],
                "properties": {
                    "id": {"type": "string", "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$"},
                    "name": {"type": "string", "minLength": 1},
                    "version": {"type": "integer", "minimum": 1},
                    "kind": {"type": "string", "enum": ["fixture"]},
                },
            },
        )
    return schema_dir / "manifest.json"


def make_content_fixture(root: Path) -> Path:
    content_dir = root / "content"
    for category in CONTENT_CATEGORIES:
        write_json(
            content_dir / category / f"{category}-fixture.json",
            {
                "id": f"{category}-fixture",
                "name": f"{category} fixture",
                "version": 1,
                "kind": "fixture",
            },
        )
    return content_dir


class ContentSchemaContractValidatorTests(unittest.TestCase):
    def test_valid_fixture_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            schema_manifest = make_schema_fixture(root)
            content_dir = make_content_fixture(root)

            report = build_report(schema_manifest, [content_dir])

            self.assertEqual(report["decision"], "content_schema_contract_valid")
            self.assertEqual(report["schema_count"], len(CONTENT_CATEGORIES))

    def test_missing_required_field_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            schema_manifest = make_schema_fixture(root)
            content_dir = make_content_fixture(root)
            target = content_dir / "weapons" / "weapons-fixture.json"
            payload = json.loads(target.read_text(encoding="utf-8"))
            del payload["name"]
            write_json(target, payload)

            report = build_report(schema_manifest, [content_dir])

            self.assertEqual(report["decision"], "content_schema_contract_invalid")
            self.assertTrue(any("missing required `name`" in error for error in report["errors"]))

    def test_enum_violation_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            schema_manifest = make_schema_fixture(root)
            content_dir = make_content_fixture(root)
            target = content_dir / "events" / "events-fixture.json"
            payload = json.loads(target.read_text(encoding="utf-8"))
            payload["kind"] = "wrong"
            write_json(target, payload)

            report = build_report(schema_manifest, [content_dir])

            self.assertEqual(report["decision"], "content_schema_contract_invalid")
            self.assertTrue(any("not in enum" in error for error in report["errors"]))

    def test_missing_cross_file_reference_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            schema_manifest = make_schema_fixture(root)
            content_dir = make_content_fixture(root)
            target = content_dir / "characters" / "characters-fixture.json"
            payload = json.loads(target.read_text(encoding="utf-8"))
            payload["initial_loadout"] = {
                "weapons": ["missing-weapon"],
                "passives": ["passives-fixture"],
            }
            write_json(target, payload)

            report = build_report(schema_manifest, [content_dir])

            self.assertEqual(report["decision"], "content_schema_contract_invalid")
            self.assertTrue(any("references missing weapons id `missing-weapon`" in error for error in report["errors"]))

    def test_wave_timing_and_pool_semantics_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            schema_manifest = make_schema_fixture(root)
            content_dir = make_content_fixture(root)
            target = content_dir / "waves" / "waves-fixture.json"
            payload = json.loads(target.read_text(encoding="utf-8"))
            payload.update(
                {
                    "map_id": "maps-fixture",
                    "duration_seconds": 60,
                    "segments": [
                        {
                            "start_second": 30,
                            "end_second": 10,
                            "enemy_pool": [{"enemy_id": "missing-enemy", "weight": 1.0}],
                        }
                    ],
                    "boss_events": [{"time_second": 90, "boss_id": "missing-boss"}],
                }
            )
            write_json(target, payload)

            report = build_report(schema_manifest, [content_dir])

            self.assertEqual(report["decision"], "content_schema_contract_invalid")
            self.assertTrue(any("start_second 30 must be before end_second 10" in error for error in report["errors"]))
            self.assertTrue(any("references missing enemies id `missing-enemy`" in error for error in report["errors"]))
            self.assertTrue(any("references missing bosses id `missing-boss`" in error for error in report["errors"]))
            self.assertTrue(any("time_second 90 exceeds duration_seconds 60" in error for error in report["errors"]))

    def test_spawn_hazard_forward_lane_semantics_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            schema_manifest = make_schema_fixture(root)
            content_dir = make_content_fixture(root)
            target = content_dir / "events" / "events-fixture.json"
            payload = json.loads(target.read_text(encoding="utf-8"))
            payload["effects"] = [
                {
                    "type": "spawn_hazard",
                    "value": 2,
                    "duration_seconds": 3,
                    "placement": "player_forward_lane",
                    "min_distance": 80,
                    "max_distance": 160,
                    "lane_width": 40,
                }
            ]
            write_json(target, payload)

            report = build_report(schema_manifest, [content_dir])

            self.assertEqual(report["decision"], "content_schema_contract_valid")

    def test_spawn_hazard_bad_placement_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            schema_manifest = make_schema_fixture(root)
            content_dir = make_content_fixture(root)
            target = content_dir / "events" / "events-fixture.json"
            payload = json.loads(target.read_text(encoding="utf-8"))
            payload["effects"] = [
                {
                    "type": "spawn_hazard",
                    "value": 2,
                    "duration_seconds": 3,
                    "placement": "diagonal_soup",
                }
            ]
            write_json(target, payload)

            report = build_report(schema_manifest, [content_dir])

            self.assertEqual(report["decision"], "content_schema_contract_invalid")
            self.assertTrue(any("diagonal_soup" in error for error in report["errors"]))

    def test_evolution_level_semantics_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            schema_manifest = make_schema_fixture(root)
            content_dir = make_content_fixture(root)
            weapon_path = content_dir / "weapons" / "weapons-fixture.json"
            weapon = json.loads(weapon_path.read_text(encoding="utf-8"))
            weapon["scaling"] = {"max_level": 3}
            write_json(weapon_path, weapon)
            passive_path = content_dir / "passives" / "passives-fixture.json"
            passive = json.loads(passive_path.read_text(encoding="utf-8"))
            passive["max_level"] = 2
            write_json(passive_path, passive)
            evolution_path = content_dir / "evolutions" / "evolutions-fixture.json"
            evolution = json.loads(evolution_path.read_text(encoding="utf-8"))
            evolution.update(
                {
                    "requirements": {
                        "weapon": {"id": "weapons-fixture", "min_level": 5},
                        "passive": {"id": "passives-fixture", "min_level": 4},
                    },
                    "replaces_weapon": "other-weapon",
                }
            )
            write_json(evolution_path, evolution)

            report = build_report(schema_manifest, [content_dir])

            self.assertEqual(report["decision"], "content_schema_contract_invalid")
            self.assertTrue(any("must match requirements.weapon.id" in error for error in report["errors"]))
            self.assertTrue(any("weapon `weapons-fixture` max_level 3" in error for error in report["errors"]))
            self.assertTrue(any("passive `passives-fixture` max_level 2" in error for error in report["errors"]))

    def test_cli_writes_report_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            schema_manifest = make_schema_fixture(root)
            content_dir = make_content_fixture(root)
            report_path = root / "report.json"
            markdown_path = root / "summary.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(content_dir),
                    "--schema-manifest",
                    str(schema_manifest),
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
            self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["decision"], "content_schema_contract_valid")
            self.assertIn("Content Schema Contract Validation", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
