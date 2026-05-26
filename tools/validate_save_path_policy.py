#!/usr/bin/env python3
"""Validate platform save path policy contracts.

This gate checks logical storage roots and local-data guardrails for save files,
Runtime settings, telemetry, replay, and crash reports. It does not inspect the
real host filesystem or prove Runtime has implemented platform-native paths.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REQUIRED_STORAGE_ROOTS = {
    "save_files",
    "runtime_settings",
    "local_telemetry",
    "local_replay",
    "crash_reports",
}
REQUIRED_SAVE_CONTRACTS = {"save-state-v0", "save-state-v1"}
REQUIRED_PATH_RULES = {
    "local_only_by_default": True,
    "no_absolute_paths_in_save": True,
    "no_personal_identity_in_paths": True,
    "player_visible_delete_export": True,
    "delete_requires_explicit_user_action": True,
    "delete_scope_must_be_configured_roots": True,
    "export_format_json": True,
    "migration_must_keep_original_until_success": True,
    "cloud_sync_requires_manual_review": True,
    "platform_paths_must_be_reviewed_before_release": True,
}
REQUIRED_RELEASE_REQUIREMENTS = {
    "manual_privacy_review",
    "platform_path_review",
    "delete_export_controls",
    "save_migration_fixtures",
    "release_candidate_evidence_gate",
}
REQUIRED_PROHIBITED_FRAGMENTS = {
    "/Users/",
    "C:\\",
    "~/",
    "email",
    "ip_address",
    "player_name",
    "real_name",
    "absolute_path",
    "free_text_input",
}
PATH_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]*[a-z0-9]$")
LOGICAL_PATH_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_/-]*[a-z0-9]$")


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
    if payload.get("policy_version") != 1:
        errors.append("policy_version must be 1")
    if payload.get("policy_id") != "platform-save-path-v0":
        errors.append("policy_id must be platform-save-path-v0")
    if payload.get("scope") != "local-save-and-runtime-data":
        errors.append("scope must be local-save-and-runtime-data")
    if payload.get("status") not in {"contract-only", "implemented", "deprecated"}:
        errors.append("status must be one of contract-only, implemented, deprecated")
    if not is_nonempty_string(payload.get("summary")):
        errors.append("summary must be non-empty")

    save_contracts = string_set(payload.get("save_contract_ids"))
    missing_contracts = sorted(REQUIRED_SAVE_CONTRACTS - save_contracts)
    if missing_contracts:
        errors.append(f"save_contract_ids missing required entries: {', '.join(missing_contracts)}")


def validate_logical_path(path_value: Any, prohibited_fragments: set[str], label: str, errors: list[str]) -> None:
    if not is_nonempty_string(path_value):
        errors.append(f"{label} must be non-empty")
        return
    path_text = str(path_value)
    if path_text.startswith("/") or path_text.startswith("~") or ":" in path_text or "\\" in path_text:
        errors.append(f"{label} must be a logical relative path, not an absolute or host path")
    if ".." in Path(path_text).parts:
        errors.append(f"{label} must not contain parent directory traversal")
    if not LOGICAL_PATH_PATTERN.match(path_text):
        errors.append(f"{label} must use lowercase logical path fragments")
    for fragment in prohibited_fragments:
        if fragment.lower() in path_text.lower():
            errors.append(f"{label} contains prohibited path fragment `{fragment}`")


def validate_storage_roots(payload: dict[str, Any], errors: list[str]) -> int:
    roots = payload.get("storage_roots")
    if not isinstance(roots, list) or not roots:
        errors.append("storage_roots must be a non-empty list")
        return 0

    prohibited = string_set(payload.get("prohibited_path_fragments"))
    seen_ids: set[str] = set()
    for index, root in enumerate(roots):
        label = f"storage_roots[{index}]"
        if not isinstance(root, dict):
            errors.append(f"{label} must be an object")
            continue
        root_id = root.get("id")
        if not is_nonempty_string(root_id) or not PATH_ID_PATTERN.match(str(root_id)):
            errors.append(f"{label}.id must use lowercase snake_case")
        else:
            if root_id in seen_ids:
                errors.append(f"{label}.id duplicates another storage root: {root_id}")
            seen_ids.add(str(root_id))
        for field in ("purpose", "logical_path"):
            if not is_nonempty_string(root.get(field)):
                errors.append(f"{label}.{field} must be non-empty")
        validate_logical_path(root.get("logical_path"), prohibited, f"{label}.logical_path", errors)
        contains = string_set(root.get("contains"))
        if not contains:
            errors.append(f"{label}.contains must be a non-empty list")
        for field in ("delete_supported", "export_supported"):
            if root.get(field) is not True:
                errors.append(f"{label}.{field} must be true")
        if not isinstance(root.get("migration_participates"), bool):
            errors.append(f"{label}.migration_participates must be a boolean")
        if root.get("cloud_sync_allowed") is not False:
            errors.append(f"{label}.cloud_sync_allowed must remain false until manual platform review")

    missing_roots = sorted(REQUIRED_STORAGE_ROOTS - seen_ids)
    if missing_roots:
        errors.append(f"storage_roots missing required ids: {', '.join(missing_roots)}")
    return len(seen_ids)


def validate_path_rules(payload: dict[str, Any], errors: list[str]) -> None:
    rules = payload.get("path_rules")
    if not isinstance(rules, dict):
        errors.append("path_rules must be an object")
        return
    for key, expected in REQUIRED_PATH_RULES.items():
        if rules.get(key) is not expected:
            errors.append(f"path_rules.{key} must be {json.dumps(expected)}")


def validate_prohibited_fragments(payload: dict[str, Any], errors: list[str]) -> None:
    fragments = string_set(payload.get("prohibited_path_fragments"))
    missing = sorted(REQUIRED_PROHIBITED_FRAGMENTS - fragments)
    if missing:
        errors.append(f"prohibited_path_fragments missing required entries: {', '.join(missing)}")


def validate_release_requirements(payload: dict[str, Any], errors: list[str]) -> None:
    requirements = string_set(payload.get("release_requirements"))
    missing = sorted(REQUIRED_RELEASE_REQUIREMENTS - requirements)
    if missing:
        errors.append(f"release_requirements missing required entries: {', '.join(missing)}")

    blockers = string_set(payload.get("blockers"))
    if payload.get("status") != "implemented" and not blockers:
        errors.append("non-implemented save path policy must list blockers")


def build_report(policy_path: Path) -> dict[str, Any]:
    payload = load_json_object(policy_path)
    errors: list[str] = []
    warnings: list[str] = []

    validate_top_level(payload, errors)
    validate_prohibited_fragments(payload, errors)
    root_count = validate_storage_roots(payload, errors)
    validate_path_rules(payload, errors)
    validate_release_requirements(payload, errors)

    blockers = sorted(string_set(payload.get("blockers")))
    return {
        "report_version": 1,
        "source": str(policy_path),
        "policy_id": payload.get("policy_id"),
        "status": payload.get("status"),
        "decision": "save_path_policy_valid" if not errors else "save_path_policy_invalid",
        "storage_root_count": root_count,
        "blocker_count": len(blockers),
        "errors": errors,
        "warnings": warnings,
        "blockers": blockers,
        "limitations": [
            "This validator checks logical path policy structure only; it does not inspect the host filesystem.",
            "A valid policy does not prove Runtime has implemented platform-native save paths.",
            "A valid policy does not replace legal review, platform review, cloud save policy, or manual UI verification.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Save Path Policy Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Policy: `{report['policy_id']}`",
        f"- Status: `{report['status']}`",
        f"- Decision: `{report['decision']}`",
        f"- Storage roots: {report['storage_root_count']}",
        f"- Blockers: {report['blocker_count']}",
        "",
        "## Blockers",
        "",
    ]
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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm save path policies.")
    parser.add_argument(
        "policy",
        type=Path,
        nargs="?",
        default=Path("harness/save_contract/platform_save_path_policy_v0.json"),
        help="Save path policy JSON",
    )
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
    return 0 if report["decision"] == "save_path_policy_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
