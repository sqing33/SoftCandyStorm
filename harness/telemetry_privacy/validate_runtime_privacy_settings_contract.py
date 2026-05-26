#!/usr/bin/env python3
"""Validate Runtime privacy settings UI contracts.

This dependency-free gate checks the contract that future Runtime settings UI
must implement for telemetry, raw replay upload, crash reports, and local data
controls. It does not prove the UI is already implemented; it makes the expected
Runtime surface machine-checkable before release evidence can claim completion.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_SETTINGS = {
    "telemetry_upload_enabled": False,
    "raw_replay_upload_enabled": False,
    "crash_report_upload_enabled": False,
}
REQUIRED_DATA_ACTIONS = {
    "delete_local_data",
    "export_local_data",
    "open_privacy_notice",
}
REQUIRED_NOTICE_TOPICS = {
    "purposes",
    "anonymous_session",
    "default_off",
    "delete_export",
    "raw_replay_separate_consent",
    "prohibited_fields",
    "retention_days",
}
REQUIRED_RELEASE_REQUIREMENTS = {
    "manual_privacy_review",
    "runtime_settings_toggle",
    "privacy_notice_text",
    "delete_export_controls",
    "save_contract_binding",
    "release_candidate_evidence_gate",
}
REQUIRED_PURPOSE_LABELS = {
    "balance",
    "crash_analysis",
    "gameplay_improvement",
}
DISALLOWED_NOTICE_TEXT = {
    "always on",
    "always_on",
    "cannot disable",
    "cannot_disable",
    "自动上传",
    "无法关闭",
    "默认上传",
}


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


def validate_top_level(payload: dict[str, Any], errors: list[str]) -> None:
    if not isinstance(payload.get("contract_version"), int) or payload["contract_version"] <= 0:
        errors.append("contract_version must be a positive integer")
    for field in ("contract_id", "scope", "policy_id", "save_contract_id", "summary"):
        if not is_nonempty_string(payload.get(field)):
            errors.append(f"{field} must be non-empty")


def validate_policy_binding(payload: dict[str, Any], policy_path: Path | None, errors: list[str]) -> None:
    if policy_path is None:
        return
    policy = load_json_object(policy_path)
    if payload.get("policy_id") != policy.get("policy_id"):
        errors.append("policy_id must match telemetry privacy policy")

    upload = policy.get("upload")
    if isinstance(upload, dict):
        if upload.get("default_enabled") is not False:
            errors.append("bound telemetry policy upload.default_enabled must be false")
        if upload.get("requires_explicit_consent") is not True:
            errors.append("bound telemetry policy upload.requires_explicit_consent must be true")
    else:
        errors.append("bound telemetry policy upload must be an object")

    raw_replay = policy.get("raw_replay_upload")
    if isinstance(raw_replay, dict):
        if raw_replay.get("default_enabled") is not False:
            errors.append("bound telemetry policy raw_replay_upload.default_enabled must be false")
        if raw_replay.get("requires_explicit_consent") is not True:
            errors.append("bound telemetry policy raw_replay_upload.requires_explicit_consent must be true")
    else:
        errors.append("bound telemetry policy raw_replay_upload must be an object")


def validate_save_binding(payload: dict[str, Any], save_contract_path: Path | None, errors: list[str]) -> None:
    bindings = payload.get("settings_bindings")
    if not isinstance(bindings, dict):
        errors.append("settings_bindings must be an object")
        bindings = {}

    for setting, expected in REQUIRED_SETTINGS.items():
        if bindings.get(setting) is not expected:
            errors.append(f"settings_bindings.{setting} must be {json.dumps(expected)}")

    if save_contract_path is None:
        return
    save_contract = load_json_object(save_contract_path)
    if payload.get("save_contract_id") != save_contract.get("contract_id"):
        errors.append("save_contract_id must match save contract")
    save_settings = save_contract.get("settings")
    if not isinstance(save_settings, dict):
        errors.append("save contract settings must be an object")
    else:
        for setting, expected in REQUIRED_SETTINGS.items():
            if save_settings.get(setting) is not expected:
                errors.append(f"save contract settings.{setting} must be {json.dumps(expected)}")

    data_controls = save_contract.get("data_controls")
    if not isinstance(data_controls, dict):
        errors.append("save contract data_controls must be an object")
    else:
        expected_controls = {
            "local_only_by_default": True,
            "upload_requires_opt_in": True,
            "delete_save_available": True,
            "export_save_available": True,
        }
        for field, expected in expected_controls.items():
            if data_controls.get(field) is not expected:
                errors.append(f"save contract data_controls.{field} must be {json.dumps(expected)}")
        if data_controls.get("export_format") != "json":
            errors.append("save contract data_controls.export_format must be json")


def validate_ui_controls(payload: dict[str, Any], errors: list[str]) -> None:
    controls = payload.get("ui_controls")
    if not isinstance(controls, list):
        errors.append("ui_controls must be a list")
        return

    seen_settings: set[str] = set()
    for index, control in enumerate(controls):
        if not isinstance(control, dict):
            errors.append(f"ui_controls[{index}] must be an object")
            continue
        display_id = control.get("id") if is_nonempty_string(control.get("id")) else f"ui_controls[{index}]"
        for field in ("id", "label", "type", "setting"):
            if not is_nonempty_string(control.get(field)):
                errors.append(f"{display_id}: {field} must be non-empty")
        if control.get("type") != "toggle":
            errors.append(f"{display_id}: type must be toggle")
        setting = control.get("setting")
        if setting not in REQUIRED_SETTINGS:
            errors.append(f"{display_id}: setting must be one of {', '.join(sorted(REQUIRED_SETTINGS))}")
        else:
            if setting in seen_settings:
                errors.append(f"{display_id}: duplicate setting `{setting}`")
            seen_settings.add(str(setting))

        expected_bool_fields = {
            "default_enabled": False,
            "visible": True,
            "requires_explicit_consent": True,
            "can_disable": True,
            "separate_consent": True,
        }
        for field, expected in expected_bool_fields.items():
            if control.get(field) is not expected:
                errors.append(f"{display_id}: {field} must be {json.dumps(expected)}")

        notice_topics = string_set(control.get("notice_topics"))
        if not notice_topics:
            errors.append(f"{display_id}: notice_topics must be a non-empty list")
        if setting == "raw_replay_upload_enabled" and "raw_replay_separate_consent" not in notice_topics:
            errors.append(f"{display_id}: raw replay toggle must mention raw_replay_separate_consent")

    missing_settings = sorted(set(REQUIRED_SETTINGS) - seen_settings)
    if missing_settings:
        errors.append(f"ui_controls missing settings: {', '.join(missing_settings)}")


def validate_data_action_controls(payload: dict[str, Any], errors: list[str]) -> None:
    controls = payload.get("data_action_controls")
    if not isinstance(controls, list):
        errors.append("data_action_controls must be a list")
        return

    seen_actions: set[str] = set()
    for index, control in enumerate(controls):
        if not isinstance(control, dict):
            errors.append(f"data_action_controls[{index}] must be an object")
            continue
        display_id = control.get("id") if is_nonempty_string(control.get("id")) else f"data_action_controls[{index}]"
        for field in ("id", "label", "action"):
            if not is_nonempty_string(control.get(field)):
                errors.append(f"{display_id}: {field} must be non-empty")
        action = control.get("action")
        if is_nonempty_string(action):
            seen_actions.add(str(action))
        if control.get("visible") is not True:
            errors.append(f"{display_id}: visible must be true")
        if action == "delete_local_data":
            if control.get("confirmation_required") is not True:
                errors.append(f"{display_id}: delete_local_data requires confirmation_required true")
            if control.get("destructive") is not True:
                errors.append(f"{display_id}: delete_local_data requires destructive true")
        if action == "export_local_data" and control.get("format") != "json":
            errors.append(f"{display_id}: export_local_data format must be json")

    missing_actions = sorted(REQUIRED_DATA_ACTIONS - seen_actions)
    if missing_actions:
        errors.append(f"data_action_controls missing actions: {', '.join(missing_actions)}")


def validate_privacy_notice(payload: dict[str, Any], errors: list[str]) -> None:
    notice = payload.get("privacy_notice")
    if not isinstance(notice, dict):
        errors.append("privacy_notice must be an object")
        return
    if notice.get("language") != "zh-CN":
        errors.append("privacy_notice.language must be zh-CN")
    short_text = notice.get("short_text")
    if not is_nonempty_string(short_text):
        errors.append("privacy_notice.short_text must be non-empty")
    else:
        lowered = short_text.lower()
        for fragment in DISALLOWED_NOTICE_TEXT:
            if fragment in lowered:
                errors.append(f"privacy_notice.short_text contains disallowed claim `{fragment}`")

    missing_topics = sorted(REQUIRED_NOTICE_TOPICS - string_set(notice.get("required_topics")))
    if missing_topics:
        errors.append(f"privacy_notice.required_topics missing entries: {', '.join(missing_topics)}")

    prohibited_claims = string_set(notice.get("prohibited_claims"))
    if not prohibited_claims:
        errors.append("privacy_notice.prohibited_claims must be a non-empty list")
    purpose_labels = notice.get("purpose_labels")
    if not isinstance(purpose_labels, dict):
        errors.append("privacy_notice.purpose_labels must be an object")
    else:
        missing_purposes = sorted(
            purpose for purpose in REQUIRED_PURPOSE_LABELS if not is_nonempty_string(purpose_labels.get(purpose))
        )
        if missing_purposes:
            errors.append(f"privacy_notice.purpose_labels missing entries: {', '.join(missing_purposes)}")


def validate_release_requirements(payload: dict[str, Any], errors: list[str]) -> None:
    missing = sorted(REQUIRED_RELEASE_REQUIREMENTS - string_set(payload.get("release_requirements")))
    if missing:
        errors.append(f"release_requirements missing required entries: {', '.join(missing)}")


def build_report(
    contract_path: Path,
    policy_path: Path | None = None,
    save_contract_path: Path | None = None,
) -> dict[str, Any]:
    payload = load_json_object(contract_path)
    errors: list[str] = []
    warnings: list[str] = []

    validate_top_level(payload, errors)
    validate_policy_binding(payload, policy_path, errors)
    validate_save_binding(payload, save_contract_path, errors)
    validate_ui_controls(payload, errors)
    validate_data_action_controls(payload, errors)
    validate_privacy_notice(payload, errors)
    validate_release_requirements(payload, errors)

    return {
        "report_version": 1,
        "source": str(contract_path),
        "policy": str(policy_path) if policy_path is not None else None,
        "save_contract": str(save_contract_path) if save_contract_path is not None else None,
        "decision": "runtime_privacy_settings_contract_valid" if not errors else "runtime_privacy_settings_contract_invalid",
        "errors": errors,
        "warnings": warnings,
        "limitations": [
            "This validator checks the expected Runtime settings UI contract only.",
            "It does not prove Bevy Runtime has implemented the settings screen, persistence, deletion, export, or upload transport.",
            "Release still requires manual privacy review and executable Runtime verification.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Runtime Privacy Settings Contract Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Policy: `{report['policy']}`",
        f"- Save contract: `{report['save_contract']}`",
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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm Runtime privacy settings contract.")
    parser.add_argument("contract", type=Path, help="Runtime privacy settings contract JSON file")
    parser.add_argument("--policy", type=Path, default=None, help="Telemetry privacy policy JSON file")
    parser.add_argument("--save-contract", type=Path, default=None, help="Save state contract JSON file")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON validation report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown validation summary")
    args = parser.parse_args()

    report = build_report(args.contract, args.policy, args.save_contract)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "runtime_privacy_settings_contract_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
