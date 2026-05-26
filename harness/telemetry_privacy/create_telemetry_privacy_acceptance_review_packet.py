#!/usr/bin/env python3
"""Create a telemetry/privacy release acceptance evidence packet.

This packet aggregates the privacy policy, Runtime privacy settings contract,
upload transport contract, manual privacy review, manual platform path review,
manual legal/compliance review, and the Release Candidate telemetry_privacy
gate. It does not provide legal advice, approve platform compliance, implement
upload transport, or mark a release candidate as ready.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


TODO_MARKERS = ("TODO", "<", ">")
REQUIRED_EVIDENCE = [
    {
        "field": "policy_validation_report",
        "label": "Telemetry privacy policy",
        "expected_decision": "telemetry_privacy_policy_valid",
        "blocking_if_missing": True,
    },
    {
        "field": "runtime_contract_validation_report",
        "label": "Runtime privacy settings contract",
        "expected_decision": "runtime_privacy_settings_contract_valid",
        "blocking_if_missing": True,
    },
    {
        "field": "upload_transport_validation_report",
        "label": "Upload transport contract",
        "expected_decision": "upload_transport_contract_valid",
        "blocking_if_missing": True,
    },
    {
        "field": "save_path_policy_report",
        "label": "Platform save path policy",
        "expected_decision": "save_path_policy_valid",
        "blocking_if_missing": True,
    },
    {
        "field": "manual_privacy_review_template",
        "label": "Manual privacy review source",
        "expected_decision": None,
        "blocking_if_missing": True,
    },
    {
        "field": "manual_privacy_review_packet",
        "label": "Manual privacy review packet",
        "expected_decision": None,
        "blocking_if_missing": True,
    },
    {
        "field": "manual_privacy_review_validation_report",
        "label": "Manual privacy review validation",
        "expected_decision": "manual_privacy_review_valid",
        "blocking_if_missing": True,
    },
    {
        "field": "manual_platform_path_review_template",
        "label": "Manual platform path review source",
        "expected_decision": None,
        "blocking_if_missing": True,
    },
    {
        "field": "manual_platform_path_review_packet",
        "label": "Manual platform path review packet",
        "expected_decision": None,
        "blocking_if_missing": True,
    },
    {
        "field": "manual_platform_path_review_validation_report",
        "label": "Manual platform path review validation",
        "expected_decision": "manual_platform_path_review_valid",
        "blocking_if_missing": True,
    },
    {
        "field": "manual_legal_review_template",
        "label": "Manual legal/compliance review source",
        "expected_decision": None,
        "blocking_if_missing": True,
    },
    {
        "field": "manual_legal_review_packet",
        "label": "Manual legal/compliance review packet",
        "expected_decision": None,
        "blocking_if_missing": True,
    },
    {
        "field": "manual_legal_review_validation_report",
        "label": "Manual legal/compliance review validation",
        "expected_decision": "manual_legal_review_valid",
        "blocking_if_missing": True,
    },
    {
        "field": "release_candidate_evidence",
        "label": "Release candidate telemetry_privacy gate",
        "expected_decision": None,
        "blocking_if_missing": True,
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


def markdown_escape(text: Any) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def code(value: Any) -> str:
    return f"`{markdown_escape(value)}`"


def evidence_status(repo_root: Path, value: str | None) -> tuple[str, str | None, Path | None]:
    if not is_nonempty_string(value):
        return "missing", None, None
    path = resolve_repo_path(repo_root, str(value))
    if not is_inside_repo(repo_root, path):
        return "outside_repo", None, None
    if not path.exists():
        return "missing_file", relative_repo_path(repo_root, path), None
    return "exists", relative_repo_path(repo_root, path), path


def report_payload(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists() or path.suffix != ".json":
        return None
    try:
        return load_json_object(path)
    except (OSError, ValueError, json.JSONDecodeError):
        return None


def report_decision(path: Path | None) -> str | None:
    payload = report_payload(path)
    if payload is None:
        return None
    decision = payload.get("decision")
    return str(decision) if is_nonempty_string(decision) else None


def upload_transport_status(path: Path | None) -> dict[str, Any]:
    payload = report_payload(path)
    if payload is None:
        return {"decision": None, "implementation_status": None, "transport_mode": None}
    return {
        "decision": payload.get("decision"),
        "implementation_status": payload.get("implementation_status"),
        "transport_mode": payload.get("transport_mode"),
    }


def manual_review_source_status(path: Path | None, repo_root: Path) -> dict[str, Any]:
    if path is None or not path.exists():
        return {
            "path": None,
            "gate_decision": None,
            "reviewer": "",
            "reviewed_at": "",
            "check_count": 0,
            "todo_count": 0,
            "status": "missing",
        }
    try:
        payload = load_json_object(path)
    except (OSError, ValueError, json.JSONDecodeError):
        return {
            "path": relative_repo_path(repo_root, path),
            "gate_decision": None,
            "reviewer": "",
            "reviewed_at": "",
            "check_count": 0,
            "todo_count": 0,
            "status": "invalid_json",
        }
    checks = payload.get("checks")
    check_count = len([item for item in checks if isinstance(item, dict)]) if isinstance(checks, list) else 0
    count = todo_count(payload)
    if count:
        status = "draft_todo"
    elif payload.get("gate_decision") == "pass":
        status = "filled_pass"
    else:
        status = "filled_not_pass"
    return {
        "path": relative_repo_path(repo_root, path),
        "gate_decision": payload.get("gate_decision"),
        "reviewer": payload.get("reviewer", ""),
        "reviewed_at": payload.get("reviewed_at", ""),
        "check_count": check_count,
        "todo_count": count,
        "status": status,
    }


def rc_telemetry_gate_status(path: Path | None) -> dict[str, Any]:
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
        if isinstance(gate, dict) and gate.get("id") == "telemetry_privacy":
            evidence = string_list(gate.get("evidence_paths"))
            return {
                "status": gate.get("status"),
                "summary": gate.get("summary", ""),
                "synthetic": gate.get("synthetic"),
                "evidence_count": len(evidence),
            }
    return {"status": "missing_gate", "summary": "", "synthetic": None, "evidence_count": 0}


def build_packet(repo_root: Path, evidence_paths: dict[str, str]) -> dict[str, Any]:
    errors: list[str] = []
    evidence = []
    resolved_paths: dict[str, Path | None] = {}
    for requirement in REQUIRED_EVIDENCE:
        field = str(requirement["field"])
        status, resolved_text, resolved_path = evidence_status(repo_root, evidence_paths.get(field))
        resolved_paths[field] = resolved_path
        decision = report_decision(resolved_path)
        expected = requirement["expected_decision"]
        evidence.append(
            {
                "field": field,
                "label": requirement["label"],
                "value": evidence_paths.get(field),
                "status": status,
                "resolved_path": resolved_text,
                "decision": decision,
                "expected_decision": expected,
                "blocking_if_missing": requirement["blocking_if_missing"],
            }
        )
        if status != "exists" and requirement["blocking_if_missing"]:
            errors.append(f"{field} evidence must exist")

    decisions = {
        field: report_decision(path)
        for field, path in resolved_paths.items()
        if field.endswith("_validation_report") or field.endswith("_policy_report")
    }
    upload_status = upload_transport_status(resolved_paths.get("upload_transport_validation_report"))
    manual_sources = {
        "privacy": manual_review_source_status(
            resolved_paths.get("manual_privacy_review_template"),
            repo_root,
        ),
        "platform_path": manual_review_source_status(
            resolved_paths.get("manual_platform_path_review_template"),
            repo_root,
        ),
        "legal": manual_review_source_status(
            resolved_paths.get("manual_legal_review_template"),
            repo_root,
        ),
    }
    release_gate = rc_telemetry_gate_status(resolved_paths.get("release_candidate_evidence"))

    blockers: list[str] = []
    for item in evidence:
        expected = item["expected_decision"]
        if expected is not None and item["decision"] != expected:
            blockers.append(f"{item['field']} decision is `{item['decision']}`; expected `{expected}`")

    for label, status in manual_sources.items():
        if status["todo_count"]:
            blockers.append(f"{label} manual review source still contains TODO placeholders")
        if status["gate_decision"] != "pass":
            blockers.append(f"{label} manual review gate is `{status['gate_decision']}`")

    if upload_status["implementation_status"] != "implemented":
        blockers.append(
            "upload transport implementation_status is "
            f"`{upload_status['implementation_status']}`; Runtime upload evidence is still missing"
        )
    if release_gate["status"] != "pass":
        blockers.append(f"release candidate telemetry_privacy gate is `{release_gate['status']}`")

    if errors:
        decision = "telemetry_privacy_acceptance_review_packet_invalid"
    elif blockers:
        decision = "telemetry_privacy_acceptance_review_packet_needs_evidence"
    else:
        decision = "telemetry_privacy_acceptance_review_packet_ready_for_release_gate"

    return {
        "report_version": 1,
        "repo_root": str(repo_root),
        "decision": decision,
        "evidence_count": len(evidence),
        "existing_evidence_count": sum(1 for item in evidence if item["status"] == "exists"),
        "errors": errors,
        "blockers": blockers,
        "evidence": evidence,
        "decisions": decisions,
        "upload_transport_status": upload_status,
        "manual_review_sources": manual_sources,
        "release_candidate_telemetry_privacy_gate": release_gate,
        "required_next_steps": [
            "Replace TODO placeholders in manual privacy, platform path, and legal/compliance review records.",
            "Run each manual review validator and keep valid JSON/Markdown reports.",
            "Implement or explicitly remove upload transport from the release scope, then attach Runtime evidence for the chosen path.",
            "Update the Release Candidate telemetry_privacy gate only after real human review and Runtime evidence exist.",
        ],
        "limitations": [
            "This packet organizes telemetry/privacy release acceptance evidence only.",
            "It does not provide legal advice, platform approval, store approval, upload approval, or release approval.",
            "Template packets, TODO review drafts, and fixture reports cannot replace real human review evidence.",
            "A ready packet still must be combined with compile, Harness, Replay, performance, playtest, content, and package gates.",
        ],
    }


def write_markdown(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Telemetry Privacy Acceptance Review Packet",
        "",
        f"- Decision: `{packet['decision']}`",
        f"- Evidence files: {packet['existing_evidence_count']} / {packet['evidence_count']}",
        f"- Upload implementation status: `{packet['upload_transport_status']['implementation_status']}`",
        f"- RC telemetry_privacy gate: `{packet['release_candidate_telemetry_privacy_gate']['status']}`",
        "",
        "## Evidence",
        "",
        "| Field | Status | Decision | Expected | Path |",
        "|---|---|---|---|---|",
    ]
    for item in packet["evidence"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    code(item["field"]),
                    code(item["status"]),
                    code(item["decision"] or ""),
                    code(item["expected_decision"] or ""),
                    code(item["resolved_path"] or item["value"]),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Manual Review Sources", "", "| Review | Status | Gate | Checks | TODO |", "|---|---|---|---:|---:|"])
    for name, status in packet["manual_review_sources"].items():
        lines.append(
            f"| `{name}` | `{status['status']}` | `{status['gate_decision']}` | "
            f"{status['check_count']} | {status['todo_count']} |"
        )

    lines.extend(["", "## Release Candidate Gate", ""])
    gate = packet["release_candidate_telemetry_privacy_gate"]
    lines.append(f"- Status: `{gate['status']}`")
    lines.append(f"- Evidence count: `{gate['evidence_count']}`")
    lines.append(f"- Synthetic: `{gate['synthetic']}`")
    lines.append(f"- Summary: {markdown_escape(gate['summary'])}")

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
        "policy_validation_report": "harness/reports/2026-05-26_telemetry_privacy_policy_001/telemetry_privacy_policy.json",
        "runtime_contract_validation_report": "harness/reports/2026-05-26_runtime_privacy_settings_contract_001/runtime_privacy_settings_contract.json",
        "upload_transport_validation_report": "harness/reports/2026-05-26_upload_transport_contract_001/upload_transport_contract.json",
        "save_path_policy_report": "harness/reports/2026-05-26_save_path_policy_v0_001/save_path_policy.json",
        "manual_privacy_review_template": "harness/telemetry_privacy/manual_privacy_review_template.json",
        "manual_privacy_review_packet": "harness/reports/2026-05-26_manual_privacy_review_packet_001/summary.md",
        "manual_privacy_review_validation_report": "harness/reports/2026-05-26_manual_privacy_review_template_001/manual_privacy_review.json",
        "manual_platform_path_review_template": "harness/save_contract/manual_platform_path_review_template.json",
        "manual_platform_path_review_packet": "harness/reports/2026-05-26_manual_platform_path_review_packet_001/summary.md",
        "manual_platform_path_review_validation_report": "harness/reports/2026-05-26_manual_platform_path_review_template_001/manual_platform_path_review.json",
        "manual_legal_review_template": "harness/telemetry_privacy/manual_legal_review_template.json",
        "manual_legal_review_packet": "harness/reports/2026-05-26_manual_legal_review_packet_001/summary.md",
        "manual_legal_review_validation_report": "harness/reports/2026-05-26_manual_legal_review_template_001/manual_legal_review.json",
        "release_candidate_evidence": "harness/release/current_local_rc_evidence.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a telemetry/privacy release acceptance evidence packet.")
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
