#!/usr/bin/env python3
"""Regression tests for roadmap phase audit validation.

Run with:
    python3 tools/test_validate_roadmap_phase_audit.py
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
VALIDATOR = SCRIPT_DIR / "validate_roadmap_phase_audit.py"
AUDIT = REPO_ROOT / "harness" / "roadmap_audit" / "roadmap_phase_audit.json"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_roadmap_phase_audit import build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_audit() -> dict:
    return json.loads(AUDIT.read_text(encoding="utf-8"))


class RoadmapPhaseAuditValidatorTests(unittest.TestCase):
    def test_current_audit_is_honestly_incomplete(self) -> None:
        report = build_report(AUDIT, REPO_ROOT)

        self.assertEqual(report["decision"], "roadmap_phase_audit_incomplete")
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["phase_count"], 11)
        self.assertGreater(report["incomplete_phase_count"], 0)

    def test_missing_phase_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = load_audit()
            payload["phases"] = payload["phases"][:-1]
            path = Path(temp_dir) / "audit.json"
            write_json(path, payload)

            report = build_report(path, REPO_ROOT)

            self.assertEqual(report["decision"], "roadmap_phase_audit_invalid")
            self.assertTrue(any("missing phase `10`" in error for error in report["errors"]))

    def test_complete_phase_with_gap_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = load_audit()
            payload["phases"][0]["gaps"] = ["should not be here"]
            path = Path(temp_dir) / "audit.json"
            write_json(path, payload)

            report = build_report(path, REPO_ROOT)

            self.assertEqual(report["decision"], "roadmap_phase_audit_invalid")
            self.assertTrue(any("complete phase cannot list open gaps" in error for error in report["errors"]))

    def test_missing_evidence_path_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = load_audit()
            payload["phases"][1]["evidence"].append("missing/evidence.md")
            path = Path(temp_dir) / "audit.json"
            write_json(path, payload)

            report = build_report(path, REPO_ROOT)

            self.assertEqual(report["decision"], "roadmap_phase_audit_invalid")
            self.assertTrue(any("evidence path does not exist" in error for error in report["errors"]))

    def test_cli_allow_incomplete_writes_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = Path(temp_dir) / "report.json"
            markdown_path = Path(temp_dir) / "summary.md"
            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(AUDIT),
                    "--repo-root",
                    str(REPO_ROOT),
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
                "roadmap_phase_audit_incomplete",
            )
            self.assertIn("Roadmap Phase Audit", markdown_path.read_text(encoding="utf-8"))

    def test_cli_without_allow_incomplete_fails(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), str(AUDIT), "--repo-root", str(REPO_ROOT)],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
