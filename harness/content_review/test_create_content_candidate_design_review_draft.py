#!/usr/bin/env python3
"""Regression tests for content candidate design review draft generation.

Run with:
    python3 harness/content_review/test_create_content_candidate_design_review_draft.py
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
GENERATOR = SCRIPT_DIR / "create_content_candidate_design_review_draft.py"

sys.path.insert(0, str(SCRIPT_DIR))

from create_content_candidate_design_review_draft import build_draft  # noqa: E402
from validate_content_candidate_design_review import build_report as build_review_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def make_candidate_pack(root: Path) -> Path:
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
    return pack


def make_preflight_report(root: Path) -> Path:
    report = root / "harness/reports/fixture_preflight/summary.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("# Fixture preflight\n", encoding="utf-8")
    return report


class ContentCandidateDesignReviewDraftTests(unittest.TestCase):
    def test_build_draft_covers_source_patch_contents(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            pack = make_candidate_pack(root)

            draft = build_draft(
                pack,
                root,
                "harness/reports/fixture_preflight/summary.md",
                "TODO: human reviewer",
                "TODO: YYYY-MM-DD",
            )

            self.assertEqual(draft["candidate_pack_id"], "fixture_full_pack")
            self.assertIn("AUTO-GENERATED DRAFT ONLY", draft["draft_notice"])
            self.assertEqual(
                [item["id"] for item in draft["content_reviews"]],
                ["honey-heart", "licorice-skipper"],
            )
            self.assertIn("TODO", str(draft["content_reviews"][0]["theme_fit"]))

    def test_cli_writes_draft_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            pack = make_candidate_pack(root)
            out = root / "draft.json"

            result = subprocess.run(
                [
                    sys.executable,
                    str(GENERATOR),
                    str(pack),
                    "--repo-root",
                    str(root),
                    "--preflight-report",
                    "harness/reports/fixture_preflight/summary.md",
                    "--out",
                    str(out),
                ],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(len(payload["content_reviews"]), 2)
            self.assertEqual(payload["gate_decision"], "needs_more_review")

    def test_draft_is_not_valid_until_human_fills_todo(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            pack = make_candidate_pack(root)
            report_path = make_preflight_report(root)
            draft = build_draft(
                pack,
                root,
                str(report_path.relative_to(root)),
                "TODO: human reviewer",
                "TODO: YYYY-MM-DD",
            )
            draft_path = root / "harness/content_review/draft.json"
            write_json(draft_path, draft)

            report = build_review_report(draft_path, root)

            self.assertEqual(report["decision"], "content_candidate_design_review_invalid")
            self.assertTrue(any("theme_fit must be an integer" in error for error in report["errors"]))
            self.assertTrue(any("placeholder" in error for error in report["errors"]))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
