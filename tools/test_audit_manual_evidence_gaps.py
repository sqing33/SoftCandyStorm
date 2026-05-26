#!/usr/bin/env python3
"""Regression tests for manual evidence gap audit.

Run with:
    python3 tools/test_audit_manual_evidence_gaps.py
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
VALIDATOR = SCRIPT_DIR / "audit_manual_evidence_gaps.py"

sys.path.insert(0, str(SCRIPT_DIR))

from audit_manual_evidence_gaps import build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str = "summary\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def requirement(req_id: str, report: str, *, domain: str = "fixture") -> dict:
    return {
        "id": req_id,
        "domain": domain,
        "title": req_id,
        "report": report,
        "summary": report.replace(".json", ".md"),
        "pass_decisions": [f"{req_id}_ready"],
        "required_gate_decisions": ["pass"],
        "required_action": f"finish {req_id}",
    }


class ManualEvidenceGapAuditTests(unittest.TestCase):
    def test_reports_ready_when_all_requirements_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_json(root / "reports/playtest.json", {"decision": "playtest_ready", "gate_decision": "pass"})
            write_text(root / "reports/playtest.md")

            report = build_report(root, [requirement("playtest", "reports/playtest.json")])

            self.assertEqual(report["decision"], "manual_evidence_ready")
            self.assertEqual(report["satisfied_count"], 1)
            self.assertEqual(report["gap_count"], 0)

    def test_collects_pending_and_missing_gaps(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_json(
                root / "reports/playtest.json",
                {
                    "decision": "manual_review_invalid",
                    "gate_decision": "needs_more_review",
                    "errors": ["TODO ratings remain"],
                },
            )
            write_text(root / "reports/playtest.md")
            requirements = [
                requirement("playtest", "reports/playtest.json", domain="playtest"),
                requirement("asset", "reports/asset.json", domain="asset"),
            ]

            report = build_report(root, requirements)

            self.assertEqual(report["decision"], "manual_evidence_gaps_present")
            self.assertEqual(report["gap_count"], 2)
            self.assertEqual(report["missing_report_count"], 1)
            self.assertEqual(report["domain_counts"]["playtest"]["gaps"], 1)
            self.assertEqual(report["domain_counts"]["asset"]["gaps"], 1)
            self.assertTrue(any(gap["id"] == "playtest" for gap in report["gaps"]))

    def test_cli_writes_known_gap_report_with_allow_flag(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_json(root / "reports/privacy.json", {"decision": "manual_privacy_review_invalid"})
            write_text(root / "reports/privacy.md")
            requirements_path = root / "requirements.json"
            write_json(
                requirements_path,
                {
                    "requirements": [
                        {
                            "id": "privacy",
                            "domain": "privacy",
                            "title": "Privacy",
                            "report": "reports/privacy.json",
                            "summary": "reports/privacy.md",
                            "pass_decisions": ["manual_privacy_review_valid"],
                            "required_gate_decisions": ["pass"],
                            "required_action": "fill human privacy review",
                        }
                    ]
                },
            )
            report_path = root / "out" / "audit.json"
            markdown_path = root / "out" / "summary.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--repo-root",
                    str(root),
                    "--requirements",
                    str(requirements_path),
                    "--report",
                    str(report_path),
                    "--markdown",
                    str(markdown_path),
                    "--allow-gaps",
                ],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["decision"], "manual_evidence_gaps_present")
            self.assertIn("Manual Evidence Gap Audit", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
