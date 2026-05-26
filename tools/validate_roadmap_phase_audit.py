#!/usr/bin/env python3
"""Validate docs/12 roadmap phase implementation audit.

The audit is allowed to be incomplete during Goal mode, but it must be honest:
every phase needs concrete evidence paths, and any non-complete phase must name
gaps and next actions.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


EXPECTED_PHASES = list(range(0, 11))
PHASE_STATUSES = {"complete", "partial", "blocked", "pending"}


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


def resolve_repo_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def is_inside_repo(repo_root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return False
    return True


def validate_evidence_paths(repo_root: Path, label: str, evidence: list[str], errors: list[str]) -> None:
    for evidence_path in evidence:
        resolved = resolve_repo_path(repo_root, evidence_path)
        if not is_inside_repo(repo_root, resolved):
            errors.append(f"{label}: evidence path must stay inside repository: {evidence_path}")
        elif not resolved.exists():
            errors.append(f"{label}: evidence path does not exist: {evidence_path}")


def validate_phase(repo_root: Path, item: Any, index: int) -> tuple[dict[str, Any] | None, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(item, dict):
        return None, [f"phases[{index}] must be an object"], warnings

    phase = item.get("phase")
    label = f"phase {phase}" if isinstance(phase, int) else f"phases[{index}]"
    if not isinstance(phase, int) or isinstance(phase, bool):
        errors.append(f"{label}: phase must be an integer")
    if not is_nonempty_string(item.get("title")):
        errors.append(f"{label}: title must be non-empty")
    if not is_nonempty_string(item.get("goal")):
        errors.append(f"{label}: goal must be non-empty")

    status = item.get("status")
    if status not in PHASE_STATUSES:
        errors.append(f"{label}: status must be one of {', '.join(sorted(PHASE_STATUSES))}")

    acceptance = string_list(item.get("acceptance"))
    evidence = string_list(item.get("evidence"))
    gaps = string_list(item.get("gaps"))
    blockers = string_list(item.get("blockers"))
    next_actions = string_list(item.get("next_actions"))
    for field in ("acceptance", "evidence", "gaps", "blockers", "next_actions"):
        if item.get(field) is not None and not isinstance(item.get(field), list):
            errors.append(f"{label}: {field} must be a list")

    if not acceptance:
        errors.append(f"{label}: acceptance must contain at least one item")
    if not evidence:
        errors.append(f"{label}: evidence must contain at least one path")
    validate_evidence_paths(repo_root, label, evidence, errors)

    if status == "complete":
        if gaps:
            errors.append(f"{label}: complete phase cannot list open gaps")
        if blockers:
            errors.append(f"{label}: complete phase cannot list blockers")
    else:
        if not gaps:
            errors.append(f"{label}: non-complete phase must list gaps")
        if not next_actions:
            warnings.append(f"{label}: non-complete phase should list next_actions")
    if status == "blocked" and not blockers:
        errors.append(f"{label}: blocked phase requires blockers")

    return (
        {
            "phase": phase if isinstance(phase, int) else index,
            "title": item.get("title"),
            "status": status,
            "acceptance_count": len(acceptance),
            "evidence_count": len(evidence),
            "gap_count": len(gaps),
            "blocker_count": len(blockers),
            "next_action_count": len(next_actions),
        },
        errors,
        warnings,
    )


def build_report(audit_path: Path, repo_root: Path) -> dict[str, Any]:
    payload = load_json_object(audit_path)
    errors: list[str] = []
    warnings: list[str] = []

    for field in ("updated_at", "scope", "summary"):
        if not is_nonempty_string(payload.get(field)):
            errors.append(f"`{field}` must be non-empty")
    if payload.get("report_version") != 1:
        errors.append("report_version must be 1")

    phases = payload.get("phases")
    if not isinstance(phases, list):
        phases = []
        errors.append("`phases` must be a list")

    phase_reports: list[dict[str, Any]] = []
    seen_phases: set[int] = set()
    for index, phase in enumerate(phases):
        phase_report, phase_errors, phase_warnings = validate_phase(repo_root, phase, index)
        errors.extend(phase_errors)
        warnings.extend(phase_warnings)
        if phase_report is None:
            continue
        phase_number = phase_report["phase"]
        if phase_number in seen_phases:
            errors.append(f"duplicate phase `{phase_number}`")
        seen_phases.add(phase_number)
        phase_reports.append(phase_report)

    missing_phases = sorted(set(EXPECTED_PHASES) - seen_phases)
    extra_phases = sorted(seen_phases - set(EXPECTED_PHASES))
    for phase in missing_phases:
        errors.append(f"missing phase `{phase}`")
    for phase in extra_phases:
        errors.append(f"unexpected phase `{phase}`")

    status_counts: dict[str, int] = {}
    for phase_report in phase_reports:
        status = str(phase_report["status"])
        status_counts[status] = status_counts.get(status, 0) + 1
    incomplete_count = sum(1 for phase_report in phase_reports if phase_report["status"] != "complete")

    if errors:
        decision = "roadmap_phase_audit_invalid"
    elif incomplete_count:
        decision = "roadmap_phase_audit_incomplete"
    else:
        decision = "roadmap_phase_audit_complete"

    return {
        "report_version": 1,
        "source": str(audit_path),
        "repo_root": str(repo_root),
        "decision": decision,
        "phase_count": len(phase_reports),
        "incomplete_phase_count": incomplete_count,
        "status_counts": dict(sorted(status_counts.items())),
        "errors": errors,
        "warnings": warnings,
        "phases": sorted(phase_reports, key=lambda item: item["phase"]),
        "limitations": [
            "This audit checks roadmap evidence paths, status honesty, and gap accounting only.",
            "It does not execute Rust, Bevy, Harness simulations, Replay, performance tests, or manual playtests.",
            "Non-complete phases remain incomplete until their acceptance evidence is produced and verified.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Roadmap Phase Audit",
        "",
        f"- Source: `{report['source']}`",
        f"- Decision: `{report['decision']}`",
        f"- Phases: {report['phase_count']} / {len(EXPECTED_PHASES)}",
        f"- Incomplete phases: {report['incomplete_phase_count']}",
        "",
        "## Status Counts",
        "",
        "| Status | Count |",
        "|---|---:|",
    ]
    for status, count in report["status_counts"].items():
        lines.append(f"| `{status}` | {count} |")

    lines.extend(["", "## Phases", "", "| Phase | Title | Status | Evidence | Gaps | Blockers |", "|---:|---|---|---:|---:|---:|"])
    for phase in report["phases"]:
        lines.append(
            f"| {phase['phase']} | {phase['title']} | `{phase['status']}` | "
            f"{phase['evidence_count']} | {phase['gap_count']} | {phase['blocker_count']} |"
        )

    lines.extend(["", "## Errors", ""])
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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm roadmap phase audit.")
    parser.add_argument("audit", type=Path, nargs="?", default=Path("harness/roadmap_audit/roadmap_phase_audit.json"))
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON validation report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown validation summary")
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="Return success for an honest incomplete audit without structural errors",
    )
    args = parser.parse_args()

    report = build_report(args.audit, args.repo_root)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    if report["decision"] == "roadmap_phase_audit_complete":
        return 0
    if args.allow_incomplete and report["decision"] == "roadmap_phase_audit_incomplete":
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
