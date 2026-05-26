#!/usr/bin/env python3
"""Regression tests for GameCore API contract validation.

Run with:
    python3 tools/test_validate_gamecore_api_contract.py
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
VALIDATOR = SCRIPT_DIR / "validate_gamecore_api_contract.py"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_gamecore_api_contract import build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_source(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_fixture(root: Path, *, omit_field: bool = False, bad_policy: bool = False) -> Path:
    lib = root / "crates" / "game_core" / "src" / "lib.rs"
    movement_field = "" if omit_field else "    pub movement: Vec2,\n"
    write_source(
        lib,
        f"""
pub use math::Vec2;

pub struct RunConfig {{
    pub seed: u64,
}}

pub struct PlayerAction {{
{movement_field}    pub upgrade_choice: Option<usize>,
}}

pub struct GameCore {{}}

impl GameCore {{
    pub fn reset(config: RunConfig) -> Self {{ Self {{}} }}
    pub fn step(&mut self, action: PlayerAction) -> StepResult {{ todo!() }}
}}

pub struct StepResult {{
    pub snapshot: RunSnapshot,
}}

pub struct RunSnapshot {{
    pub time_seconds: f32,
}}

pub enum GameEvent {{
    EnemySpawned {{ entity_id: u64 }},
    RunEnded,
}}
""",
    )
    write_source(
        root / "crates" / "game_core" / "src" / "math.rs",
        """
pub struct Vec2 {
    pub x: f32,
    pub y: f32,
}

impl Vec2 {
    pub const fn new(x: f32, y: f32) -> Self { Self { x, y } }
}
""",
    )
    contract = root / "harness" / "interface_contract" / "fixture_contract.json"
    write_json(
        contract,
        {
            "contract_version": 1,
            "contract_id": "fixture-api",
            "ruleset_version": "fixture-v0",
            "status": "fixture",
            "summary": "Fixture contract",
            "source_files": {
                "lib": str(lib.relative_to(root)),
                "math": "crates/game_core/src/math.rs",
            },
            "compatibility_policy": {
                "breaking_change_requires_contract_bump": not bad_policy,
                "breaking_change_requires_migration_note": True,
                "breaking_change_requires_replay_compatibility_note": True,
                "runtime_must_not_mutate_game_state_directly": True,
                "harness_and_runtime_must_use_same_gamecore": True,
            },
            "public_structs": [
                {"file": "lib", "name": "RunConfig", "required_fields": ["seed"]},
                {"file": "lib", "name": "PlayerAction", "required_fields": ["movement", "upgrade_choice"]},
                {"file": "lib", "name": "GameCore", "required_methods": ["reset", "step"]},
                {"file": "lib", "name": "StepResult", "required_fields": ["snapshot"]},
                {"file": "lib", "name": "RunSnapshot", "required_fields": ["time_seconds"]},
                {"file": "math", "name": "Vec2", "required_fields": ["x", "y"], "required_methods": ["new"]},
            ],
            "public_enums": [
                {"file": "lib", "name": "GameEvent", "required_variants": ["EnemySpawned", "RunEnded"]},
            ],
            "reexports": [
                {"file": "lib", "symbols": ["Vec2"]},
            ],
            "known_gaps": ["fixture does not compile"],
        },
    )
    return contract


class GameCoreApiContractValidatorTests(unittest.TestCase):
    def test_valid_fixture_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            contract = make_fixture(root)
            report = build_report(contract, root)

            self.assertEqual(report["decision"], "gamecore_api_contract_valid")
            self.assertEqual(report["errors"], [])

    def test_missing_field_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            contract = make_fixture(root, omit_field=True)
            report = build_report(contract, root)

            self.assertEqual(report["decision"], "gamecore_api_contract_invalid")
            self.assertTrue(any("missing public field `movement`" in error for error in report["errors"]))

    def test_bad_compatibility_policy_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            contract = make_fixture(root, bad_policy=True)
            report = build_report(contract, root)

            self.assertEqual(report["decision"], "gamecore_api_contract_invalid")
            self.assertTrue(any("breaking_change_requires_contract_bump" in error for error in report["errors"]))

    def test_cli_writes_report_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            contract = make_fixture(root)
            report_path = root / "report.json"
            markdown_path = root / "summary.md"
            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(contract),
                    "--repo-root",
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
            self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["decision"], "gamecore_api_contract_valid")
            self.assertIn("GameCore API Contract Validation", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
