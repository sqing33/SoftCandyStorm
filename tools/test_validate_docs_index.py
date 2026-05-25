#!/usr/bin/env python3
"""Regression tests for docs index validation.

Run with:
    python3 tools/test_validate_docs_index.py
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
VALIDATOR = SCRIPT_DIR / "validate_docs_index.py"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_docs_index import EXPECTED_DOCS, build_report  # noqa: E402


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_docs_fixture(root: Path) -> None:
    docs_dir = root / "docs"
    for doc in EXPECTED_DOCS:
        if doc == "00_index.md":
            continue
        write_text(docs_dir / doc, f"# {doc}\n")
    links = "\n".join(f"- [{doc}](./{doc})" for doc in EXPECTED_DOCS if doc != "00_index.md")
    write_text(docs_dir / "00_index.md", f"# Index\n\n{links}\n")
    write_text(
        root / "AGENTS.md",
        " ".join(doc[:2] for doc in EXPECTED_DOCS) + "\n",
    )


class DocsIndexValidatorTests(unittest.TestCase):
    def test_valid_docs_fixture_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            make_docs_fixture(root)

            report = build_report(root)

            self.assertEqual(report["decision"], "docs_index_valid")
            self.assertEqual(report["doc_count"], len(EXPECTED_DOCS))

    def test_missing_doc_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            make_docs_fixture(root)
            (root / "docs" / "18_完整游戏流程与局外成长.md").unlink()

            report = build_report(root)

            self.assertEqual(report["decision"], "docs_index_invalid")
            self.assertTrue(any("18_完整游戏流程" in error for error in report["errors"]))

    def test_broken_index_link_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            make_docs_fixture(root)
            index = root / "docs" / "00_index.md"
            index.write_text(index.read_text(encoding="utf-8") + "- [Broken](./missing.md)\n", encoding="utf-8")

            report = build_report(root)

            self.assertEqual(report["decision"], "docs_index_invalid")
            self.assertTrue(any("missing.md" in error for error in report["errors"]))

    def test_cli_writes_report_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            make_docs_fixture(root)
            report_path = root / "report.json"
            markdown_path = root / "summary.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
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
            self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["decision"], "docs_index_valid")
            self.assertIn("Docs Index Validation", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
