#!/usr/bin/env python3
"""Regression tests for asset Runtime preview review validation.

Run with:
    python3 harness/asset_review/test_validate_asset_runtime_preview_review.py
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
TEMPLATE = SCRIPT_DIR / "asset_runtime_preview_review_template.json"

sys.path.insert(0, str(SCRIPT_DIR))

from test_validate_asset_acceptance_manifest import create_runtime_candidate, valid_runtime_preview_review  # noqa: E402
from validate_asset_runtime_preview_review import build_report, load_json_object  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


class AssetRuntimePreviewReviewValidatorTests(unittest.TestCase):
    def test_valid_runtime_preview_review_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            create_runtime_candidate(repo_root)
            review = valid_runtime_preview_review(repo_root)

            report = build_report(review, repo_root)

            self.assertEqual(report["decision"], "asset_runtime_preview_review_valid")
            self.assertEqual(report["gate_decision"], "runtime_preview_pass")
            self.assertEqual(report["runtime_candidate_manifest_decision"], "asset_runtime_candidate_manifest_valid")

    def test_template_is_invalid_until_human_fills_placeholders(self) -> None:
        report = build_report(TEMPLATE, REPO_ROOT)

        self.assertEqual(report["decision"], "asset_runtime_preview_review_invalid")
        self.assertTrue(any("placeholder" in error for error in report["errors"]))
        self.assertTrue(any("source_runtime_candidate_manifest" in error for error in report["errors"]))

    def test_pass_requires_all_checks_true(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            create_runtime_candidate(repo_root)
            review = valid_runtime_preview_review(repo_root)
            payload = load_json_object(review)
            payload["checks"]["small_size_readable"] = False
            write_json(review, payload)

            report = build_report(review, repo_root)

            self.assertEqual(report["decision"], "asset_runtime_preview_review_invalid")
            self.assertTrue(any("checks.small_size_readable" in error for error in report["errors"]))

    def test_pass_rejects_unresolved_issues(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            create_runtime_candidate(repo_root)
            review = valid_runtime_preview_review(repo_root)
            payload = load_json_object(review)
            payload["unresolved_issues"] = ["64px 预览里玩家轮廓仍不够清晰。"]
            write_json(review, payload)

            report = build_report(review, repo_root)

            self.assertEqual(report["decision"], "asset_runtime_preview_review_invalid")
            self.assertTrue(any("unresolved_issues" in error for error in report["errors"]))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
