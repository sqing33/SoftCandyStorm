#!/usr/bin/env python3
"""Regression tests for content acceptance manifest validation.

Run with:
    python3 harness/content_review/test_validate_content_acceptance_manifest.py
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
TEMPLATE = SCRIPT_DIR / "content_acceptance_manifest_template.json"

sys.path.insert(0, str(SCRIPT_DIR))

from test_validate_content_final_acceptance import (  # noqa: E402
    accepted_lockfile_report,
    create_simulation_candidate,
    valid_final_acceptance,
)
from validate_content_acceptance_manifest import build_report, load_json_object  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def valid_acceptance_manifest(repo_root: Path) -> Path:
    create_simulation_candidate(repo_root)
    accepted_lockfile_report(repo_root)
    valid_final_acceptance(repo_root)
    manifest = repo_root / "harness/content_review/accepted/fixture_full_pack/acceptance_manifest.json"
    write_json(
        manifest,
        {
            "manifest_version": 1,
            "manifest_contract_id": "content-acceptance-manifest-v0",
            "stage": "content_acceptance",
            "candidate_pack_id": "fixture_full_pack",
            "accepted_at": "2026-05-26T00:00:00Z",
            "source_simulation_candidate_manifest": "harness/content_review/simulation_candidates/fixture_full_pack/simulation_candidate_manifest.json",
            "final_human_acceptance_file": "harness/content_review/final_acceptance/fixture-final.json",
            "accepted_content_lockfile_report": "harness/reports/lockfile/accepted_content_lockfile.json",
            "content_pack_count": 1,
            "content_count": 2,
            "accepted_contents": [
                {
                    "id": "honey-heart",
                    "type": "passive",
                    "accepted_use": "accepted_content_pack",
                    "path": "passives/honey-heart.json",
                },
                {
                    "id": "licorice-skipper",
                    "type": "enemy",
                    "accepted_use": "accepted_content_pack",
                    "path": "enemies/licorice-skipper.json",
                },
            ],
            "rules": {
                "accepted_content": True,
                "runtime_integrated": False,
                "release_ready": False,
                "requires_simulation_candidate_manifest": True,
                "requires_final_human_acceptance": True,
                "requires_accepted_content_lockfile": True,
                "generated_candidate_direct_acceptance_allowed": False,
            },
        },
    )
    return manifest


class ContentAcceptanceManifestValidatorTests(unittest.TestCase):
    def test_valid_acceptance_manifest_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            manifest = valid_acceptance_manifest(repo_root)

            report = build_report(manifest, repo_root)

            self.assertEqual(report["decision"], "content_acceptance_manifest_valid")
            self.assertEqual(report["simulation_candidate_manifest_decision"], "content_simulation_candidate_manifest_valid")
            self.assertEqual(report["final_acceptance_decision"], "accepted_content")
            self.assertEqual(report["accepted_content_lockfile_decision"], "accepted_content_lockfile_valid")
            self.assertEqual(report["validated_content_count"], 2)

    def test_template_is_invalid_without_human_evidence(self) -> None:
        report = build_report(TEMPLATE, REPO_ROOT)

        self.assertEqual(report["decision"], "content_acceptance_manifest_invalid")
        self.assertTrue(any("placeholder" in error for error in report["errors"]))
        self.assertTrue(any("final_human_acceptance_file" in error for error in report["errors"]))

    def test_rejects_release_ready_claim(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            manifest = valid_acceptance_manifest(repo_root)
            payload = load_json_object(manifest)
            payload["rules"]["release_ready"] = True
            write_json(manifest, payload)

            report = build_report(manifest, repo_root)

            self.assertEqual(report["decision"], "content_acceptance_manifest_invalid")
            self.assertTrue(any("rules.release_ready" in error for error in report["errors"]))

    def test_rejects_unpassed_final_acceptance(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            manifest = valid_acceptance_manifest(repo_root)
            final_acceptance = repo_root / "harness/content_review/final_acceptance/fixture-final.json"
            payload = load_json_object(final_acceptance)
            payload["decision"] = "needs_more_review"
            payload["unresolved_issues"] = ["需要补充人工试玩记录。"]
            write_json(final_acceptance, payload)

            report = build_report(manifest, repo_root)

            self.assertEqual(report["decision"], "content_acceptance_manifest_invalid")
            self.assertTrue(any("final_human_acceptance_file.decision" in error for error in report["errors"]))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
