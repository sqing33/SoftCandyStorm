#!/usr/bin/env python3
"""Regression tests for content candidate review packet generation.

Run with:
    python3 harness/content_review/test_create_content_candidate_review_packet.py
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
PACKET = SCRIPT_DIR / "create_content_candidate_review_packet.py"

sys.path.insert(0, str(SCRIPT_DIR))

from create_content_candidate_review_packet import build_packet  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def make_candidate_pack(root: Path) -> Path:
    pack = root / "harness/generated_candidates/fixture_full_pack"
    project_rules = {
        "candidate_only": True,
        "accepted_content": False,
        "runtime_integrated": False,
        "required_next_steps": ["human design review", "simulation"],
    }
    write_json(
        pack / "metadata/manifest.json",
        {
            "batch_id": "fixture_full_pack",
            "candidate_kind": "full_content_pack",
            "generated_at": "2026-05-26",
            "project_rules": project_rules,
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
            "project_rules": project_rules,
            "contents": [
                {
                    "id": "honey-heart",
                    "type": "passive",
                    "path": "passives/honey-heart.json",
                    "role": "低速恢复",
                    "balance_budget": {
                        "risk": "回复叠加可能让防御流过于安全",
                        "gate_focus": "IdleBot 不能只靠续航活到 600 秒",
                    },
                    "counterplay_or_limit": "单级回复较低，且不提供直接输出。",
                },
                {
                    "id": "licorice-skipper",
                    "type": "enemy",
                    "path": "enemies/licorice-skipper.json",
                    "role": "跳跃干扰怪",
                    "balance_budget": {
                        "risk": "跳跃时机不可读会造成不公平接触伤害",
                        "gate_focus": "死亡原因清晰度和中前期压力",
                    },
                    "counterplay_or_limit": "跳跃前有可见压低动作。",
                },
            ],
        },
    )
    write_json(
        pack / "passives/honey-heart.json",
        {
            "id": "honey-heart",
            "name": "蜂蜜糖心",
            "rarity": "common",
            "tags": ["defense", "beginner"],
            "description": "低速恢复生命。",
        },
    )
    write_json(
        pack / "enemies/licorice-skipper.json",
        {
            "id": "licorice-skipper",
            "name": "甘草跳跳",
            "rarity": "common",
            "tags": ["jump", "pressure"],
            "description": "会跳跃接近玩家。",
        },
    )
    return pack


def make_review(root: Path, candidate: Path) -> Path:
    review_path = root / "harness/content_review/drafts/fixture_review.json"
    write_json(
        review_path,
        {
            "review_version": 1,
            "candidate_pack_id": candidate.name,
            "candidate_pack_path": str(candidate.relative_to(root)),
            "source_patch_manifest": str((candidate / "metadata/source_patch_manifest.json").relative_to(root)),
            "candidate_preflight_report": "harness/reports/fixture_preflight/summary.md",
            "reviewer": "TODO: human reviewer",
            "reviewed_at": "TODO: YYYY-MM-DD",
            "gate_decision": "needs_more_review",
            "summary": "TODO",
            "content_reviews": [
                {
                    "id": "honey-heart",
                    "content_type": "passive",
                    "decision": "revise",
                    "theme_fit": "TODO: 1-5",
                },
                {
                    "id": "licorice-skipper",
                    "content_type": "enemy",
                    "decision": "revise",
                    "theme_fit": "TODO: 1-5",
                },
            ],
            "batch_risks": ["TODO"],
            "next_actions": ["TODO"],
        },
    )
    return review_path


class ContentCandidateReviewPacketTests(unittest.TestCase):
    def test_build_packet_covers_source_patch_contents(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidate = make_candidate_pack(root)
            review = make_review(root, candidate)

            packet = build_packet(
                candidate,
                root,
                "harness/reports/fixture_preflight/summary.md",
                review,
            )

            self.assertEqual(packet["pack_id"], "fixture_full_pack")
            self.assertEqual(packet["content_count"], 2)
            self.assertEqual(packet["type_counts"], {"enemy": 1, "passive": 1})
            self.assertEqual(packet["missing_review_count"], 0)
            self.assertEqual([item["review_status"] for item in packet["items"]], ["draft_todo", "draft_todo"])
            self.assertIn("IdleBot", packet["items"][0]["gate_focus"])

    def test_cli_writes_markdown_packet(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidate = make_candidate_pack(root)
            review = make_review(root, candidate)
            out = root / "packet.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(PACKET),
                    str(candidate),
                    "--repo-root",
                    str(root),
                    "--preflight-report",
                    "harness/reports/fixture_preflight/summary.md",
                    "--review-draft",
                    str(review),
                    "--out",
                    str(out),
                ],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            text = out.read_text(encoding="utf-8")
            self.assertIn("Content Candidate Review Packet", text)
            self.assertIn("honey-heart", text)
            self.assertIn("licorice-skipper", text)
            self.assertIn("draft_todo", text)
            self.assertIn("It does not validate human ratings", text)


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
