#!/usr/bin/env python3
"""Validate consistency across long-running Goal evidence ledgers.

This gate does not decide that the project is complete. It checks that the
major ledgers agree with each other about current blockers, not-ready release
state, and manual-review boundaries.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


BINARY_BLOCKER = "local_binary_launch_blocked"
BINARY_FAILURE_CASE = "harness/failed_cases/fail_20260526_024_local_binary_launch_blocked.json"
MANUAL_PLAYTEST_BLOCKER = "manual_playtest_still_pending"
RELEASE_NOT_READY_BLOCKER = "release_candidate_not_ready"

BINARY_DEPENDENT_RELEASE_GATES = [
    "compile",
    "unit_tests",
    "headless_simulation",
    "multi_seed_no_deadlock",
    "content_schema",
    "static_budget",
    "bot_matrix",
    "replay_regression",
    "performance",
    "failure_case_review",
    "release_package",
]

MANUAL_WAITING_GATES = {
    "manual_playtest",
    "asset_manual_review",
    "story_codex_review",
    "telemetry_privacy",
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


def is_inside_repo(repo_root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return False
    return True


def validate_input_path(repo_root: Path, label: str, path: Path, errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"{label} does not exist: {path}")
        return
    if not is_inside_repo(repo_root, path):
        errors.append(f"{label} must stay inside repository: {path}")


def collect_docs_blockers(docs_payload: dict[str, Any]) -> set[str]:
    blockers: set[str] = set()
    for doc in docs_payload.get("docs", []):
        if not isinstance(doc, dict):
            continue
        for item in doc.get("coverage", []):
            if isinstance(item, dict):
                blockers.update(string_list(item.get("blockers")))
    return blockers


def collect_docs_statuses(docs_payload: dict[str, Any]) -> dict[str, str]:
    statuses: dict[str, str] = {}
    for doc in docs_payload.get("docs", []):
        if isinstance(doc, dict) and is_nonempty_string(doc.get("doc_path")):
            statuses[str(doc["doc_path"])] = str(doc.get("status"))
    return statuses


def collect_roadmap_blockers(roadmap_payload: dict[str, Any]) -> set[str]:
    blockers: set[str] = set()
    for phase in roadmap_payload.get("phases", []):
        if isinstance(phase, dict):
            blockers.update(string_list(phase.get("blockers")))
    return blockers


def roadmap_phases_by_id(roadmap_payload: dict[str, Any]) -> dict[int, dict[str, Any]]:
    phases: dict[int, dict[str, Any]] = {}
    for phase in roadmap_payload.get("phases", []):
        if isinstance(phase, dict) and isinstance(phase.get("phase"), int):
            phases[int(phase["phase"])] = phase
    return phases


def progress_ids_by_section(progress_payload: dict[str, Any]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for section in ("completed", "current_findings", "next_recommended"):
        ids: set[str] = set()
        for item in progress_payload.get(section, []):
            if isinstance(item, dict) and is_nonempty_string(item.get("id")):
                ids.add(str(item["id"]))
        result[section] = ids
    return result


def gates_by_id(rc_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    gates: dict[str, dict[str, Any]] = {}
    for gate in rc_payload.get("gates", []):
        if isinstance(gate, dict) and is_nonempty_string(gate.get("id")):
            gates[str(gate["id"])] = gate
    return gates


def release_candidate_is_ready(rc_payload: dict[str, Any]) -> bool:
    gates = rc_payload.get("gates")
    if not isinstance(gates, list) or not gates:
        return False
    return all(isinstance(gate, dict) and gate.get("status") == "pass" for gate in gates)


def add_check(checks: list[dict[str, Any]], check_id: str, status: str, summary: str) -> None:
    checks.append({"id": check_id, "status": status, "summary": summary})


def build_report(
    docs_path: Path,
    roadmap_path: Path,
    progress_path: Path,
    rc_path: Path,
    package_path: Path,
    repo_root: Path,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    checks: list[dict[str, Any]] = []

    for label, source_path in (
        ("docs_coverage", docs_path),
        ("roadmap_audit", roadmap_path),
        ("progress", progress_path),
        ("release_candidate_evidence", rc_path),
        ("release_package_manifest", package_path),
    ):
        validate_input_path(repo_root, label, source_path.resolve(), errors)

    docs_payload = load_json_object(docs_path)
    roadmap_payload = load_json_object(roadmap_path)
    progress_payload = load_json_object(progress_path)
    rc_payload = load_json_object(rc_path)
    package_payload = load_json_object(package_path)

    docs_statuses = collect_docs_statuses(docs_payload)
    docs_blockers = collect_docs_blockers(docs_payload)
    roadmap_blockers = collect_roadmap_blockers(roadmap_payload)
    progress_ids = progress_ids_by_section(progress_payload)
    rc_gates = gates_by_id(rc_payload)
    package_blockers = set(string_list(package_payload.get("blockers")))
    package_status = package_payload.get("package_status")
    rc_ready = release_candidate_is_ready(rc_payload)
    docs_incomplete = [path for path, status in docs_statuses.items() if status != "complete"]
    roadmap_phases = roadmap_phases_by_id(roadmap_payload)
    roadmap_incomplete = [
        phase_id
        for phase_id, phase in roadmap_phases.items()
        if phase.get("status") != "complete"
    ]

    binary_blocker_seen = (
        BINARY_BLOCKER in docs_blockers
        or BINARY_BLOCKER in roadmap_blockers
        or BINARY_BLOCKER in package_blockers
        or BINARY_BLOCKER in progress_ids.get("current_findings", set())
    )
    if binary_blocker_seen:
        missing_sources: list[str] = []
        if BINARY_BLOCKER not in docs_blockers:
            missing_sources.append("docs_implementation_coverage")
        if BINARY_BLOCKER not in roadmap_blockers:
            missing_sources.append("roadmap_phase_audit")
        if BINARY_BLOCKER not in progress_ids.get("current_findings", set()):
            missing_sources.append("progress.current_findings")
        if BINARY_BLOCKER not in package_blockers:
            missing_sources.append("release_package_manifest.blockers")
        if missing_sources:
            errors.append(f"{BINARY_BLOCKER}: missing from {', '.join(missing_sources)}")
        else:
            add_check(
                checks,
                "binary_blocker_sources",
                "pass",
                "local_binary_launch_blocked is recorded in docs coverage, roadmap audit, progress, and package blockers.",
            )

        binary_gate_error_count = len(errors)
        for gate_id in BINARY_DEPENDENT_RELEASE_GATES:
            gate = rc_gates.get(gate_id)
            if gate is None:
                errors.append(f"{gate_id}: binary-dependent release gate is missing")
                continue
            if gate.get("status") != "blocked":
                errors.append(
                    f"{gate_id}: must remain `blocked` while {BINARY_BLOCKER} is active, got `{gate.get('status')}`"
                )
            evidence_paths = string_list(gate.get("evidence_paths"))
            if BINARY_FAILURE_CASE not in evidence_paths:
                errors.append(f"{gate_id}: must cite {BINARY_FAILURE_CASE}")
        add_check(
            checks,
            "binary_release_gates",
            "pass" if len(errors) == binary_gate_error_count else "fail",
            "Binary-dependent release gates are checked against the active local binary launch blocker.",
        )
    else:
        warnings.append(f"{BINARY_BLOCKER}: not present in any checked ledger")

    manual_playtest_seen = (
        MANUAL_PLAYTEST_BLOCKER in docs_blockers
        or MANUAL_PLAYTEST_BLOCKER in roadmap_blockers
        or MANUAL_PLAYTEST_BLOCKER in progress_ids.get("current_findings", set())
    )
    if manual_playtest_seen:
        manual_playtest_error_count = len(errors)
        if MANUAL_PLAYTEST_BLOCKER not in progress_ids.get("current_findings", set()):
            errors.append(f"{MANUAL_PLAYTEST_BLOCKER}: missing from progress.current_findings")
        manual_gate = rc_gates.get("manual_playtest")
        if manual_gate is None:
            errors.append("manual_playtest: release gate is missing")
        elif manual_gate.get("status") != "waiting":
            errors.append(
                f"manual_playtest: must remain `waiting` while {MANUAL_PLAYTEST_BLOCKER} is active, got `{manual_gate.get('status')}`"
            )
        add_check(
            checks,
            "manual_playtest_waiting",
            "pass" if len(errors) == manual_playtest_error_count else "fail",
            "Manual playtest evidence is kept as a waiting release gate until a real human review exists.",
        )

    manual_gate_error_count = len(errors)
    for gate_id in MANUAL_WAITING_GATES:
        gate = rc_gates.get(gate_id)
        if gate is None:
            errors.append(f"{gate_id}: manual release gate is missing")
            continue
        if gate.get("status") == "pass":
            errors.append(f"{gate_id}: cannot be `pass` without a corresponding real manual review record")
    add_check(
        checks,
        "manual_gates_not_overclaimed",
        "pass" if len(errors) == manual_gate_error_count else "fail",
        "Manual review gates are not overclaimed as passing evidence.",
    )

    not_ready_error_count = len(errors)
    if docs_incomplete and rc_ready:
        errors.append("release_candidate_evidence: cannot be ready while docs implementation coverage is incomplete")
    if roadmap_incomplete and rc_ready:
        errors.append("release_candidate_evidence: cannot be ready while roadmap phase audit is incomplete")
    if package_status == "ready" and not rc_ready:
        errors.append("release_package_manifest: package cannot be ready while release candidate gates are not all pass")
    if not rc_ready:
        if package_status == "ready":
            errors.append("release_package_manifest: package_status must not be ready while RC is not ready")
        if RELEASE_NOT_READY_BLOCKER not in package_blockers:
            errors.append(f"release_package_manifest: blockers must include {RELEASE_NOT_READY_BLOCKER}")
    add_check(
        checks,
        "not_ready_state_coherence",
        "pass" if len(errors) == not_ready_error_count else "fail",
        "Docs, roadmap, RC evidence, and package manifest agree that the current local build is not ready.",
    )

    if binary_blocker_seen:
        optimistic_docs = [
            doc_path
            for doc_path in (
                "docs/02_核心玩法规格.md",
                "docs/06_Bevy技术架构计划.md",
                "docs/07_Harness工程计划.md",
                "docs/08_Bot测试计划.md",
                "docs/14_GameCore接口规格.md",
                "docs/16_Replay与遥测设计.md",
            )
            if docs_statuses.get(doc_path) == "complete"
        ]
        if optimistic_docs:
            errors.append(
                f"{BINARY_BLOCKER}: binary-dependent docs cannot be complete yet: {', '.join(optimistic_docs)}"
            )
        else:
            add_check(
                checks,
                "binary_dependent_docs_not_complete",
                "pass",
                "Binary-dependent docs remain incomplete while local binary launch is blocked.",
            )

    ledger_blockers = (
        docs_blockers
        | roadmap_blockers
        | package_blockers
        | ({BINARY_BLOCKER, MANUAL_PLAYTEST_BLOCKER} & progress_ids.get("current_findings", set()))
    )
    decision = "goal_evidence_consistent" if not errors else "goal_evidence_inconsistent"
    return {
        "report_version": 1,
        "source": {
            "docs_coverage": str(docs_path),
            "roadmap_audit": str(roadmap_path),
            "progress": str(progress_path),
            "release_candidate_evidence": str(rc_path),
            "release_package_manifest": str(package_path),
        },
        "repo_root": str(repo_root),
        "decision": decision,
        "docs_incomplete_count": len(docs_incomplete),
        "roadmap_incomplete_phase_count": len(roadmap_incomplete),
        "release_candidate_ready": rc_ready,
        "release_package_status": package_status,
        "blockers_seen": sorted(ledger_blockers),
        "errors": errors,
        "warnings": warnings,
        "checks": checks,
        "limitations": [
            "This validator checks ledger consistency only; it does not execute Rust, Bevy, Harness simulations, Replay, performance tests, or manual playtests.",
            "A consistent not-ready decision is not release approval.",
            "Manual review gates require real human-filled review records before they can become passing evidence.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal Evidence Consistency",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Docs incomplete: {report['docs_incomplete_count']}",
        f"- Roadmap incomplete phases: {report['roadmap_incomplete_phase_count']}",
        f"- Release candidate ready: {report['release_candidate_ready']}",
        f"- Release package status: `{report['release_package_status']}`",
        "",
        "## Sources",
        "",
    ]
    for label, source in report["source"].items():
        lines.append(f"- {label}: `{source}`")

    lines.extend(["", "## Checks", "", "| Check | Status | Summary |", "|---|---|---|"])
    for check in report["checks"]:
        lines.append(f"| `{check['id']}` | `{check['status']}` | {check['summary']} |")

    lines.extend(["", "## Blockers Seen", ""])
    if report["blockers_seen"]:
        lines.extend(f"- `{blocker}`" for blocker in report["blockers_seen"])
    else:
        lines.append("- None")

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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm Goal evidence consistency.")
    parser.add_argument(
        "--docs-coverage",
        type=Path,
        default=Path("harness/docs_implementation_coverage.json"),
        help="Docs implementation coverage ledger",
    )
    parser.add_argument(
        "--roadmap-audit",
        type=Path,
        default=Path("harness/roadmap_audit/roadmap_phase_audit.json"),
        help="Roadmap phase audit ledger",
    )
    parser.add_argument(
        "--progress",
        type=Path,
        default=Path("harness/progress.json"),
        help="Goal progress ledger",
    )
    parser.add_argument(
        "--release-candidate",
        type=Path,
        default=Path("harness/release/current_local_rc_evidence.json"),
        help="Release candidate evidence manifest",
    )
    parser.add_argument(
        "--release-package",
        type=Path,
        default=Path("harness/release/current_local_package_manifest.json"),
        help="Release package manifest",
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON consistency report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown consistency summary")
    args = parser.parse_args()

    report = build_report(
        args.docs_coverage,
        args.roadmap_audit,
        args.progress,
        args.release_candidate,
        args.release_package,
        args.repo_root,
    )
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "goal_evidence_consistent" else 1


if __name__ == "__main__":
    raise SystemExit(main())
