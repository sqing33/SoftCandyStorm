#!/usr/bin/env python3
"""Regression tests for manual base UI review validation.

Run with:
    python3 tools/test_validate_base_ui_manual_review.py
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
VALIDATOR = SCRIPT_DIR / "validate_base_ui_manual_review.py"
TEMPLATE = REPO_ROOT / "harness" / "save_contract" / "base_ui_manual_review_template.json"
RUNTIME_SURFACE = REPO_ROOT / "harness" / "runtime_contract" / "runtime_surface_contract_v0.json"
RUNTIME_SURFACE_REPORT = (
    REPO_ROOT
    / "harness"
    / "reports"
    / "2026-05-26_runtime_surface_contract_platform_paths_001"
    / "summary.md"
)
SAVE_V1 = REPO_ROOT / "harness" / "save_contract" / "save_state_v1_template.json"
SAVE_V1_REPORT = REPO_ROOT / "harness" / "reports" / "2026-05-26_save_state_contract_v1_001" / "summary.md"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_base_ui_manual_review import build_report, load_json_object  # noqa: E402


REQUIRED_CHECK_IDS = [
    "overview_panel",
    "chapter_navigation",
    "character_map_selection",
    "codex_navigation",
    "privacy_settings_access",
    "local_data_controls",
    "candidate_content_boundaries",
    "runtime_evidence_limits",
]


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def make_review(root: Path, *, gate_decision: str = "base_ui_review_pass") -> Path:
    if gate_decision == "base_ui_review_pass":
        checks = [
            {
                "id": check_id,
                "decision": "pass",
                "notes": f"{check_id} 已人工确认，当前源码形状和审查范围覆盖对应局外 UI 要求。",
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
        checks[0]["required_changes"] = ["补充 F1 概览截图和真实操作记录后重新审查。"]
        global_risks = ["Runtime 二进制尚未恢复，缺少真实基地 UI 截图。"]
        next_actions = ["恢复 Runtime 后补齐人工审查证据。"]

    review = root / "harness/save_contract/base_ui_manual_review.json"
    write_json(
        review,
        {
            "review_version": 1,
            "review_type": "base_ui_manual_review",
            "review_id": "fixture-base-ui-review",
            "runtime_surface_contract": str(RUNTIME_SURFACE.relative_to(REPO_ROOT)),
            "runtime_surface_validation_report": str(RUNTIME_SURFACE_REPORT.relative_to(REPO_ROOT)),
            "save_state_contract": str(SAVE_V1.relative_to(REPO_ROOT)),
            "save_state_validation_report": str(SAVE_V1_REPORT.relative_to(REPO_ROOT)),
            "reviewer": "fixture reviewer",
            "reviewed_at": "2026-05-26",
            "gate_decision": gate_decision,
            "summary": "人工基地 UI 审查 fixture，确认四页面板、选择入口、图鉴、隐私和候选内容边界。",
            "checks": checks,
            "global_risks": global_risks,
            "next_actions": next_actions,
        },
    )
    return review


class BaseUiManualReviewValidatorTests(unittest.TestCase):
    def test_valid_pass_review_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            review = make_review(Path(temp_dir))

            report = build_report(review, REPO_ROOT)

            self.assertEqual(report["decision"], "base_ui_manual_review_valid")
            self.assertEqual(report["gate_decision"], "base_ui_review_pass")
            self.assertEqual(report["check_count"], len(REQUIRED_CHECK_IDS))
            self.assertEqual(report["runtime_surface_contract_decision"], "runtime_surface_contract_valid")
            self.assertEqual(report["save_state_contract_decision"], "save_state_contract_valid")

    def test_template_is_invalid_until_human_fills_placeholders(self) -> None:
        report = build_report(TEMPLATE, REPO_ROOT)

        self.assertEqual(report["decision"], "base_ui_manual_review_invalid")
        self.assertTrue(any("placeholder" in error for error in report["errors"]))

    def test_pass_review_requires_every_check_to_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            review = make_review(Path(temp_dir))
            payload = load_json_object(review)
            payload["checks"][0]["decision"] = "repair"
            payload["checks"][0]["required_changes"] = ["补充操作记录。"]
            write_json(review, payload)

            report = build_report(review, REPO_ROOT)

            self.assertEqual(report["decision"], "base_ui_manual_review_invalid")
            self.assertTrue(any("base_ui_review_pass requires every check" in error for error in report["errors"]))

    def test_repair_review_passes_with_next_actions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            review = make_review(Path(temp_dir), gate_decision="repair")

            report = build_report(review, REPO_ROOT)

            self.assertEqual(report["decision"], "base_ui_manual_review_valid")
            self.assertEqual(report["issue_check_count"], 1)
            self.assertEqual(report["global_risk_count"], 1)

    def test_forbidden_gate_decision_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            review = make_review(Path(temp_dir))
            payload = load_json_object(review)
            payload["gate_decision"] = "release_ready"
            write_json(review, payload)

            report = build_report(review, REPO_ROOT)

            self.assertEqual(report["decision"], "base_ui_manual_review_invalid")
            self.assertTrue(any("forbidden gate_decision" in error for error in report["errors"]))

    def test_missing_required_check_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            review = make_review(Path(temp_dir))
            payload = load_json_object(review)
            payload["checks"] = payload["checks"][1:]
            write_json(review, payload)

            report = build_report(review, REPO_ROOT)

            self.assertEqual(report["decision"], "base_ui_manual_review_invalid")
            self.assertTrue(any("overview_panel" in error for error in report["errors"]))

    def test_cli_writes_report_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            review = make_review(root)
            report_path = root / "base_ui_manual_review.json"
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
                "base_ui_manual_review_valid",
            )
            self.assertIn("Base UI Manual Review Validation", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
