#!/usr/bin/env python3
"""Validate save-state migration plans.

This gate checks that a planned save migration preserves local data controls and
meta progress before any Runtime migration code exists. It does not migrate
saves or approve a future schema by itself.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


PLAN_STATUSES = {"planned", "implemented", "deprecated"}
MAPPING_MODES = {"preserve", "copy", "set", "drop"}
REQUIRED_PRIVACY_INVARIANTS = {
    "telemetry_upload_enabled": False,
    "raw_replay_upload_enabled": False,
    "crash_report_upload_enabled": False,
    "local_only_by_default": True,
    "upload_requires_opt_in": True,
    "delete_save_available": True,
    "export_save_available": True,
}
REQUIRED_PRESERVED_SECTIONS = {
    "settings",
    "data_controls",
    "meta_progress.resources",
    "meta_progress.unlocks",
    "meta_progress.codex",
    "meta_progress.chapters",
    "meta_progress.completed_runs",
    "meta_progress.best_survival_seconds",
}
REQUIRED_FAILURE_POLICIES = {
    "on_missing_required_section": "abort_migration",
    "on_unknown_source_version": "abort_migration",
    "on_privacy_invariant_violation": "abort_migration",
    "on_partial_write": "keep_original_save",
}
REQUIRED_VALIDATION_TOPICS = {
    "source save must pass",
    "target save must pass",
    "never enable uploads by default",
    "migration_history",
    "write atomically",
}
TODO_MARKERS = ("TODO", "<", ">")
KEBAB_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$")


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


def resolve_repo_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def is_inside_repo(repo_root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return False
    return True


def validate_existing_repo_path(repo_root: Path, label: str, value: Any, errors: list[str]) -> Path | None:
    if not is_nonempty_string(value):
        errors.append(f"{label} must be non-empty")
        return None
    if has_placeholder(value):
        errors.append(f"{label} must not contain TODO or placeholder markers")
        return None
    resolved = resolve_repo_path(repo_root, str(value))
    if not is_inside_repo(repo_root, resolved):
        errors.append(f"{label} must stay inside repository: {value}")
        return None
    if not resolved.exists():
        errors.append(f"{label} does not exist: {value}")
        return None
    return resolved


def validate_metadata(payload: dict[str, Any], errors: list[str]) -> None:
    if payload.get("plan_version") != 1:
        errors.append("plan_version must be 1")
    migration_id = payload.get("migration_id")
    if not is_nonempty_string(migration_id):
        errors.append("migration_id must be non-empty")
    elif has_placeholder(migration_id) or not KEBAB_ID_PATTERN.match(str(migration_id)):
        errors.append("migration_id must be lowercase kebab-case without placeholders")
    if payload.get("status") not in PLAN_STATUSES:
        errors.append(f"status must be one of {', '.join(sorted(PLAN_STATUSES))}")
    if not is_nonempty_string(payload.get("summary")):
        errors.append("summary must be non-empty")
    elif has_placeholder(payload.get("summary")):
        errors.append("summary must not contain TODO or placeholder markers")

    if payload.get("source_contract_id") != "save-state-v0":
        errors.append("source_contract_id must be save-state-v0")
    source_schema_version = payload.get("source_schema_version")
    if source_schema_version != 1:
        errors.append("source_schema_version must be 1")
    if not is_nonempty_string(payload.get("target_contract_id")):
        errors.append("target_contract_id must be non-empty")
    elif payload.get("target_contract_id") == payload.get("source_contract_id"):
        errors.append("target_contract_id must differ from source_contract_id")
    target_schema_version = payload.get("target_schema_version")
    if not isinstance(target_schema_version, int) or isinstance(target_schema_version, bool):
        errors.append("target_schema_version must be an integer")
    elif (
        isinstance(source_schema_version, int)
        and not isinstance(source_schema_version, bool)
        and target_schema_version <= source_schema_version
    ):
        errors.append("target_schema_version must be greater than source_schema_version")


def validate_source_template(repo_root: Path, payload: dict[str, Any], errors: list[str]) -> None:
    template_path = validate_existing_repo_path(repo_root, "source_template", payload.get("source_template"), errors)
    if template_path is None:
        return
    try:
        template = load_json_object(template_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"source_template is invalid JSON: {error}")
        return
    if template.get("contract_id") != payload.get("source_contract_id"):
        errors.append("source_template contract_id must match source_contract_id")
    if template.get("schema_version") != payload.get("source_schema_version"):
        errors.append("source_template schema_version must match source_schema_version")


def validate_target_template(repo_root: Path, payload: dict[str, Any], errors: list[str]) -> None:
    template_path = validate_existing_repo_path(repo_root, "target_template", payload.get("target_template"), errors)
    if template_path is None:
        return
    try:
        template = load_json_object(template_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"target_template is invalid JSON: {error}")
        return
    if template.get("contract_id") != payload.get("target_contract_id"):
        errors.append("target_template contract_id must match target_contract_id")
    if template.get("schema_version") != payload.get("target_schema_version"):
        errors.append("target_template schema_version must match target_schema_version")
    for required in payload.get("required_new_sections", []):
        if isinstance(required, str) and required not in template:
            errors.append(f"target_template must include required new section `{required}`")


def validate_preserved_sections(payload: dict[str, Any], errors: list[str]) -> None:
    sections = set(string_list(payload.get("required_preserved_sections")))
    if payload.get("required_preserved_sections") is not None and not isinstance(payload.get("required_preserved_sections"), list):
        errors.append("required_preserved_sections must be a list")
    missing = sorted(REQUIRED_PRESERVED_SECTIONS - sections)
    if missing:
        errors.append(f"required_preserved_sections missing: {', '.join(missing)}")


def validate_new_sections(payload: dict[str, Any], errors: list[str]) -> None:
    sections = set(string_list(payload.get("required_new_sections")))
    if payload.get("required_new_sections") is not None and not isinstance(payload.get("required_new_sections"), list):
        errors.append("required_new_sections must be a list")
    if "migration_history" not in sections:
        errors.append("required_new_sections must include migration_history")


def validate_privacy_invariants(payload: dict[str, Any], errors: list[str]) -> None:
    invariants = payload.get("privacy_invariants")
    if not isinstance(invariants, dict):
        errors.append("privacy_invariants must be an object")
        return
    for key, expected in REQUIRED_PRIVACY_INVARIANTS.items():
        if invariants.get(key) is not expected:
            errors.append(f"privacy_invariants.{key} must be {json.dumps(expected)}")


def validate_field_mappings(payload: dict[str, Any], errors: list[str]) -> None:
    mappings = payload.get("field_mappings")
    if not isinstance(mappings, list) or not mappings:
        errors.append("field_mappings must be a non-empty list")
        return
    seen_targets: set[str] = set()
    has_settings_preserve = False
    has_data_controls_preserve = False
    has_meta_preserve = False
    has_contract_set = False
    has_schema_set = False
    has_migration_history = False
    for index, item in enumerate(mappings):
        label = f"field_mappings[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        for field in ("source", "target", "mode"):
            value = item.get(field)
            if not is_nonempty_string(value):
                errors.append(f"{label}.{field} must be non-empty")
            elif has_placeholder(value):
                errors.append(f"{label}.{field} must not contain TODO or placeholder markers")
        mode = item.get("mode")
        if mode not in MAPPING_MODES:
            errors.append(f"{label}.mode must be one of {', '.join(sorted(MAPPING_MODES))}")
        target = item.get("target")
        if is_nonempty_string(target):
            if str(target) in seen_targets:
                errors.append(f"{label}.target duplicates another mapping: {target}")
            seen_targets.add(str(target))
        source = item.get("source")
        if source == "settings" and target == "settings" and mode == "preserve":
            has_settings_preserve = True
        if source == "data_controls" and target == "data_controls" and mode == "preserve":
            has_data_controls_preserve = True
        if source == "meta_progress" and target == "meta_progress" and mode == "preserve":
            has_meta_preserve = True
        if source == "contract_id" and target == "contract_id" and mode == "set":
            has_contract_set = item.get("target_value") == payload.get("target_contract_id")
        if source == "schema_version" and target == "schema_version" and mode == "set":
            has_schema_set = item.get("target_value") == payload.get("target_schema_version")
        if is_nonempty_string(target) and str(target).startswith("migration_history"):
            has_migration_history = True
        if mode == "set" and "target_value" not in item:
            errors.append(f"{label}.target_value is required for set mode")
    if not has_settings_preserve:
        errors.append("field_mappings must preserve settings")
    if not has_data_controls_preserve:
        errors.append("field_mappings must preserve data_controls")
    if not has_meta_preserve:
        errors.append("field_mappings must preserve meta_progress")
    if not has_contract_set:
        errors.append("field_mappings must set target contract_id")
    if not has_schema_set:
        errors.append("field_mappings must set target schema_version")
    if not has_migration_history:
        errors.append("field_mappings must write migration_history")


def validate_failure_policy(payload: dict[str, Any], errors: list[str]) -> None:
    policy = payload.get("failure_policy")
    if not isinstance(policy, dict):
        errors.append("failure_policy must be an object")
        return
    for key, expected in REQUIRED_FAILURE_POLICIES.items():
        if policy.get(key) != expected:
            errors.append(f"failure_policy.{key} must be {expected}")


def validate_validation_requirements(payload: dict[str, Any], errors: list[str]) -> None:
    requirements = string_list(payload.get("validation_requirements"))
    if payload.get("validation_requirements") is not None and not isinstance(payload.get("validation_requirements"), list):
        errors.append("validation_requirements must be a list")
    if has_placeholder(payload.get("validation_requirements")):
        errors.append("validation_requirements must not contain TODO or placeholder markers")
    joined = "\n".join(requirements).lower()
    for topic in REQUIRED_VALIDATION_TOPICS:
        if topic not in joined:
            errors.append(f"validation_requirements must mention `{topic}`")


def validate_blockers_and_next_actions(payload: dict[str, Any], errors: list[str], warnings: list[str]) -> None:
    blockers = string_list(payload.get("blockers"))
    next_actions = string_list(payload.get("next_actions"))
    if payload.get("blockers") is not None and not isinstance(payload.get("blockers"), list):
        errors.append("blockers must be a list")
    if payload.get("next_actions") is not None and not isinstance(payload.get("next_actions"), list):
        errors.append("next_actions must be a list")
    if has_placeholder(payload.get("blockers")):
        errors.append("blockers must not contain TODO or placeholder markers")
    if has_placeholder(payload.get("next_actions")):
        errors.append("next_actions must not contain TODO or placeholder markers")
    if payload.get("status") == "implemented" and blockers:
        errors.append("implemented migration plan cannot list blockers")
    if payload.get("status") != "implemented" and not blockers:
        errors.append("non-implemented migration plan must list blockers")
    if payload.get("status") != "implemented" and not next_actions:
        warnings.append("non-implemented migration plan should list next_actions")


def build_report(plan_path: Path, repo_root: Path) -> dict[str, Any]:
    payload = load_json_object(plan_path)
    errors: list[str] = []
    warnings: list[str] = []
    validate_metadata(payload, errors)
    validate_source_template(repo_root, payload, errors)
    validate_target_template(repo_root, payload, errors)
    validate_preserved_sections(payload, errors)
    validate_new_sections(payload, errors)
    validate_privacy_invariants(payload, errors)
    validate_field_mappings(payload, errors)
    validate_failure_policy(payload, errors)
    validate_validation_requirements(payload, errors)
    validate_blockers_and_next_actions(payload, errors, warnings)

    blockers = string_list(payload.get("blockers"))
    if errors:
        decision = "save_migration_plan_invalid"
    elif payload.get("status") == "implemented" and not blockers:
        decision = "save_migration_plan_ready"
    else:
        decision = "save_migration_plan_planned"

    return {
        "report_version": 1,
        "source": str(plan_path),
        "repo_root": str(repo_root),
        "migration_id": payload.get("migration_id"),
        "source_contract_id": payload.get("source_contract_id"),
        "target_contract_id": payload.get("target_contract_id"),
        "status": payload.get("status"),
        "decision": decision,
        "preserved_section_count": len(string_list(payload.get("required_preserved_sections"))),
        "new_section_count": len(string_list(payload.get("required_new_sections"))),
        "field_mapping_count": len(payload.get("field_mappings")) if isinstance(payload.get("field_mappings"), list) else 0,
        "blocker_count": len(blockers),
        "errors": errors,
        "warnings": warnings,
        "blockers": blockers,
        "limitations": [
            "This validator checks migration plan evidence only; it does not migrate save files.",
            "A planned migration is not a Runtime implementation and must not be treated as release-ready.",
            "Target save contract validation does not prove Runtime can accept migrated saves.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Save Migration Plan Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Migration: `{report['migration_id']}`",
        f"- Source contract: `{report['source_contract_id']}`",
        f"- Target contract: `{report['target_contract_id']}`",
        f"- Status: `{report['status']}`",
        f"- Decision: `{report['decision']}`",
        f"- Preserved sections: {report['preserved_section_count']}",
        f"- New sections: {report['new_section_count']}",
        f"- Field mappings: {report['field_mapping_count']}",
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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm save migration plans.")
    parser.add_argument("plan", type=Path, help="Save migration plan JSON")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON validation report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown validation summary")
    parser.add_argument(
        "--allow-planned",
        action="store_true",
        help="Exit 0 for structurally valid planned migrations",
    )
    args = parser.parse_args()

    report = build_report(args.plan, args.repo_root)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    if report["decision"] == "save_migration_plan_ready":
        return 0
    if args.allow_planned and report["decision"] == "save_migration_plan_planned":
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
