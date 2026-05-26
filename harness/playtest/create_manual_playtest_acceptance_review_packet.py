#!/usr/bin/env python3
"""Create a final manual playtest acceptance evidence packet.

This packet sits between a human-filled 9-run playtest review and the later
accepted-content lockfile flow. It gathers the review source, strict validation
report, release gate status, and downstream content-lock status. It does not
run Runtime, fill human ratings, promote content, write lockfiles, or approve a
release.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


TODO_MARKERS = ("TODO", "<", ">")
REQUIRED_RUN_IDS = {
    "new_001",
    "new_002",
    "new_003",
    "skilled_001",
    "skilled_002",
    "skilled_003",
    "build_001",
    "build_002",
    "build_003",
}
REQUIRED_EVIDENCE = [
    {
        "field": "manual_review_template",
        "label": "Manual review template",
        "expected": "9-run manual playtest template exists",
        "blocking_if_missing": True,
    },
    {
        "field": "manual_review_source",
        "label": "Manual review source",
        "expected": "human-filled 9-run review source must replace TODO values",
        "blocking_if_missing": True,
    },
    {
        "field": "manual_review_packet",
        "label": "Manual review packet",
        "expected": "human checklist packet exists for reviewer handoff",
        "blocking_if_missing": True,
    },
    {
        "field": "strict_validation_report",
        "label": "Strict validation",
        "expected": "validate_manual_review.py --strict-acceptance JSON report exists",
        "blocking_if_missing": True,
    },
    {
        "field": "release_candidate_evidence",
        "label": "Release candidate evidence",
        "expected": "manual_playtest release gate must pass only after real human acceptance",
        "blocking_if_missing": True,
    },
    {
        "field": "content_acceptance_review_packet",
        "label": "Content acceptance packet",
        "expected": "downstream content acceptance evidence packet status is visible",
        "blocking_if_missing": False,
    },
    {
        "field": "accepted_content_lockfile_report",
        "label": "Accepted content lockfile",
        "expected": "downstream accepted content lockfile status is visible",
        "blocking_if_missing": False,
    },
]


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]


def has_placeholder(value: Any) -> bool:
    if isinstance(value, str):
        return any(marker in value for marker in TODO_MARKERS)
    if isinstance(value, list):
        return any(has_placeholder(item) for item in value)
    if isinstance(value, dict):
        return any(has_placeholder(item) for item in value.values())
    return False


def todo_count(value: Any) -> int:
    if isinstance(value, str):
        return value.count("TODO")
    if isinstance(value, list):
        return sum(todo_count(item) for item in value)
    if isinstance(value, dict):
        return sum(todo_count(item) for item in value.values())
    return 0


def resolve_repo_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def relative_repo_path(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(path)


def is_inside_repo(repo_root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return False
    return True


def markdown_escape(text: Any) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def code(value: Any) -> str:
    return f"`{markdown_escape(value)}`"


def evidence_status(repo_root: Path, value: str | None) -> tuple[str, str | None]:
    if not is_nonempty_string(value):
        return "missing", None
    path = resolve_repo_path(repo_root, str(value))
    if not is_inside_repo(repo_root, path):
        return "outside_repo", None
    if not path.exists():
        return "missing_file", relative_repo_path(repo_root, path)
    return "exists", relative_repo_path(repo_root, path)


def manual_review_source_status(path: Path | None, repo_root: Path) -> dict[str, Any]:
    if path is None or not path.exists():
        return {
            "path": None,
            "candidate_id": "",
            "content_hash": "",
            "acceptance_decision": None,
            "run_count": 0,
            "completed_run_count": 0,
            "missing_run_ids": sorted(REQUIRED_RUN_IDS),
            "todo_count": 0,
            "status": "missing",
        }
    try:
        payload = load_json_object(path)
    except (OSError, ValueError, json.JSONDecodeError):
        return {
            "path": relative_repo_path(repo_root, path),
            "candidate_id": "",
            "content_hash": "",
            "acceptance_decision": None,
            "run_count": 0,
            "completed_run_count": 0,
            "missing_run_ids": sorted(REQUIRED_RUN_IDS),
            "todo_count": 0,
            "status": "invalid_json",
        }
    runs = payload.get("runs")
    run_items = [run for run in runs if isinstance(run, dict)] if isinstance(runs, list) else []
    run_ids = {str(run["run_id"]) for run in run_items if is_nonempty_string(run.get("run_id"))}
    completed = [
        run for run in run_items if run.get("gate_decision") == "playtest_pass" and not has_placeholder(run)
    ]
    count = todo_count(payload)
    if count:
        status = "draft_todo"
    elif payload.get("acceptance_decision") == "accept_candidate" and len(completed) >= len(REQUIRED_RUN_IDS):
        status = "filled_acceptance_candidate"
    else:
        status = "filled_not_accepted"
    return {
        "path": relative_repo_path(repo_root, path),
        "candidate_id": payload.get("candidate_id", ""),
        "content_hash": payload.get("content_hash", ""),
        "acceptance_decision": payload.get("acceptance_decision"),
        "reviewer": payload.get("reviewer", ""),
        "reviewed_at": payload.get("reviewed_at", ""),
        "run_count": len(run_items),
        "completed_run_count": len(completed),
        "missing_run_ids": sorted(REQUIRED_RUN_IDS - run_ids),
        "todo_count": count,
        "status": status,
    }


def strict_validation_status(path: Path | None, repo_root: Path) -> dict[str, Any]:
    if path is None or not path.exists():
        return {
            "path": None,
            "decision": None,
            "strict_acceptance": None,
            "run_count": 0,
            "error_count": 0,
            "warning_count": 0,
            "status": "missing",
        }
    try:
        payload = load_json_object(path)
    except (OSError, ValueError, json.JSONDecodeError):
        return {
            "path": relative_repo_path(repo_root, path),
            "decision": None,
            "strict_acceptance": None,
            "run_count": 0,
            "error_count": 0,
            "warning_count": 0,
            "status": "invalid_json",
        }
    errors = payload.get("errors")
    warnings = payload.get("warnings")
    decision = payload.get("decision")
    return {
        "path": relative_repo_path(repo_root, path),
        "decision": decision,
        "strict_acceptance": payload.get("strict_acceptance"),
        "run_count": payload.get("run_count", 0),
        "error_count": len(errors) if isinstance(errors, list) else 0,
        "warning_count": len(warnings) if isinstance(warnings, list) else 0,
        "status": "valid" if decision == "manual_review_valid" else "invalid",
    }


def release_manual_gate_status(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {"status": "missing", "summary": "", "synthetic": None, "evidence_count": 0}
    try:
        payload = load_json_object(path)
    except (OSError, ValueError, json.JSONDecodeError):
        return {"status": "invalid_json", "summary": "", "synthetic": None, "evidence_count": 0}
    gates = payload.get("gates")
    if not isinstance(gates, list):
        return {"status": "missing_gate", "summary": "", "synthetic": None, "evidence_count": 0}
    for gate in gates:
        if isinstance(gate, dict) and gate.get("id") == "manual_playtest":
            evidence = string_list(gate.get("evidence_paths"))
            return {
                "status": gate.get("status"),
                "summary": gate.get("summary", ""),
                "synthetic": gate.get("synthetic"),
                "evidence_count": len(evidence),
            }
    return {"status": "missing_gate", "summary": "", "synthetic": None, "evidence_count": 0}


def report_decision(path: Path | None) -> str | None:
    if path is None or not path.exists():
        return None
    try:
        payload = load_json_object(path)
    except (OSError, ValueError, json.JSONDecodeError):
        return None
    return payload.get("decision") if is_nonempty_string(payload.get("decision")) else None


def build_packet(
    repo_root: Path,
    evidence_paths: dict[str, str],
) -> dict[str, Any]:
    errors: list[str] = []
    evidence = []
    resolved_paths: dict[str, Path | None] = {}
    for requirement in REQUIRED_EVIDENCE:
        field = str(requirement["field"])
        status, resolved_text = evidence_status(repo_root, evidence_paths.get(field))
        resolved_paths[field] = resolve_repo_path(repo_root, evidence_paths[field]) if status == "exists" else None
        evidence.append(
            {
                "field": field,
                "label": requirement["label"],
                "value": evidence_paths.get(field),
                "status": status,
                "resolved_path": resolved_text,
                "expected": requirement["expected"],
                "blocking_if_missing": requirement["blocking_if_missing"],
            }
        )
        if status != "exists" and requirement["blocking_if_missing"]:
            errors.append(f"{field} evidence must exist")

    manual_status = manual_review_source_status(resolved_paths.get("manual_review_source"), repo_root)
    validation_status = strict_validation_status(resolved_paths.get("strict_validation_report"), repo_root)
    release_gate = release_manual_gate_status(resolved_paths.get("release_candidate_evidence"))
    content_acceptance_decision = report_decision(resolved_paths.get("content_acceptance_review_packet"))
    lockfile_decision = report_decision(resolved_paths.get("accepted_content_lockfile_report"))

    blockers: list[str] = []
    if manual_status["todo_count"]:
        blockers.append("manual review source still contains TODO placeholders")
    if manual_status["acceptance_decision"] != "accept_candidate":
        blockers.append("manual review has not accepted the candidate")
    if manual_status["missing_run_ids"]:
        blockers.append("manual review is missing required run ids")
    if manual_status["completed_run_count"] < len(REQUIRED_RUN_IDS):
        blockers.append("manual review has fewer than 9 completed playtest_pass runs")
    if validation_status["decision"] != "manual_review_valid":
        blockers.append(f"strict manual review validation is `{validation_status['decision']}`")
    if release_gate["status"] != "pass":
        blockers.append(f"release candidate manual_playtest gate is `{release_gate['status']}`")

    if errors:
        decision = "manual_playtest_acceptance_review_packet_invalid"
    elif blockers:
        decision = "manual_playtest_acceptance_review_packet_needs_evidence"
    else:
        decision = "manual_playtest_acceptance_review_packet_ready_for_content_lock"

    return {
        "report_version": 1,
        "repo_root": str(repo_root),
        "decision": decision,
        "candidate_id": manual_status["candidate_id"],
        "content_hash": manual_status["content_hash"],
        "evidence_count": len(evidence),
        "existing_evidence_count": sum(1 for item in evidence if item["status"] == "exists"),
        "errors": errors,
        "blockers": blockers,
        "evidence": evidence,
        "manual_review_status": manual_status,
        "strict_validation_status": validation_status,
        "release_candidate_manual_playtest_gate": release_gate,
        "downstream_status": {
            "content_acceptance_review_packet": content_acceptance_decision,
            "accepted_content_lockfile": lockfile_decision,
        },
        "required_next_steps": [
            "Run the 9 human playtest sessions and replace every TODO rating, note, tag, and next action.",
            "Run validate_manual_review.py --strict-acceptance and keep a manual_review_valid JSON/Markdown report.",
            "Update the release candidate manual_playtest gate only after real human evidence exists.",
            "Use the validated manual review as evidence for content acceptance and accepted content lockfile generation.",
        ],
        "limitations": [
            "This packet organizes manual playtest acceptance evidence only.",
            "It does not run Runtime, inspect gameplay, fill human review fields, promote content, write lockfiles, or approve release.",
            "Automated capture, Bot results, and fixture reviews cannot replace the real human review source.",
        ],
    }


def write_markdown(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Manual Playtest Acceptance Review Packet",
        "",
        f"- Decision: `{packet['decision']}`",
        f"- Candidate id: `{packet['candidate_id']}`",
        f"- Content hash: `{packet['content_hash']}`",
        f"- Evidence files: {packet['existing_evidence_count']} / {packet['evidence_count']}",
        f"- Strict validation: `{packet['strict_validation_status']['decision']}`",
        f"- RC manual playtest gate: `{packet['release_candidate_manual_playtest_gate']['status']}`",
        f"- Downstream content acceptance: `{packet['downstream_status']['content_acceptance_review_packet']}`",
        f"- Downstream accepted content lockfile: `{packet['downstream_status']['accepted_content_lockfile']}`",
        "",
        "## Evidence",
        "",
        "| Field | Status | Expected | Path |",
        "|---|---|---|---|",
    ]
    for item in packet["evidence"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    code(item["field"]),
                    code(item["status"]),
                    markdown_escape(item["expected"]),
                    code(item["resolved_path"] or item["value"]),
                ]
            )
            + " |"
        )

    review = packet["manual_review_status"]
    validation = packet["strict_validation_status"]
    lines.extend(["", "## Manual Review Status", ""])
    lines.append(f"- Source status: `{review['status']}`")
    lines.append(f"- Acceptance decision: `{review['acceptance_decision']}`")
    lines.append(f"- Runs: {review['completed_run_count']} completed / {review['run_count']} present")
    lines.append(f"- Missing run ids: {', '.join(code(run_id) for run_id in review['missing_run_ids']) or 'None'}")
    lines.append(f"- TODO count: `{review['todo_count']}`")
    lines.append(f"- Reviewer: `{review.get('reviewer', '')}`")
    lines.append(f"- Reviewed at: `{review.get('reviewed_at', '')}`")

    lines.extend(["", "## Strict Validation", ""])
    lines.append(f"- Status: `{validation['status']}`")
    lines.append(f"- Decision: `{validation['decision']}`")
    lines.append(f"- Strict acceptance: `{validation['strict_acceptance']}`")
    lines.append(f"- Error count: `{validation['error_count']}`")
    lines.append(f"- Warning count: `{validation['warning_count']}`")

    lines.extend(["", "## Blockers", ""])
    if packet["blockers"]:
        lines.extend(f"- {blocker}" for blocker in packet["blockers"])
    else:
        lines.append("- None")

    lines.extend(["", "## Errors", ""])
    if packet["errors"]:
        lines.extend(f"- {error}" for error in packet["errors"])
    else:
        lines.append("- None")

    lines.extend(["", "## Required Next Steps", ""])
    lines.extend(f"- {item}" for item in packet["required_next_steps"])
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in packet["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def default_evidence_paths() -> dict[str, str]:
    return {
        "manual_review_template": "harness/playtest/runtime_manual_review_template.json",
        "manual_review_source": "harness/playtest/drafts/2026-05-26_runtime_manual_playtest_review_draft.json",
        "manual_review_packet": "harness/reports/2026-05-26_runtime_manual_playtest_review_packet_001/summary.md",
        "strict_validation_report": "harness/reports/2026-05-26_runtime_manual_playtest_strict_validation_current_local_001/manual_review_validation.json",
        "release_candidate_evidence": "harness/release/current_local_rc_evidence.json",
        "content_acceptance_review_packet": "harness/reports/2026-05-26_phase4_content_acceptance_review_packet_001/content_acceptance_review_packet.json",
        "accepted_content_lockfile_report": "harness/reports/2026-05-26_accepted_content_lockfile_current_local_001/accepted_content_lockfile.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a manual playtest acceptance evidence packet.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--markdown", type=Path, default=None)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    packet = build_packet(repo_root, default_evidence_paths())
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(packet, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(packet, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
