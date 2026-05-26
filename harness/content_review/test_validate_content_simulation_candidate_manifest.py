#!/usr/bin/env python3
"""Regression tests for content simulation-candidate manifest validation.

Run with:
    python3 harness/content_review/test_validate_content_simulation_candidate_manifest.py
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
TEMPLATE = SCRIPT_DIR / "content_simulation_candidate_manifest_template.json"

sys.path.insert(0, str(SCRIPT_DIR))

from promote_content_simulation_candidate import promote_content_simulation_candidate  # noqa: E402
from test_promote_content_simulation_candidate import create_candidate_pack, valid_design_review  # noqa: E402
from validate_content_simulation_candidate_manifest import build_report, load_json_object  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


class ContentSimulationCandidateManifestValidatorTests(unittest.TestCase):
    def test_promoted_manifest_validates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            create_candidate_pack(repo_root)
            review = valid_design_review(repo_root)
            out_dir = repo_root / "harness/content_review/simulation_candidates"
            promote_content_simulation_candidate(review, repo_root, out_dir)

            manifest = out_dir / "fixture_full_pack/simulation_candidate_manifest.json"
            report = build_report(manifest, repo_root)

            self.assertEqual(report["decision"], "content_simulation_candidate_manifest_valid")
            self.assertEqual(report["manual_gate_decision"], "simulate_candidate")
            self.assertEqual(report["content_count"], 2)
            self.assertEqual(report["validated_content_count"], 2)

    def test_template_is_invalid_until_human_review_exists(self) -> None:
        report = build_report(TEMPLATE, REPO_ROOT)

        self.assertEqual(report["decision"], "content_simulation_candidate_manifest_invalid")
        self.assertTrue(any("placeholder" in error for error in report["errors"]))
        self.assertTrue(any("manual_design_review_file" in error for error in report["errors"]))

    def test_rejects_manifest_that_claims_accepted_content(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            create_candidate_pack(repo_root)
            review = valid_design_review(repo_root)
            out_dir = repo_root / "harness/content_review/simulation_candidates"
            promote_content_simulation_candidate(review, repo_root, out_dir)
            manifest = out_dir / "fixture_full_pack/simulation_candidate_manifest.json"
            payload = load_json_object(manifest)
            payload["rules"]["accepted_content"] = True
            write_json(manifest, payload)

            report = build_report(manifest, repo_root)

            self.assertEqual(report["decision"], "content_simulation_candidate_manifest_invalid")
            self.assertTrue(any("rules.accepted_content" in error for error in report["errors"]))

    def test_content_count_must_match_source_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            create_candidate_pack(repo_root)
            review = valid_design_review(repo_root)
            out_dir = repo_root / "harness/content_review/simulation_candidates"
            promote_content_simulation_candidate(review, repo_root, out_dir)
            manifest = out_dir / "fixture_full_pack/simulation_candidate_manifest.json"
            payload = load_json_object(manifest)
            payload["content_count"] = 99
            write_json(manifest, payload)

            report = build_report(manifest, repo_root)

            self.assertEqual(report["decision"], "content_simulation_candidate_manifest_invalid")
            self.assertTrue(any("content_count" in error for error in report["errors"]))

    def test_content_metadata_must_match_source_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            create_candidate_pack(repo_root)
            review = valid_design_review(repo_root)
            out_dir = repo_root / "harness/content_review/simulation_candidates"
            promote_content_simulation_candidate(review, repo_root, out_dir)
            manifest = out_dir / "fixture_full_pack/simulation_candidate_manifest.json"
            payload = load_json_object(manifest)
            payload["contents"][0]["type"] = "weapon"
            write_json(manifest, payload)

            report = build_report(manifest, repo_root)

            self.assertEqual(report["decision"], "content_simulation_candidate_manifest_invalid")
            self.assertTrue(any("type" in error for error in report["errors"]))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
