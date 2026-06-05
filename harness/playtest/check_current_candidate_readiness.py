#!/usr/bin/env python3
"""Summarize current candidate readiness across human evidence gates."""

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

from check_current_design_review_status import DEFAULT_DRAFT as DESIGN_DRAFT  # noqa: E402
from check_current_design_review_status import build_report as build_design_review_report  # noqa: E402
from check_current_manual_playtest_status import build_report as build_manual_playtest_report  # noqa: E402
from create_current_manual_playtest_review_draft import DEFAULT_OUT as PLAYTEST_DRAFT  # noqa: E402
from current_candidate import CANDIDATE_ID, CANDIDATE_LABEL, CONTENT_HASH, shell_quote  # noqa: E402
from run_current_manual_playtest import build_manual_playtest_command, first_missing_run  # noqa: E402


def next_manual_command(repo_root: Path) -> str | None:
    run = first_missing_run(repo_root)
    if run is None:
        return None
    return f"python3 harness/playtest/run_current_manual_playtest.py {run.run_id}"


def next_manual_runtime_command(repo_root: Path) -> str | None:
    run = first_missing_run(repo_root)
    if run is None:
        return None
    return shell_quote(build_manual_playtest_command(run))


def build_report(repo_root: Path) -> dict[str, Any]:
    design = build_design_review_report(repo_root)
    manual = build_manual_playtest_report(repo_root)

    design_ready = design["decision"] == "design_review_ready_for_validation"
    manual_ready = manual["decision"] == "manual_playtest_ready_for_strict_validation"
    blockers: list[str] = []
    next_actions: list[str] = []
    if not design_ready:
        blockers.append("design_review_incomplete")
        next_actions.append(
            "Fill the current candidate design review draft, then run "
            "`python3 harness/content_review/check_current_design_review_status.py --allow-incomplete`."
        )
    else:
        next_actions.append(
            "Run `python3 harness/content_review/validate_content_candidate_design_review.py "
            f"{DESIGN_DRAFT} --repo-root .`."
        )

    missing_command = next_manual_command(repo_root)
    if not manual_ready:
        blockers.append("manual_playtest_incomplete")
        if missing_command is not None:
            next_actions.append(f"Run the next human playtest with `{missing_command}`.")
        else:
            next_actions.append(
                "Fill the current manual playtest draft TODOs, then run "
                "`python3 harness/playtest/check_current_manual_playtest_status.py --allow-incomplete`."
            )
    else:
        next_actions.append(
            "Run strict manual playtest validation with `python3 harness/playtest/validate_manual_review.py "
            f"{PLAYTEST_DRAFT} --strict-acceptance`."
        )

    decision = (
        "candidate_ready_for_human_validation"
        if design_ready and manual_ready
        else "candidate_waiting_for_human_evidence"
    )
    return {
        "report_version": 1,
        "candidate_label": CANDIDATE_LABEL,
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
        "limitations": [
            "This readiness report only combines local human-evidence status checks.",
            "It does not fill human review evidence, play the game, judge fun, or promote content.",
            "Current candidate content must stay out of content/base_demo, accepted_content, and Runtime official content until human gates pass.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    summary = report["summary"]
    lines = [
        f"# {report['candidate_label']} Candidate Readiness",
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

    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=f"Summarize {CANDIDATE_LABEL} candidate readiness.")
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
