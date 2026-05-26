#!/usr/bin/env python3
"""Validate Soft Candy Storm save-state contract JSON.

This gate checks local save data shape for docs/18 and local data controls for
docs/16. It is intentionally dependency-free and does not execute Runtime code.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


UNLOCK_CATEGORIES = [
    "characters",
    "weapons",
    "passives",
    "maps",
    "evolutions",
    "chapters",
    "events",
    "cosmetics",
]

CODEX_CATEGORIES = [
    "characters",
    "weapons",
    "passives",
    "enemies",
    "bosses",
    "maps",
    "evolutions",
    "events",
]

FORBIDDEN_KEYS = {
    "email",
    "phone",
    "ip",
    "ip_address",
    "file_path",
    "absolute_path",
    "free_text_input",
    "raw_action_stream",
    "raw_replay_input",
}

ISO_UTC_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$")

REQUIRED_CHAPTERS = {
    "frosting-grassland": ("frosting-grassland", "runaway-sugar-mixer"),
    "soda-creek": ("soda-creek", "soda-fountain-dragon"),
    "cotton-cloud-pasture": ("cotton-cloud-pasture", "giant-cotton-clump"),
    "caramel-workshop": ("caramel-workshop", "caramel-furnace"),
    "jelly-platform": ("jelly-platform", "giant-gummy-bear-king"),
    "cracked-star-jar": ("cracked-star-jar", "cracked-star-jar-core"),
}

CONTRACT_SCHEMA_VERSIONS = {
    "save-state-v0": 1,
    "save-state-v1": 2,
}

BASE_UI_PANELS = {"overview", "chapters", "codex", "privacy"}
MIGRATION_STATUSES = {"completed", "dry-run", "planned-template"}


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def require_object(value: Any, label: str, errors: list[str]) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    errors.append(f"{label} must be an object")
    return {}


def require_bool(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, bool):
        errors.append(f"{label} must be a boolean")


def require_nonnegative_int(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        errors.append(f"{label} must be a non-negative integer")


def require_nonnegative_number(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
        errors.append(f"{label} must be a non-negative number")


def require_id(value: Any, label: str, errors: list[str]) -> None:
    if not is_nonempty_string(value):
        errors.append(f"{label} must be a non-empty string")
    elif not ID_PATTERN.match(value):
        errors.append(f"{label} must use lowercase kebab-case id format")


def require_string_list(value: Any, label: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list):
        errors.append(f"{label} must be a list")
        return []
    items: list[str] = []
    for index, item in enumerate(value):
        item_label = f"{label}[{index}]"
        if not is_nonempty_string(item):
            errors.append(f"{item_label} must be a non-empty string")
        else:
            items.append(item)
            require_id(item, item_label, errors)
    if len(items) != len(set(items)):
        errors.append(f"{label} must not contain duplicate ids")
    return items


def find_forbidden_keys(value: Any, prefix: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            key_path = f"{prefix}.{key}" if prefix else str(key)
            if str(key).lower() in FORBIDDEN_KEYS:
                found.append(key_path)
            found.extend(find_forbidden_keys(item, key_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(find_forbidden_keys(item, f"{prefix}[{index}]"))
    return found


def validate_metadata(payload: dict[str, Any], errors: list[str]) -> None:
    contract_id = payload.get("contract_id")
    schema_version = payload.get("schema_version")
    if contract_id not in CONTRACT_SCHEMA_VERSIONS:
        errors.append("contract_id must be one of `save-state-v0`, `save-state-v1`")
    elif schema_version != CONTRACT_SCHEMA_VERSIONS[contract_id]:
        errors.append(f"schema_version must be {CONTRACT_SCHEMA_VERSIONS[contract_id]} for {contract_id}")
    for field in ("save_id", "profile_id", "game_version", "ruleset_version"):
        require_id(payload.get(field), field, errors)
    for field in ("created_at", "updated_at"):
        value = payload.get(field)
        if not is_nonempty_string(value) or not ISO_UTC_PATTERN.match(str(value)):
            errors.append(f"{field} must use UTC format YYYY-MM-DDTHH:MM:SSZ")
    content_pack_ids = require_string_list(payload.get("content_pack_ids"), "content_pack_ids", errors)
    if not content_pack_ids:
        errors.append("content_pack_ids must not be empty")


def validate_settings(payload: dict[str, Any], errors: list[str]) -> None:
    settings = require_object(payload.get("settings"), "settings", errors)
    for field in ("telemetry_upload_enabled", "raw_replay_upload_enabled", "crash_report_upload_enabled"):
        require_bool(settings.get(field), f"settings.{field}", errors)
        if settings.get(field) is not False:
            errors.append(f"settings.{field} must default to false in the save template")


def validate_data_controls(payload: dict[str, Any], errors: list[str]) -> None:
    controls = require_object(payload.get("data_controls"), "data_controls", errors)
    required_true = [
        "local_only_by_default",
        "upload_requires_opt_in",
        "delete_save_available",
        "export_save_available",
    ]
    for field in required_true:
        require_bool(controls.get(field), f"data_controls.{field}", errors)
        if controls.get(field) is not True:
            errors.append(f"data_controls.{field} must be true")
    if controls.get("export_format") != "json":
        errors.append("data_controls.export_format must be `json`")
    retention_days = controls.get("retention_days")
    require_nonnegative_int(retention_days, "data_controls.retention_days", errors)
    if isinstance(retention_days, int) and retention_days <= 0:
        errors.append("data_controls.retention_days must be greater than 0")


def validate_resources(meta: dict[str, Any], errors: list[str]) -> None:
    resources = require_object(meta.get("resources"), "meta_progress.resources", errors)
    for field in ("candy_crystal_shards", "star_shards", "storm_grains"):
        require_nonnegative_int(resources.get(field), f"meta_progress.resources.{field}", errors)


def validate_unlocks(meta: dict[str, Any], errors: list[str]) -> dict[str, list[str]]:
    unlocks = require_object(meta.get("unlocks"), "meta_progress.unlocks", errors)
    result: dict[str, list[str]] = {}
    for category in UNLOCK_CATEGORIES:
        result[category] = require_string_list(unlocks.get(category), f"meta_progress.unlocks.{category}", errors)
    return result


def validate_codex_entry(value: Any, label: str, errors: list[str]) -> None:
    entry = require_object(value, label, errors)
    require_bool(entry.get("discovered"), f"{label}.discovered", errors)
    first_seen_run = entry.get("first_seen_run")
    if first_seen_run is not None and not is_nonempty_string(first_seen_run):
        errors.append(f"{label}.first_seen_run must be null or a non-empty string")
    for field in ("seen_count", "defeated_count", "used_count"):
        require_nonnegative_int(entry.get(field), f"{label}.{field}", errors)


def validate_codex(meta: dict[str, Any], errors: list[str]) -> int:
    codex = require_object(meta.get("codex"), "meta_progress.codex", errors)
    entry_count = 0
    for category in CODEX_CATEGORIES:
        bucket = require_object(codex.get(category), f"meta_progress.codex.{category}", errors)
        for item_id, entry in bucket.items():
            require_id(item_id, f"meta_progress.codex.{category} key", errors)
            validate_codex_entry(entry, f"meta_progress.codex.{category}.{item_id}", errors)
            entry_count += 1
    return entry_count


def validate_chapters(
    meta: dict[str, Any],
    unlocks: dict[str, list[str]],
    errors: list[str],
) -> int:
    chapters = require_object(meta.get("chapters"), "meta_progress.chapters", errors)
    unlocked_chapters = set(unlocks.get("chapters", []))

    for required_id, (expected_map_id, expected_boss_id) in REQUIRED_CHAPTERS.items():
        chapter = chapters.get(required_id)
        if not isinstance(chapter, dict):
            errors.append(f"meta_progress.chapters must include required chapter `{required_id}`")
            continue
        if chapter.get("map_id") != expected_map_id:
            errors.append(
                f"meta_progress.chapters.{required_id}.map_id must be `{expected_map_id}`"
            )
        if chapter.get("boss_id") != expected_boss_id:
            errors.append(
                f"meta_progress.chapters.{required_id}.boss_id must be `{expected_boss_id}`"
            )

    for unlocked_id in unlocked_chapters:
        if unlocked_id not in chapters:
            errors.append(
                f"meta_progress.unlocks.chapters includes `{unlocked_id}` without chapter progress"
            )

    for chapter_key, chapter in chapters.items():
        require_id(chapter_key, "meta_progress.chapters key", errors)
        chapter_obj = require_object(chapter, f"meta_progress.chapters.{chapter_key}", errors)
        for field in ("chapter_id", "map_id", "boss_id"):
            require_id(chapter_obj.get(field), f"meta_progress.chapters.{chapter_key}.{field}", errors)
        if chapter_obj.get("chapter_id") != chapter_key:
            errors.append(f"meta_progress.chapters.{chapter_key}.chapter_id must match its object key")
        require_bool(chapter_obj.get("unlocked"), f"meta_progress.chapters.{chapter_key}.unlocked", errors)
        require_string_list(
            chapter_obj.get("completed_goals"),
            f"meta_progress.chapters.{chapter_key}.completed_goals",
            errors,
        )
        if chapter_obj.get("unlocked") is True and chapter_key not in unlocked_chapters:
            errors.append(
                f"meta_progress.chapters.{chapter_key}.unlocked requires unlocks.chapters entry"
            )
        if chapter_key in unlocked_chapters and chapter_obj.get("unlocked") is not True:
            errors.append(
                f"meta_progress.unlocks.chapters `{chapter_key}` requires chapter.unlocked true"
            )
    return len(chapters)


def validate_meta_progress(payload: dict[str, Any], errors: list[str]) -> tuple[int, int]:
    meta = require_object(payload.get("meta_progress"), "meta_progress", errors)
    validate_resources(meta, errors)
    unlocks = validate_unlocks(meta, errors)
    codex_count = validate_codex(meta, errors)
    chapter_count = validate_chapters(meta, unlocks, errors)
    require_nonnegative_int(meta.get("completed_runs"), "meta_progress.completed_runs", errors)
    require_nonnegative_number(meta.get("best_survival_seconds"), "meta_progress.best_survival_seconds", errors)
    return codex_count, chapter_count


def validate_migration_history(payload: dict[str, Any], errors: list[str]) -> int:
    history = payload.get("migration_history")
    if not isinstance(history, list) or not history:
        errors.append("migration_history must be a non-empty list for save-state-v1")
        return 0
    for index, item in enumerate(history):
        label = f"migration_history[{index}]"
        entry = require_object(item, label, errors)
        require_id(entry.get("migration_id"), f"{label}.migration_id", errors)
        require_id(entry.get("source_save_id"), f"{label}.source_save_id", errors)
        if entry.get("source_contract_id") != "save-state-v0":
            errors.append(f"{label}.source_contract_id must be `save-state-v0`")
        if entry.get("source_schema_version") != 1:
            errors.append(f"{label}.source_schema_version must be 1")
        if entry.get("target_contract_id") != "save-state-v1":
            errors.append(f"{label}.target_contract_id must be `save-state-v1`")
        if entry.get("target_schema_version") != 2:
            errors.append(f"{label}.target_schema_version must be 2")
        value = entry.get("migrated_at")
        if not is_nonempty_string(value) or not ISO_UTC_PATTERN.match(str(value)):
            errors.append(f"{label}.migrated_at must use UTC format YYYY-MM-DDTHH:MM:SSZ")
        if entry.get("status") not in MIGRATION_STATUSES:
            errors.append(f"{label}.status must be one of {', '.join(sorted(MIGRATION_STATUSES))}")
    return len(history)


def validate_base_ui_state(payload: dict[str, Any], errors: list[str]) -> bool:
    state = require_object(payload.get("base_ui_state"), "base_ui_state", errors)
    selected_panel = state.get("selected_panel")
    if selected_panel not in BASE_UI_PANELS:
        errors.append(f"base_ui_state.selected_panel must be one of {', '.join(sorted(BASE_UI_PANELS))}")
    for field in ("last_selected_character_id", "last_selected_map_id", "last_selected_chapter_id"):
        require_id(state.get(field), f"base_ui_state.{field}", errors)

    codex_view = require_object(state.get("codex_view"), "base_ui_state.codex_view", errors)
    if codex_view.get("selected_category") not in CODEX_CATEGORIES:
        errors.append("base_ui_state.codex_view.selected_category must be a known codex category")
    require_bool(codex_view.get("discovered_only"), "base_ui_state.codex_view.discovered_only", errors)

    privacy_view = require_object(state.get("privacy_view"), "base_ui_state.privacy_view", errors)
    require_id(privacy_view.get("last_notice_version"), "base_ui_state.privacy_view.last_notice_version", errors)
    require_bool(privacy_view.get("pending_privacy_review"), "base_ui_state.privacy_view.pending_privacy_review", errors)
    return isinstance(payload.get("base_ui_state"), dict)


def validate_version_specific_sections(payload: dict[str, Any], errors: list[str]) -> tuple[int, bool]:
    contract_id = payload.get("contract_id")
    if contract_id == "save-state-v0":
        for field in ("migration_history", "base_ui_state"):
            if field in payload:
                errors.append(f"{field} is reserved for save-state-v1 and must not appear in save-state-v0")
        return 0, False
    if contract_id == "save-state-v1":
        history_count = validate_migration_history(payload, errors)
        has_base_ui_state = validate_base_ui_state(payload, errors)
        return history_count, has_base_ui_state
    return 0, False


def build_report(save_path: Path) -> dict[str, Any]:
    payload = load_json_object(save_path)
    errors: list[str] = []
    warnings: list[str] = []
    validate_metadata(payload, errors)
    validate_settings(payload, errors)
    validate_data_controls(payload, errors)
    codex_count, chapter_count = validate_meta_progress(payload, errors)
    migration_history_count, has_base_ui_state = validate_version_specific_sections(payload, errors)

    forbidden_keys = find_forbidden_keys(payload)
    for key_path in forbidden_keys:
        errors.append(f"forbidden personal/local data key present: {key_path}")
    if chapter_count == 0:
        warnings.append("meta_progress.chapters is empty; demo flow should include at least one chapter")
    if codex_count == 0:
        warnings.append("meta_progress.codex has no discovered or seed entries")

    return {
        "report_version": 1,
        "source": str(save_path),
        "contract_id": payload.get("contract_id"),
        "schema_version": payload.get("schema_version"),
        "decision": "save_state_contract_valid" if not errors else "save_state_contract_invalid",
        "codex_entry_count": codex_count,
        "chapter_count": chapter_count,
        "migration_history_count": migration_history_count,
        "base_ui_state_present": has_base_ui_state,
        "errors": errors,
        "warnings": warnings,
        "limitations": [
            "This validator checks save-state JSON shape and local data controls only.",
            "It does not prove Runtime can read, write, delete, or export saves.",
            "It does not replace platform privacy review or manual UI verification.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Save State Contract Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Contract: `{report['contract_id']}`",
        f"- Schema version: `{report['schema_version']}`",
        f"- Decision: `{report['decision']}`",
        f"- Codex entries: {report['codex_entry_count']}",
        f"- Chapters: {report['chapter_count']}",
        f"- Migration history entries: {report['migration_history_count']}",
        f"- Base UI state: {report['base_ui_state_present']}",
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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm save-state contract JSON.")
    parser.add_argument(
        "save",
        type=Path,
        nargs="?",
        default=Path("harness/save_contract/save_state_v0_template.json"),
        help="Save-state JSON to validate",
    )
    parser.add_argument("--report", type=Path, default=None, help="Write JSON validation report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown validation summary")
    args = parser.parse_args()

    report = build_report(args.save)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "save_state_contract_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
