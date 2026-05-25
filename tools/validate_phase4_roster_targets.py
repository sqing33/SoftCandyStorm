#!/usr/bin/env python3
"""Validate Phase 4 roster target coverage for a content pack.

This preflight maps the docs/04 first roster and docs/12 Phase 4 count targets
to a dependency-free content-pack check. It does not replace GameCore schema,
budget, Bot, replay, or human playtest gates.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


COUNT_TARGETS = {
    "characters": 5,
    "weapons": 12,
    "passives": 12,
    "evolutions": 8,
    "enemies": 12,
    "bosses": 3,
    "maps": 1,
    "waves": 1,
}

EXPECTED_IDS = {
    "characters": {
        "jar-keeper",
        "bubble-courier",
        "cream-knight",
        "sour-plum-doctor",
        "pudding-crafter",
    },
    "weapons": {
        "rainbow-candy-shot",
        "marshmallow-shield",
        "soda-fountain",
        "lollipop-boomerang",
        "popping-candy-mine",
        "caramel-sticky-ground",
        "pudding-turret",
        "mint-cyclone",
        "candy-crystal-lance",
        "star-sugar-ray",
    },
    "passives": {
        "big-candy-jar",
        "nonstick-apron",
        "star-spoon",
        "bubble-shoes",
        "cream-clockwork",
        "candy-crystal-lens",
        "sour-tuner",
        "frosting-gloves",
    },
    "evolutions": {
        "rainbow-candy-meteor",
        "marshmallow-fortress",
        "soda-volcano",
        "sugar-windmill",
        "popping-candy-chain-reaction",
        "caramel-vortex",
        "pudding-bastion",
        "star-sugar-prism",
    },
    "enemies": {
        "bouncy-gummy",
        "sour-gummy",
        "sticky-bear-gummy",
        "sandwich-cookie-creep",
        "soda-bubble",
        "cotton-candy-clump",
        "caramel-slime",
        "spicy-gummy",
    },
    "bosses": {
        "runaway-sugar-mixer",
        "soda-fountain-dragon",
        "giant-cotton-clump",
        "caramel-furnace",
        "giant-gummy-bear-king",
        "cracked-star-jar-core",
    },
    "maps": {
        "frosting-grassland",
        "soda-creek",
        "cotton-cloud-pasture",
        "caramel-workshop",
        "jelly-platform",
        "cracked-star-jar",
    },
    "waves": {
        "frosting-grassland-standard",
        "soda-creek-standard",
        "cotton-cloud-pasture-standard",
        "caramel-workshop-standard",
        "jelly-platform-standard",
        "cracked-star-jar-standard",
    },
}

CATEGORY_REQUIRED_FIELDS = {
    "characters": ["name", "version", "base_stats", "initial_loadout", "visual_description", "sfx_description"],
    "weapons": ["name", "version", "type", "targeting", "base_stats", "scaling", "balance_budget", "visual_description", "sfx_description"],
    "passives": ["name", "version", "stat_modifiers", "max_level", "visual_description", "sfx_description"],
    "evolutions": ["name", "version", "requirements", "replaces_weapon", "weapon_definition", "visual_description", "sfx_description"],
    "enemies": ["name", "version", "family", "stats", "behavior", "spawn_budget", "counterplay", "visual_description", "death_effect", "sfx_description"],
    "bosses": ["name", "version", "stats", "phases", "counterplay", "visual_description", "sfx_description"],
    "maps": ["name", "version", "size", "spawn_rules", "visual_description", "music_theme"],
    "waves": ["name", "version", "map_id", "duration_seconds", "segments", "boss_events", "pressure_budget"],
}


def load_json(path: Path) -> dict[str, Any]:
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


def collect_category(content_dir: Path, category: str) -> tuple[dict[str, dict[str, Any]], list[str]]:
    records: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for path in content_files(content_dir, category):
        try:
            payload = load_json(path)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            errors.append(f"{category}/{path.name} is invalid JSON: {error}")
            continue
        item_id = payload.get("id")
        if not is_nonempty_string(item_id):
            errors.append(f"{category}/{path.name} missing non-empty id")
            continue
        if item_id != path.stem:
            errors.append(f"{category}/{path.name} id `{item_id}` must match file stem")
        if item_id in records:
            errors.append(f"{category} duplicate id `{item_id}`")
            continue
        records[str(item_id)] = payload
    return records, errors


def validate_required_fields(category: str, records: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for item_id, payload in records.items():
        for field in CATEGORY_REQUIRED_FIELDS[category]:
            if field not in payload:
                errors.append(f"{category} `{item_id}` missing `{field}`")
            elif isinstance(payload[field], str) and not payload[field].strip():
                errors.append(f"{category} `{item_id}` has empty `{field}`")
    return errors


def validate_references(records_by_category: dict[str, dict[str, dict[str, Any]]]) -> list[str]:
    errors: list[str] = []
    for character_id, character in records_by_category["characters"].items():
        loadout = character.get("initial_loadout", {})
        if not isinstance(loadout, dict):
            errors.append(f"character `{character_id}` initial_loadout must be an object")
            continue
        for weapon_id in loadout.get("weapons", []):
            if weapon_id not in records_by_category["weapons"]:
                errors.append(f"character `{character_id}` references unknown weapon `{weapon_id}`")
        for passive_id in loadout.get("passives", []):
            if passive_id not in records_by_category["passives"]:
                errors.append(f"character `{character_id}` references unknown passive `{passive_id}`")

    for evolution_id, evolution in records_by_category["evolutions"].items():
        requirements = evolution.get("requirements", {})
        if not isinstance(requirements, dict):
            errors.append(f"evolution `{evolution_id}` requirements must be an object")
            continue
        weapon = requirements.get("weapon", {})
        passive = requirements.get("passive", {})
        weapon_id = weapon.get("id") if isinstance(weapon, dict) else None
        passive_id = passive.get("id") if isinstance(passive, dict) else None
        if weapon_id not in records_by_category["weapons"]:
            errors.append(f"evolution `{evolution_id}` references unknown weapon `{weapon_id}`")
        if passive_id not in records_by_category["passives"]:
            errors.append(f"evolution `{evolution_id}` references unknown passive `{passive_id}`")
        replaces_weapon = evolution.get("replaces_weapon")
        if replaces_weapon not in records_by_category["weapons"]:
            errors.append(f"evolution `{evolution_id}` replaces unknown weapon `{replaces_weapon}`")

    for wave_id, wave in records_by_category["waves"].items():
        map_id = wave.get("map_id")
        if map_id not in records_by_category["maps"]:
            errors.append(f"wave `{wave_id}` references unknown map `{map_id}`")
        for index, segment in enumerate(wave.get("segments", [])):
            if not isinstance(segment, dict):
                errors.append(f"wave `{wave_id}` segments[{index}] must be an object")
                continue
            for entry in segment.get("enemy_pool", []):
                enemy_id = entry.get("enemy_id") if isinstance(entry, dict) else None
                if enemy_id not in records_by_category["enemies"]:
                    errors.append(f"wave `{wave_id}` references unknown enemy `{enemy_id}`")
        for event in wave.get("boss_events", []):
            boss_id = event.get("boss_id") if isinstance(event, dict) else None
            if boss_id not in records_by_category["bosses"]:
                errors.append(f"wave `{wave_id}` references unknown boss `{boss_id}`")
    return errors


def build_report(content_dir: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    records_by_category: dict[str, dict[str, dict[str, Any]]] = {}

    for category in COUNT_TARGETS:
        records, category_errors = collect_category(content_dir, category)
        records_by_category[category] = records
        errors.extend(category_errors)

        count = len(records)
        target = COUNT_TARGETS[category]
        if count < target:
            errors.append(f"{category} count {count} is below Phase 4 target {target}")

        missing_ids = sorted(EXPECTED_IDS[category] - set(records))
        if missing_ids:
            errors.append(f"{category} missing docs/04 roster ids: {', '.join(missing_ids)}")

        extra_count = count - len(EXPECTED_IDS[category])
        if extra_count > 0:
            warnings.append(f"{category} has {extra_count} extra ids beyond docs/04 named roster")

        errors.extend(validate_required_fields(category, records))

    errors.extend(validate_references(records_by_category))

    category_counts = {
        category: len(records_by_category[category])
        for category in COUNT_TARGETS
    }
    return {
        "report_version": 1,
        "content_dir": str(content_dir),
        "decision": "phase4_roster_targets_valid" if not errors else "phase4_roster_targets_invalid",
        "category_counts": category_counts,
        "count_targets": COUNT_TARGETS,
        "errors": errors,
        "warnings": warnings,
        "limitations": [
            "This validator checks docs/04 roster coverage, docs/12 Phase 4 counts, required fields, and lightweight references only.",
            "It does not replace GameCore schema validation, static budget gates, Bot simulation, replay regression, or human review.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Phase 4 Roster Target Validation",
        "",
        f"- Content dir: `{report['content_dir']}`",
        f"- Decision: `{report['decision']}`",
        "",
        "## Counts",
        "",
        "| Category | Count | Target |",
        "|---|---:|---:|",
    ]
    for category, target in report["count_targets"].items():
        lines.append(f"| `{category}` | {report['category_counts'][category]} | {target} |")
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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm Phase 4 roster target coverage.")
    parser.add_argument("content_dir", type=Path, help="Content pack directory")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON validation report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown validation summary")
    parser.add_argument("--allow-invalid", action="store_true", help="Exit 0 while recording an invalid/gap report")
    args = parser.parse_args()

    report = build_report(args.content_dir)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))

    if report["decision"] == "phase4_roster_targets_valid" or args.allow_invalid:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
