#!/usr/bin/env python3
"""Regression tests for materializing partial content candidates.

Run with:
    python3 tools/test_materialize_content_candidate_pack.py
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
MATERIALIZER = SCRIPT_DIR / "materialize_content_candidate_pack.py"

sys.path.insert(0, str(SCRIPT_DIR))

from materialize_content_candidate_pack import CONTENT_CATEGORIES, materialize_pack  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def make_base_content(root: Path) -> Path:
    base = root / "base_demo"
    for category in CONTENT_CATEGORIES:
        (base / category).mkdir(parents=True, exist_ok=True)
    write_json(base / "passives" / "big-candy-jar.json", {"id": "big-candy-jar"})
    write_json(base / "enemies" / "bouncy-gummy.json", {"id": "bouncy-gummy"})
    write_json(base / "characters" / "jar-keeper.json", {"id": "jar-keeper"})
    return base


def make_patch(root: Path, *, duplicate_passive: bool = False) -> Path:
    patch = root / "patch"
    passive_id = "big-candy-jar" if duplicate_passive else "honey-heart"
    write_json(
        patch / "metadata" / "manifest.json",
        {
            "batch_id": "patch",
            "candidate_kind": "partial_content_patch",
            "project_rules": {
                "candidate_only": True,
                "accepted_content": False,
                "runtime_integrated": False,
            },
        },
    )
    write_json(patch / "passives" / f"{passive_id}.json", {"id": passive_id})
    write_json(patch / "enemies" / "licorice-skipper.json", {"id": "licorice-skipper"})
    write_json(patch / "waves" / "frosting-grassland-standard.json", {"id": "frosting-grassland-standard"})
    return patch


class MaterializeContentCandidatePackTests(unittest.TestCase):
    def test_materializes_base_plus_patch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            base = make_base_content(root)
            patch = make_patch(root)
            output = root / "generated_candidates" / "full-pack"

            report = materialize_pack(patch, base, output, allow_overrides=False)

            self.assertEqual(report["overlay_counts"], {"enemies": 1, "passives": 1, "waves": 1})
            self.assertEqual(report["overridden_counts"], {"enemies": 0, "passives": 0, "waves": 0})
            self.assertTrue((output / "passives" / "big-candy-jar.json").exists())
            self.assertTrue((output / "passives" / "honey-heart.json").exists())
            self.assertTrue((output / "enemies" / "bouncy-gummy.json").exists())
            self.assertTrue((output / "enemies" / "licorice-skipper.json").exists())
            self.assertTrue((output / "metadata" / "materialization.json").exists())

    def test_duplicate_overlay_requires_explicit_override(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            base = make_base_content(root)
            patch = make_patch(root, duplicate_passive=True)
            output = root / "generated_candidates" / "full-pack"

            with self.assertRaises(ValueError):
                materialize_pack(patch, base, output, allow_overrides=False)
            self.assertFalse(output.exists())

    def test_cli_writes_report_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            base = make_base_content(root)
            patch = make_patch(root)
            output = root / "generated_candidates" / "full-pack"
            report_path = root / "report.json"
            markdown_path = root / "summary.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(MATERIALIZER),
                    str(patch),
                    "--base-content-dir",
                    str(base),
                    "--output-dir",
                    str(output),
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
            self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["overlay_counts"]["passives"], 1)
            self.assertIn("Materialized Content Candidate Pack", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
