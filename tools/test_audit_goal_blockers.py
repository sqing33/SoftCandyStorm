#!/usr/bin/env python3
"""Regression tests for Goal blocker priority audit.

Run with:
    python3 tools/test_audit_goal_blockers.py
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
VALIDATOR = SCRIPT_DIR / "audit_goal_blockers.py"

sys.path.insert(0, str(SCRIPT_DIR))

from audit_goal_blockers import build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def fixture_reports(root: Path, *, clear: bool = False) -> dict[str, Path]:
    paths = {
        "manual_evidence": root / "reports/manual.json",
        "local_binary": root / "reports/binary.json",
        "release_candidate": root / "reports/rc.json",
        "release_package": root / "reports/package.json",
        "docs_coverage": root / "reports/docs.json",
        "roadmap_audit": root / "reports/roadmap.json",
        "goal_consistency": root / "reports/goal.json",
    }
    write_json(
        paths["manual_evidence"],
        {"decision": "manual_evidence_ready", "gap_count": 0, "requirement_count": 2, "domain_counts": {}}
        if clear
        else {
            "decision": "manual_evidence_gaps_present",
            "gap_count": 3,
            "requirement_count": 5,
            "domain_counts": {"asset": {"gaps": 2}, "playtest": {"gaps": 1}},
        },
    )
    write_json(
        paths["local_binary"],
        {"decision": "local_binary_launch_ok", "next_actions": []}
        if clear
        else {"decision": "local_binary_launch_blocked", "signals": {"spctl": "rejected"}, "next_actions": ["enable Developer Mode"]},
    )
    write_json(
        paths["release_candidate"],
        {"decision": "release_candidate_ready", "blockers": [], "missing_gates": []}
        if clear
        else {"decision": "release_candidate_not_ready", "blockers": ["compile blocked"], "missing_gates": []},
    )
    write_json(
        paths["release_package"],
        {"decision": "release_package_ready", "package_status": "ready", "blockers": []}
        if clear
        else {"decision": "release_package_not_ready", "package_status": "blocked", "blockers": ["release_candidate_not_ready"]},
    )
    write_json(
        paths["docs_coverage"],
        {"decision": "docs_implementation_complete", "incomplete_docs": [], "doc_status_counts": {"complete": 20}}
        if clear
        else {
            "decision": "docs_implementation_incomplete",
            "incomplete_docs": ["docs/01.md", "docs/02.md"],
            "doc_status_counts": {"partial": 2},
            "item_status_counts": {"blocked": 1},
        },
    )
    write_json(
        paths["roadmap_audit"],
        {"phases": [{"phase": 0, "title": "done", "status": "complete", "next_actions": []}]}
        if clear
        else {
            "phases": [
                {"phase": 0, "title": "done", "status": "complete", "next_actions": []},
                {"phase": 1, "title": "blocked", "status": "blocked", "next_actions": ["recover binary"]},
            ]
        },
    )
    write_json(paths["goal_consistency"], {"decision": "goal_evidence_consistent", "errors": []})
    return paths


class GoalBlockerAuditTests(unittest.TestCase):
    def test_prioritizes_current_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = fixture_reports(root)

            report = build_report(root, **paths)

            self.assertEqual(report["decision"], "goal_blockers_present")
            self.assertGreaterEqual(report["blocker_count"], 5)
            self.assertEqual(report["blockers"][0]["severity"], "P0")
            ids = {item["id"] for item in report["blockers"]}
            self.assertIn("local_binary_launch_blocked", ids)
            self.assertIn("manual_evidence_gaps", ids)

    def test_reports_clear_when_all_sources_are_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = fixture_reports(root, clear=True)

            report = build_report(root, **paths)

            self.assertEqual(report["decision"], "goal_blockers_clear")
            self.assertEqual(report["blocker_count"], 0)

    def test_docs_coverage_ledger_without_validation_decision_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = fixture_reports(root, clear=True)
            write_json(
                paths["docs_coverage"],
                {
                    "docs": [
                        {"doc_path": "docs/00_index.md", "status": "complete"},
                        {"doc_path": "docs/02_核心玩法规格.md", "status": "partial"},
                    ]
                },
            )

            report = build_report(root, **paths)

            ids = {item["id"] for item in report["blockers"]}
            self.assertEqual(report["decision"], "goal_blockers_present")
            self.assertIn("docs_implementation_incomplete", ids)

    def test_recovered_local_binary_is_not_listed_as_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = fixture_reports(root)
            write_json(paths["local_binary"], {"decision": "local_binary_launch_ok", "next_actions": []})

            report = build_report(root, **paths)

            self.assertEqual(report["decision"], "goal_blockers_present")
            ids = {item["id"] for item in report["blockers"]}
            self.assertNotIn("local_binary_launch_blocked", ids)
            for item in report["blockers"]:
                self.assertNotIn("local_binary_launch_blocked", item.get("blocked_by", []))

    def test_cli_writes_report_with_allow_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = fixture_reports(root)
            report_path = root / "out" / "blockers.json"
            markdown_path = root / "out" / "summary.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--repo-root",
                    str(root),
                    "--manual-evidence",
                    str(paths["manual_evidence"]),
                    "--local-binary",
                    str(paths["local_binary"]),
                    "--release-candidate",
                    str(paths["release_candidate"]),
                    "--release-package",
                    str(paths["release_package"]),
                    "--docs-coverage",
                    str(paths["docs_coverage"]),
                    "--roadmap-audit",
                    str(paths["roadmap_audit"]),
                    "--goal-consistency",
                    str(paths["goal_consistency"]),
                    "--report",
                    str(report_path),
                    "--markdown",
                    str(markdown_path),
                    "--allow-blockers",
                ],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["decision"], "goal_blockers_present")
            self.assertIn("Goal Blocker Priority Audit", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
