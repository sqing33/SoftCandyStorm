#!/usr/bin/env python3
"""Regression tests for manual platform path review validation.

Run with:
    python3 tools/test_validate_manual_platform_path_review.py
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
VALIDATOR = SCRIPT_DIR / "validate_manual_platform_path_review.py"
TEMPLATE = REPO_ROOT / "harness" / "save_contract" / "manual_platform_path_review_template.json"
POLICY = REPO_ROOT / "harness" / "save_contract" / "platform_save_path_policy_v0.json"
POLICY_REPORT = REPO_ROOT / "harness" / "reports" / "2026-05-26_save_path_policy_v0_001" / "summary.md"
SAVE_V0 = REPO_ROOT / "harness" / "save_contract" / "save_state_v0_template.json"
SAVE_V1 = REPO_ROOT / "harness" / "save_contract" / "save_state_v1_template.json"
SAVE_V0_REPORT = REPO_ROOT / "harness" / "reports" / "2026-05-26_save_state_contract_001" / "summary.md"
SAVE_V1_REPORT = REPO_ROOT / "harness" / "reports" / "2026-05-26_save_state_contract_v1_001" / "summary.md"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_manual_platform_path_review import build_report, load_json_object  # noqa: E402


REQUIRED_CHECK_IDS = [
    "logical_roots",
    "no_host_absolute_paths",
    "delete_scope",
    "export_scope",
    "migration_original_retention",
    "cloud_sync_policy",
    "runtime_evidence_limits",
]


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def make_review(root: Path, *, gate_decision: str = "pass") -> Path:
    if gate_decision == "pass":
        checks = [
            {
                "id": check_id,
                "decision": "pass",
                "notes": f"{check_id} 已人工确认，当前策略边界与本地优先、逻辑路径和删除导出限制一致。",
                "required_changes": [],
            }
            for check_id in REQUIRED_CHECK_IDS
        ]
        global_risks: list[str] = []
        next_actions: list[str] = []
    else:
        checks = [
            {
                "id": check_id,
                "decision": "pass",
                "notes": f"{check_id} 已人工确认。",
                "required_changes": [],
            }
            for check_id in REQUIRED_CHECK_IDS
        ]
        checks[0]["decision"] = "repair"
        checks[0]["required_changes"] = ["补充平台路径截图或系统目录说明后重新审查。"]
        global_risks = ["Runtime 默认路径尚未绑定平台目录。"]
        next_actions = ["补齐平台路径证据后重新运行审查。"]

    review = root / "harness/save_contract/manual_platform_path_review.json"
    write_json(
        review,
        {
            "review_version": 1,
            "review_id": "fixture-manual-platform-path-review",
            "path_policy_path": str(POLICY.relative_to(REPO_ROOT)),
            "path_policy_validation_report": str(POLICY_REPORT.relative_to(REPO_ROOT)),
            "save_contract_paths": [
                str(SAVE_V0.relative_to(REPO_ROOT)),
                str(SAVE_V1.relative_to(REPO_ROOT)),
            ],
            "save_contract_validation_reports": [
                str(SAVE_V0_REPORT.relative_to(REPO_ROOT)),
                str(SAVE_V1_REPORT.relative_to(REPO_ROOT)),
            ],
            "reviewer": "fixture reviewer",
            "reviewed_at": "2026-05-26",
            "gate_decision": gate_decision,
            "summary": "人工平台路径审查 fixture，确认逻辑目录、删除导出边界和 Runtime 证据限制。",
            "checks": checks,
            "global_risks": global_risks,
            "next_actions": next_actions,
        },
    )
    return review


class ManualPlatformPathReviewValidatorTests(unittest.TestCase):
    def test_valid_pass_review_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            review = make_review(Path(temp_dir))

            report = build_report(review, REPO_ROOT)

            self.assertEqual(report["decision"], "manual_platform_path_review_valid")
            self.assertEqual(report["check_count"], len(REQUIRED_CHECK_IDS))
            self.assertEqual(report["bound_path_policy_decision"], "save_path_policy_valid")
            self.assertEqual(report["bound_save_contract_decisions"].count("save_state_contract_valid"), 2)

    def test_template_is_invalid_until_human_fills_placeholders(self) -> None:
        report = build_report(TEMPLATE, REPO_ROOT)

        self.assertEqual(report["decision"], "manual_platform_path_review_invalid")
        self.assertTrue(any("placeholder" in error for error in report["errors"]))

    def test_pass_review_requires_every_check_to_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            review = make_review(Path(temp_dir))
            payload = json.loads(review.read_text(encoding="utf-8"))
            payload["checks"][0]["decision"] = "repair"
            payload["checks"][0]["required_changes"] = ["补充说明。"]
            write_json(review, payload)

            report = build_report(review, REPO_ROOT)

            self.assertEqual(report["decision"], "manual_platform_path_review_invalid")
            self.assertTrue(any("pass gate requires every check" in error for error in report["errors"]))

    def test_repair_review_passes_with_required_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            review = make_review(Path(temp_dir), gate_decision="repair")

            report = build_report(review, REPO_ROOT)

            self.assertEqual(report["decision"], "manual_platform_path_review_valid")
            self.assertEqual(report["issue_check_count"], 1)
            self.assertEqual(report["global_risk_count"], 1)

    def test_forbidden_gate_decision_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            review = make_review(Path(temp_dir))
            payload = json.loads(review.read_text(encoding="utf-8"))
            payload["gate_decision"] = "platform_approved"
            write_json(review, payload)

            report = build_report(review, REPO_ROOT)

            self.assertEqual(report["decision"], "manual_platform_path_review_invalid")
            self.assertTrue(any("forbidden gate_decision" in error for error in report["errors"]))

    def test_missing_v1_save_contract_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            review = make_review(Path(temp_dir))
            payload = json.loads(review.read_text(encoding="utf-8"))
            payload["save_contract_paths"] = [payload["save_contract_paths"][0]]
            payload["save_contract_validation_reports"] = [payload["save_contract_validation_reports"][0]]
            write_json(review, payload)

            report = build_report(review, REPO_ROOT)

            self.assertEqual(report["decision"], "manual_platform_path_review_invalid")
            self.assertTrue(any("save-state-v1" in error for error in report["errors"]))

    def test_cli_writes_report_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            review = make_review(root)
            report_path = root / "manual_platform_path_review.json"
            markdown_path = root / "summary.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(review),
                    "--repo-root",
                    str(REPO_ROOT),
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
                "manual_platform_path_review_valid",
            )
            self.assertIn("Manual Platform Path Review Validation", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
