#!/usr/bin/env python3
"""Create a human-fillable manual playtest review draft for the current candidate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from current_candidate import CANDIDATE_ID, CANDIDATE_LABEL, CONTENT_HASH, MANUAL_PLAYTEST_RUNS


DEFAULT_OUT = Path("harness/playtest/drafts/2026-06-05_demo_buildcraft_repair_v61_manual_playtest_review_draft.json")
RATING_PLACEHOLDER = "TODO: 1-5"
RATING_FIELDS = [
    "fun_rating",
    "clarity_rating",
    "difficulty_rating",
    "projectile_readability",
    "hit_feedback",
    "xp_pickup_rhythm",
    "boss_spawn_clarity",
    "death_reason_clarity",
]


def placeholder_manual_review() -> dict[str, Any]:
    review: dict[str, Any] = {field: RATING_PLACEHOLDER for field in RATING_FIELDS}
    review.update(
        {
            "notes": "TODO: human reviewer must record concrete moment-to-moment observation.",
            "tags": ["TODO: choose tags such as fun, unclear, too_easy, too_hard, readable, confusing"],
            "next_actions": ["TODO: record concrete code, content, balance, asset, or documentation action."],
        }
    )
    return review


def build_draft(*, reviewer: str = "TODO: human reviewer", reviewed_at: str = "2026-06-05") -> dict[str, Any]:
    return {
        "review_pack_version": 1,
        "draft_notice": "AUTO-GENERATED DRAFT ONLY. A human playtester must replace TODO placeholders before validation or promotion.",
        "source_docs": [
            "docs/02_核心玩法规格.md",
            "docs/04_内容系统与素材库.md",
            "docs/11_测试指标与上线门禁.md",
            "docs/18_完整游戏流程与局外成长.md",
        ],
        "candidate_label": CANDIDATE_LABEL,
        "candidate_id": CANDIDATE_ID,
        "content_hash": CONTENT_HASH,
        "reviewer": reviewer,
        "reviewed_at": reviewed_at,
        "summary": "TODO: human reviewer must summarize current-candidate playtest findings and final decision.",
        "acceptance_decision": "needs_more_runs",
        "allowed_acceptance_decisions": ["accept_candidate", "repair", "needs_more_runs"],
        "required_run_ids": [run.run_id for run in MANUAL_PLAYTEST_RUNS],
        "runs": [
            {
                "run_id": run.run_id,
                "player_skill": run.skill,
                "character_id": run.character_id,
                "map_id": run.map_id,
                "seed": run.seed,
                "intent": run.intent,
                "required_observations": list(run.required_observations),
                "gate_decision": "needs_more_runs",
                "manual_review": placeholder_manual_review(),
            }
            for run in MANUAL_PLAYTEST_RUNS
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=f"Create a {CANDIDATE_LABEL} manual playtest review draft.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--reviewer", default="TODO: human reviewer")
    parser.add_argument("--reviewed-at", default="2026-06-05")
    args = parser.parse_args()

    draft = build_draft(reviewer=args.reviewer, reviewed_at=args.reviewed_at)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(draft, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
