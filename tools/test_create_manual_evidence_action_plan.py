#!/usr/bin/env python3
"""Regression tests for manual evidence action-plan generation.

Run with:
    python3 tools/test_create_manual_evidence_action_plan.py
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
TOOL = SCRIPT_DIR / "create_manual_evidence_action_plan.py"

sys.path.insert(0, str(SCRIPT_DIR))

from create_manual_evidence_action_plan import build_plan  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def fixture_audit() -> dict:
    return {
        "decision": "manual_evidence_gaps_present",
        "items": [
            {
                "id": "manual_playtest_acceptance",
                "domain": "playtest",
                "title": "9-run human playtest acceptance",
                "status": "gap",
                "satisfied": False,
                "decision": "manual_playtest_acceptance_review_packet_needs_evidence",
                "required_action": "Replace TODO values with real human ratings.",
                "report": "reports/playtest.json",
                "summary": "reports/playtest.md",
                "evidence_paths": [{"kind": "report", "path": "reports/playtest.json", "exists": True}],
                "details": {
                    "required_next_steps": [
                        "Run the 9 human playtest sessions.",
                        "Run validate_manual_review.py --strict-acceptance.",
                    ]
                },
            },
            {
                "id": "asset_final_acceptance",
                "domain": "asset",
                "title": "Final human asset acceptance",
                "status": "gap",
                "satisfied": False,
                "decision": "asset_final_acceptance_invalid",
                "gate_decision": "needs_more_review",
                "required_action": "Bind passing preview and loudness reviews.",
                "report": "reports/asset.json",
            },
            {
                "id": "privacy_policy",
                "domain": "privacy",
                "title": "Privacy policy",
                "status": "satisfied",
                "satisfied": True,
                "decision": "manual_privacy_review_valid",
                "gate_decision": "pass",
                "required_action": "No action.",
                "report": "reports/privacy.json",
            },
        ],
    }


class ManualEvidenceActionPlanTests(unittest.TestCase):
    def test_groups_gaps_without_marking_them_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            audit_path = root / "audit.json"
            write_json(audit_path, fixture_audit())

            plan = build_plan(audit_path, root)

            self.assertEqual(plan["decision"], "manual_evidence_action_plan_ready")
            self.assertEqual(plan["source_decision"], "manual_evidence_gaps_present")
            self.assertEqual(plan["gap_count"], 2)
            self.assertEqual(plan["satisfied_count"], 1)
            domains = {domain["domain"]: domain for domain in plan["domains"]}
            self.assertEqual(domains["playtest"]["gaps"], 1)
            self.assertEqual(domains["privacy"]["satisfied"], 1)
            self.assertIn("Every gap remains blocked", " ".join(plan["limitations"]))

    def test_domain_filter_keeps_only_requested_domain(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            audit_path = root / "audit.json"
            write_json(audit_path, fixture_audit())

            plan = build_plan(audit_path, root, "asset")

            self.assertEqual(plan["item_count"], 1)
            self.assertEqual(plan["gap_count"], 1)
            self.assertEqual(plan["domains"][0]["domain"], "asset")

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            audit_path = root / "audit.json"
            report_path = root / "out" / "plan.json"
            markdown_path = root / "out" / "plan.md"
            write_json(audit_path, fixture_audit())

            result = subprocess.run(
                [
                    sys.executable,
                    str(TOOL),
                    str(audit_path),
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
            payload = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["gap_count"], 2)
            markdown = markdown_path.read_text(encoding="utf-8")
            self.assertIn("Manual Evidence Action Plan", markdown)
            self.assertIn("manual_playtest_acceptance", markdown)


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
