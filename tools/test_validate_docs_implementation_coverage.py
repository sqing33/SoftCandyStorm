#!/usr/bin/env python3
"""Regression tests for docs implementation coverage validation.

Run with:
    python3 tools/test_validate_docs_implementation_coverage.py
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
VALIDATOR = SCRIPT_DIR / "validate_docs_implementation_coverage.py"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_docs_implementation_coverage import EXPECTED_DOCS, build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str = "evidence\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_fixture(root: Path, *, incomplete_doc: str | None = None) -> Path:
    write_text(root / "evidence.md")
    docs = []
    for doc in EXPECTED_DOCS:
        doc_id = doc[:2]
        doc_path = f"docs/{doc}"
        write_text(root / doc_path, f"# {doc}\n")
        is_incomplete = doc_id == incomplete_doc
        docs.append(
            {
                "doc_id": doc_id,
                "doc_path": doc_path,
                "status": "partial" if is_incomplete else "complete",
                "summary": f"{doc} coverage",
                "coverage": [
                    {
                        "id": "main",
                        "requirement": "Fixture requirement.",
                        "status": "partial" if is_incomplete else "complete",
                        "evidence": ["evidence.md"],
                        "gaps": ["Fixture gap."] if is_incomplete else [],
                    }
                ],
            }
        )
    manifest = root / "coverage.json"
    write_json(
        manifest,
        {
            "updated_at": "2026-05-26",
            "scope": "fixture docs coverage",
            "summary": "Fixture manifest.",
            "docs": docs,
        },
    )
    return manifest


class DocsImplementationCoverageValidatorTests(unittest.TestCase):
    def test_complete_fixture_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = make_fixture(root)

            report = build_report(manifest, root)

            self.assertEqual(report["decision"], "docs_implementation_complete")
            self.assertEqual(report["missing_docs"], [])
            self.assertEqual(report["doc_count"], len(EXPECTED_DOCS))

    def test_incomplete_fixture_reports_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = make_fixture(root, incomplete_doc="11")

            report = build_report(manifest, root)

            self.assertEqual(report["decision"], "docs_implementation_incomplete")
            self.assertTrue(any("11_" in doc for doc in report["incomplete_docs"]))

    def test_missing_evidence_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = make_fixture(root)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["docs"][0]["coverage"][0]["evidence"] = ["missing.md"]
            write_json(manifest, payload)

            report = build_report(manifest, root)

            self.assertEqual(report["decision"], "docs_implementation_incomplete")
            self.assertTrue(any("does not exist" in error for error in report["errors"]))

    def test_missing_doc_entry_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = make_fixture(root)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["docs"] = payload["docs"][1:]
            write_json(manifest, payload)

            report = build_report(manifest, root)

            self.assertEqual(report["decision"], "docs_implementation_incomplete")
            self.assertTrue(any("docs/00_index.md" in error for error in report["errors"]))

    def test_cli_writes_incomplete_report_with_allow_flag(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = make_fixture(root, incomplete_doc="18")
            report_path = root / "report.json"
            markdown_path = root / "summary.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(manifest),
                    "--repo-root",
                    str(root),
                    "--report",
                    str(report_path),
                    "--markdown",
                    str(markdown_path),
                    "--allow-incomplete",
                ],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                json.loads(report_path.read_text(encoding="utf-8"))["decision"],
                "docs_implementation_incomplete",
            )
            self.assertIn("Docs Implementation Coverage Validation", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
