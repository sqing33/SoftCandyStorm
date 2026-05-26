#!/usr/bin/env python3
"""Build a prioritized blocker audit for the active Goal work.

The Goal spans many docs and subsystems. This tool reads existing machine
reports and turns them into a conservative next-action queue. It does not fix
host policy, fill human reviews, run Runtime, or approve a release.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SEVERITY_RANK = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
DEFAULT_REPORT_PATTERNS = {
    "manual_evidence": "harness/reports/*_manual_evidence_gap_audit_*/manual_evidence_gap_audit.json",
    "local_binary": "harness/reports/*_local_binary_launch_diagnostic_*/local_binary_launch_diagnostic.json",
    "release_candidate": "harness/reports/*_release_candidate_evidence_current_local_*/release_candidate_evidence.json",
    "release_package": "harness/reports/*_release_package_manifest_current_local_*/release_package_manifest.json",
    "goal_consistency": "harness/reports/*_goal_evidence_consistency_*/goal_evidence_consistency.json",
}


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


def relative_repo_path(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(path)


def read_optional_report(repo_root: Path, value: str, errors: list[str]) -> tuple[dict[str, Any] | None, str]:
    path = resolve_repo_path(repo_root, value)
    if not path.exists():
        errors.append(f"required report does not exist: {value}")
        return None, relative_repo_path(repo_root, path)
    try:
        return load_json_object(path), relative_repo_path(repo_root, path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"required report is invalid JSON: {value}: {error}")
        return None, relative_repo_path(repo_root, path)


def latest_report_path(repo_root: Path, label: str, explicit: Path | None, fallback: Path) -> Path:
    if explicit is not None:
        return explicit
    pattern = DEFAULT_REPORT_PATTERNS.get(label)
    if pattern:
        matches = sorted(repo_root.glob(pattern))
        if matches:
            return matches[-1]
    return fallback


def compact(value: Any, limit: int = 6) -> list[str]:
    return string_list(value)[:limit]


def blocker(
    *,
    blocker_id: str,
    severity: str,
    category: str,
    summary: str,
    source: str,
    status: str,
    next_actions: list[str],
    blocked_by: list[str] | None = None,
    requires_external_action: bool = False,
    requires_human: bool = False,
    detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "id": blocker_id,
        "severity": severity,
        "category": category,
        "status": status,
        "summary": summary,
        "source": source,
        "blocked_by": list(blocked_by or []),
        "requires_external_action": requires_external_action,
        "requires_human": requires_human,
        "next_actions": next_actions,
        "detail": detail or {},
    }


def build_binary_blocker(report: dict[str, Any], source: str) -> dict[str, Any] | None:
    decision = str(report.get("decision", ""))
    if decision == "local_binary_launch_ok":
        return None
    signals = report.get("signals") if isinstance(report.get("signals"), dict) else {}
    next_actions = compact(report.get("next_actions"))
    if not next_actions:
        next_actions = [
            "Resolve host execution policy for newly built Mach-O binaries.",
            "Rerun tools/diagnose_local_binary_launch.py until it reports local_binary_launch_ok.",
        ]
    return blocker(
        blocker_id="local_binary_launch_blocked",
        severity="P0",
        category="host_environment",
        status=decision or "unknown",
        summary="Newly built local binaries cannot be trusted as executable evidence yet.",
        source=source,
        requires_external_action=True,
        next_actions=next_actions,
        detail={
            "signals": signals,
            "policy_log_lines": report.get("policy_log", {}).get("line_count")
            if isinstance(report.get("policy_log"), dict)
            else None,
        },
    )


def build_manual_blocker(report: dict[str, Any], source: str) -> dict[str, Any] | None:
    gap_count = report.get("gap_count")
    if gap_count == 0 and report.get("decision") == "manual_evidence_ready":
        return None
    domain_counts = report.get("domain_counts") if isinstance(report.get("domain_counts"), dict) else {}
    top_domains = [
        f"{domain}:{counts.get('gaps', 0)}"
        for domain, counts in domain_counts.items()
        if isinstance(counts, dict) and counts.get("gaps", 0)
    ]
    return blocker(
        blocker_id="manual_evidence_gaps",
        severity="P0",
        category="human_review",
        status=str(report.get("decision", "unknown")),
        summary=f"Manual review evidence is still incomplete across {gap_count} requirement(s).",
        source=source,
        requires_human=True,
        next_actions=[
            "Use the manual evidence gap audit as the human-review checklist.",
            "Do not mark playtest, content, story, asset, privacy, platform, base UI, or release gates as passing until their validators pass.",
        ],
        detail={
            "gap_count": gap_count,
            "requirement_count": report.get("requirement_count"),
            "domains_with_gaps": top_domains,
        },
    )


def build_release_candidate_blocker(report: dict[str, Any], source: str) -> dict[str, Any] | None:
    if report.get("decision") == "release_candidate_ready":
        return None
    blockers = compact(report.get("blockers"), limit=10)
    return blocker(
        blocker_id="release_candidate_not_ready",
        severity="P1",
        category="release",
        status=str(report.get("decision", "unknown")),
        summary="Release Candidate evidence is not ready.",
        source=source,
        blocked_by=["local_binary_launch_blocked", "manual_evidence_gaps"],
        next_actions=[
            "Keep release_candidate_not_ready until binary-dependent gates and human gates are real pass evidence.",
            "After blockers clear, rerun tools/validate_release_candidate_evidence.py without --allow-not-ready.",
        ],
        detail={"blockers": blockers, "missing_gates": report.get("missing_gates", [])},
    )


def build_release_package_blocker(report: dict[str, Any], source: str) -> dict[str, Any] | None:
    if report.get("decision") == "release_package_ready":
        return None
    return blocker(
        blocker_id="release_package_not_ready",
        severity="P1",
        category="release",
        status=str(report.get("decision", "unknown")),
        summary="Release package manifest is not ready.",
        source=source,
        blocked_by=["release_candidate_not_ready"],
        next_actions=[
            "Do not prepare a release package until Release Candidate evidence is ready.",
            "After a concrete package exists, rerun tools/validate_release_package_manifest.py.",
        ],
        detail={
            "package_status": report.get("package_status"),
            "blockers": compact(report.get("blockers")),
            "missing_ready_checks": report.get("missing_ready_checks", []),
        },
    )


def build_docs_blocker(report: dict[str, Any], source: str) -> dict[str, Any] | None:
    docs = report.get("docs") if isinstance(report.get("docs"), list) else []
    incomplete_docs_from_ledger = [
        str(doc.get("doc_path"))
        for doc in docs
        if isinstance(doc, dict) and doc.get("status") != "complete" and is_nonempty_string(doc.get("doc_path"))
    ]
    incomplete = int(report.get("incomplete_docs_count", report.get("docs_incomplete_count", 0)) or 0)
    if incomplete_docs_from_ledger:
        incomplete = len(incomplete_docs_from_ledger)
    if not incomplete and report.get("decision") == "docs_implementation_complete":
        return None
    incomplete_docs = report.get("incomplete_docs")
    if isinstance(incomplete_docs, list):
        incomplete = len(incomplete_docs)
    elif incomplete_docs_from_ledger:
        incomplete_docs = incomplete_docs_from_ledger
    status = str(report.get("decision") or ("docs_implementation_incomplete" if incomplete else "docs_implementation_complete"))
    return blocker(
        blocker_id="docs_implementation_incomplete",
        severity="P2",
        category="coverage",
        status=status,
        summary=f"Docs coverage remains incomplete for {incomplete} document(s).",
        source=source,
        blocked_by=["local_binary_launch_blocked", "manual_evidence_gaps"],
        next_actions=[
            "Use docs coverage gaps to choose only tasks that can be honestly evidenced.",
            "Keep binary- and human-dependent docs partial/blocked until real validation exists.",
        ],
        detail={
            "doc_status_counts": report.get("doc_status_counts", {}),
            "item_status_counts": report.get("item_status_counts", {}),
            "incomplete_docs": compact(incomplete_docs, limit=12),
        },
    )


def build_roadmap_blocker(report: dict[str, Any], source: str) -> dict[str, Any] | None:
    phases = report.get("phases") if isinstance(report.get("phases"), list) else []
    incomplete = [phase for phase in phases if isinstance(phase, dict) and phase.get("status") != "complete"]
    if not incomplete:
        return None
    phase_counts: dict[str, int] = {}
    next_actions: list[str] = []
    for phase in incomplete:
        status = str(phase.get("status", "unknown"))
        phase_counts[status] = phase_counts.get(status, 0) + 1
        for action in compact(phase.get("next_actions"), limit=2):
            if action not in next_actions:
                next_actions.append(action)
    if not next_actions:
        next_actions = ["Continue from the earliest incomplete roadmap phase with non-blocked evidence work."]
    return blocker(
        blocker_id="roadmap_incomplete",
        severity="P2",
        category="roadmap",
        status="roadmap_phase_audit_incomplete",
        summary=f"Roadmap has {len(incomplete)} incomplete phase(s).",
        source=source,
        blocked_by=["local_binary_launch_blocked", "manual_evidence_gaps"],
        next_actions=next_actions[:6],
        detail={
            "phase_status_counts": phase_counts,
            "incomplete_phases": [
                {"phase": phase.get("phase"), "title": phase.get("title"), "status": phase.get("status")}
                for phase in incomplete[:10]
            ],
        },
    )


def build_report(
    repo_root: Path,
    *,
    manual_evidence: Path,
    local_binary: Path,
    release_candidate: Path,
    release_package: Path,
    docs_coverage: Path,
    roadmap_audit: Path,
    goal_consistency: Path,
) -> dict[str, Any]:
    errors: list[str] = []
    sources: dict[str, str] = {}
    loaded: dict[str, dict[str, Any]] = {}
    for label, path in {
        "manual_evidence": manual_evidence,
        "local_binary": local_binary,
        "release_candidate": release_candidate,
        "release_package": release_package,
        "docs_coverage": docs_coverage,
        "roadmap_audit": roadmap_audit,
        "goal_consistency": goal_consistency,
    }.items():
        payload, source = read_optional_report(repo_root, str(path), errors)
        sources[label] = source
        if payload is not None:
            loaded[label] = payload

    blockers: list[dict[str, Any]] = []
    builders = [
        ("local_binary", build_binary_blocker),
        ("manual_evidence", build_manual_blocker),
        ("release_candidate", build_release_candidate_blocker),
        ("release_package", build_release_package_blocker),
        ("docs_coverage", build_docs_blocker),
        ("roadmap_audit", build_roadmap_blocker),
    ]
    for label, builder in builders:
        payload = loaded.get(label)
        if payload is None:
            continue
        item = builder(payload, sources[label])
        if item is not None:
            blockers.append(item)

    consistency = loaded.get("goal_consistency", {})
    if consistency.get("decision") != "goal_evidence_consistent":
        blockers.append(
            blocker(
                blocker_id="goal_evidence_inconsistent",
                severity="P0",
                category="ledger",
                status=str(consistency.get("decision", "missing")),
                summary="Goal ledgers disagree and must be reconciled before making readiness claims.",
                source=sources.get("goal_consistency", ""),
                next_actions=["Fix progress, docs coverage, roadmap, RC, or package ledgers until goal consistency passes."],
                detail={"errors": consistency.get("errors", [])},
            )
        )

    blockers.sort(key=lambda item: (SEVERITY_RANK.get(str(item["severity"]), 99), str(item["id"])))
    severity_counts: dict[str, int] = {}
    category_counts: dict[str, int] = {}
    for item in blockers:
        severity_counts[item["severity"]] = severity_counts.get(item["severity"], 0) + 1
        category_counts[item["category"]] = category_counts.get(item["category"], 0) + 1

    decision = "goal_blockers_clear" if not errors and not blockers else "goal_blockers_present"
    if errors:
        decision = "goal_blocker_audit_invalid"

    return {
        "report_version": 1,
        "repo_root": str(repo_root),
        "decision": decision,
        "blocker_count": len(blockers),
        "severity_counts": dict(sorted(severity_counts.items())),
        "category_counts": dict(sorted(category_counts.items())),
        "sources": sources,
        "errors": errors,
        "blockers": blockers,
        "next_queue": [
            {
                "id": item["id"],
                "severity": item["severity"],
                "summary": item["summary"],
                "next_actions": item["next_actions"],
            }
            for item in blockers[:6]
        ],
        "limitations": [
            "This audit prioritizes existing blocker reports only; it does not execute binaries, run Harness, fill human reviews, or approve release readiness.",
            "External host policy and human review blockers must be cleared outside this script before downstream gates can become passing evidence.",
            "Derived release, docs, and roadmap blockers should remain until their source validators report ready or complete.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal Blocker Priority Audit",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Blockers: {report['blocker_count']}",
        "",
        "## Severity",
        "",
        "| Severity | Count |",
        "|---|---:|",
    ]
    for severity, count in report["severity_counts"].items():
        lines.append(f"| `{severity}` | {count} |")

    lines.extend(["", "## Next Queue", ""])
    if report["next_queue"]:
        for item in report["next_queue"]:
            lines.append(f"### {item['severity']} `{item['id']}`")
            lines.append("")
            lines.append(item["summary"])
            lines.append("")
            for action in item["next_actions"]:
                lines.append(f"- {action}")
            lines.append("")
    else:
        lines.append("- None")

    lines.extend(["## Blockers", "", "| Severity | Category | Blocker | Status | Source |", "|---|---|---|---|---|"])
    for item in report["blockers"]:
        lines.append(
            f"| `{item['severity']}` | `{item['category']}` | `{item['id']}` | `{item['status']}` | `{item['source']}` |"
        )

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
    parser = argparse.ArgumentParser(description="Audit and prioritize Soft Candy Storm Goal blockers.")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--manual-evidence", type=Path, default=None)
    parser.add_argument("--local-binary", type=Path, default=None)
    parser.add_argument("--release-candidate", type=Path, default=None)
    parser.add_argument("--release-package", type=Path, default=None)
    parser.add_argument("--docs-coverage", type=Path, default=Path("harness/docs_implementation_coverage.json"))
    parser.add_argument("--roadmap-audit", type=Path, default=Path("harness/roadmap_audit/roadmap_phase_audit.json"))
    parser.add_argument("--goal-consistency", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=None, help="Write JSON audit report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown audit summary")
    parser.add_argument(
        "--allow-blockers",
        action="store_true",
        help="Exit 0 when blockers are present; useful for recording the current active Goal state",
    )
    args = parser.parse_args()

    report = build_report(
        args.repo_root,
        manual_evidence=latest_report_path(
            args.repo_root,
            "manual_evidence",
            args.manual_evidence,
            Path("harness/reports/2026-05-26_manual_evidence_gap_audit_001/manual_evidence_gap_audit.json"),
        ),
        local_binary=latest_report_path(
            args.repo_root,
            "local_binary",
            args.local_binary,
            Path("harness/reports/2026-05-26_local_binary_launch_diagnostic_001/local_binary_launch_diagnostic.json"),
        ),
        release_candidate=latest_report_path(
            args.repo_root,
            "release_candidate",
            args.release_candidate,
            Path("harness/reports/2026-05-26_release_candidate_evidence_current_local_004/release_candidate_evidence.json"),
        ),
        release_package=latest_report_path(
            args.repo_root,
            "release_package",
            args.release_package,
            Path("harness/reports/2026-05-26_release_package_manifest_current_local_002/release_package_manifest.json"),
        ),
        docs_coverage=args.docs_coverage,
        roadmap_audit=args.roadmap_audit,
        goal_consistency=latest_report_path(
            args.repo_root,
            "goal_consistency",
            args.goal_consistency,
            Path("harness/reports/2026-05-26_goal_evidence_consistency_022/goal_evidence_consistency.json"),
        ),
    )
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))

    if report["decision"] == "goal_blockers_clear" or args.allow_blockers:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
