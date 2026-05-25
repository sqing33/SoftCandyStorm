#!/usr/bin/env python3
"""Regression tests for materialized content pack preflight validation.

Run with:
    python3 tools/test_validate_materialized_content_pack.py
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
VALIDATOR = SCRIPT_DIR / "validate_materialized_content_pack.py"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_materialized_content_pack import CONTENT_CATEGORIES, build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def candidate_rules(*, runtime_integrated: bool = False) -> dict:
    return {
        "candidate_only": True,
        "accepted_content": False,
        "runtime_integrated": runtime_integrated,
        "required_next_steps": ["game_harness validate-candidates", "human review"],
    }


def make_full_pack(
    root: Path,
    *,
    bad_wave_enemy_ref: bool = False,
    runtime_integrated: bool = False,
    wrong_count: bool = False,
) -> Path:
    pack = root / "2026-05-26_fixture_full_pack"
    source_patch = root / "patches" / "fixture_patch"
    write_json(
        source_patch / "metadata" / "manifest.json",
        {
            "batch_id": "fixture_patch",
            "generated_at": "2026-05-26",
            "project_rules": candidate_rules(),
        },
    )
    write_json(
        pack / "characters" / "jar-keeper.json",
        {
            "id": "jar-keeper",
            "name": "Jar Keeper",
            "version": 1,
            "description": "Starter character.",
            "initial_loadout": {"weapons": ["rainbow-candy-shot"], "passives": ["big-candy-jar"]},
        },
    )
    write_json(
        pack / "weapons" / "rainbow-candy-shot.json",
        {"id": "rainbow-candy-shot", "name": "Rainbow Candy Shot", "version": 1, "description": "Starter shot."},
    )
    write_json(
        pack / "passives" / "big-candy-jar.json",
        {"id": "big-candy-jar", "name": "Big Candy Jar", "version": 1, "description": "More health."},
    )
    write_json(
        pack / "evolutions" / "rainbow-candy-meteor.json",
        {
            "id": "rainbow-candy-meteor",
            "name": "Rainbow Candy Meteor",
            "version": 1,
            "description": "Evolution.",
            "requirements": {
                "weapon": {"id": "rainbow-candy-shot", "min_level": 5},
                "passive": {"id": "big-candy-jar", "min_level": 3},
            },
            "replaces_weapon": "rainbow-candy-shot",
        },
    )
    write_json(
        pack / "enemies" / "bouncy-gummy.json",
        {"id": "bouncy-gummy", "name": "Bouncy Gummy", "version": 1, "description": "Basic enemy."},
    )
    write_json(
        pack / "bosses" / "runaway-sugar-mixer.json",
        {"id": "runaway-sugar-mixer", "name": "Runaway Sugar Mixer", "version": 1, "description": "Boss."},
    )
    write_json(
        pack / "maps" / "frosting-grassland.json",
        {"id": "frosting-grassland", "name": "Frosting Grassland", "version": 1, "description": "Map."},
    )
    write_json(
        pack / "events" / "rainbow-candy-rush.json",
        {"id": "rainbow-candy-rush", "name": "Rainbow Candy Rush", "version": 1, "description": "Event."},
    )
    enemy_ref = "missing-gummy" if bad_wave_enemy_ref else "bouncy-gummy"
    write_json(
        pack / "waves" / "frosting-grassland-standard.json",
        {
            "id": "frosting-grassland-standard",
            "name": "Frosting Grassland Standard",
            "version": 1,
            "map_id": "frosting-grassland",
            "segments": [
                {
                    "start_second": 0,
                    "end_second": 60,
                    "enemy_pool": [{"enemy_id": enemy_ref, "weight": 1.0}],
                }
            ],
            "boss_events": [{"time_second": 60, "boss_id": "runaway-sugar-mixer"}],
        },
    )
    (pack / "README.md").write_text("# Fixture Full Pack\n", encoding="utf-8")

    content_counts = {category: 1 for category in CONTENT_CATEGORIES}
    if wrong_count:
        content_counts["weapons"] = 2
    write_json(
        pack / "metadata" / "manifest.json",
        {
            "batch_id": pack.name,
            "candidate_kind": "full_content_pack",
            "generated_at": "2026-05-26",
            "source_patch": source_patch.name,
            "base_content_dir": "content/base_demo",
            "project_rules": candidate_rules(runtime_integrated=runtime_integrated),
            "content_counts": content_counts,
        },
    )
    write_json(
        pack / "metadata" / "materialization.json",
        {
            "source_patch": str(source_patch),
            "base_content_dir": "content/base_demo",
            "output_dir": str(pack),
            "copied_counts": content_counts if not wrong_count else {category: 1 for category in CONTENT_CATEGORIES},
            "overlay_counts": {},
            "project_rules": candidate_rules(),
        },
    )
    write_json(pack / "metadata" / "source_patch_manifest.json", load_json(source_patch / "metadata" / "manifest.json"))
    return pack


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class MaterializedContentPackValidatorTests(unittest.TestCase):
    def test_valid_materialized_pack_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "generated_candidates"
            make_full_pack(root)

            report = build_report(root)

            self.assertEqual(report["decision"], "materialized_content_packs_valid")
            self.assertEqual(report["candidate_count"], 1)
            self.assertEqual(report["content_count"], len(CONTENT_CATEGORIES))

    def test_unknown_wave_enemy_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "generated_candidates"
            make_full_pack(root, bad_wave_enemy_ref=True)

            report = build_report(root)

            self.assertEqual(report["decision"], "materialized_content_packs_invalid")
            self.assertTrue(any("unknown enemy" in error for error in report["errors"]))

    def test_runtime_integrated_manifest_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "generated_candidates"
            make_full_pack(root, runtime_integrated=True)

            report = build_report(root)

            self.assertEqual(report["decision"], "materialized_content_packs_invalid")
            self.assertTrue(any("runtime_integrated" in error for error in report["errors"]))

    def test_manifest_count_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "generated_candidates"
            make_full_pack(root, wrong_count=True)

            report = build_report(root)

            self.assertEqual(report["decision"], "materialized_content_packs_invalid")
            self.assertTrue(any("content_counts.weapons" in error for error in report["errors"]))

    def test_cli_writes_report_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "generated_candidates"
            make_full_pack(root)
            report_path = Path(temp_dir) / "report.json"
            markdown_path = Path(temp_dir) / "summary.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(root),
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
                "materialized_content_packs_valid",
            )
            self.assertIn("Materialized Content Pack Preflight", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
