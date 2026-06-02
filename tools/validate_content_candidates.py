#!/usr/bin/env python3
"""Validate partial generated content candidate patches.

This dependency-free validator is a stopgap for AI-generated candidate patches
that are not yet full GameCore content packs. It checks common schema fields,
passive/enemy-specific fields, candidate-only metadata, and duplicate ids
against an existing base content directory.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any


ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ALLOWED_RARITIES = {"common", "rare", "epic", "legendary", "boss", "debug"}
BASE_ID_CATEGORIES = ("weapons", "passives", "evolutions", "enemies", "waves", "maps", "bosses")
SUPPORTED_CONTENT_CATEGORIES = ("weapons", "passives", "evolutions", "enemies", "waves", "maps")
ALLOWED_WEAPON_TYPES = {"projectile", "orbit", "burst", "zone", "summon", "beam", "special"}
ALLOWED_TARGETING_MODES = {
    "nearest_enemy",
    "highest_health_enemy",
    "boss_priority",
    "random_enemy",
    "random_direction",
    "movement_direction",
    "self_centered",
    "ground_near_player",
}
ALLOWED_PERFORMANCE_COSTS = {"low", "medium", "high"}
ALLOWED_MAP_BOUNDS = {"rectangle"}
ALLOWED_MAP_SPAWN_MODES = {"around_player"}

ALLOWED_PASSIVE_STATS = {
    "max_health",
    "move_speed",
    "pickup_radius",
    "damage_multiplier",
    "cooldown_multiplier",
    "xp_multiplier",
    "regen_per_second",
    "damage_reduction",
    "projectile_size",
    "effect_duration",
}
ALLOWED_PASSIVE_MODES = {"add", "multiply", "set_min", "set_max"}
ALLOWED_ENEMY_BEHAVIORS = {
    "chase",
    "dash",
    "split",
    "leave_hazard",
    "orbit_player",
    "jump",
    "ranged_spit",
    "shielded",
}
REQUIRED_PROJECT_RULES = {
    "candidate_only": True,
    "accepted_content": False,
    "runtime_integrated": False,
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]


def discover_candidates(root: Path) -> list[Path]:
    if (root / "metadata" / "manifest.json").exists():
        return [root]
    return sorted(path for path in root.iterdir() if path.is_dir()) if root.exists() else []


def collect_base_ids(base_content_dir: Path | None) -> dict[str, set[str]]:
    ids: dict[str, set[str]] = {category: set() for category in BASE_ID_CATEGORIES}
    if base_content_dir is None or not base_content_dir.exists():
        return ids
    for category in ids:
        category_dir = base_content_dir / category
        if not category_dir.exists():
            continue
        for path in sorted(category_dir.glob("*.json")):
            try:
                payload = load_json(path)
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            item_id = payload.get("id")
            if is_nonempty_string(item_id):
                ids[category].add(item_id)
    return ids


def collect_candidate_ids(candidate_dir: Path) -> dict[str, set[str]]:
    ids: dict[str, set[str]] = {category: set() for category in SUPPORTED_CONTENT_CATEGORIES}
    for category in SUPPORTED_CONTENT_CATEGORIES:
        category_dir = candidate_dir / category
        if not category_dir.exists():
            continue
        for path in sorted(category_dir.glob("*.json")):
            try:
                payload = load_json(path)
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            item_id = payload.get("id")
            if is_nonempty_string(item_id):
                ids[category].add(str(item_id))
    return ids


def validate_common(
    category: str,
    payload: dict[str, Any],
    path: Path,
    base_ids: set[str],
    allow_overrides: bool,
) -> tuple[str, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    item_id = payload.get("id")
    display_id = item_id if is_nonempty_string(item_id) else path.stem

    if not is_nonempty_string(item_id) or not ID_PATTERN.match(str(item_id)):
        errors.append(f"{category} `{display_id}` has invalid kebab-case id")
    elif item_id != path.stem:
        warnings.append(f"{category} `{item_id}` id does not match file stem `{path.stem}`")

    if is_nonempty_string(item_id) and item_id in base_ids and not allow_overrides:
        errors.append(f"{category} `{item_id}` duplicates base content id")

    for field in ("name", "description", "visual_description", "sfx_description"):
        if not is_nonempty_string(payload.get(field)):
            errors.append(f"{category} `{display_id}` missing non-empty `{field}`")

    if not isinstance(payload.get("version"), int) or payload["version"] <= 0:
        errors.append(f"{category} `{display_id}` version must be a positive integer")

    rarity = payload.get("rarity")
    if rarity not in ALLOWED_RARITIES:
        errors.append(f"{category} `{display_id}` has invalid rarity `{rarity}`")

    tags = string_list(payload.get("tags"))
    if not tags or len(tags) != len(payload.get("tags", [])):
        errors.append(f"{category} `{display_id}` tags must be a non-empty list of strings")

    unlock = payload.get("unlock")
    if not isinstance(unlock, dict) or not is_nonempty_string(unlock.get("type")):
        errors.append(f"{category} `{display_id}` unlock.type must be non-empty")

    return str(display_id), errors, warnings


def validate_passive(
    path: Path,
    payload: dict[str, Any],
    base_ids: set[str],
    allow_overrides: bool,
) -> tuple[list[str], list[str]]:
    item_id, errors, warnings = validate_common("passive", payload, path, base_ids, allow_overrides)

    if not isinstance(payload.get("max_level"), int) or payload["max_level"] <= 0:
        errors.append(f"passive `{item_id}` max_level must be a positive integer")

    modifiers = payload.get("stat_modifiers")
    if not isinstance(modifiers, list) or not modifiers:
        errors.append(f"passive `{item_id}` stat_modifiers must be a non-empty list")
        return errors, warnings

    for index, modifier in enumerate(modifiers):
        if not isinstance(modifier, dict):
            errors.append(f"passive `{item_id}` stat_modifiers[{index}] must be an object")
            continue
        stat = modifier.get("stat")
        mode = modifier.get("mode")
        if stat not in ALLOWED_PASSIVE_STATS:
            errors.append(f"passive `{item_id}` stat_modifiers[{index}].stat is invalid: {stat}")
        if mode not in ALLOWED_PASSIVE_MODES:
            errors.append(f"passive `{item_id}` stat_modifiers[{index}].mode is invalid: {mode}")
        if not is_number(modifier.get("value_per_level")):
            errors.append(f"passive `{item_id}` stat_modifiers[{index}].value_per_level must be finite")
        if mode == "multiply" and is_number(modifier.get("value_per_level")) and modifier["value_per_level"] <= 0:
            errors.append(f"passive `{item_id}` multiply modifier must stay positive")

    return errors, warnings


def validate_weapon(
    path: Path,
    payload: dict[str, Any],
    base_ids: set[str],
    allow_overrides: bool,
) -> tuple[list[str], list[str]]:
    item_id, errors, warnings = validate_common("weapon", payload, path, base_ids, allow_overrides)

    if payload.get("type") not in ALLOWED_WEAPON_TYPES:
        errors.append(f"weapon `{item_id}` type is invalid: {payload.get('type')}")

    targeting = payload.get("targeting")
    if not isinstance(targeting, dict):
        errors.append(f"weapon `{item_id}` targeting must be an object")
    else:
        if targeting.get("mode") not in ALLOWED_TARGETING_MODES:
            errors.append(f"weapon `{item_id}` targeting.mode is invalid: {targeting.get('mode')}")
        if not is_number(targeting.get("range")) or targeting["range"] < 0:
            errors.append(f"weapon `{item_id}` targeting.range must be non-negative")

    base_stats = payload.get("base_stats")
    if not isinstance(base_stats, dict):
        errors.append(f"weapon `{item_id}` base_stats must be an object")
    else:
        for field in ("damage", "projectile_speed", "area_radius", "duration_ms"):
            if not is_number(base_stats.get(field)) or base_stats[field] < 0:
                errors.append(f"weapon `{item_id}` base_stats.{field} must be non-negative")
        if not is_number(base_stats.get("cooldown_ms")) or base_stats["cooldown_ms"] <= 0:
            errors.append(f"weapon `{item_id}` base_stats.cooldown_ms must be positive")
        for field in ("projectile_count", "pierce"):
            if not isinstance(base_stats.get(field), int) or isinstance(base_stats.get(field), bool) or base_stats[field] < 0:
                errors.append(f"weapon `{item_id}` base_stats.{field} must be a non-negative integer")

    scaling = payload.get("scaling")
    if not isinstance(scaling, dict):
        errors.append(f"weapon `{item_id}` scaling must be an object")
    else:
        if not isinstance(scaling.get("max_level"), int) or scaling["max_level"] <= 0:
            errors.append(f"weapon `{item_id}` scaling.max_level must be a positive integer")
        for field in ("damage_per_level", "range_per_level", "area_per_level"):
            if not is_number(scaling.get(field)) or scaling[field] < 0:
                errors.append(f"weapon `{item_id}` scaling.{field} must be non-negative")
        if not is_number(scaling.get("cooldown_multiplier_per_level")) or scaling["cooldown_multiplier_per_level"] <= 0:
            errors.append(f"weapon `{item_id}` scaling.cooldown_multiplier_per_level must be positive")
        bonus_levels = scaling.get("projectile_count_bonus_levels")
        if not isinstance(bonus_levels, list):
            errors.append(f"weapon `{item_id}` scaling.projectile_count_bonus_levels must be a list")
        else:
            for index, level in enumerate(bonus_levels):
                if not isinstance(level, int) or isinstance(level, bool) or level <= 0:
                    errors.append(f"weapon `{item_id}` scaling.projectile_count_bonus_levels[{index}] must be positive integer")

    balance_budget = payload.get("balance_budget")
    if not isinstance(balance_budget, dict):
        errors.append(f"weapon `{item_id}` balance_budget must be an object")
    else:
        if not is_nonempty_string(balance_budget.get("role")):
            errors.append(f"weapon `{item_id}` balance_budget.role must be non-empty")
        for field in ("single_target_dps", "group_dps"):
            if not is_number(balance_budget.get(field)) or balance_budget[field] < 0:
                errors.append(f"weapon `{item_id}` balance_budget.{field} must be non-negative")
        if balance_budget.get("performance_cost") not in ALLOWED_PERFORMANCE_COSTS:
            errors.append(f"weapon `{item_id}` balance_budget.performance_cost is invalid: {balance_budget.get('performance_cost')}")

    return errors, warnings


def validate_enemy(
    path: Path,
    payload: dict[str, Any],
    base_ids: set[str],
    allow_overrides: bool,
) -> tuple[list[str], list[str]]:
    item_id, errors, warnings = validate_common("enemy", payload, path, base_ids, allow_overrides)

    for field in ("family", "counterplay", "death_effect"):
        if not is_nonempty_string(payload.get(field)):
            errors.append(f"enemy `{item_id}` missing non-empty `{field}`")

    stats = payload.get("stats")
    if not isinstance(stats, dict):
        errors.append(f"enemy `{item_id}` stats must be an object")
    else:
        positive_fields = ("health", "move_speed", "radius")
        non_negative_fields = ("contact_damage_per_second", "xp_value", "score_value")
        for field in positive_fields:
            if not is_number(stats.get(field)) or stats[field] <= 0:
                errors.append(f"enemy `{item_id}` stats.{field} must be positive")
        for field in non_negative_fields:
            if not is_number(stats.get(field)) or stats[field] < 0:
                errors.append(f"enemy `{item_id}` stats.{field} must be non-negative")

    behavior = payload.get("behavior")
    if not isinstance(behavior, dict):
        errors.append(f"enemy `{item_id}` behavior must be an object")
    else:
        behavior_type = behavior.get("type")
        if behavior_type not in ALLOWED_ENEMY_BEHAVIORS:
            errors.append(f"enemy `{item_id}` behavior.type is invalid: {behavior_type}")
        if not isinstance(behavior.get("parameters", {}), dict):
            errors.append(f"enemy `{item_id}` behavior.parameters must be an object")

    spawn_budget = payload.get("spawn_budget")
    if not isinstance(spawn_budget, dict):
        errors.append(f"enemy `{item_id}` spawn_budget must be an object")
    else:
        for field in ("threat", "performance_cost"):
            if not is_number(spawn_budget.get(field)) or spawn_budget[field] <= 0:
                errors.append(f"enemy `{item_id}` spawn_budget.{field} must be positive")

    return errors, warnings


def validate_evolution(
    path: Path,
    payload: dict[str, Any],
    base_ids: dict[str, set[str]],
    candidate_ids: dict[str, set[str]],
    allow_overrides: bool,
) -> tuple[list[str], list[str]]:
    item_id, errors, warnings = validate_common("evolution", payload, path, base_ids["evolutions"], allow_overrides)
    known_weapons = base_ids["weapons"] | candidate_ids["weapons"]
    known_passives = base_ids["passives"] | candidate_ids["passives"]

    requirements = payload.get("requirements")
    weapon_id: Any = None
    if not isinstance(requirements, dict):
        errors.append(f"evolution `{item_id}` requirements must be an object")
    else:
        weapon_req = requirements.get("weapon")
        if not isinstance(weapon_req, dict):
            errors.append(f"evolution `{item_id}` requirements.weapon must be an object")
        else:
            weapon_id = weapon_req.get("id")
            if not is_nonempty_string(weapon_id) or weapon_id not in known_weapons:
                errors.append(f"evolution `{item_id}` references unknown weapon `{weapon_id}`")
            if not isinstance(weapon_req.get("min_level"), int) or weapon_req["min_level"] <= 0:
                errors.append(f"evolution `{item_id}` requirements.weapon.min_level must be positive integer")
        passive_req = requirements.get("passive")
        if not isinstance(passive_req, dict):
            errors.append(f"evolution `{item_id}` requirements.passive must be an object")
        else:
            passive_id = passive_req.get("id")
            if not is_nonempty_string(passive_id) or passive_id not in known_passives:
                errors.append(f"evolution `{item_id}` references unknown passive `{passive_id}`")
            if not isinstance(passive_req.get("min_level"), int) or passive_req["min_level"] <= 0:
                errors.append(f"evolution `{item_id}` requirements.passive.min_level must be positive integer")
        if not is_nonempty_string(requirements.get("trigger")):
            errors.append(f"evolution `{item_id}` requirements.trigger must be non-empty")

    replaces_weapon = payload.get("replaces_weapon")
    if not is_nonempty_string(replaces_weapon) or replaces_weapon not in known_weapons:
        errors.append(f"evolution `{item_id}` replaces unknown weapon `{replaces_weapon}`")
    if is_nonempty_string(weapon_id) and is_nonempty_string(replaces_weapon) and weapon_id != replaces_weapon:
        errors.append(f"evolution `{item_id}` replaces_weapon must match requirements.weapon.id")

    weapon_definition = payload.get("weapon_definition")
    if not isinstance(weapon_definition, dict):
        errors.append(f"evolution `{item_id}` weapon_definition must be an object")
        return errors, warnings
    if weapon_definition.get("type") not in ALLOWED_WEAPON_TYPES:
        errors.append(f"evolution `{item_id}` weapon_definition.type is invalid: {weapon_definition.get('type')}")
    targeting = weapon_definition.get("targeting")
    if not isinstance(targeting, dict):
        errors.append(f"evolution `{item_id}` weapon_definition.targeting must be an object")
    else:
        if targeting.get("mode") not in ALLOWED_TARGETING_MODES:
            errors.append(f"evolution `{item_id}` weapon_definition.targeting.mode is invalid: {targeting.get('mode')}")
        if not is_number(targeting.get("range")) or targeting["range"] < 0:
            errors.append(f"evolution `{item_id}` weapon_definition.targeting.range must be non-negative")
    base_stats = weapon_definition.get("base_stats")
    if not isinstance(base_stats, dict):
        errors.append(f"evolution `{item_id}` weapon_definition.base_stats must be an object")
    else:
        if not is_number(base_stats.get("damage")) or base_stats["damage"] <= 0:
            errors.append(f"evolution `{item_id}` weapon_definition.base_stats.damage must be positive")
        if not is_number(base_stats.get("cooldown_ms")) or base_stats["cooldown_ms"] <= 0:
            errors.append(f"evolution `{item_id}` weapon_definition.base_stats.cooldown_ms must be positive")
        if not isinstance(base_stats.get("projectile_count"), int) or isinstance(base_stats.get("projectile_count"), bool) or base_stats["projectile_count"] <= 0:
            errors.append(f"evolution `{item_id}` weapon_definition.base_stats.projectile_count must be positive integer")
        if not is_number(base_stats.get("area_radius")) or base_stats["area_radius"] <= 0:
            errors.append(f"evolution `{item_id}` weapon_definition.base_stats.area_radius must be positive")
        if "projectile_speed" in base_stats and (not is_number(base_stats.get("projectile_speed")) or base_stats["projectile_speed"] <= 0):
            errors.append(f"evolution `{item_id}` weapon_definition.base_stats.projectile_speed must be positive when present")
        if "pierce" in base_stats and (not isinstance(base_stats.get("pierce"), int) or isinstance(base_stats.get("pierce"), bool) or base_stats["pierce"] <= 0):
            errors.append(f"evolution `{item_id}` weapon_definition.base_stats.pierce must be positive integer when present")
        if "duration_ms" in base_stats and (not is_number(base_stats.get("duration_ms")) or base_stats["duration_ms"] < 0):
            errors.append(f"evolution `{item_id}` weapon_definition.base_stats.duration_ms must be non-negative when present")

    return errors, warnings


def validate_wave(
    path: Path,
    payload: dict[str, Any],
    base_ids: dict[str, set[str]],
    candidate_ids: dict[str, set[str]],
    allow_overrides: bool,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    item_id = payload.get("id")
    display_id = item_id if is_nonempty_string(item_id) else path.stem

    if not is_nonempty_string(item_id) or not ID_PATTERN.match(str(item_id)):
        errors.append(f"wave `{display_id}` has invalid kebab-case id")
    elif item_id != path.stem:
        warnings.append(f"wave `{item_id}` id does not match file stem `{path.stem}`")

    if is_nonempty_string(item_id) and item_id in base_ids["waves"] and not allow_overrides:
        errors.append(f"wave `{item_id}` duplicates base content id")

    if not is_nonempty_string(payload.get("name")):
        errors.append(f"wave `{display_id}` missing non-empty `name`")
    if not isinstance(payload.get("version"), int) or payload["version"] <= 0:
        errors.append(f"wave `{display_id}` version must be a positive integer")

    known_maps = base_ids["maps"] | candidate_ids["maps"]
    map_id = payload.get("map_id")
    if not is_nonempty_string(map_id) or map_id not in known_maps:
        errors.append(f"wave `{display_id}` references unknown map `{map_id}`")

    if not is_number(payload.get("duration_seconds")) or payload["duration_seconds"] <= 0:
        errors.append(f"wave `{display_id}` duration_seconds must be positive")

    known_enemies = base_ids["enemies"] | candidate_ids["enemies"]
    segments = payload.get("segments")
    if not isinstance(segments, list) or not segments:
        errors.append(f"wave `{display_id}` segments must be a non-empty list")
    else:
        for segment_index, segment in enumerate(segments):
            if not isinstance(segment, dict):
                errors.append(f"wave `{display_id}` segments[{segment_index}] must be an object")
                continue
            start_second = segment.get("start_second")
            end_second = segment.get("end_second")
            if not is_number(start_second) or not is_number(end_second) or start_second >= end_second:
                errors.append(f"wave `{display_id}` segments[{segment_index}] must have start_second < end_second")
            for field in ("spawn_interval_ms", "spawn_count", "max_alive"):
                if not is_number(segment.get(field)) or segment[field] <= 0:
                    errors.append(f"wave `{display_id}` segments[{segment_index}].{field} must be positive")
            enemy_pool = segment.get("enemy_pool")
            if not isinstance(enemy_pool, list) or not enemy_pool:
                errors.append(f"wave `{display_id}` segments[{segment_index}].enemy_pool must be non-empty")
                continue
            for entry_index, entry in enumerate(enemy_pool):
                if not isinstance(entry, dict):
                    errors.append(f"wave `{display_id}` enemy_pool[{entry_index}] must be an object")
                    continue
                enemy_id = entry.get("enemy_id")
                if not is_nonempty_string(enemy_id) or enemy_id not in known_enemies:
                    errors.append(f"wave `{display_id}` references unknown enemy `{enemy_id}`")
                if not is_number(entry.get("weight")) or entry["weight"] <= 0:
                    errors.append(f"wave `{display_id}` enemy `{enemy_id}` weight must be positive")

    boss_events = payload.get("boss_events", [])
    if not isinstance(boss_events, list):
        errors.append(f"wave `{display_id}` boss_events must be a list when present")
    else:
        for event_index, event in enumerate(boss_events):
            if not isinstance(event, dict):
                errors.append(f"wave `{display_id}` boss_events[{event_index}] must be an object")
                continue
            boss_id = event.get("boss_id")
            if not is_nonempty_string(boss_id) or boss_id not in base_ids["bosses"]:
                errors.append(f"wave `{display_id}` references unknown boss `{boss_id}`")
            if not is_number(event.get("time_second")) or event["time_second"] < 0:
                errors.append(f"wave `{display_id}` boss_events[{event_index}].time_second must be non-negative")

    pressure_budget = payload.get("pressure_budget")
    if not isinstance(pressure_budget, dict):
        warnings.append(f"wave `{display_id}` should include pressure_budget for review")

    return errors, warnings


def validate_map(
    path: Path,
    payload: dict[str, Any],
    base_ids: set[str],
    allow_overrides: bool,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    item_id = payload.get("id")
    display_id = item_id if is_nonempty_string(item_id) else path.stem

    if not is_nonempty_string(item_id) or not ID_PATTERN.match(str(item_id)):
        errors.append(f"map `{display_id}` has invalid kebab-case id")
    elif item_id != path.stem:
        warnings.append(f"map `{item_id}` id does not match file stem `{path.stem}`")

    if is_nonempty_string(item_id) and item_id in base_ids and not allow_overrides:
        errors.append(f"map `{item_id}` duplicates base content id")

    for field in ("name", "description", "visual_description", "music_theme"):
        if not is_nonempty_string(payload.get(field)):
            errors.append(f"map `{display_id}` missing non-empty `{field}`")

    if not isinstance(payload.get("version"), int) or payload["version"] <= 0:
        errors.append(f"map `{display_id}` version must be a positive integer")

    tags = string_list(payload.get("tags"))
    if not tags or len(tags) != len(payload.get("tags", [])):
        errors.append(f"map `{display_id}` tags must be a non-empty list of strings")

    size = payload.get("size")
    if not isinstance(size, dict):
        errors.append(f"map `{display_id}` size must be an object")
    else:
        for field in ("width", "height"):
            if not is_number(size.get(field)) or size[field] <= 0:
                errors.append(f"map `{display_id}` size.{field} must be positive")

    bounds = payload.get("bounds")
    if not isinstance(bounds, dict):
        errors.append(f"map `{display_id}` bounds must be an object")
    elif bounds.get("type") not in ALLOWED_MAP_BOUNDS:
        errors.append(f"map `{display_id}` bounds.type is invalid: {bounds.get('type')}")

    spawn_rules = payload.get("spawn_rules")
    if not isinstance(spawn_rules, dict):
        errors.append(f"map `{display_id}` spawn_rules must be an object")
    else:
        if spawn_rules.get("mode") not in ALLOWED_MAP_SPAWN_MODES:
            errors.append(f"map `{display_id}` spawn_rules.mode is invalid: {spawn_rules.get('mode')}")
        min_distance = spawn_rules.get("min_distance")
        max_distance = spawn_rules.get("max_distance")
        if not is_number(min_distance) or min_distance <= 0:
            errors.append(f"map `{display_id}` spawn_rules.min_distance must be positive")
        if not is_number(max_distance) or max_distance <= 0:
            errors.append(f"map `{display_id}` spawn_rules.max_distance must be positive")
        if is_number(min_distance) and is_number(max_distance) and min_distance >= max_distance:
            errors.append(f"map `{display_id}` spawn_rules must have min_distance < max_distance")

    hazards = payload.get("hazards")
    if not isinstance(hazards, list):
        errors.append(f"map `{display_id}` hazards must be a list")

    return errors, warnings


def validate_manifest(candidate_dir: Path) -> tuple[list[str], list[str]]:
    manifest_path = candidate_dir / "metadata" / "manifest.json"
    errors: list[str] = []
    warnings: list[str] = []
    if not manifest_path.exists():
        return ["candidate is missing metadata/manifest.json"], warnings
    try:
        manifest = load_json(manifest_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return [f"metadata/manifest.json is invalid: {error}"], warnings

    if manifest.get("batch_id") != candidate_dir.name:
        warnings.append("manifest batch_id should match candidate directory name")
    if not is_nonempty_string(manifest.get("generated_at")):
        errors.append("manifest generated_at must be non-empty")

    project_rules = manifest.get("project_rules")
    if not isinstance(project_rules, dict):
        errors.append("manifest project_rules must be an object")
    else:
        for key, expected in REQUIRED_PROJECT_RULES.items():
            if project_rules.get(key) is not expected:
                errors.append(f"manifest project_rules.{key} must be {json.dumps(expected)}")
        if not string_list(project_rules.get("required_next_steps")):
            errors.append("manifest project_rules.required_next_steps must be non-empty")

    source_docs = string_list(manifest.get("source_docs"))
    if not source_docs:
        warnings.append("manifest should list source_docs for provenance")

    return errors, warnings


def validate_candidate(
    candidate_dir: Path,
    base_ids: dict[str, set[str]],
    allow_overrides: bool,
) -> dict[str, Any]:
    errors, warnings = validate_manifest(candidate_dir)
    candidate_ids = collect_candidate_ids(candidate_dir)
    content_count = 0

    for category, validator in (
        ("weapons", validate_weapon),
        ("passives", validate_passive),
        ("enemies", validate_enemy),
    ):
        category_dir = candidate_dir / category
        if not category_dir.exists():
            continue
        for path in sorted(category_dir.glob("*.json")):
            content_count += 1
            try:
                payload = load_json(path)
            except (OSError, ValueError, json.JSONDecodeError) as error:
                errors.append(f"{path.relative_to(candidate_dir)} is invalid JSON: {error}")
                continue
            item_errors, item_warnings = validator(
                path,
                payload,
                base_ids[category],
                allow_overrides,
            )
            errors.extend(item_errors)
            warnings.extend(item_warnings)

    category_dir = candidate_dir / "evolutions"
    if category_dir.exists():
        for path in sorted(category_dir.glob("*.json")):
            content_count += 1
            try:
                payload = load_json(path)
            except (OSError, ValueError, json.JSONDecodeError) as error:
                errors.append(f"{path.relative_to(candidate_dir)} is invalid JSON: {error}")
                continue
            item_errors, item_warnings = validate_evolution(path, payload, base_ids, candidate_ids, allow_overrides)
            errors.extend(item_errors)
            warnings.extend(item_warnings)

    category_dir = candidate_dir / "waves"
    if category_dir.exists():
        for path in sorted(category_dir.glob("*.json")):
            content_count += 1
            try:
                payload = load_json(path)
            except (OSError, ValueError, json.JSONDecodeError) as error:
                errors.append(f"{path.relative_to(candidate_dir)} is invalid JSON: {error}")
                continue
            item_errors, item_warnings = validate_wave(path, payload, base_ids, candidate_ids, allow_overrides)
            errors.extend(item_errors)
            warnings.extend(item_warnings)

    category_dir = candidate_dir / "maps"
    if category_dir.exists():
        for path in sorted(category_dir.glob("*.json")):
            content_count += 1
            try:
                payload = load_json(path)
            except (OSError, ValueError, json.JSONDecodeError) as error:
                errors.append(f"{path.relative_to(candidate_dir)} is invalid JSON: {error}")
                continue
            item_errors, item_warnings = validate_map(path, payload, base_ids["maps"], allow_overrides)
            errors.extend(item_errors)
            warnings.extend(item_warnings)

    if content_count == 0:
        errors.append("candidate contains no supported partial content files")

    if not (candidate_dir / "README.md").exists():
        warnings.append("candidate is missing README.md")

    return {
        "id": candidate_dir.name,
        "path": str(candidate_dir),
        "content_count": content_count,
        "decision": "valid" if not errors else "invalid",
        "errors": errors,
        "warnings": warnings,
    }


def build_report(root: Path, base_content_dir: Path | None, allow_overrides: bool) -> dict[str, Any]:
    candidates = discover_candidates(root)
    base_ids = collect_base_ids(base_content_dir)
    reviews = [validate_candidate(path, base_ids, allow_overrides) for path in candidates]
    errors = [
        f"{review['id']}: {error}"
        for review in reviews
        for error in review["errors"]
    ]
    warnings = [
        f"{review['id']}: {warning}"
        for review in reviews
        for warning in review["warnings"]
    ]
    if not candidates:
        errors.append(f"no candidate directories found under {root}")

    return {
        "report_version": 1,
        "root": str(root),
        "base_content_dir": str(base_content_dir) if base_content_dir is not None else None,
        "allow_overrides": allow_overrides,
        "decision": "content_candidates_valid" if not errors else "content_candidates_invalid",
        "candidate_count": len(reviews),
        "content_count": sum(review["content_count"] for review in reviews),
        "errors": errors,
        "warnings": warnings,
        "candidates": reviews,
        "limitations": [
            "This validator checks partial candidate schema only; full GameCore validation still requires game_harness validate-candidates.",
            "A passing partial candidate report does not promote content beyond generated_candidates.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Content Candidate Validation",
        "",
        f"- Root: `{report['root']}`",
        f"- Decision: `{report['decision']}`",
        f"- Candidate count: {report['candidate_count']}",
        f"- Content count: {report['content_count']}",
        "",
        "## Candidates",
        "",
        "| Candidate | Decision | Content | Errors | Warnings |",
        "|---|---|---:|---:|---:|",
    ]
    for candidate in report["candidates"]:
        lines.append(
            f"| `{candidate['id']}` | `{candidate['decision']}` | {candidate['content_count']} | "
            f"{len(candidate['errors'])} | {len(candidate['warnings'])} |"
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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm partial content candidates.")
    parser.add_argument(
        "root",
        type=Path,
        nargs="?",
        default=Path("harness/generated_candidate_patches"),
        help="Generated content candidate patch root or a single patch directory",
    )
    parser.add_argument("--base-content-dir", type=Path, default=Path("content/base_demo"))
    parser.add_argument("--allow-overrides", action="store_true")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON validation report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown validation summary")
    args = parser.parse_args()

    report = build_report(args.root, args.base_content_dir, args.allow_overrides)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "content_candidates_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
