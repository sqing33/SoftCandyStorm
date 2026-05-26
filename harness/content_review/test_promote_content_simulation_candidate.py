#!/usr/bin/env python3
"""Regression tests for content simulation-candidate promotion.

Run with:
    python3 harness/content_review/test_promote_content_simulation_candidate.py
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from promote_content_simulation_candidate import promote_content_simulation_candidate


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def create_candidate_pack(repo_root: Path) -> Path:
    pack = repo_root / "harness/generated_candidates/fixture_full_pack"
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
            },
            "contents": [
                {"id": "honey-heart", "type": "passive", "path": "passives/honey-heart.json"},
                {"id": "licorice-skipper", "type": "enemy", "path": "enemies/licorice-skipper.json"},
            ],
        },
    )
    write_json(pack / "passives/honey-heart.json", {"id": "honey-heart", "name": "蜂蜜糖心"})
    write_json(pack / "enemies/licorice-skipper.json", {"id": "licorice-skipper", "name": "甘草跳跳"})
    report = repo_root / "harness/reports/preflight/summary.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("# Fixture preflight\n", encoding="utf-8")
    return pack


def valid_design_review(repo_root: Path) -> Path:
    review_path = repo_root / "harness/content_review/reviews/fixture_review.json"
    write_json(
        review_path,
        {
            "review_version": 1,
            "candidate_pack_id": "fixture_full_pack",
            "candidate_pack_path": "harness/generated_candidates/fixture_full_pack",
            "source_patch_manifest": "harness/generated_candidates/fixture_full_pack/metadata/source_patch_manifest.json",
            "candidate_preflight_report": "harness/reports/preflight/summary.md",
            "reviewer": "human-reviewer",
            "reviewed_at": "2026-05-26",
            "gate_decision": "simulate_candidate",
            "summary": "人工内容设计审查确认主题、反制、流派潜力和视听适配可进入仿真候选。",
            "content_reviews": [
                {
                    "id": "honey-heart",
                    "content_type": "passive",
                    "decision": "pass",
                    "theme_fit": 4,
                    "novelty": 4,
                    "build_potential": 4,
                    "counterplay_clarity": 4,
                    "visual_audio_fit": 4,
                    "balance_risk": "medium",
                    "notes": "蜂蜜糖心主题可爱，适合作为续航候选，但需要通过预算确认。",
                    "required_changes": [],
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
            "batch_risks": [],
            "next_actions": [],
        },
    )
    return review_path


class ContentSimulationCandidatePromotionTests(unittest.TestCase):
    def test_promotes_valid_design_review_without_writing_playtest_or_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            create_candidate_pack(repo_root)
            review = valid_design_review(repo_root)
            out_dir = repo_root / "harness/content_review/simulation_candidates"

            report = promote_content_simulation_candidate(review, repo_root, out_dir)
            manifest = json.loads(
                (out_dir / "fixture_full_pack/simulation_candidate_manifest.json").read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(report["decision"], "content_simulation_candidate_promoted")
            self.assertEqual(report["content_count"], 2)
            self.assertEqual(
                manifest["manifest_contract_id"],
                "content-simulation-candidate-manifest-v0",
            )
            self.assertEqual(manifest["manual_gate_decision"], "simulate_candidate")
            self.assertFalse(manifest["rules"]["validated_candidates_written"])
            self.assertFalse(manifest["rules"]["simulated_candidates_written"])
            self.assertFalse(manifest["rules"]["playtest_candidate"])
            self.assertFalse(manifest["rules"]["accepted_content"])

    def test_rejects_non_simulate_candidate_review(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            create_candidate_pack(repo_root)
            review = valid_design_review(repo_root)
            payload = json.loads(review.read_text(encoding="utf-8"))
            payload["gate_decision"] = "repair"
            payload["content_reviews"][0]["decision"] = "revise"
            payload["content_reviews"][0]["novelty"] = 3
            payload["content_reviews"][0]["required_changes"] = ["补充差异化触发条件后重新审查。"]
            payload["batch_risks"] = ["恢复被动可能和现有防御流重叠。"]
            payload["next_actions"] = ["修订后重新审查。"]
            write_json(review, payload)

            with self.assertRaisesRegex(ValueError, "gate_decision"):
                promote_content_simulation_candidate(
                    review,
                    repo_root,
                    repo_root / "harness/content_review/simulation_candidates",
                )

    def test_refuses_to_overwrite_existing_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            create_candidate_pack(repo_root)
            review = valid_design_review(repo_root)
            out_dir = repo_root / "harness/content_review/simulation_candidates"

            promote_content_simulation_candidate(review, repo_root, out_dir)

            with self.assertRaises(FileExistsError):
                promote_content_simulation_candidate(review, repo_root, out_dir)


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
