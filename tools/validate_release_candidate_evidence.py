#!/usr/bin/env python3
"""Validate release candidate evidence manifests.

This dependency-free gate turns the release checklist from docs/11 into a
machine-checkable evidence manifest. It does not run the Rust harness; it checks
that every required release gate has explicit, non-synthetic evidence before a
candidate can be called ready.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_GATES = [
    "content_frozen",
    "compile",
    "unit_tests",
    "headless_simulation",
    "multi_seed_no_deadlock",
    "content_schema",
    "static_budget",
    "bot_matrix",
    "replay_regression",
    "performance",
    "manual_playtest",
    "asset_provenance",
    "failure_case_review",
    "release_package",
]

ALLOWED_STATUSES = {"pass", "fail", "blocked", "waiting"}
PASS_STATUS = "pass"


def load_json(path: Path) -> dict[str, Any]:
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


def resolve_evidence_path(repo_root: Path, evidence_path: str) -> Path:
    path = Path(evidence_path)
    return path if path.is_absolute() else repo_root / path


def validate_gate(gate: Any, index: int, repo_root: Path) -> tuple[str | None, list[str], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    blockers: list[str] = []
    if not isinstance(gate, dict):
        return None, [f"gates[{index}] must be an object"], warnings, blockers

    gate_id = gate.get("id")
    display_id = gate_id if is_nonempty_string(gate_id) else f"gates[{index}]"
    if not is_nonempty_string(gate_id):
        errors.append(f"{display_id}: id must be non-empty")
        gate_id = None

    status = gate.get("status")
    if status not in ALLOWED_STATUSES:
        errors.append(f"{display_id}: status must be one of {', '.join(sorted(ALLOWED_STATUSES))}")
    elif status != PASS_STATUS:
        blockers.append(f"{display_id}: gate status is `{status}`")

    if not is_nonempty_string(gate.get("summary")):
        errors.append(f"{display_id}: summary must be non-empty")

    evidence_paths = string_list(gate.get("evidence_paths"))
    if status == PASS_STATUS and not evidence_paths:
        errors.append(f"{display_id}: pass gate requires at least one evidence path")
    if status in {"fail", "blocked"} and not evidence_paths:
        errors.append(f"{display_id}: {status} gate requires evidence path explaining the condition")

    for evidence_path in evidence_paths:
        resolved = resolve_evidence_path(repo_root, evidence_path)
        if not resolved.exists():
            errors.append(f"{display_id}: evidence path does not exist: {evidence_path}")

    if gate.get("synthetic") is True and status == PASS_STATUS:
        errors.append(f"{display_id}: synthetic evidence cannot satisfy a release gate")
    if gate.get("synthetic") is True and status != PASS_STATUS:
        warnings.append(f"{display_id}: synthetic evidence is recorded but does not satisfy the gate")

    return str(gate_id) if gate_id is not None else None, errors, warnings, blockers


def build_report(manifest_path: Path, repo_root: Path) -> dict[str, Any]:
    payload = load_json(manifest_path)
    errors: list[str] = []
    warnings: list[str] = []
    blockers: list[str] = []

    for field in ("candidate_id", "generated_at", "release_stage", "summary"):
        if not is_nonempty_string(payload.get(field)):
            errors.append(f"`{field}` must be non-empty")

    gates = payload.get("gates")
    if not isinstance(gates, list):
        gates = []
        errors.append("`gates` must be a list")

    seen_gate_ids: set[str] = set()
    gate_reports: list[dict[str, Any]] = []
    for index, gate in enumerate(gates):
        gate_id, gate_errors, gate_warnings, gate_blockers = validate_gate(gate, index, repo_root)
        errors.extend(gate_errors)
        warnings.extend(gate_warnings)
        blockers.extend(gate_blockers)
        if gate_id is not None:
            if gate_id in seen_gate_ids:
                errors.append(f"duplicate gate id `{gate_id}`")
            seen_gate_ids.add(gate_id)
        if isinstance(gate, dict):
            gate_reports.append(
                {
                    "id": gate.get("id", f"gates[{index}]"),
                    "status": gate.get("status"),
                    "synthetic": gate.get("synthetic", False),
                    "evidence_count": len(string_list(gate.get("evidence_paths"))),
                }
            )

    missing_gates = [gate_id for gate_id in REQUIRED_GATES if gate_id not in seen_gate_ids]
    for gate_id in missing_gates:
        blockers.append(f"{gate_id}: required release gate is missing")

    unknown_gates = sorted(gate_id for gate_id in seen_gate_ids if gate_id not in REQUIRED_GATES)
    for gate_id in unknown_gates:
        warnings.append(f"{gate_id}: gate is not part of the required release checklist")

    decision = "release_candidate_ready" if not errors and not blockers else "release_candidate_not_ready"
    return {
        "report_version": 1,
        "source": str(manifest_path),
        "repo_root": str(repo_root),
        "candidate_id": payload.get("candidate_id"),
        "release_stage": payload.get("release_stage"),
        "decision": decision,
        "required_gate_count": len(REQUIRED_GATES),
        "provided_gate_count": len(seen_gate_ids),
        "missing_gates": missing_gates,
        "errors": errors,
        "warnings": warnings,
        "blockers": blockers,
        "gates": gate_reports,
        "limitations": [
            "This validator checks release evidence completeness only; it does not run compile, tests, harness, replay, performance, or manual playtests.",
            "Historical smoke reports are only acceptable when they directly cover the current release candidate and are marked non-synthetic.",
            "A ready decision requires every required gate to be present, passing, and backed by existing evidence paths.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Release Candidate Evidence Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Candidate: `{report['candidate_id']}`",
        f"- Release stage: `{report['release_stage']}`",
        f"- Decision: `{report['decision']}`",
        f"- Required gates: {report['required_gate_count']}",
        f"- Provided gates: {report['provided_gate_count']}",
        "",
        "## Gate Summary",
        "",
        "| Gate | Status | Evidence | Synthetic |",
        "|---|---|---:|---|",
    ]
    for gate in report["gates"]:
        lines.append(
            f"| `{gate['id']}` | `{gate['status']}` | {gate['evidence_count']} | {gate['synthetic']} |"
        )
    lines.extend(["", "## Blockers", ""])
    if report["blockers"]:
        lines.extend(f"- {blocker}" for blocker in report["blockers"])
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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm release candidate evidence.")
    parser.add_argument("manifest", type=Path, help="Release candidate evidence manifest JSON")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root for resolving evidence paths")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON validation report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown validation summary")
    parser.add_argument(
        "--allow-not-ready",
        action="store_true",
        help="Exit 0 after writing a not-ready report; useful for recording known blockers",
    )
    args = parser.parse_args()

    report = build_report(args.manifest, args.repo_root)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))

    if report["decision"] == "release_candidate_ready" or args.allow_not_ready:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
