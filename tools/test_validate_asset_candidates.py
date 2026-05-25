#!/usr/bin/env python3
"""Regression tests for generated asset candidate metadata validation.

Run with:
    python3 tools/test_validate_asset_candidates.py
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
VALIDATOR = SCRIPT_DIR / "validate_asset_candidates.py"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_asset_candidates import build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def make_batch(root: Path, *, runtime_integrated: bool = False, with_commands: bool = True) -> Path:
    batch_dir = root / "2026-05-26_mmx_fixture_pass"
    (batch_dir / "images").mkdir(parents=True)
    (batch_dir / "metadata").mkdir(parents=True)
    (batch_dir / "images" / "sprite.png").write_bytes(b"fixture image")
    (batch_dir / "README.md").write_text("# Fixture\n", encoding="utf-8")
    (batch_dir / "metadata" / "review_2026-05-26.md").write_text("# Review\n", encoding="utf-8")
    manifest = {
        "batch_id": batch_dir.name,
        "generated_at": "2026-05-26",
        "generator": {
            "tool": "mmx-cli",
            "auth_method": "api-key",
            "source": "test fixture",
        },
        "project_rules": {
            "candidate_only": True,
            "accepted_content": False,
            "runtime_integrated": runtime_integrated,
            "required_next_steps": ["human review"],
        },
        "assets": [
            {
                "id": "sprite_fixture",
                "type": "image",
                "path": "images/sprite.png",
                "format": "png",
                "prompt": "cute candy sprite fixture",
                "qa_status": "needs_review",
                "qa_notes": ["fixture note"],
            }
        ],
    }
    if with_commands:
        manifest["commands"] = ["mmx image generate --prompt <fixture> --out images/sprite.png"]
    write_json(batch_dir / "metadata" / "manifest.json", manifest)
    return batch_dir


class AssetCandidateValidatorTests(unittest.TestCase):
    def test_valid_fixture_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            make_batch(root)
            report = build_report(root, require_commands=True)

            self.assertEqual(report["decision"], "asset_candidates_valid")
            self.assertEqual(report["batch_count"], 1)
            self.assertEqual(report["asset_count"], 1)
            self.assertEqual(report["errors"], [])

    def test_runtime_integrated_candidate_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            make_batch(root, runtime_integrated=True)
            report = build_report(root, require_commands=True)

            self.assertEqual(report["decision"], "asset_candidates_invalid")
            self.assertTrue(any("runtime_integrated" in error for error in report["errors"]))

    def test_require_commands_turns_missing_mmx_commands_into_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            make_batch(root, with_commands=False)

            permissive_report = build_report(root, require_commands=False)
            strict_report = build_report(root, require_commands=True)

            self.assertEqual(permissive_report["decision"], "asset_candidates_valid")
            self.assertTrue(any("generation commands" in warning for warning in permissive_report["warnings"]))
            self.assertEqual(strict_report["decision"], "asset_candidates_invalid")
            self.assertTrue(any("generation commands" in error for error in strict_report["errors"]))

    def test_cli_writes_report_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "candidates"
            make_batch(root)
            report_path = Path(temp_dir) / "report.json"
            markdown_path = Path(temp_dir) / "summary.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(root),
                    "--require-commands",
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
            self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["decision"], "asset_candidates_valid")
            self.assertIn("Asset Candidate Metadata Validation", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
