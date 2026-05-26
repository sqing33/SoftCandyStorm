#!/usr/bin/env python3
"""Regression tests for final content acceptance validation.

Run with:
    python3 harness/content_review/test_validate_content_final_acceptance.py
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
TEMPLATE = SCRIPT_DIR / "content_final_acceptance_template.json"

sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(REPO_ROOT / "tools"))

from promote_content_simulation_candidate import promote_content_simulation_candidate  # noqa: E402
from test_promote_content_simulation_candidate import create_candidate_pack, valid_design_review  # noqa: E402
from validate_content_final_acceptance import build_report, load_json_object  # noqa: E402
from test_validate_accepted_content_lockfile import make_lock_tree  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def create_simulation_candidate(repo_root: Path) -> Path:
    manifest = repo_root / "harness/content_review/simulation_candidates/fixture_full_pack/simulation_candidate_manifest.json"
    if manifest.exists():
        return manifest
    create_candidate_pack(repo_root)
    review = valid_design_review(repo_root)
    out_dir = repo_root / "harness/content_review/simulation_candidates"
    promote_content_simulation_candidate(review, repo_root, out_dir)
    return manifest


def accepted_lockfile_report(repo_root: Path, candidate_pack_id: str = "fixture_full_pack") -> Path:
    lockfile = make_lock_tree(repo_root)
    report = repo_root / "harness/reports/lockfile/accepted_content_lockfile.json"
    payload = {
        "decision": "accepted_content_lockfile_valid",
        "locked_count": 1,
        "entries": [
            {
                "id": candidate_pack_id,
                "status": "locked",
                "content_hash": "fnv1a64:0123456789abcdef",
                "source": "harness/accepted_content/base-demo-smoke",
            }
        ],
        "source_lockfile": str(lockfile.relative_to(repo_root)),
    }
    write_json(report, payload)
    return report


def valid_final_acceptance(repo_root: Path) -> Path:
    create_simulation_candidate(repo_root)
    accepted_lockfile_report(repo_root)
    path = repo_root / "harness/content_review/final_acceptance/fixture-final.json"
    write_json(
        path,
        {
            "review_version": 1,
            "review_type": "content_final_acceptance",
            "candidate_pack_id": "fixture_full_pack",
            "source_simulation_candidate_manifest": "harness/content_review/simulation_candidates/fixture_full_pack/simulation_candidate_manifest.json",
            "accepted_content_lockfile_report": "harness/reports/lockfile/accepted_content_lockfile.json",
            "reviewer": "final-human-reviewer",
            "reviewed_at": "2026-05-26",
            "decision": "accepted_content",
            "summary": "最终人工接受该完整内容包进入 accepted content 证据链。",
            "checks": {
                "accepts_content_pack": True,
                "accepted_content_only_after_reviews": True,
                "lockfile_valid": True,
                "release_ready": False,
                "runtime_integrated": False,
                "generated_candidate_direct_acceptance_allowed": False,
            },
            "concrete_observations": [
                "新增被动和敌人均来自已 staging 的 simulation candidate manifest。",
                "accepted content lockfile 报告包含该候选包的 locked 条目。",
            ],
            "unresolved_issues": [],
        },
    )
    return path


class ContentFinalAcceptanceValidatorTests(unittest.TestCase):
    def test_valid_final_acceptance_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            review = valid_final_acceptance(repo_root)

            report = build_report(review, repo_root)

            self.assertEqual(report["decision"], "content_final_acceptance_valid")
            self.assertEqual(report["gate_decision"], "accepted_content")
            self.assertEqual(report["simulation_candidate_manifest_decision"], "content_simulation_candidate_manifest_valid")
            self.assertEqual(report["accepted_content_lockfile_decision"], "accepted_content_lockfile_valid")

    def test_template_is_invalid_until_human_fills_placeholders(self) -> None:
        report = build_report(TEMPLATE, REPO_ROOT)

        self.assertEqual(report["decision"], "content_final_acceptance_invalid")
        self.assertTrue(any("placeholder" in error for error in report["errors"]))
        self.assertTrue(any("source_simulation_candidate_manifest" in error for error in report["errors"]))

    def test_acceptance_cannot_claim_release_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            review = valid_final_acceptance(repo_root)
            payload = load_json_object(review)
            payload["checks"]["release_ready"] = True
            write_json(review, payload)

            report = build_report(review, repo_root)

            self.assertEqual(report["decision"], "content_final_acceptance_invalid")
            self.assertTrue(any("checks.release_ready" in error for error in report["errors"]))

    def test_acceptance_requires_valid_lockfile(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            review = valid_final_acceptance(repo_root)
            lockfile_report = repo_root / "harness/reports/lockfile/accepted_content_lockfile.json"
            payload = load_json_object(lockfile_report)
            payload["decision"] = "accepted_content_lockfile_blocked"
            payload["locked_count"] = 0
            write_json(lockfile_report, payload)

            report = build_report(review, repo_root)

            self.assertEqual(report["decision"], "content_final_acceptance_invalid")
            self.assertTrue(any("accepted_content_lockfile_report decision" in error for error in report["errors"]))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
