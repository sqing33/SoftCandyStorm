#!/usr/bin/env python3
"""Validate telemetry privacy policy records.

This dependency-free gate checks that a future telemetry policy stays local
first, anonymous, opt-out capable, and explicit-consent based for uploads. It is
not legal advice and does not prove Runtime has implemented the policy.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_PROHIBITED_FIELDS = {
    "personal_identity",
    "email",
    "ip_address",
    "file_path",
    "free_text_input",
    "raw_replay_action_stream",
}
REQUIRED_PURPOSES = {"balance", "crash_analysis", "gameplay_improvement"}
REQUIRED_PLAYER_CONTROLS = {
    "disable_upload": True,
    "delete_local_data": True,
    "export_local_data": True,
    "separate_raw_replay_consent": True,
}
REQUIRED_RELEASE_REQUIREMENTS = {
    "manual_privacy_review",
    "release_candidate_evidence_gate",
    "runtime_settings_toggle",
    "privacy_notice_text",
}
DISALLOWED_ALLOWED_FIELD_FRAGMENTS = [
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


def validate_bool_field(container: dict[str, Any], field: str, expected: bool, label: str, errors: list[str]) -> None:
    if container.get(field) is not expected:
        errors.append(f"{label}.{field} must be {json.dumps(expected)}")


def validate_upload_policy(payload: dict[str, Any], errors: list[str]) -> None:
    upload = payload.get("upload")
    if not isinstance(upload, dict):
        errors.append("upload must be an object")
        return
    validate_bool_field(upload, "default_enabled", False, "upload", errors)
    validate_bool_field(upload, "requires_explicit_consent", True, "upload", errors)

    enabled = upload.get("enabled")
    if not isinstance(enabled, bool):
        errors.append("upload.enabled must be a boolean")
    if enabled is True and not is_nonempty_string(upload.get("endpoint")):
        errors.append("upload.endpoint must be non-empty when upload.enabled is true")


def validate_identity_policy(payload: dict[str, Any], errors: list[str]) -> None:
    identity = payload.get("identity")
    if not isinstance(identity, dict):
        errors.append("identity must be an object")
        return
    expected = {
        "anonymous_session_ids": True,
        "collects_personal_identity": False,
        "collects_ip_address": False,
        "collects_file_paths": False,
        "collects_free_text": False,
    }
    for field, value in expected.items():
        validate_bool_field(identity, field, value, "identity", errors)


def validate_raw_replay_policy(payload: dict[str, Any], errors: list[str]) -> None:
    replay = payload.get("raw_replay_upload")
    if not isinstance(replay, dict):
        errors.append("raw_replay_upload must be an object")
        return
    validate_bool_field(replay, "default_enabled", False, "raw_replay_upload", errors)
    validate_bool_field(replay, "requires_explicit_consent", True, "raw_replay_upload", errors)
    validate_bool_field(replay, "allowed_only_for_debug_cases", True, "raw_replay_upload", errors)
    if replay.get("enabled") is True and replay.get("requires_explicit_consent") is not True:
        errors.append("raw_replay_upload.enabled requires explicit consent")


def validate_field_lists(payload: dict[str, Any], errors: list[str]) -> None:
    allowed = string_set(payload.get("allowed_event_fields"))
    prohibited = string_set(payload.get("prohibited_fields"))
    if not allowed:
        errors.append("allowed_event_fields must be a non-empty list of strings")
    if not prohibited:
        errors.append("prohibited_fields must be a non-empty list of strings")

    missing_prohibited = sorted(REQUIRED_PROHIBITED_FIELDS - prohibited)
    if missing_prohibited:
        errors.append(f"prohibited_fields missing required entries: {', '.join(missing_prohibited)}")

    overlap = sorted(allowed & prohibited)
    if overlap:
        errors.append(f"allowed_event_fields overlap prohibited_fields: {', '.join(overlap)}")

    for field in sorted(allowed):
        lowered = field.lower()
        for fragment in DISALLOWED_ALLOWED_FIELD_FRAGMENTS:
            if fragment in lowered:
                errors.append(f"allowed_event_fields contains disallowed field `{field}`")


def validate_purpose_and_storage(payload: dict[str, Any], errors: list[str]) -> None:
    purposes = string_set(payload.get("purposes"))
    missing_purposes = sorted(REQUIRED_PURPOSES - purposes)
    if missing_purposes:
        errors.append(f"purposes missing required entries: {', '.join(missing_purposes)}")

    storage = payload.get("storage")
    if not isinstance(storage, dict):
        errors.append("storage must be an object")
        return
    local_paths = string_set(storage.get("local_paths"))
    if not local_paths:
        errors.append("storage.local_paths must be a non-empty list of strings")
    retention_days = storage.get("retention_days")
    if not isinstance(retention_days, int) or not 1 <= retention_days <= 180:
        errors.append("storage.retention_days must be an integer from 1 to 180")
    validate_bool_field(storage, "delete_local_data_supported", True, "storage", errors)
    validate_bool_field(storage, "export_local_data_supported", True, "storage", errors)


def validate_controls_and_release(payload: dict[str, Any], errors: list[str]) -> None:
    controls = payload.get("player_controls")
    if not isinstance(controls, dict):
        errors.append("player_controls must be an object")
    else:
        for field, expected in REQUIRED_PLAYER_CONTROLS.items():
            validate_bool_field(controls, field, expected, "player_controls", errors)

    release_requirements = string_set(payload.get("release_requirements"))
    missing_requirements = sorted(REQUIRED_RELEASE_REQUIREMENTS - release_requirements)
    if missing_requirements:
        errors.append(f"release_requirements missing required entries: {', '.join(missing_requirements)}")


def build_report(policy_path: Path) -> dict[str, Any]:
    payload = load_json_object(policy_path)
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(payload.get("policy_version"), int) or payload["policy_version"] <= 0:
        errors.append("policy_version must be a positive integer")
    for field in ("policy_id", "scope", "summary"):
        if not is_nonempty_string(payload.get(field)):
            errors.append(f"{field} must be non-empty")

    validate_upload_policy(payload, errors)
    validate_identity_policy(payload, errors)
    validate_raw_replay_policy(payload, errors)
    validate_field_lists(payload, errors)
    validate_purpose_and_storage(payload, errors)
    validate_controls_and_release(payload, errors)

    return {
        "report_version": 1,
        "source": str(policy_path),
        "decision": "telemetry_privacy_policy_valid" if not errors else "telemetry_privacy_policy_invalid",
        "errors": errors,
        "warnings": warnings,
        "limitations": [
            "This validator checks privacy policy structure and guardrails only.",
            "It does not prove Runtime settings, upload transport, deletion flows, or legal compliance are implemented.",
            "Future telemetry upload still requires manual privacy review and release evidence.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Telemetry Privacy Policy Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Decision: `{report['decision']}`",
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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm telemetry privacy policy.")
    parser.add_argument("policy", type=Path, help="Telemetry privacy policy JSON file")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON validation report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown validation summary")
    args = parser.parse_args()

    report = build_report(args.policy)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "telemetry_privacy_policy_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
