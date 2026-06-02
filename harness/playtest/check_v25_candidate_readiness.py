#!/usr/bin/env python3
"""Summarize v25 candidate readiness across design review and playtest gates."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
CONTENT_REVIEW_DIR = SCRIPT_DIR.parent / "content_review"
if str(CONTENT_REVIEW_DIR) not in sys.path:
    sys.path.insert(0, str(CONTENT_REVIEW_DIR))

from check_v25_design_review_status import build_report as build_design_review_report  # noqa: E402
from check_v25_manual_playtest_status import build_report as build_manual_playtest_report  # noqa: E402
from create_v25_content_repair_action_plan import build_plan as build_content_repair_plan  # noqa: E402
from run_v25_manual_playtest import CANDIDATE_ID, CONTENT_HASH, first_missing_run, shell_quote, build_runtime_command  # noqa: E402


def next_manual_command(repo_root: Path) -> str | None:
    run = first_missing_run(repo_root)
    if run is None:
        return None
    return f"python3 harness/playtest/run_v25_manual_playtest.py {run.run_id}"


def next_manual_runtime_command(repo_root: Path) -> str | None:
    run = first_missing_run(repo_root)
    if run is None:
        return None
    return shell_quote(build_runtime_command(run))


def build_report(repo_root: Path) -> dict[str, Any]:
    design = build_design_review_report(repo_root)
    manual = build_manual_playtest_report(repo_root)
    repair_plan = build_content_repair_plan(repo_root)

    design_ready = design["decision"] == "design_review_ready_for_validation"
    manual_ready = manual["decision"] == "manual_playtest_ready_for_strict_validation"
    blockers: list[str] = []
    next_actions: list[str] = []
    if not design_ready:
        blockers.append("design_review_incomplete")
        next_actions.append(
            "Fill the v25 design review draft for pudding-turret, then run "
            "`python3 harness/content_review/check_v25_design_review_status.py --allow-incomplete`."
        )
    else:
        next_actions.append(
            "Run `python3 harness/content_review/validate_content_candidate_design_review.py "
            "harness/content_review/drafts/2026-06-02_demo_buildcraft_repair_v25_full_pack_design_review_draft.json "
            "--repo-root .`."
        )

    missing_command = next_manual_command(repo_root)
    if not manual_ready:
        blockers.append("manual_playtest_incomplete")
        if missing_command is not None:
            next_actions.append(f"Run the next human playtest with `{missing_command}`.")
        else:
            next_actions.append(
                "Fill the v25 manual playtest draft TODOs, then run "
                "`python3 harness/playtest/check_v25_manual_playtest_status.py --allow-incomplete`."
            )
    else:
        next_actions.append(
            "Run strict manual playtest validation with `python3 harness/playtest/validate_manual_review.py "
            "harness/playtest/drafts/2026-06-02_demo_buildcraft_repair_v25_manual_playtest_review_draft.json "
            "--strict-acceptance`."
        )
    if repair_plan["action_items"]:
        first_repair_command = repair_plan["next_commands"][0] if repair_plan["next_commands"] else None
        if first_repair_command:
            next_actions.append(f"Start v25 playable-content repair triage with `{first_repair_command}`.")
        next_actions.append(
            "Refresh the repair triage packet with "
            "`python3 harness/playtest/create_v25_content_repair_action_plan.py` after new local reports."
        )

    decision = (
        "candidate_ready_for_human_validation"
        if design_ready and manual_ready
        else "candidate_waiting_for_human_evidence"
    )
    return {
        "report_version": 1,
        "candidate_id": CANDIDATE_ID,
        "content_hash": CONTENT_HASH,
        "decision": decision,
        "summary": {
            "design_review_decision": design["decision"],
            "manual_playtest_decision": manual["decision"],
            "design_review_ready": design_ready,
            "manual_playtest_ready": manual_ready,
            "manual_reports": manual["summary"]["existing_report_count"],
            "manual_required_reports": manual["summary"]["required_run_count"],
            "next_manual_command": missing_command,
            "next_manual_runtime_command": next_manual_runtime_command(repo_root),
            "content_repair_plan_decision": repair_plan["decision"],
            "content_repair_action_items": repair_plan["summary"]["action_item_count"],
            "content_repair_missing_reports": repair_plan["summary"]["missing_report_count"],
            "content_repair_coverage_gaps": repair_plan["summary"].get("content_coverage_gap_count", 0),
            "next_repair_commands": repair_plan["next_commands"][:5],
        },
        "blockers": blockers,
        "next_actions": next_actions,
        "design_review": {
            "decision": design["decision"],
            "draft_has_placeholder": design["summary"]["draft_has_placeholder"],
            "expected_content_ids": design["expected_content_ids"],
            "placeholder_reviews": design["placeholder_reviews"],
            "errors": design["errors"],
        },
        "manual_playtest": {
            "decision": manual["decision"],
            "existing_report_count": manual["summary"]["existing_report_count"],
            "required_run_count": manual["summary"]["required_run_count"],
            "draft_has_todo": manual["summary"]["draft_has_todo"],
            "missing_reports": manual["missing_reports"],
            "draft_todo_runs": manual["draft_todo_runs"],
            "errors": manual["errors"],
        },
        "content_repair_plan": {
            "decision": repair_plan["decision"],
            "action_item_count": repair_plan["summary"]["action_item_count"],
            "missing_report_count": repair_plan["summary"]["missing_report_count"],
            "report_attention_count": repair_plan["summary"]["report_attention_count"],
            "objective_metric_risk_count": repair_plan["summary"]["objective_metric_risk_count"],
            "content_coverage_gap_count": repair_plan["summary"].get("content_coverage_gap_count", 0),
            "next_commands": repair_plan["next_commands"][:5],
        },
        "limitations": [
            "This readiness report only combines local status checks.",
            "It does not fill human review evidence, play the game, judge fun, or promote content.",
            "The content repair plan is triage only; it does not add acceptance evidence or promote v25.",
            "v25 must not be copied into content/base_demo, accepted_content, or Runtime official content before human gates pass.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# v25 Candidate Readiness",
        "",
        f"- Candidate id: `{report['candidate_id']}`",
        f"- Content hash: `{report['content_hash']}`",
        f"- Decision: `{report['decision']}`",
        f"- Design review: `{summary['design_review_decision']}`",
        f"- Manual playtest: `{summary['manual_playtest_decision']}`",
        f"- Manual reports: `{summary['manual_reports']}` / `{summary['manual_required_reports']}`",
        "",
        "## Next Actions",
        "",
    ]
    lines.extend(f"- {item}" for item in report["next_actions"])

    lines.extend(["", "## Next Manual Command", ""])
    if summary["next_manual_command"] is None:
        lines.append("- None")
    else:
        lines.append(f"- `{summary['next_manual_command']}`")
        lines.append(f"- Runtime command: `{summary['next_manual_runtime_command']}`")

    lines.extend(["", "## Blockers", ""])
    if report["blockers"]:
        lines.extend(f"- `{item}`" for item in report["blockers"])
    else:
        lines.append("- None")

    lines.extend(["", "## Design Review", ""])
    design = report["design_review"]
    lines.append(f"- Draft has placeholder: `{design['draft_has_placeholder']}`")
    lines.append(f"- Placeholder reviews: `{', '.join(design['placeholder_reviews']) or 'none'}`")

    lines.extend(["", "## Manual Playtest", ""])
    manual = report["manual_playtest"]
    lines.append(f"- Draft has TODO: `{manual['draft_has_todo']}`")
    lines.append(f"- Missing reports: `{len(manual['missing_reports'])}`")
    if manual["missing_reports"]:
        lines.extend(f"- `{item}`" for item in manual["missing_reports"])

    lines.extend(["", "## Content Repair Plan", ""])
    repair = report["content_repair_plan"]
    lines.append(f"- Decision: `{repair['decision']}`")
    lines.append(f"- Action items: `{repair['action_item_count']}`")
    lines.append(f"- Missing reports: `{repair['missing_report_count']}`")
    lines.append(f"- Report attention: `{repair['report_attention_count']}`")
    lines.append(f"- Objective metric risks: `{repair['objective_metric_risk_count']}`")
    lines.append(f"- Content coverage gaps: `{repair['content_coverage_gap_count']}`")
    lines.append("- Next commands:")
    if repair["next_commands"]:
        lines.extend(f"  - `{item}`" for item in repair["next_commands"])
    else:
        lines.append("  - None")

    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize v25 candidate readiness.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--markdown", type=Path, default=None)
    parser.add_argument("--allow-incomplete", action="store_true")
    args = parser.parse_args()

    report = build_report(args.repo_root)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))

    if report["decision"] == "candidate_ready_for_human_validation" or args.allow_incomplete:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
