#!/usr/bin/env python3
"""Regression tests for progress report reference validation.

Run with:
    python3 tools/test_validate_progress_reports.py
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
VALIDATOR = SCRIPT_DIR / "validate_progress_reports.py"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_progress_reports import build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str = "evidence\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_progress_fixture(root: Path) -> Path:
    write_text(root / "harness" / "reports" / "valid" / "summary.md")
    progress_path = root / "harness" / "progress.json"
    write_json(
        progress_path,
        {
            "updated_at": "2026-05-26",
            "phase": "fixture",
            "completed": [
                {
                    "id": "completed_gate",
                    "summary": "Completed entry with evidence.",
                    "report": "harness/reports/valid/summary.md",
                }
            ],
            "current_findings": [
                {
                    "id": "finding_without_report",
                    "summary": "Legacy finding without a report is only a warning.",
                }
            ],
            "next_recommended": [
                {
                    "id": "next_step",
                    "summary": "Next step does not need evidence yet.",
                }
            ],
        },
    )
    return progress_path


class ProgressReportValidatorTests(unittest.TestCase):
    def test_existing_report_references_pass_with_legacy_warning(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            progress_path = make_progress_fixture(root)

            report = build_report(progress_path, root)

            self.assertEqual(report["decision"], "progress_reports_valid")
            self.assertEqual(report["report_reference_count"], 1)
            self.assertEqual(report["existing_report_reference_count"], 1)
            self.assertEqual(report["items_without_report_count"], 1)

    def test_missing_report_reference_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            progress_path = make_progress_fixture(root)
            payload = json.loads(progress_path.read_text(encoding="utf-8"))
            payload["completed"][0]["report"] = "harness/reports/missing/summary.md"
            write_json(progress_path, payload)

            report = build_report(progress_path, root)

            self.assertEqual(report["decision"], "progress_reports_invalid")
            self.assertTrue(any("does not exist" in error for error in report["errors"]))

    def test_duplicate_ids_in_same_section_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            progress_path = make_progress_fixture(root)
            payload = json.loads(progress_path.read_text(encoding="utf-8"))
            payload["completed"].append(
                {
                    "id": "completed_gate",
                    "summary": "Duplicate completed entry.",
                    "report": "harness/reports/valid/summary.md",
                }
            )
            write_json(progress_path, payload)

            report = build_report(progress_path, root)

            self.assertEqual(report["decision"], "progress_reports_invalid")
            self.assertTrue(any("duplicate progress id" in error for error in report["errors"]))

    def test_duplicate_ids_across_sections_warn_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            progress_path = make_progress_fixture(root)
            payload = json.loads(progress_path.read_text(encoding="utf-8"))
            payload["current_findings"][0]["id"] = "completed_gate"
            write_json(progress_path, payload)

            report = build_report(progress_path, root)

            self.assertEqual(report["decision"], "progress_reports_valid")
            self.assertTrue(any("multiple sections" in warning for warning in report["warnings"]))

    def test_report_outside_repo_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            progress_path = make_progress_fixture(root)
            payload = json.loads(progress_path.read_text(encoding="utf-8"))
            payload["completed"][0]["report"] = "../outside.md"
            write_json(progress_path, payload)

            report = build_report(progress_path, root)

            self.assertEqual(report["decision"], "progress_reports_invalid")
            self.assertTrue(any("inside the repository" in error for error in report["errors"]))

    def test_cli_writes_report_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            progress_path = make_progress_fixture(root)
            report_path = root / "report.json"
            markdown_path = root / "summary.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(progress_path),
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
            self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["decision"], "progress_reports_valid")
            self.assertIn("Progress Report Reference Validation", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
