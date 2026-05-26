#!/usr/bin/env python3
"""Validate accepted content lockfiles and their human acceptance evidence.

This pure Python gate checks the shape and evidence references produced by the
Rust `lock-accepted-content` command. It does not promote candidates, compute
GameCore content hashes, run Harness simulations, copy content into Runtime, or
approve a release package.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


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
TODO_MARKERS = ("TODO", "<", ">")


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


def is_content_hash(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("fnv1a64:") and len(value) > len("fnv1a64:")


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


def validate_optional_repo_path(
    repo_root: Path,
    label: str,
    value: Any,
    errors: list[str],
    *,
    require_exists: bool = True,
) -> Path | None:
    if not is_nonempty_string(value):
        errors.append(f"{label} must be non-empty")
        return None
    if has_placeholder(value):
        errors.append(f"{label} must not contain TODO or placeholder markers")
        return None
    path = resolve_repo_path(repo_root, str(value))
    if not is_inside_repo(repo_root, path):
        errors.append(f"{label} must stay inside repository: {value}")
        return None
    if require_exists and not path.exists():
        errors.append(f"{label} does not exist: {value}")
        return None
    return path


def review_string(payload: dict[str, Any], key: str) -> str | None:
    value = payload.get(key)
    if is_nonempty_string(value):
        return str(value).strip()
    human_review = payload.get("human_review")
    if isinstance(human_review, dict) and is_nonempty_string(human_review.get(key)):
        return str(human_review[key]).strip()
    return None


def run_review_value(run: dict[str, Any], key: str) -> Any:
    if key in run:
        return run[key]
    manual_review = run.get("manual_review")
    if isinstance(manual_review, dict):
        return manual_review.get(key)
    return None


def validate_manual_review(
    review_path: Path | None,
    candidate_id: str,
    content_hash: str,
    repo_root: Path,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if review_path is None:
        return {
            "path": None,
            "decision": None,
            "completed_run_count": 0,
            "average_rating": None,
            "errors": ["manual review path is missing"],
            "warnings": warnings,
        }

    try:
        payload = load_json_object(review_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return {
            "path": relative_repo_path(repo_root, review_path),
            "decision": None,
            "completed_run_count": 0,
            "average_rating": None,
            "errors": [f"manual review is invalid JSON: {error}"],
            "warnings": warnings,
        }

    if has_placeholder(payload):
        errors.append("manual review must not contain TODO or placeholder markers")
    if review_string(payload, "candidate_id") != candidate_id:
        errors.append("manual review candidate_id must match lock entry")
    if review_string(payload, "content_hash") != content_hash:
        errors.append("manual review content_hash must match lock entry")
    for field in ("reviewer", "reviewed_at", "summary"):
        if not is_nonempty_string(review_string(payload, field)):
            errors.append(f"manual review must include {field}")
    decision = review_string(payload, "acceptance_decision") or review_string(payload, "decision")
    if decision != "accept_candidate":
        errors.append("manual review acceptance_decision must be `accept_candidate`")

    runs = payload.get("runs")
    if not isinstance(runs, list):
        errors.append("manual review must include runs array")
        runs = []

    seen_run_ids: set[str] = set()
    completed_run_count = 0
    rating_sum = 0.0
    rating_count = 0
    for index, run in enumerate(runs):
        if not isinstance(run, dict):
            errors.append(f"runs[{index}] must be an object")
            continue
        run_id = run_review_value(run, "run_id")
        if not is_nonempty_string(run_id):
            errors.append(f"runs[{index}] must include run_id")
            continue
        run_label = str(run_id)
        seen_run_ids.add(run_label)
        gate_decision = run_review_value(run, "gate_decision") or run_review_value(run, "decision")
        run_complete = True
        if gate_decision != "playtest_pass":
            errors.append(f"run `{run_label}` gate_decision must be `playtest_pass`")
            run_complete = False
        for field in RATING_FIELDS:
            rating = run_review_value(run, field)
            if not isinstance(rating, int) or isinstance(rating, bool):
                errors.append(f"run `{run_label}` rating `{field}` must be an integer")
                run_complete = False
                continue
            rating_sum += rating
            rating_count += 1
            if not 1 <= rating <= 5:
                errors.append(f"run `{run_label}` rating `{field}` must be 1-5")
                run_complete = False
            elif rating < 3:
                errors.append(f"run `{run_label}` rating `{field}` must be at least 3 for acceptance")
                run_complete = False
        if not is_nonempty_string(run_review_value(run, "notes")):
            errors.append(f"run `{run_label}` must include notes")
            run_complete = False
        if not string_list(run_review_value(run, "next_actions")):
            errors.append(f"run `{run_label}` must include next_actions")
            run_complete = False
        if run_complete:
            completed_run_count += 1

    missing_runs = sorted(REQUIRED_RUN_IDS - seen_run_ids)
    if missing_runs:
        errors.append(f"manual review is missing required runs: {', '.join(missing_runs)}")
    average_rating = rating_sum / rating_count if rating_count else None
    return {
        "path": relative_repo_path(repo_root, review_path),
        "decision": decision,
        "completed_run_count": completed_run_count,
        "average_rating": average_rating,
        "errors": errors,
        "warnings": warnings,
    }


def validate_acceptance_gate(
    gate_path: Path | None,
    candidate_id: str,
    content_hash: str,
    entry: dict[str, Any],
    repo_root: Path,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if gate_path is None:
        return {
            "path": None,
            "manual_review_file": None,
            "completed_run_count": None,
            "average_rating": None,
            "errors": ["acceptance gate path is missing"],
            "warnings": warnings,
        }
    try:
        payload = load_json_object(gate_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return {
            "path": relative_repo_path(repo_root, gate_path),
            "manual_review_file": None,
            "completed_run_count": None,
            "average_rating": None,
            "errors": [f"acceptance gate is invalid JSON: {error}"],
            "warnings": warnings,
        }

    if has_placeholder(payload):
        errors.append("acceptance gate must not contain TODO or placeholder markers")
    if payload.get("candidate_id") != candidate_id:
        errors.append("acceptance gate candidate_id must match lock entry")
    if payload.get("decision") != "accept_candidate":
        errors.append("acceptance gate decision must be `accept_candidate`")
    if payload.get("category") != "human_playtest_passed":
        errors.append("acceptance gate category must be `human_playtest_passed`")
    if payload.get("content_hash") != content_hash:
        errors.append("acceptance gate content_hash must match lock entry")

    manual_review_file = payload.get("manual_review_file")
    manual_review_path = validate_optional_repo_path(
        repo_root,
        "acceptance gate manual_review_file",
        manual_review_file,
        errors,
    )
    entry_manual_review = entry.get("manual_review_file")
    if is_nonempty_string(entry_manual_review) and is_nonempty_string(manual_review_file):
        entry_review_path = resolve_repo_path(repo_root, str(entry_manual_review))
        gate_review_path = resolve_repo_path(repo_root, str(manual_review_file))
        if entry_review_path.resolve() != gate_review_path.resolve():
            errors.append("acceptance gate manual_review_file must match lock entry")

    completed_run_count = payload.get("completed_run_count")
    if not isinstance(completed_run_count, int) or isinstance(completed_run_count, bool):
        errors.append("acceptance gate completed_run_count must be an integer")
    elif completed_run_count < len(REQUIRED_RUN_IDS):
        errors.append(f"acceptance gate completed_run_count must be at least {len(REQUIRED_RUN_IDS)}")
    elif entry.get("completed_run_count") is not None and entry.get("completed_run_count") != completed_run_count:
        errors.append("acceptance gate completed_run_count must match lock entry")

    average_rating = payload.get("average_rating")
    if not isinstance(average_rating, (int, float)) or isinstance(average_rating, bool):
        errors.append("acceptance gate average_rating must be numeric")
    elif not 1 <= float(average_rating) <= 5:
        errors.append("acceptance gate average_rating must be between 1 and 5")
    elif entry.get("average_rating") is not None and abs(float(entry["average_rating"]) - float(average_rating)) > 0.001:
        errors.append("acceptance gate average_rating must match lock entry")

    return {
        "path": relative_repo_path(repo_root, gate_path),
        "manual_review_file": relative_repo_path(repo_root, manual_review_path) if manual_review_path else None,
        "completed_run_count": completed_run_count if isinstance(completed_run_count, int) else None,
        "average_rating": float(average_rating) if isinstance(average_rating, (int, float)) and not isinstance(average_rating, bool) else None,
        "errors": errors,
        "warnings": warnings,
    }


def validate_entry(
    repo_root: Path,
    entry: Any,
    index: int,
) -> tuple[dict[str, Any] | None, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(entry, dict):
        return None, [f"entries[{index}] must be an object"], warnings

    candidate_id = entry.get("id")
    label = str(candidate_id) if is_nonempty_string(candidate_id) else f"entries[{index}]"
    if not is_nonempty_string(candidate_id):
        errors.append(f"{label}: id must be non-empty")
        candidate_id = label
    elif has_placeholder(candidate_id):
        errors.append(f"{label}: id must not contain TODO or placeholder markers")
    candidate_id = str(candidate_id)

    status = entry.get("status")
    if status not in {"locked", "blocked"}:
        errors.append(f"{label}: status must be `locked` or `blocked`")
    entry_errors = entry.get("errors")
    if not isinstance(entry_errors, list):
        errors.append(f"{label}: errors must be a list")
        entry_errors = []
    if status == "locked" and entry_errors:
        errors.append(f"{label}: locked entry must not include errors")
    if status == "blocked" and not entry_errors:
        errors.append(f"{label}: blocked entry must include errors")

    source_path = validate_optional_repo_path(repo_root, f"{label}: source", entry.get("source"), errors)
    runtime_content_path = validate_optional_repo_path(
        repo_root,
        f"{label}: runtime_content_dir",
        entry.get("runtime_content_dir"),
        errors,
        require_exists=False,
    )
    if source_path is not None and runtime_content_path is not None and status == "locked":
        if source_path.resolve() != runtime_content_path.resolve():
            warnings.append(f"{label}: runtime_content_dir differs from source; ensure packaging copies locked content")

    content_hash = entry.get("content_hash")
    if not is_content_hash(content_hash):
        errors.append(f"{label}: content_hash must look like `fnv1a64:<hex>`")
        content_hash_text = ""
    else:
        content_hash_text = str(content_hash)
    object_count = entry.get("object_count")
    if not isinstance(object_count, int) or isinstance(object_count, bool) or object_count <= 0:
        errors.append(f"{label}: object_count must be a positive integer")

    gate_path = validate_optional_repo_path(
        repo_root,
        f"{label}: acceptance_gate",
        entry.get("acceptance_gate"),
        errors,
    )
    gate_report = validate_acceptance_gate(gate_path, candidate_id, content_hash_text, entry, repo_root)
    errors.extend(f"{label}: {error}" for error in gate_report["errors"])
    warnings.extend(f"{label}: {warning}" for warning in gate_report["warnings"])

    manual_review_file = entry.get("manual_review_file")
    manual_review_path = validate_optional_repo_path(
        repo_root,
        f"{label}: manual_review_file",
        manual_review_file,
        errors,
    )
    review_report = validate_manual_review(manual_review_path, candidate_id, content_hash_text, repo_root)
    errors.extend(f"{label}: {error}" for error in review_report["errors"])
    warnings.extend(f"{label}: {warning}" for warning in review_report["warnings"])

    completed_run_count = entry.get("completed_run_count")
    if not isinstance(completed_run_count, int) or isinstance(completed_run_count, bool):
        errors.append(f"{label}: completed_run_count must be an integer")
    elif completed_run_count < len(REQUIRED_RUN_IDS):
        errors.append(f"{label}: completed_run_count must be at least {len(REQUIRED_RUN_IDS)}")
    elif review_report["completed_run_count"] and completed_run_count != review_report["completed_run_count"]:
        errors.append(f"{label}: completed_run_count must match manual review")

    average_rating = entry.get("average_rating")
    if not isinstance(average_rating, (int, float)) or isinstance(average_rating, bool):
        errors.append(f"{label}: average_rating must be numeric")
    elif not 1 <= float(average_rating) <= 5:
        errors.append(f"{label}: average_rating must be between 1 and 5")
    elif review_report["average_rating"] is not None and abs(float(average_rating) - float(review_report["average_rating"])) > 0.05:
        errors.append(f"{label}: average_rating must match manual review")

    return (
        {
            "id": candidate_id,
            "status": status,
            "source": relative_repo_path(repo_root, source_path) if source_path else entry.get("source"),
            "runtime_content_dir": relative_repo_path(repo_root, runtime_content_path) if runtime_content_path else entry.get("runtime_content_dir"),
            "content_hash": content_hash,
            "object_count": object_count,
            "completed_run_count": completed_run_count,
            "average_rating": average_rating,
            "acceptance_gate": gate_report,
            "manual_review": review_report,
            "error_count": len(errors),
            "warning_count": len(warnings),
        },
        errors,
        warnings,
    )


def build_report(lockfile_path: Path, repo_root: Path) -> dict[str, Any]:
    payload = load_json_object(lockfile_path)
    errors: list[str] = []
    warnings: list[str] = []

    if payload.get("lock_version") != 1:
        errors.append("lock_version must be 1")
    status = payload.get("status")
    if status not in {"locked", "blocked"}:
        errors.append("status must be `locked` or `blocked`")
    accepted_dir = validate_optional_repo_path(repo_root, "accepted_dir", payload.get("accepted_dir"), errors)
    lock_file = validate_optional_repo_path(repo_root, "lock_file", payload.get("lock_file"), errors)
    runtime_content_root = validate_optional_repo_path(
        repo_root,
        "runtime_content_root",
        payload.get("runtime_content_root"),
        errors,
        require_exists=False,
    )
    if lock_file is not None and lock_file.resolve() != lockfile_path.resolve():
        errors.append("lock_file must point to the validated lockfile path")

    entries = payload.get("entries")
    if not isinstance(entries, list):
        entries = []
        errors.append("entries must be a list")
    entry_reports: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, entry in enumerate(entries):
        entry_report, entry_errors, entry_warnings = validate_entry(repo_root, entry, index)
        errors.extend(entry_errors)
        warnings.extend(entry_warnings)
        if entry_report is None:
            continue
        if entry_report["id"] in seen_ids:
            errors.append(f"duplicate entry id `{entry_report['id']}`")
        seen_ids.add(entry_report["id"])
        entry_reports.append(entry_report)

    locked_count = sum(1 for entry in entry_reports if entry["status"] == "locked")
    blocked_count = sum(1 for entry in entry_reports if entry["status"] == "blocked")
    if payload.get("candidate_count") != len(entry_reports):
        errors.append("candidate_count must match entries length")
    if payload.get("locked_count") != locked_count:
        errors.append("locked_count must match locked entries")
    if payload.get("blocked_count") != blocked_count:
        errors.append("blocked_count must match blocked entries")
    if status == "locked" and blocked_count:
        errors.append("locked report cannot contain blocked entries")
    if status == "blocked" and not blocked_count and entry_reports:
        errors.append("blocked report with entries must contain at least one blocked entry")
    top_errors = payload.get("errors")
    if not isinstance(top_errors, list):
        errors.append("errors must be a list")
        top_errors = []
    if status == "locked" and top_errors:
        errors.append("locked report must not include top-level errors")
    if status == "blocked" and not top_errors:
        errors.append("blocked report must include top-level errors")

    if errors:
        decision = "accepted_content_lockfile_invalid"
    elif status == "locked":
        decision = "accepted_content_lockfile_valid"
    else:
        decision = "accepted_content_lockfile_blocked"

    return {
        "report_version": 1,
        "source": relative_repo_path(repo_root, lockfile_path),
        "repo_root": str(repo_root),
        "decision": decision,
        "lock_status": status,
        "accepted_dir": relative_repo_path(repo_root, accepted_dir) if accepted_dir else payload.get("accepted_dir"),
        "runtime_content_root": relative_repo_path(repo_root, runtime_content_root) if runtime_content_root else payload.get("runtime_content_root"),
        "candidate_count": len(entry_reports),
        "locked_count": locked_count,
        "blocked_count": blocked_count,
        "errors": errors,
        "warnings": warnings,
        "top_level_errors": string_list(top_errors),
        "entries": entry_reports,
        "limitations": [
            "This validator checks accepted content lockfile evidence shape and local paths only.",
            "It does not run Rust GameCore, recompute content hashes, promote candidates, or copy Runtime content.",
            "A valid lockfile is not release approval; release candidate and package gates still apply.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Accepted Content Lockfile Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Decision: `{report['decision']}`",
        f"- Lock status: `{report['lock_status']}`",
        f"- Accepted dir: `{report['accepted_dir']}`",
        f"- Runtime content root: `{report['runtime_content_root']}`",
        f"- Result: {report['locked_count']} locked, {report['blocked_count']} blocked, {report['candidate_count']} total",
        "",
        "## Entries",
        "",
        "| Candidate | Status | Objects | Runs | Average Rating | Entry Errors |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for entry in report["entries"]:
        average_rating = entry["average_rating"]
        rating_text = f"{float(average_rating):.2f}" if isinstance(average_rating, (int, float)) else "-"
        lines.append(
            f"| `{entry['id']}` | `{entry['status']}` | {entry['object_count']} | "
            f"{entry['completed_run_count']} | {rating_text} | {entry['error_count']} |"
        )

    lines.extend(["", "## Errors", ""])
    if report["errors"]:
        lines.extend(f"- {error}" for error in report["errors"])
    else:
        lines.append("- None")

    lines.extend(["", "## Lockfile Notes", ""])
    if report["top_level_errors"]:
        lines.extend(f"- {item}" for item in report["top_level_errors"])
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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm accepted content lockfiles.")
    parser.add_argument("lockfile", type=Path, help="Accepted content lockfile JSON")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON validation report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown validation summary")
    parser.add_argument(
        "--allow-blocked",
        action="store_true",
        help="Exit 0 for structurally valid blocked lockfiles",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    lockfile_path = args.lockfile if args.lockfile.is_absolute() else repo_root / args.lockfile
    report = build_report(lockfile_path, repo_root)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))

    if report["decision"] == "accepted_content_lockfile_valid":
        return 0
    if args.allow_blocked and report["decision"] == "accepted_content_lockfile_blocked":
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
