#!/usr/bin/env python3
"""Regression tests for manual legal review validation.

Run with:
    python3 harness/telemetry_privacy/test_validate_manual_legal_review.py
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
TEMPLATE = SCRIPT_DIR / "manual_legal_review_template.json"
POLICY = SCRIPT_DIR / "telemetry_privacy_policy_template.json"
RUNTIME_CONTRACT = SCRIPT_DIR / "runtime_privacy_settings_contract_v0.json"
UPLOAD_CONTRACT = SCRIPT_DIR / "upload_transport_contract_v0.json"
SAVE_CONTRACT = REPO_ROOT / "harness" / "save_contract" / "save_state_v0_template.json"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_manual_legal_review import REQUIRED_CHECK_IDS, build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def copy_contracts(root: Path) -> None:
    targets = [
        (POLICY, root / "harness/telemetry_privacy/telemetry_privacy_policy_template.json"),
        (RUNTIME_CONTRACT, root / "harness/telemetry_privacy/runtime_privacy_settings_contract_v0.json"),
        (UPLOAD_CONTRACT, root / "harness/telemetry_privacy/upload_transport_contract_v0.json"),
        (SAVE_CONTRACT, root / "harness/save_contract/save_state_v0_template.json"),
    ]
    for source, target in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def valid_review(root: Path, *, gate_decision: str = "pass") -> Path:
    if gate_decision == "pass":
        check_decision = "pass"
        required_changes: list[str] = []
        global_risks: list[str] = []
        next_actions: list[str] = []
    else:
        check_decision = "repair"
        required_changes = ["补齐商店页面隐私文案后重新审查。"]
        global_risks = ["商店页面隐私说明仍未定稿。"]
        next_actions = ["更新文案并重新审查。"]

    write_text(root / "harness/reports/policy/summary.md", "# policy\n")
    write_text(root / "harness/reports/runtime_contract/summary.md", "# runtime\n")
    write_text(root / "harness/reports/upload_contract/summary.md", "# upload\n")
    write_json(
        root / "harness/reports/manual_privacy/manual_privacy_review.json",
        {"decision": "manual_privacy_review_valid"},
    )
    write_json(
        root / "harness/reports/manual_platform/manual_platform_path_review.json",
        {"decision": "manual_platform_path_review_valid"},
    )

    checks = []
    for check_id in sorted(REQUIRED_CHECK_IDS):
        checks.append(
            {
                "id": check_id,
                "decision": check_decision,
                "notes": f"{check_id} 已由人工法律/合规审查覆盖。",
                "required_changes": required_changes,
            }
        )

    review = root / "harness/telemetry_privacy/reviews/manual_legal_review.json"
    write_json(
        review,
        {
            "review_version": 1,
            "review_id": "fixture-manual-legal-review",
            "policy_path": "harness/telemetry_privacy/telemetry_privacy_policy_template.json",
            "runtime_privacy_contract_path": "harness/telemetry_privacy/runtime_privacy_settings_contract_v0.json",
            "save_contract_path": "harness/save_contract/save_state_v0_template.json",
            "upload_transport_contract_path": "harness/telemetry_privacy/upload_transport_contract_v0.json",
            "policy_validation_report": "harness/reports/policy/summary.md",
            "runtime_contract_validation_report": "harness/reports/runtime_contract/summary.md",
            "upload_transport_validation_report": "harness/reports/upload_contract/summary.md",
            "manual_privacy_review_report": "harness/reports/manual_privacy/manual_privacy_review.json",
            "manual_platform_path_review_report": "harness/reports/manual_platform/manual_platform_path_review.json",
            "reviewer": "human legal reviewer",
            "reviewer_role": "legal_or_compliance",
            "reviewed_at": "2026-05-26",
            "jurisdiction_scope": ["prototype_local", "steam_pc"],
            "gate_decision": gate_decision,
            "summary": "人工法律/合规审查 fixture，确认发布证据边界和隐私文案检查项完整。",
            "checks": checks,
            "global_risks": global_risks,
            "next_actions": next_actions,
        },
    )
    return review


class ManualLegalReviewValidatorTests(unittest.TestCase):
    def test_valid_pass_review_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            copy_contracts(root)
            review = valid_review(root)

            report = build_report(review, root)

            self.assertEqual(report["decision"], "manual_legal_review_valid")
            self.assertEqual(report["gate_decision"], "pass")
            self.assertEqual(report["check_count"], len(REQUIRED_CHECK_IDS))
            self.assertEqual(report["manual_privacy_review_decision"], "manual_privacy_review_valid")
            self.assertEqual(
                report["manual_platform_path_review_decision"],
                "manual_platform_path_review_valid",
            )

    def test_template_is_invalid_until_human_fills_placeholders(self) -> None:
        report = build_report(TEMPLATE, REPO_ROOT)

        self.assertEqual(report["decision"], "manual_legal_review_invalid")
        self.assertTrue(any("placeholder" in error for error in report["errors"]))
        self.assertTrue(any("manual_privacy_review_report" in error for error in report["errors"]))

    def test_repair_review_passes_with_next_actions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            copy_contracts(root)
            review = valid_review(root, gate_decision="repair")

            report = build_report(review, root)

            self.assertEqual(report["decision"], "manual_legal_review_valid")
            self.assertEqual(report["gate_decision"], "repair")
            self.assertGreater(report["issue_count"], 0)
            self.assertEqual(report["global_risk_count"], 1)

    def test_pass_rejects_unresolved_risks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            copy_contracts(root)
            review = valid_review(root)
            payload = json.loads(review.read_text(encoding="utf-8"))
            payload["global_risks"] = ["仍有未解决的隐私文案风险。"]
            write_json(review, payload)

            report = build_report(review, root)

            self.assertEqual(report["decision"], "manual_legal_review_invalid")
            self.assertTrue(any("global_risks" in error for error in report["errors"]))

    def test_forbidden_gate_decision_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            copy_contracts(root)
            review = valid_review(root)
            payload = json.loads(review.read_text(encoding="utf-8"))
            payload["gate_decision"] = "legal_approved"
            write_json(review, payload)

            report = build_report(review, root)

            self.assertEqual(report["decision"], "manual_legal_review_invalid")
            self.assertTrue(any("forbidden gate_decision" in error for error in report["errors"]))

    def test_invalid_manual_review_report_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            copy_contracts(root)
            review = valid_review(root)
            write_json(
                root / "harness/reports/manual_privacy/manual_privacy_review.json",
                {"decision": "manual_privacy_review_invalid"},
            )

            report = build_report(review, root)

            self.assertEqual(report["decision"], "manual_legal_review_invalid")
            self.assertTrue(any("manual_privacy_review_report decision" in error for error in report["errors"]))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
