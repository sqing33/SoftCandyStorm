#!/usr/bin/env python3
"""Regression tests for content candidate design review validation.

Run with:
    python3 harness/content_review/test_validate_content_candidate_design_review.py
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
VALIDATOR = SCRIPT_DIR / "validate_content_candidate_design_review.py"
TEMPLATE = SCRIPT_DIR / "content_candidate_design_review_template.json"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_content_candidate_design_review import build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def make_candidate_pack(root: Path) -> tuple[Path, Path]:
    pack = root / "harness/generated_candidates/fixture_full_pack"
    write_json(
        pack / "metadata/manifest.json",
        {
            "batch_id": "fixture_full_pack",
            "candidate_kind": "full_content_pack",
            "generated_at": "2026-05-26",
            "project_rules": {
                "candidate_only": True,
                "accepted_content": False,
                "runtime_integrated": False,
                "required_next_steps": ["human design review", "simulation"],
            },
            "content_counts": {
                "passives": 1,
                "enemies": 1,
            },
        },
    )
    write_json(
        pack / "metadata/source_patch_manifest.json",
        {
            "batch_id": "fixture_patch",
            "generated_at": "2026-05-26",
            "project_rules": {
                "candidate_only": True,
                "accepted_content": False,
                "runtime_integrated": False,
                "required_next_steps": ["human design review"],
            },
            "contents": [
                {
                    "id": "honey-heart",
                    "type": "passive",
                    "path": "passives/honey-heart.json",
                    "role": "低速恢复",
                },
                {
                    "id": "licorice-skipper",
                    "type": "enemy",
                    "path": "enemies/licorice-skipper.json",
                    "role": "跳跃干扰怪",
                },
            ],
        },
    )
    write_json(pack / "passives/honey-heart.json", {"id": "honey-heart", "name": "蜂蜜糖心"})
    write_json(pack / "enemies/licorice-skipper.json", {"id": "licorice-skipper", "name": "甘草跳跳"})
    report = root / "harness/reports/fixture_preflight/summary.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("# Fixture preflight\n", encoding="utf-8")
    return pack, report


def make_review(root: Path, pack: Path, preflight: Path, *, gate_decision: str = "simulate_candidate") -> Path:
    if gate_decision == "simulate_candidate":
        first_decision = "pass"
        first_rating = 4
        first_changes: list[str] = []
        batch_risks: list[str] = []
        next_actions: list[str] = []
    else:
        first_decision = "revise"
        first_rating = 3
        first_changes = ["蜂蜜糖心和现有恢复被动差异不足，需要补充触发条件。"]
        batch_risks = ["恢复被动可能和防御流过度重叠。"]
        next_actions = ["修订后重新审查。"]

    review = root / "harness/content_review/reviews/fixture_review.json"
    write_json(
        review,
        {
            "review_version": 1,
            "candidate_pack_id": pack.name,
            "candidate_pack_path": str(pack.relative_to(root)),
            "source_patch_manifest": str((pack / "metadata/source_patch_manifest.json").relative_to(root)),
            "candidate_preflight_report": str(preflight.relative_to(root)),
            "reviewer": "fixture reviewer",
            "reviewed_at": "2026-05-26",
            "gate_decision": gate_decision,
            "summary": "人工内容设计审查 fixture，用于验证新增候选的主题、反制、流派和可读性字段。",
            "content_reviews": [
                {
                    "id": "honey-heart",
                    "content_type": "passive",
                    "decision": first_decision,
                    "theme_fit": first_rating,
                    "novelty": first_rating,
                    "build_potential": first_rating,
                    "counterplay_clarity": first_rating,
                    "visual_audio_fit": first_rating,
                    "balance_risk": "medium",
                    "notes": "蜂蜜糖心主题可爱，适合作为续航候选，但需要通过预算确认。",
                    "required_changes": first_changes,
                },
                {
                    "id": "licorice-skipper",
                    "content_type": "enemy",
                    "decision": "pass",
                    "theme_fit": 4,
                    "novelty": 4,
                    "build_potential": 4,
                    "counterplay_clarity": 4,
                    "visual_audio_fit": 4,
                    "balance_risk": "medium",
                    "notes": "甘草跳跳提供清晰跳跃预警，适合作为干扰怪候选。",
                    "required_changes": [],
                },
            ],
            "batch_risks": batch_risks,
            "next_actions": next_actions,
        },
    )
    return review


class ContentCandidateDesignReviewValidatorTests(unittest.TestCase):
    def test_valid_simulate_candidate_review_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            pack, preflight = make_candidate_pack(root)
            review = make_review(root, pack, preflight)

            report = build_report(review, root)

            self.assertEqual(report["decision"], "content_candidate_design_review_valid")
            self.assertEqual(report["content_review_count"], 2)
            self.assertEqual(report["expected_content_count"], 2)

    def test_repair_review_passes_with_required_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            pack, preflight = make_candidate_pack(root)
            review = make_review(root, pack, preflight, gate_decision="repair")

            report = build_report(review, root)

            self.assertEqual(report["decision"], "content_candidate_design_review_valid")
            self.assertEqual(report["repair_item_count"], 1)
            self.assertEqual(report["batch_risk_count"], 1)

    def test_template_is_invalid_until_human_fills_placeholders(self) -> None:
        report = build_report(TEMPLATE, REPO_ROOT)

        self.assertEqual(report["decision"], "content_candidate_design_review_invalid")
        self.assertTrue(any("placeholder" in error for error in report["errors"]))

    def test_simulate_candidate_rejects_low_rating(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            pack, preflight = make_candidate_pack(root)
            review = make_review(root, pack, preflight)
            payload = json.loads(review.read_text(encoding="utf-8"))
            payload["content_reviews"][0]["novelty"] = 3
            write_json(review, payload)

            report = build_report(review, root)

            self.assertEqual(report["decision"], "content_candidate_design_review_invalid")
            self.assertTrue(any("requires all ratings" in error for error in report["errors"]))

    def test_missing_content_review_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            pack, preflight = make_candidate_pack(root)
            review = make_review(root, pack, preflight)
            payload = json.loads(review.read_text(encoding="utf-8"))
            payload["content_reviews"] = payload["content_reviews"][:1]
            write_json(review, payload)

            report = build_report(review, root)

            self.assertEqual(report["decision"], "content_candidate_design_review_invalid")
            self.assertTrue(any("missing candidate ids" in error for error in report["errors"]))

    def test_forbidden_gate_decision_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            pack, preflight = make_candidate_pack(root)
            review = make_review(root, pack, preflight)
            payload = json.loads(review.read_text(encoding="utf-8"))
            payload["gate_decision"] = "accepted_content"
            write_json(review, payload)

            report = build_report(review, root)

            self.assertEqual(report["decision"], "content_candidate_design_review_invalid")
            self.assertTrue(any("forbidden gate_decision" in error for error in report["errors"]))

    def test_cli_writes_report_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            pack, preflight = make_candidate_pack(root)
            review = make_review(root, pack, preflight)
            report_path = root / "content_design_review.json"
            markdown_path = root / "summary.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(review),
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
            self.assertEqual(
                json.loads(report_path.read_text(encoding="utf-8"))["decision"],
                "content_candidate_design_review_valid",
            )
            self.assertIn("Content Candidate Design Review Validation", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
