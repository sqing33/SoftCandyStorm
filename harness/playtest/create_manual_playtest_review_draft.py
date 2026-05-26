#!/usr/bin/env python3
"""Create a human playtest review draft from the runtime review pack template.

The generated draft is intentionally incomplete. It covers every required run
id from the template, sets the overall decision to needs_more_runs, and leaves
TODO ratings so the validator rejects it until a human reviewer fills concrete
observations.
"""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any


RATING_PLACEHOLDER = "TODO: 1-5"


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def rating_fields_from_template(template: dict[str, Any]) -> list[str]:
    fields = template.get("manual_review_fields")
    if not isinstance(fields, dict):
        raise ValueError("template manual_review_fields must be an object")
    rating_fields = [
        field
        for field, value in fields.items()
        if value is None and field.endswith("_rating")
        or field
        in {
            "projectile_readability",
            "hit_feedback",
            "xp_pickup_rhythm",
            "boss_spawn_clarity",
            "death_reason_clarity",
        }
    ]
    if not rating_fields:
        raise ValueError("template manual_review_fields must contain rating fields")
    return rating_fields


def placeholder_manual_review(template: dict[str, Any]) -> dict[str, Any]:
    fields = deepcopy(template["manual_review_fields"])
    for field in rating_fields_from_template(template):
        fields[field] = RATING_PLACEHOLDER
    fields["notes"] = "TODO: human reviewer must record concrete moment-to-moment observation."
    fields["tags"] = ["TODO: choose allowed tag"]
    fields["next_actions"] = [
        "TODO: record concrete code, content, balance, asset, or documentation action."
    ]
    return fields


def build_draft(
    template_path: Path,
    candidate_id: str,
    content_hash: str,
    reviewer: str,
    reviewed_at: str,
) -> dict[str, Any]:
    template = load_json_object(template_path)
    runs = template.get("runs")
    if not isinstance(runs, list) or not runs:
        raise ValueError("template runs must be a non-empty list")

    draft_runs: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, run in enumerate(runs):
        if not isinstance(run, dict):
            raise ValueError(f"template runs[{index}] must be an object")
        run_id = run.get("run_id")
        if not is_nonempty_string(run_id):
            raise ValueError(f"template runs[{index}] missing non-empty run_id")
        if str(run_id) in seen:
            raise ValueError(f"template has duplicate run_id `{run_id}`")
        seen.add(str(run_id))
        draft_runs.append(
            {
                "run_id": run_id,
                "player_skill": run.get("player_skill", "TODO: player skill"),
                "intent": run.get("intent", "TODO: run intent"),
                "required_observations": run.get("required_observations", []),
                "gate_decision": "needs_more_runs",
                "manual_review": placeholder_manual_review(template),
            }
        )

    return {
        "review_pack_version": 1,
        "draft_notice": "AUTO-GENERATED DRAFT ONLY. A human playtester must replace TODO placeholders before validation or promotion.",
        "source_template": str(template_path),
        "source_docs": template.get("source_docs", []),
        "candidate_id": candidate_id,
        "content_hash": content_hash,
        "reviewer": reviewer,
        "reviewed_at": reviewed_at,
        "summary": "TODO: human reviewer must summarize 9-run playtest findings and final acceptance decision.",
        "acceptance_decision": "needs_more_runs",
        "allowed_acceptance_decisions": ["accept_candidate", "repair", "needs_more_runs"],
        "runs": draft_runs,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a draft human playtest review JSON.")
    parser.add_argument(
        "--template",
        type=Path,
        default=Path("harness/playtest/runtime_manual_review_template.json"),
        help="Runtime manual review pack template",
    )
    parser.add_argument("--candidate-id", default="TODO: candidate id", help="Candidate id placeholder")
    parser.add_argument("--content-hash", default="TODO: content hash", help="Content hash placeholder")
    parser.add_argument("--reviewer", default="TODO: human reviewer", help="Reviewer placeholder")
    parser.add_argument("--reviewed-at", default="TODO: YYYY-MM-DD", help="Review date placeholder")
    parser.add_argument("--out", type=Path, required=True, help="Output review draft JSON path")
    args = parser.parse_args()

    draft = build_draft(
        args.template,
        args.candidate_id,
        args.content_hash,
        args.reviewer,
        args.reviewed_at,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(draft, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
