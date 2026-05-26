#!/usr/bin/env python3
"""Validate telemetry upload transport contracts.

This dependency-free gate checks the guardrails for a future upload transport:
default-off behavior, explicit consent, privacy policy bindings, payload field
whitelists, raw replay blocking, local queue bounds, and release evidence
requirements. It does not prove Runtime upload transport exists.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from validate_runtime_privacy_settings_contract import build_report as build_runtime_contract_report
from validate_telemetry_privacy_policy import build_report as build_policy_report


REQUIRED_RELEASE_REQUIREMENTS = {
    "telemetry_privacy_policy",
    "runtime_privacy_settings_contract",
    "manual_privacy_review",
    "manual_platform_path_review",
    "upload_transport_runtime_smoke",
    "release_candidate_evidence_gate",
}
REQUIRED_LIMITATIONS = {
    "does_not_prove_runtime_upload_transport",
    "does_not_provide_legal_or_platform_approval",
    "does_not_make_release_candidate_ready",
}
REQUIRED_PAYLOAD_FIELDS = {
    "timestamp",
    "run_id",
    "session_id",
    "game_version",
    "content_hash",
    "map_id",
    "character_id",
    "difficulty",
    "elapsed_seconds",
    "event_type",
    "event_counts",
    "final_metrics",
}
REQUIRED_FALSE_PAYLOAD_FLAGS = {
    "includes_personal_identity",
    "includes_ip_address",
    "includes_file_paths",
    "includes_free_text",
    "includes_raw_replay",
}
DISALLOWED_FIELD_FRAGMENTS = [
    "email",
    "ip",
    "file_path",
    "path",
    "free_text",
    "player_name",
    "real_name",
    "action_stream",
    "raw_replay",
]
ALLOWED_IMPLEMENTATION_STATUSES = {"planned", "disabled", "implemented"}


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_set(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {item for item in value if isinstance(item, str) and item.strip()}


def require_bool(container: dict[str, Any], field: str, expected: bool, label: str, errors: list[str]) -> None:
    if container.get(field) is not expected:
        errors.append(f"{label}.{field} must be {json.dumps(expected)}")


def validate_top_level(payload: dict[str, Any], errors: list[str]) -> None:
    if not isinstance(payload.get("contract_version"), int) or payload["contract_version"] <= 0:
        errors.append("contract_version must be a positive integer")
    for field in ("contract_id", "scope", "policy_id", "runtime_privacy_contract_id", "summary"):
        if not is_nonempty_string(payload.get(field)):
            errors.append(f"{field} must be non-empty")
    if payload.get("implementation_status") not in ALLOWED_IMPLEMENTATION_STATUSES:
        errors.append(
            "implementation_status must be one of "
            + ", ".join(sorted(ALLOWED_IMPLEMENTATION_STATUSES))
        )


def validate_bindings(
    payload: dict[str, Any],
    policy_path: Path | None,
    runtime_contract_path: Path | None,
    errors: list[str],
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None]:
    policy: dict[str, Any] | None = None
    runtime_contract: dict[str, Any] | None = None
    policy_report: dict[str, Any] | None = None
    runtime_report: dict[str, Any] | None = None

    if policy_path is not None:
        policy = load_json_object(policy_path)
        policy_report = build_policy_report(policy_path)
        if policy_report["decision"] != "telemetry_privacy_policy_valid":
            errors.append("bound telemetry privacy policy must validate")
        if payload.get("policy_id") != policy.get("policy_id"):
            errors.append("policy_id must match telemetry privacy policy")

    if runtime_contract_path is not None:
        runtime_contract = load_json_object(runtime_contract_path)
        runtime_report = build_runtime_contract_report(runtime_contract_path, policy_path, None)
        if runtime_report["decision"] != "runtime_privacy_settings_contract_valid":
            errors.append("bound runtime privacy settings contract must validate")
        if payload.get("runtime_privacy_contract_id") != runtime_contract.get("contract_id"):
            errors.append("runtime_privacy_contract_id must match Runtime privacy settings contract")
        if policy is not None and runtime_contract.get("policy_id") != policy.get("policy_id"):
            errors.append("Runtime privacy settings contract policy_id must match telemetry privacy policy")

    return policy, policy_report, runtime_report


def validate_transport(payload: dict[str, Any], errors: list[str]) -> None:
    transport = payload.get("transport")
    if not isinstance(transport, dict):
        errors.append("transport must be an object")
        return

    for field in (
        "upload_enabled",
        "implementation_ready",
        "default_enabled",
    ):
        require_bool(transport, field, False, "transport", errors)
    for field in (
        "requires_explicit_consent",
        "requires_manual_privacy_review",
        "requires_release_candidate_gate",
    ):
        require_bool(transport, field, True, "transport", errors)

    if transport.get("upload_enabled") is False and transport.get("endpoint") is not None:
        errors.append("transport.endpoint must be null while upload is disabled")
    if transport.get("implementation_ready") is False and transport.get("method") is not None:
        errors.append("transport.method must be null while implementation is not ready")
    if transport.get("upload_enabled") is True:
        endpoint = transport.get("endpoint")
        if not is_nonempty_string(endpoint) or not str(endpoint).startswith("https://"):
            errors.append("transport.endpoint must be https when upload_enabled is true")
    if not is_nonempty_string(transport.get("failure_mode")):
        errors.append("transport.failure_mode must be non-empty")
    if not is_nonempty_string(transport.get("retry_policy")):
        errors.append("transport.retry_policy must be non-empty")


def validate_queue(payload: dict[str, Any], policy: dict[str, Any] | None, errors: list[str]) -> None:
    queue = payload.get("queue")
    if not isinstance(queue, dict):
        errors.append("queue must be an object")
        return

    for field in ("local_spool_only", "flush_requires_consent", "delete_with_local_data", "export_with_local_data"):
        require_bool(queue, field, True, "queue", errors)
    if not is_nonempty_string(queue.get("path_root")):
        errors.append("queue.path_root must be non-empty")
    retention_days = queue.get("retention_days")
    if not isinstance(retention_days, int) or not 1 <= retention_days <= 180:
        errors.append("queue.retention_days must be an integer from 1 to 180")
    if not isinstance(queue.get("max_batch_events"), int) or queue["max_batch_events"] <= 0:
        errors.append("queue.max_batch_events must be a positive integer")
    if not isinstance(queue.get("max_batch_bytes"), int) or queue["max_batch_bytes"] <= 0:
        errors.append("queue.max_batch_bytes must be a positive integer")

    if policy is not None:
        storage = policy.get("storage")
        if isinstance(storage, dict) and isinstance(storage.get("retention_days"), int):
            if isinstance(retention_days, int) and retention_days > storage["retention_days"]:
                errors.append("queue.retention_days must not exceed telemetry policy retention_days")


def validate_payload(payload: dict[str, Any], policy: dict[str, Any] | None, errors: list[str]) -> None:
    payload_contract = payload.get("payload")
    if not isinstance(payload_contract, dict):
        errors.append("payload must be an object")
        return

    if payload_contract.get("format") != "json":
        errors.append("payload.format must be json")
    event_fields = string_set(payload_contract.get("event_fields"))
    if not event_fields:
        errors.append("payload.event_fields must be a non-empty list")
    missing_fields = sorted(REQUIRED_PAYLOAD_FIELDS - event_fields)
    if missing_fields:
        errors.append(f"payload.event_fields missing required entries: {', '.join(missing_fields)}")
    for field in sorted(event_fields):
        lowered = field.lower()
        for fragment in DISALLOWED_FIELD_FRAGMENTS:
            if fragment in lowered:
                errors.append(f"payload.event_fields contains disallowed field `{field}`")

    if policy is not None:
        allowed = string_set(policy.get("allowed_event_fields"))
        prohibited = string_set(policy.get("prohibited_fields"))
        outside_policy = sorted(event_fields - allowed)
        if outside_policy:
            errors.append(f"payload.event_fields outside telemetry policy: {', '.join(outside_policy)}")
        prohibited_overlap = sorted(event_fields & prohibited)
        if prohibited_overlap:
            errors.append(f"payload.event_fields overlap prohibited_fields: {', '.join(prohibited_overlap)}")

    require_bool(payload_contract, "aggregate_only", True, "payload", errors)
    for field in REQUIRED_FALSE_PAYLOAD_FLAGS:
        require_bool(payload_contract, field, False, "payload", errors)
    if payload_contract.get("session_id_mode") != "anonymous":
        errors.append("payload.session_id_mode must be anonymous")
    require_bool(payload_contract, "content_hash_required", True, "payload", errors)
    require_bool(payload_contract, "run_id_required", True, "payload", errors)


def validate_raw_replay_and_crash_reports(payload: dict[str, Any], errors: list[str]) -> None:
    raw_replay = payload.get("raw_replay")
    if not isinstance(raw_replay, dict):
        errors.append("raw_replay must be an object")
    else:
        for field in ("upload_enabled", "default_enabled", "payload_allowed"):
            require_bool(raw_replay, field, False, "raw_replay", errors)
        for field in ("separate_consent_required", "debug_only"):
            require_bool(raw_replay, field, True, "raw_replay", errors)

    crash_reports = payload.get("crash_reports")
    if not isinstance(crash_reports, dict):
        errors.append("crash_reports must be an object")
    else:
        for field in ("upload_enabled", "default_enabled", "includes_stack_trace", "includes_file_paths", "includes_personal_identity"):
            require_bool(crash_reports, field, False, "crash_reports", errors)
        require_bool(crash_reports, "requires_explicit_consent", True, "crash_reports", errors)


def validate_release_and_limitations(payload: dict[str, Any], errors: list[str]) -> None:
    missing_release = sorted(REQUIRED_RELEASE_REQUIREMENTS - string_set(payload.get("release_requirements")))
    if missing_release:
        errors.append(f"release_requirements missing entries: {', '.join(missing_release)}")
    missing_limitations = sorted(REQUIRED_LIMITATIONS - string_set(payload.get("limitations")))
    if missing_limitations:
        errors.append(f"limitations missing entries: {', '.join(missing_limitations)}")


def build_report(
    contract_path: Path,
    policy_path: Path | None = None,
    runtime_contract_path: Path | None = None,
) -> dict[str, Any]:
    payload = load_json_object(contract_path)
    errors: list[str] = []
    warnings: list[str] = []

    validate_top_level(payload, errors)
    policy, policy_report, runtime_report = validate_bindings(payload, policy_path, runtime_contract_path, errors)
    validate_transport(payload, errors)
    validate_queue(payload, policy, errors)
    validate_payload(payload, policy, errors)
    validate_raw_replay_and_crash_reports(payload, errors)
    validate_release_and_limitations(payload, errors)

    return {
        "report_version": 1,
        "source": str(contract_path),
        "policy": str(policy_path) if policy_path is not None else None,
        "runtime_contract": str(runtime_contract_path) if runtime_contract_path is not None else None,
        "decision": "upload_transport_contract_valid" if not errors else "upload_transport_contract_invalid",
        "implementation_status": payload.get("implementation_status"),
        "bound_policy_decision": policy_report["decision"] if policy_report is not None else None,
        "bound_runtime_contract_decision": runtime_report["decision"] if runtime_report is not None else None,
        "errors": errors,
        "warnings": warnings,
        "limitations": [
            "This validator checks upload transport guardrails and policy bindings only.",
            "It does not prove Runtime has implemented upload transport, queue flushing, networking, deletion UI, or platform privacy compliance.",
            "Release still requires manual privacy review, platform path review, Runtime smoke evidence, and Release Candidate gates.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Upload Transport Contract Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Policy: `{report['policy']}`",
        f"- Runtime contract: `{report['runtime_contract']}`",
        f"- Decision: `{report['decision']}`",
        f"- Implementation status: `{report['implementation_status']}`",
        f"- Bound policy decision: `{report['bound_policy_decision']}`",
        f"- Bound runtime contract decision: `{report['bound_runtime_contract_decision']}`",
        "",
        "## Errors",
        "",
    ]
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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm telemetry upload transport contracts.")
    parser.add_argument("contract", type=Path, help="Telemetry upload transport contract JSON")
    parser.add_argument("--policy", type=Path, default=None, help="Telemetry privacy policy JSON")
    parser.add_argument("--runtime-contract", type=Path, default=None, help="Runtime privacy settings contract JSON")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON validation report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown validation summary")
    args = parser.parse_args()

    report = build_report(args.contract, args.policy, args.runtime_contract)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "upload_transport_contract_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
