#!/usr/bin/env python3
"""Validate human playtest review reports.

This tool is intentionally dependency-free and does not run GameCore. It checks
that manual review evidence is complete enough to support playtest or accepted
content decisions, without pretending that automated captures are human review.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_RUN_IDS = [
    "new_001",
    "new_002",
    "new_003",
    "skilled_001",
    "skilled_002",
    "skilled_003",
    "build_001",
    "build_002",
    "build_003",
]

REQUIRED_RATING_FIELDS = [
    "fun_rating",
    "clarity_rating",
    "difficulty_rating",
    "projectile_readability",
    "hit_feedback",
    "xp_pickup_rhythm",
    "boss_spawn_clarity",
    "death_reason_clarity",
]

ALLOWED_GATE_DECISIONS = {"repair", "playtest_pass", "needs_more_runs"}
ALLOWED_ACCEPTANCE_DECISIONS = {"accept_candidate", "repair", "needs_more_runs"}
FORBIDDEN_GATE_DECISIONS = {"accept_release", "accept_content"}


def required_run_ids(payload: dict[str, Any]) -> list[str]:
    raw_ids = payload.get("required_run_ids")
    if isinstance(raw_ids, list):
        ids = [item for item in raw_ids if isinstance(item, str) and item.strip()]
        if ids:
            return ids
    return REQUIRED_RUN_IDS


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def validate_rating(value: Any) -> bool:
    return isinstance(value, int) and 1 <= value <= 5


def manual_review_for_run(run: dict[str, Any]) -> dict[str, Any]:
    review = run.get("manual_review")
    if isinstance(review, dict):
        return review
    return {}


def validate_runs(payload: dict[str, Any], strict_acceptance: bool) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    runs = payload.get("runs")
    if not isinstance(runs, list):
        return ["`runs` must be a list"], warnings

    expected_run_ids = required_run_ids(payload)
    run_by_id = {
        run.get("run_id"): run
        for run in runs
        if isinstance(run, dict) and isinstance(run.get("run_id"), str)
    }
    missing = [run_id for run_id in expected_run_ids if run_id not in run_by_id]
    if missing:
        errors.append(f"missing required run ids: {', '.join(missing)}")
    if len(runs) < len(expected_run_ids):
        errors.append(f"expected at least {len(expected_run_ids)} runs, got {len(runs)}")

    for index, run in enumerate(runs):
        if not isinstance(run, dict):
            errors.append(f"runs[{index}] must be an object")
            continue
        run_id = run.get("run_id", f"runs[{index}]")
        gate_decision = run.get("gate_decision")
        if gate_decision in FORBIDDEN_GATE_DECISIONS:
            errors.append(f"{run_id}: forbidden gate_decision `{gate_decision}`")
        elif gate_decision not in ALLOWED_GATE_DECISIONS:
            errors.append(f"{run_id}: invalid gate_decision `{gate_decision}`")

        review = manual_review_for_run(run)
        if not review:
            errors.append(f"{run_id}: missing manual_review object")
            continue

        for field in REQUIRED_RATING_FIELDS:
            if not validate_rating(review.get(field)):
                errors.append(f"{run_id}: `{field}` must be an integer from 1 to 5")

        notes = review.get("notes")
        if not isinstance(notes, str) or not notes.strip():
            errors.append(f"{run_id}: notes must contain a concrete human observation")

        tags = review.get("tags")
        if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
            errors.append(f"{run_id}: tags must be a list of strings")

        next_actions = review.get("next_actions")
        if not isinstance(next_actions, list) or not all(
            isinstance(action, str) and action.strip() for action in next_actions
        ):
            errors.append(f"{run_id}: next_actions must be a non-empty list of strings")

        low_fields = [
            field
            for field in REQUIRED_RATING_FIELDS
            if validate_rating(review.get(field)) and int(review[field]) < 3
        ]
        if low_fields and gate_decision == "playtest_pass":
            warnings.append(
                f"{run_id}: playtest_pass has ratings below 3 for {', '.join(low_fields)}"
            )
        if low_fields and not next_actions:
            errors.append(f"{run_id}: ratings below 3 require next_actions")

    if strict_acceptance:
        acceptance_decision = payload.get("acceptance_decision")
        if acceptance_decision not in ALLOWED_ACCEPTANCE_DECISIONS:
            errors.append(f"invalid acceptance_decision `{acceptance_decision}`")
        if acceptance_decision == "accept_candidate":
            if not isinstance(payload.get("candidate_id"), str) or not payload["candidate_id"].strip():
                errors.append("accept_candidate requires candidate_id")
            if not isinstance(payload.get("content_hash"), str) or not payload["content_hash"].strip():
                errors.append("accept_candidate requires content_hash")
            if not isinstance(payload.get("reviewer"), str) or not payload["reviewer"].strip():
                errors.append("accept_candidate requires reviewer")
            if not isinstance(payload.get("reviewed_at"), str) or not payload["reviewed_at"].strip():
                errors.append("accept_candidate requires reviewed_at")
            if not isinstance(payload.get("summary"), str) or not payload["summary"].strip():
                errors.append("accept_candidate requires summary")
            if any(run.get("gate_decision") != "playtest_pass" for run in run_by_id.values()):
                errors.append("accept_candidate requires every provided run to be playtest_pass")

    return errors, warnings


def build_report(path: Path, payload: dict[str, Any], strict_acceptance: bool) -> dict[str, Any]:
    errors, warnings = validate_runs(payload, strict_acceptance)
    expected_run_ids = required_run_ids(payload)
    decision = "manual_review_valid" if not errors else "manual_review_invalid"
    return {
        "report_version": 1,
        "source": str(path),
        "strict_acceptance": strict_acceptance,
        "decision": decision,
        "run_count": len(payload.get("runs", [])) if isinstance(payload.get("runs"), list) else 0,
        "required_run_ids": expected_run_ids,
        "errors": errors,
        "warnings": warnings,
        "limitations": [
            "This validator checks evidence completeness only; it cannot judge whether the game is fun.",
            "Automated runtime capture reports do not satisfy manual review fields unless a human fills the review.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Manual Playtest Review Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Decision: `{report['decision']}`",
        f"- Run count: {report['run_count']}",
        f"- Strict acceptance: {report['strict_acceptance']}",
        "",
        "## Errors",
        "",
    ]
    if report["errors"]:
        lines.extend(f"- {error}" for error in report["errors"])
    else:
        lines.append("- None")
    lines.extend(["", "## Warnings", ""])
    if report["warnings"]:
        lines.extend(f"- {warning}" for warning in report["warnings"])
    else:
        lines.append("- None")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm manual playtest reviews.")
    parser.add_argument("review", type=Path, help="Manual review JSON file")
    parser.add_argument("--strict-acceptance", action="store_true")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON validation report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown validation summary")
    args = parser.parse_args()

    payload = load_json(args.review)
    report = build_report(args.review, payload, args.strict_acceptance)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "manual_review_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
