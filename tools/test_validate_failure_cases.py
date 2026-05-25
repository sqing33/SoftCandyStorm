#!/usr/bin/env python3
"""Regression tests for failure case validation.

Run with:
    python3 tools/test_validate_failure_cases.py
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
VALIDATOR = SCRIPT_DIR / "validate_failure_cases.py"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_failure_cases import build_report  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def valid_case(case_id: str = "fail_20260526_001") -> dict:
    return {
        "case_id": case_id,
        "category": "balance",
        "content_id": "frosting-grassland-standard",
        "seed": 12345,
        "bot": "KiteBot",
        "time_seconds": 87.4,
        "symptom": "前期敌人密度过高。",
        "root_cause": "快速怪权重过高。",
        "fix": "降低快速怪权重。",
        "validation": "重新运行 50 seed。",
    }


class FailureCaseValidatorTests(unittest.TestCase):
    def test_valid_canonical_failure_case_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "harness" / "failed_cases"
            write_json(root / "fail_20260526_001_fixture.json", valid_case())

            report = build_report(root)

            self.assertEqual(report["decision"], "failure_cases_valid")
            self.assertEqual(report["record_count"], 1)

    def test_missing_required_field_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "harness" / "failed_cases"
            payload = valid_case()
            del payload["validation"]
            write_json(root / "fail_20260526_001_fixture.json", payload)

            report = build_report(root)

            self.assertEqual(report["decision"], "failure_cases_invalid")
            self.assertTrue(any("validation" in error for error in report["errors"]))

    def test_filename_must_match_canonical_case_id(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "harness" / "failed_cases"
            write_json(root / "fail_20260526_999_fixture.json", valid_case("fail_20260526_001"))

            report = build_report(root)

            self.assertEqual(report["decision"], "failure_cases_invalid")
            self.assertTrue(any("file name must start" in error for error in report["errors"]))

    def test_report_local_failure_case_array_allows_local_ids_with_warning(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "harness" / "reports" / "matrix"
            payload = valid_case("coward_seed_30000")
            write_json(root / "failure_cases.json", [payload])

            report = build_report(root)

            self.assertEqual(report["decision"], "failure_cases_valid")
            self.assertTrue(any("non-canonical" in warning for warning in report["warnings"]))

    def test_cli_writes_report_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "harness" / "failed_cases"
            write_json(root / "fail_20260526_001_fixture.json", valid_case())
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
                "failure_cases_valid",
            )
            self.assertIn("Failure Case Validation", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
