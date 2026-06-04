#!/usr/bin/env python3
"""Check local evidence status for the current-candidate manual playtest matrix."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_current_manual_playtest_review_draft import DEFAULT_OUT as DEFAULT_DRAFT
from current_candidate import CANDIDATE_ID, CANDIDATE_LABEL, CONTENT_HASH, MANUAL_PLAYTEST_RUNS


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def has_todo(value: Any) -> bool:
    if isinstance(value, str):
        return "TODO" in value
    if isinstance(value, list):
        return any(has_todo(item) for item in value)
    if isinstance(value, dict):
        return any(has_todo(item) for item in value.values())
    return False


def draft_run_index(draft: dict[str, Any]) -> dict[str, dict[str, Any]]:
    runs = draft.get("runs")
    if not isinstance(runs, list):
        return {}
    indexed: dict[str, dict[str, Any]] = {}
    for run in runs:
        if isinstance(run, dict) and isinstance(run.get("run_id"), str):
            indexed[run["run_id"]] = run
    return indexed


def build_report(repo_root: Path, draft_path: Path = DEFAULT_DRAFT) -> dict[str, Any]:
    resolved_draft = repo_root / draft_path
    draft_exists = resolved_draft.exists()
    draft = load_json_object(resolved_draft) if draft_exists else {}
    draft_runs = draft_run_index(draft)

    run_statuses: list[dict[str, Any]] = []
    missing_reports: list[str] = []
    missing_draft_runs: list[str] = []
    draft_todo_runs: list[str] = []
    for run in MANUAL_PLAYTEST_RUNS:
        report_path = repo_root / run.report_path
        draft_run = draft_runs.get(run.run_id)
        if not report_path.exists():
            missing_reports.append(str(run.report_path))
        if draft_run is None:
            missing_draft_runs.append(run.run_id)
        elif has_todo(draft_run):
            draft_todo_runs.append(run.run_id)
        run_statuses.append(
            {
                "run_id": run.run_id,
                "skill": run.skill,
                "character_id": run.character_id,
                "map_id": run.map_id,
                "seed": run.seed,
                "intent": run.intent,
                "report": str(run.report_path),
                "report_exists": report_path.exists(),
                "draft_run_exists": draft_run is not None,
                "draft_has_todo": bool(draft_run is not None and has_todo(draft_run)),
            }
        )

    draft_has_todo = has_todo(draft) if draft_exists else True
    errors: list[str] = []
    if not draft_exists:
        errors.append(f"review draft missing: {draft_path}")
    if missing_reports:
        errors.append(f"{len(missing_reports)} playtest reports are missing")
    if missing_draft_runs:
        errors.append(f"{len(missing_draft_runs)} draft runs are missing")
    if draft_has_todo:
        errors.append("review draft still contains TODO placeholders")
    if draft.get("candidate_id") != CANDIDATE_ID:
        errors.append("review draft candidate_id does not match current candidate")
    if draft.get("content_hash") != CONTENT_HASH:
        errors.append("review draft content_hash does not match current content hash")

    decision = "manual_playtest_ready_for_strict_validation" if not errors else "manual_playtest_incomplete"
    return {
        "report_version": 1,
        "candidate_label": CANDIDATE_LABEL,
        "candidate_id": CANDIDATE_ID,
        "content_hash": CONTENT_HASH,
        "draft": str(draft_path),
        "decision": decision,
        "summary": {
            "required_run_count": len(MANUAL_PLAYTEST_RUNS),
            "existing_report_count": len(MANUAL_PLAYTEST_RUNS) - len(missing_reports),
            "missing_report_count": len(missing_reports),
            "draft_exists": draft_exists,
            "draft_has_todo": draft_has_todo,
            "acceptance_decision": draft.get("acceptance_decision", ""),
        },
        "missing_reports": missing_reports,
        "missing_draft_runs": missing_draft_runs,
        "draft_todo_runs": draft_todo_runs,
        "runs": run_statuses,
        "errors": errors,
        "limitations": [
            "This checker only inspects local report file presence and draft TODO status.",
            "It does not play the game, judge fun, validate ratings, or approve content.",
            "Strict acceptance still requires human-filled review evidence and validate_manual_review.py --strict-acceptance.",
            "The current candidate must not be copied into accepted_content or Runtime official content before human gates pass.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    summary = report["summary"]
    lines = [
        f"# {report['candidate_label']} Manual Playtest Status",
        "",
        f"- Candidate id: `{report['candidate_id']}`",
        f"- Content hash: `{report['content_hash']}`",
        f"- Draft: `{report['draft']}`",
        f"- Decision: `{report['decision']}`",
        f"- Reports: `{summary['existing_report_count']}` / `{summary['required_run_count']}`",
        f"- Draft has TODO: `{summary['draft_has_todo']}`",
        f"- Acceptance decision: `{summary['acceptance_decision']}`",
        "",
        "## Runs",
        "",
        "| Run | Skill | Character | Map | Seed | Report Exists | Draft TODO |",
        "|---|---|---|---|---:|---|---|",
    ]
    for run in report["runs"]:
        lines.append(
            f"| `{run['run_id']}` | `{run['skill']}` | `{run['character_id']}` | `{run['map_id']}` | "
            f"{run['seed']} | `{run['report_exists']}` | `{run['draft_has_todo']}` |"
        )

    lines.extend(["", "## Missing Reports", ""])
    if report["missing_reports"]:
        lines.extend(f"- `{item}`" for item in report["missing_reports"])
    else:
        lines.append("- None")

    lines.extend(["", "## Errors", ""])
    if report["errors"]:
        lines.extend(f"- {error}" for error in report["errors"])
    else:
        lines.append("- None")

    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=f"Check {CANDIDATE_LABEL} manual playtest local evidence status.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--draft", type=Path, default=DEFAULT_DRAFT)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--markdown", type=Path, default=None)
    parser.add_argument("--allow-incomplete", action="store_true")
    args = parser.parse_args()

    report = build_report(args.repo_root, args.draft)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))

    if report["decision"] == "manual_playtest_ready_for_strict_validation" or args.allow_incomplete:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
