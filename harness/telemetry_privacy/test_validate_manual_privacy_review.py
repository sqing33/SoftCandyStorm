#!/usr/bin/env python3
"""Regression tests for manual privacy review validation.

Run with:
    python3 harness/telemetry_privacy/test_validate_manual_privacy_review.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
VALIDATOR = SCRIPT_DIR / "validate_manual_privacy_review.py"
TEMPLATE = SCRIPT_DIR / "manual_privacy_review_template.json"
POLICY = SCRIPT_DIR / "telemetry_privacy_policy_template.json"
CONTRACT = SCRIPT_DIR / "runtime_privacy_settings_contract_v0.json"
SAVE_CONTRACT = REPO_ROOT / "harness" / "save_contract" / "save_state_v0_template.json"
POLICY_REPORT = REPO_ROOT / "harness" / "reports" / "2026-05-26_telemetry_privacy_policy_001" / "summary.md"
RUNTIME_CONTRACT_REPORT = (
    REPO_ROOT
    / "harness"
    / "reports"
    / "2026-05-26_runtime_privacy_settings_contract_001"
    / "summary.md"
)

sys.path.insert(0, str(SCRIPT_DIR))

from validate_manual_privacy_review import build_report, load_json_object  # noqa: E402


REQUIRED_CHECK_IDS = [
    "default_off",
    "explicit_consent",
    "raw_replay_separate_consent",
    "prohibited_fields",
    "delete_export_controls",
    "privacy_notice_text",
    "retention_and_storage",
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
                "notes": f"{check_id} 已人工确认，当前证据与默认关闭、本地优先和候选限制一致。",
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
        checks[0]["required_changes"] = ["补充设置页截图后重新审查。"]
        global_risks = ["设置页真实截图尚未补齐。"]
        next_actions = ["补齐截图证据后重新运行审查。"]

    review = root / "harness/telemetry_privacy/manual_review.json"
    write_json(
        review,
        {
            "review_version": 1,
            "review_id": "fixture-manual-privacy-review",
            "policy_path": str(POLICY.relative_to(REPO_ROOT)),
            "runtime_privacy_contract_path": str(CONTRACT.relative_to(REPO_ROOT)),
            "save_contract_path": str(SAVE_CONTRACT.relative_to(REPO_ROOT)),
            "policy_validation_report": str(POLICY_REPORT.relative_to(REPO_ROOT)),
            "runtime_contract_validation_report": str(RUNTIME_CONTRACT_REPORT.relative_to(REPO_ROOT)),
            "reviewer": "fixture reviewer",
            "reviewed_at": "2026-05-26",
            "gate_decision": gate_decision,
            "summary": "人工隐私审查 fixture，确认模板和契约的本地优先、默认关闭和同意边界。",
            "checks": checks,
            "global_risks": global_risks,
            "next_actions": next_actions,
        },
    )
    return review


class ManualPrivacyReviewValidatorTests(unittest.TestCase):
    def test_valid_pass_review_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            review = make_review(root)

            report = build_report(review, REPO_ROOT)

            self.assertEqual(report["decision"], "manual_privacy_review_valid")
            self.assertEqual(report["check_count"], len(REQUIRED_CHECK_IDS))
            self.assertEqual(report["bound_policy_decision"], "telemetry_privacy_policy_valid")
            self.assertEqual(report["bound_runtime_contract_decision"], "runtime_privacy_settings_contract_valid")

    def test_template_is_invalid_until_human_fills_placeholders(self) -> None:
        report = build_report(TEMPLATE, REPO_ROOT)

        self.assertEqual(report["decision"], "manual_privacy_review_invalid")
        self.assertTrue(any("placeholder" in error for error in report["errors"]))

    def test_pass_review_requires_every_check_to_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            review = make_review(root)
            payload = json.loads(review.read_text(encoding="utf-8"))
            payload["checks"][0]["decision"] = "repair"
            payload["checks"][0]["required_changes"] = ["补充说明。"]
            write_json(review, payload)

            report = build_report(review, REPO_ROOT)

            self.assertEqual(report["decision"], "manual_privacy_review_invalid")
            self.assertTrue(any("pass gate requires every check" in error for error in report["errors"]))

    def test_repair_review_passes_with_required_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            review = make_review(root, gate_decision="repair")

            report = build_report(review, REPO_ROOT)

            self.assertEqual(report["decision"], "manual_privacy_review_valid")
            self.assertEqual(report["repair_check_count"], 1)
            self.assertEqual(report["global_risk_count"], 1)

    def test_forbidden_gate_decision_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            review = make_review(root)
            payload = json.loads(review.read_text(encoding="utf-8"))
            payload["gate_decision"] = "release_ready"
            write_json(review, payload)

            report = build_report(review, REPO_ROOT)

            self.assertEqual(report["decision"], "manual_privacy_review_invalid")
            self.assertTrue(any("forbidden gate_decision" in error for error in report["errors"]))

    def test_cli_writes_report_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            review = make_review(root)
            report_path = root / "manual_privacy_review.json"
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
                "manual_privacy_review_valid",
            )
            self.assertIn("Manual Privacy Review Validation", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
