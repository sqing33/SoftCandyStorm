#!/usr/bin/env python3
"""Validate content packs against the docs/13 JSON Schema contract.

This dependency-free validator supports the JSON Schema subset used by
content/schemas/*.schema.json. It is not a replacement for the Rust GameCore
loader or Harness simulation gates; it provides a portable first pass for
schema shape, required fields, enums, id patterns, simple numeric bounds, and
cross-file semantic references that can be checked without launching Rust.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any


DEFAULT_SCHEMA_MANIFEST = Path("content/schemas/manifest.json")
CONTENT_CATEGORIES = [
    "characters",
    "weapons",
    "passives",
    "evolutions",
    "enemies",
    "bosses",
    "maps",
    "waves",
    "events",
]
ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def content_files(content_dir: Path, category: str) -> list[Path]:
    category_dir = content_dir / category
    return sorted(path for path in category_dir.glob("*.json") if path.is_file()) if category_dir.exists() else []


def type_matches(value: Any, expected_type: str) -> bool:
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    if expected_type == "boolean":
        return isinstance(value, bool)
    return True


def validate_value(schema: dict[str, Any], value: Any, label: str) -> list[str]:
    errors: list[str] = []
    expected_type = schema.get("type")
    if isinstance(expected_type, str):
        if not type_matches(value, expected_type):
            return [f"{label}: expected {expected_type}, got {type(value).__name__}"]
    elif isinstance(expected_type, list):
        if not any(type_matches(value, item) for item in expected_type if isinstance(item, str)):
            return [f"{label}: expected one of {expected_type}, got {type(value).__name__}"]

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{label}: value `{value}` is not in enum {schema['enum']}")

    if isinstance(value, str):
        min_length = schema.get("minLength")
        if isinstance(min_length, int) and len(value) < min_length:
            errors.append(f"{label}: string length {len(value)} is below {min_length}")
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and not re.match(pattern, value):
            errors.append(f"{label}: value `{value}` does not match pattern `{pattern}`")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        minimum = schema.get("minimum")
        if isinstance(minimum, (int, float)) and value < minimum:
            errors.append(f"{label}: value {value} is below minimum {minimum}")
        maximum = schema.get("maximum")
        if isinstance(maximum, (int, float)) and value > maximum:
            errors.append(f"{label}: value {value} is above maximum {maximum}")
        exclusive_minimum = schema.get("exclusiveMinimum")
        if isinstance(exclusive_minimum, (int, float)) and value <= exclusive_minimum:
            errors.append(f"{label}: value {value} must be greater than {exclusive_minimum}")

    if isinstance(value, list):
        min_items = schema.get("minItems")
        if isinstance(min_items, int) and len(value) < min_items:
            errors.append(f"{label}: array length {len(value)} is below {min_items}")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                errors.extend(validate_value(item_schema, item, f"{label}[{index}]"))

    if isinstance(value, dict):
        required = schema.get("required", [])
        if isinstance(required, list):
            for field in required:
                if isinstance(field, str) and field not in value:
                    errors.append(f"{label}: missing required `{field}`")
        properties = schema.get("properties", {})
        if isinstance(properties, dict):
            for field, field_schema in properties.items():
                if field in value and isinstance(field_schema, dict):
                    errors.extend(validate_value(field_schema, value[field], f"{label}.{field}"))

    return errors


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def semantic_label(content_dir: Path, paths_by_category: dict[str, dict[str, str]], category: str, item_id: str) -> str:
    relative_path = paths_by_category.get(category, {}).get(item_id, f"{category}/{item_id}.json")
    return f"{content_dir}/{relative_path}"


def require_reference(
    errors: list[str],
    label: str,
    field: str,
    referenced_id: Any,
    target_category: str,
    items_by_category: dict[str, dict[str, dict[str, Any]]],
) -> dict[str, Any] | None:
    if not is_nonempty_string(referenced_id):
        return None
    target = items_by_category.get(target_category, {}).get(str(referenced_id))
    if target is None:
        errors.append(f"{label}: `{field}` references missing {target_category} id `{referenced_id}`")
    return target


def validate_character_semantics(
    content_dir: Path,
    errors: list[str],
    items_by_category: dict[str, dict[str, dict[str, Any]]],
    paths_by_category: dict[str, dict[str, str]],
) -> int:
    checks = 0
    for item_id, character in items_by_category.get("characters", {}).items():
        label = semantic_label(content_dir, paths_by_category, "characters", item_id)
        loadout = character.get("initial_loadout")
        if not isinstance(loadout, dict):
            continue
        weapons = loadout.get("weapons")
        if isinstance(weapons, list):
            checks += len(weapons)
            for index, weapon_id in enumerate(weapons):
                require_reference(errors, label, f"initial_loadout.weapons[{index}]", weapon_id, "weapons", items_by_category)
        passives = loadout.get("passives")
        if isinstance(passives, list):
            checks += len(passives)
            for index, passive_id in enumerate(passives):
                require_reference(errors, label, f"initial_loadout.passives[{index}]", passive_id, "passives", items_by_category)
    return checks


def validate_evolution_semantics(
    content_dir: Path,
    errors: list[str],
    items_by_category: dict[str, dict[str, dict[str, Any]]],
    paths_by_category: dict[str, dict[str, str]],
) -> int:
    checks = 0
    for item_id, evolution in items_by_category.get("evolutions", {}).items():
        label = semantic_label(content_dir, paths_by_category, "evolutions", item_id)
        requirements = evolution.get("requirements")
        if not isinstance(requirements, dict):
            continue
        weapon_req = requirements.get("weapon")
        if isinstance(weapon_req, dict):
            weapon_id = weapon_req.get("id")
            weapon = require_reference(errors, label, "requirements.weapon.id", weapon_id, "weapons", items_by_category)
            checks += 1
            replaces_weapon = evolution.get("replaces_weapon")
            if is_nonempty_string(weapon_id) and is_nonempty_string(replaces_weapon) and weapon_id != replaces_weapon:
                errors.append(
                    f"{label}: `replaces_weapon` `{replaces_weapon}` must match requirements.weapon.id `{weapon_id}`"
                )
            min_level = weapon_req.get("min_level")
            if weapon is not None and isinstance(weapon.get("scaling"), dict) and isinstance(min_level, int):
                max_level = weapon["scaling"].get("max_level")
                if isinstance(max_level, int) and min_level > max_level:
                    errors.append(
                        f"{label}: requirements.weapon.min_level {min_level} exceeds weapon `{weapon_id}` max_level {max_level}"
                    )
        passive_req = requirements.get("passive")
        if isinstance(passive_req, dict):
            passive_id = passive_req.get("id")
            passive = require_reference(errors, label, "requirements.passive.id", passive_id, "passives", items_by_category)
            checks += 1
            min_level = passive_req.get("min_level")
            if passive is not None and isinstance(min_level, int):
                max_level = passive.get("max_level")
                if isinstance(max_level, int) and min_level > max_level:
                    errors.append(
                        f"{label}: requirements.passive.min_level {min_level} exceeds passive `{passive_id}` max_level {max_level}"
                    )
    return checks


def validate_wave_semantics(
    content_dir: Path,
    errors: list[str],
    items_by_category: dict[str, dict[str, dict[str, Any]]],
    paths_by_category: dict[str, dict[str, str]],
) -> int:
    checks = 0
    for item_id, wave in items_by_category.get("waves", {}).items():
        label = semantic_label(content_dir, paths_by_category, "waves", item_id)
        map_id = wave.get("map_id")
        require_reference(errors, label, "map_id", map_id, "maps", items_by_category)
        checks += 1
        duration = wave.get("duration_seconds")
        previous_end: float | None = None
        segments = wave.get("segments")
        if isinstance(segments, list):
            for index, segment in enumerate(segments):
                if not isinstance(segment, dict):
                    continue
                segment_label = f"{label}.segments[{index}]"
                start = segment.get("start_second")
                end = segment.get("end_second")
                if is_number(start) and is_number(end):
                    checks += 1
                    if start >= end:
                        errors.append(f"{segment_label}: start_second {start} must be before end_second {end}")
                    if is_number(duration) and end > duration:
                        errors.append(f"{segment_label}: end_second {end} exceeds duration_seconds {duration}")
                    if previous_end is not None and start < previous_end:
                        errors.append(f"{segment_label}: start_second {start} overlaps previous segment ending at {previous_end}")
                    previous_end = end
                enemy_pool = segment.get("enemy_pool")
                if isinstance(enemy_pool, list):
                    for pool_index, pool_item in enumerate(enemy_pool):
                        if not isinstance(pool_item, dict):
                            continue
                        checks += 1
                        require_reference(
                            errors,
                            label,
                            f"segments[{index}].enemy_pool[{pool_index}].enemy_id",
                            pool_item.get("enemy_id"),
                            "enemies",
                            items_by_category,
                        )
        boss_events = wave.get("boss_events")
        if isinstance(boss_events, list):
            for index, boss_event in enumerate(boss_events):
                if not isinstance(boss_event, dict):
                    continue
                checks += 1
                require_reference(
                    errors,
                    label,
                    f"boss_events[{index}].boss_id",
                    boss_event.get("boss_id"),
                    "bosses",
                    items_by_category,
                )
                time_second = boss_event.get("time_second")
                if is_number(time_second) and is_number(duration) and time_second > duration:
                    errors.append(f"{label}.boss_events[{index}]: time_second {time_second} exceeds duration_seconds {duration}")
    return checks


def validate_map_semantics(
    content_dir: Path,
    errors: list[str],
    items_by_category: dict[str, dict[str, dict[str, Any]]],
    paths_by_category: dict[str, dict[str, str]],
) -> int:
    checks = 0
    for item_id, map_item in items_by_category.get("maps", {}).items():
        label = semantic_label(content_dir, paths_by_category, "maps", item_id)
        spawn_rules = map_item.get("spawn_rules")
        if isinstance(spawn_rules, dict):
            min_distance = spawn_rules.get("min_distance")
            max_distance = spawn_rules.get("max_distance")
            if is_number(min_distance) and is_number(max_distance):
                checks += 1
                if min_distance > max_distance:
                    errors.append(f"{label}: spawn_rules.min_distance {min_distance} exceeds max_distance {max_distance}")
        size = map_item.get("size")
        if isinstance(size, dict) and is_number(size.get("width")) and is_number(size.get("height")):
            checks += 1
            if spawn_rules and is_number(spawn_rules.get("max_distance")):
                longest_spawn = spawn_rules["max_distance"]
                shortest_axis = min(size["width"], size["height"])
                if longest_spawn >= shortest_axis:
                    errors.append(
                        f"{label}: spawn_rules.max_distance {longest_spawn} should be smaller than shortest map axis {shortest_axis}"
                    )
    return checks


def validate_boss_semantics(
    content_dir: Path,
    errors: list[str],
    items_by_category: dict[str, dict[str, dict[str, Any]]],
    paths_by_category: dict[str, dict[str, str]],
) -> int:
    checks = 0
    for item_id, boss in items_by_category.get("bosses", {}).items():
        label = semantic_label(content_dir, paths_by_category, "bosses", item_id)
        phases = boss.get("phases")
        if not isinstance(phases, list):
            continue
        previous_threshold: float | None = None
        for index, phase in enumerate(phases):
            if not isinstance(phase, dict):
                continue
            threshold = phase.get("hp_threshold")
            if is_number(threshold):
                checks += 1
                if threshold > 1:
                    errors.append(f"{label}.phases[{index}]: hp_threshold {threshold} exceeds 1.0")
                if previous_threshold is not None and threshold >= previous_threshold:
                    errors.append(
                        f"{label}.phases[{index}]: hp_threshold {threshold} must be lower than previous threshold {previous_threshold}"
                    )
                previous_threshold = threshold
        if phases and isinstance(phases[0], dict) and phases[0].get("hp_threshold") != 1.0:
            errors.append(f"{label}: first boss phase should start at hp_threshold 1.0")
    return checks


def validate_event_semantics(
    content_dir: Path,
    errors: list[str],
    items_by_category: dict[str, dict[str, dict[str, Any]]],
    paths_by_category: dict[str, dict[str, str]],
) -> int:
    checks = 0
    for item_id, event in items_by_category.get("events", {}).items():
        label = semantic_label(content_dir, paths_by_category, "events", item_id)
        trigger = event.get("trigger")
        if isinstance(trigger, dict):
            start = trigger.get("start_second")
            end = trigger.get("end_second")
            if is_number(start) and is_number(end):
                checks += 1
                if start >= end:
                    errors.append(f"{label}: trigger.start_second {start} must be before end_second {end}")
            chance = trigger.get("chance")
            if is_number(chance):
                checks += 1
                if chance > 1:
                    errors.append(f"{label}: trigger.chance {chance} exceeds 1.0")
        effects = event.get("effects")
        if isinstance(effects, list):
            for index, effect in enumerate(effects):
                if not isinstance(effect, dict):
                    continue
                duration = effect.get("duration_seconds")
                if duration is not None:
                    checks += 1
                    if not is_number(duration) or duration <= 0:
                        errors.append(f"{label}.effects[{index}]: duration_seconds must be greater than 0")
                if effect.get("type") == "spawn_hazard":
                    placement = effect.get("placement")
                    if placement is not None:
                        checks += 1
                        if placement not in {"near_player", "player_forward_lane"}:
                            errors.append(
                                f"{label}.effects[{index}]: placement `{placement}` is not supported"
                            )
                    min_distance = effect.get("min_distance")
                    max_distance = effect.get("max_distance")
                    if min_distance is not None:
                        checks += 1
                        if not is_number(min_distance) or min_distance < 0:
                            errors.append(f"{label}.effects[{index}]: min_distance must be non-negative")
                    if max_distance is not None:
                        checks += 1
                        if not is_number(max_distance) or max_distance <= 0:
                            errors.append(f"{label}.effects[{index}]: max_distance must be greater than 0")
                    if is_number(min_distance) and is_number(max_distance):
                        checks += 1
                        if max_distance < min_distance:
                            errors.append(
                                f"{label}.effects[{index}]: max_distance must be at least min_distance"
                            )
                    lane_width = effect.get("lane_width")
                    if lane_width is not None:
                        checks += 1
                        if not is_number(lane_width) or lane_width < 0:
                            errors.append(f"{label}.effects[{index}]: lane_width must be non-negative")
    return checks


def validate_content_semantics(
    content_dir: Path,
    items_by_category: dict[str, dict[str, dict[str, Any]]],
    paths_by_category: dict[str, dict[str, str]],
) -> tuple[list[str], int]:
    errors: list[str] = []
    check_count = 0
    check_count += validate_character_semantics(content_dir, errors, items_by_category, paths_by_category)
    check_count += validate_evolution_semantics(content_dir, errors, items_by_category, paths_by_category)
    check_count += validate_wave_semantics(content_dir, errors, items_by_category, paths_by_category)
    check_count += validate_map_semantics(content_dir, errors, items_by_category, paths_by_category)
    check_count += validate_boss_semantics(content_dir, errors, items_by_category, paths_by_category)
    check_count += validate_event_semantics(content_dir, errors, items_by_category, paths_by_category)
    return errors, check_count


def validate_schema_shape(category: str, schema_path: Path, schema: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    label = f"schema `{category}`"
    if not is_nonempty_string(schema.get("$schema")):
        errors.append(f"{label}: missing `$schema`")
    if schema.get("type") != "object":
        errors.append(f"{label}: top-level type must be object")
    if not isinstance(schema.get("required"), list) or not schema["required"]:
        errors.append(f"{label}: required must be a non-empty list")
    if not isinstance(schema.get("properties"), dict) or not schema["properties"]:
        errors.append(f"{label}: properties must be a non-empty object")
    if schema.get("additionalProperties") is not True:
        warnings.append(f"{label}: additionalProperties should be true for forward-compatible content")
    if schema_path.name != f"{category}.schema.json":
        warnings.append(f"{label}: schema file name is `{schema_path.name}`, expected `{category}.schema.json`")
    return errors, warnings


def load_schema_manifest(schema_manifest: Path) -> tuple[dict[str, dict[str, Any]], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    schemas: dict[str, dict[str, Any]] = {}
    try:
        manifest = load_json_object(schema_manifest)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return schemas, [f"{schema_manifest}: invalid schema manifest: {error}"], warnings

    categories = manifest.get("categories")
    if not isinstance(categories, dict):
        return schemas, ["schema manifest categories must be an object"], warnings

    for category in CONTENT_CATEGORIES:
        schema_file = categories.get(category)
        if not is_nonempty_string(schema_file):
            errors.append(f"schema manifest missing category `{category}`")
            continue
        schema_path = schema_manifest.parent / str(schema_file)
        try:
            schema = load_json_object(schema_path)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            errors.append(f"{schema_path}: invalid schema JSON: {error}")
            continue
        schema_errors, schema_warnings = validate_schema_shape(category, schema_path, schema)
        errors.extend(schema_errors)
        warnings.extend(schema_warnings)
        schemas[category] = schema

    unknown_categories = sorted(set(categories) - set(CONTENT_CATEGORIES))
    for category in unknown_categories:
        warnings.append(f"schema manifest includes unknown category `{category}`")

    return schemas, errors, warnings


def validate_content_dir(content_dir: Path, schemas: dict[str, dict[str, Any]]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    category_counts: dict[str, int] = {}
    seen_ids: dict[str, str] = {}
    items_by_category: dict[str, dict[str, dict[str, Any]]] = {category: {} for category in CONTENT_CATEGORIES}
    paths_by_category: dict[str, dict[str, str]] = {category: {} for category in CONTENT_CATEGORIES}

    for category in CONTENT_CATEGORIES:
        schema = schemas.get(category)
        if schema is None:
            errors.append(f"{content_dir}: no schema loaded for category `{category}`")
            continue
        category_dir = content_dir / category
        if not category_dir.exists():
            errors.append(f"{content_dir}: missing category directory `{category}`")
            category_counts[category] = 0
            continue
        files = content_files(content_dir, category)
        category_counts[category] = len(files)
        if not files:
            errors.append(f"{content_dir}: category `{category}` contains no JSON files")
            continue
        for path in files:
            relative_path = path.relative_to(content_dir)
            try:
                payload = load_json_object(path)
            except (OSError, ValueError, json.JSONDecodeError) as error:
                errors.append(f"{content_dir}/{relative_path}: invalid JSON: {error}")
                continue
            label = f"{content_dir}/{relative_path}"
            errors.extend(validate_value(schema, payload, label))

            item_id = payload.get("id")
            if is_nonempty_string(item_id):
                if not ID_PATTERN.match(str(item_id)):
                    errors.append(f"{label}: id `{item_id}` is not kebab-case")
                if item_id != path.stem:
                    errors.append(f"{label}: id `{item_id}` must match file stem `{path.stem}`")
                qualified_id = f"{category}:{item_id}"
                if qualified_id in seen_ids:
                    errors.append(f"{label}: duplicate id also found in {seen_ids[qualified_id]}")
                else:
                    seen_ids[qualified_id] = str(relative_path)
                    items_by_category[category][str(item_id)] = payload
                    paths_by_category[category][str(item_id)] = str(relative_path)

    semantic_errors, semantic_check_count = validate_content_semantics(content_dir, items_by_category, paths_by_category)
    errors.extend(semantic_errors)

    return {
        "content_dir": str(content_dir),
        "decision": "content_schema_contract_valid" if not errors else "content_schema_contract_invalid",
        "category_counts": category_counts,
        "semantic_check_count": semantic_check_count,
        "errors": errors,
        "warnings": warnings,
    }


def build_report(schema_manifest: Path, content_dirs: list[Path]) -> dict[str, Any]:
    schemas, schema_errors, schema_warnings = load_schema_manifest(schema_manifest)
    content_reports = [validate_content_dir(content_dir, schemas) for content_dir in content_dirs] if not schema_errors else []
    errors = list(schema_errors)
    warnings = list(schema_warnings)
    for content_report in content_reports:
        errors.extend(content_report["errors"])
        warnings.extend(content_report["warnings"])

    return {
        "report_version": 1,
        "schema_manifest": str(schema_manifest),
        "decision": "content_schema_contract_valid" if not errors else "content_schema_contract_invalid",
        "schema_count": len(schemas),
        "expected_schema_count": len(CONTENT_CATEGORIES),
        "content_pack_count": len(content_reports),
        "semantic_check_count": sum(content_report["semantic_check_count"] for content_report in content_reports),
        "errors": errors,
        "warnings": warnings,
        "content_packs": content_reports,
        "limitations": [
            "This validator supports the JSON Schema subset used in content/schemas only.",
            "It checks structural contract, required fields, enums, id patterns, simple numeric bounds, cross-file references, and basic timing/range semantics.",
            "It does not run GameCore loading, static budget gates, Bot simulation, Replay regression, or human review.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Content Schema Contract Validation",
        "",
        f"- Schema manifest: `{report['schema_manifest']}`",
        f"- Decision: `{report['decision']}`",
        f"- Schemas: {report['schema_count']} / {report['expected_schema_count']}",
        f"- Content packs: {report['content_pack_count']}",
        f"- Semantic checks: {report['semantic_check_count']}",
        "",
        "## Content Packs",
        "",
        "| Content Dir | Decision | Items | Semantic Checks |",
        "|---|---|---:|---:|",
    ]
    for content_report in report["content_packs"]:
        total_items = sum(content_report["category_counts"].values())
        lines.append(
            f"| `{content_report['content_dir']}` | `{content_report['decision']}` | {total_items} | {content_report['semantic_check_count']} |"
        )

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
    parser = argparse.ArgumentParser(description="Validate content packs against the docs/13 schema contract.")
    parser.add_argument("content_dirs", type=Path, nargs="+", help="Content pack directories to validate")
    parser.add_argument("--schema-manifest", type=Path, default=DEFAULT_SCHEMA_MANIFEST)
    parser.add_argument("--report", type=Path, default=None, help="Write JSON validation report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown validation summary")
    args = parser.parse_args()

    report = build_report(args.schema_manifest, args.content_dirs)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "content_schema_contract_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
