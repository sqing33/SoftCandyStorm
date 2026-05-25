#!/usr/bin/env python3
"""Validate materialized generated content candidate packs.

This dependency-free preflight does not replace `game_harness
validate-candidates`. It checks candidate-only metadata, expected full-pack
directory structure, content counts, and cross-file references that can be
validated without launching the Rust binary.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


CONTENT_CATEGORIES = [
    "characters",
    "weapons",
    "passives",
    "evolutions",
    "enemies",
    "bosses",
    "waves",
    "maps",
    "events",
]
REQUIRED_PROJECT_RULES = {
    "candidate_only": True,
    "accepted_content": False,
    "runtime_integrated": False,
}
ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def load_json(path: Path) -> dict[str, Any]:
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


def content_files(directory: Path) -> list[Path]:
    return sorted(path for path in directory.glob("*.json") if path.is_file()) if directory.exists() else []


def discover_packs(root: Path) -> list[Path]:
    if (root / "metadata" / "manifest.json").exists():
        return [root]
    return sorted(path for path in root.iterdir() if (path / "metadata" / "manifest.json").exists()) if root.exists() else []


def validate_project_rules(label: str, project_rules: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(project_rules, dict):
        return [f"{label} project_rules must be an object"]
    for key, expected in REQUIRED_PROJECT_RULES.items():
        if project_rules.get(key) is not expected:
            errors.append(f"{label} project_rules.{key} must be {json.dumps(expected)}")
    if not string_list(project_rules.get("required_next_steps")):
        errors.append(f"{label} project_rules.required_next_steps must be non-empty")
    return errors


def collect_content(pack_dir: Path) -> tuple[dict[str, dict[str, dict[str, Any]]], dict[str, int], list[str], list[str]]:
    ids: dict[str, dict[str, dict[str, Any]]] = {category: {} for category in CONTENT_CATEGORIES}
    counts: dict[str, int] = {category: 0 for category in CONTENT_CATEGORIES}
    errors: list[str] = []
    warnings: list[str] = []

    for category in CONTENT_CATEGORIES:
        category_dir = pack_dir / category
        if not category_dir.exists():
            errors.append(f"missing required category directory `{category}`")
            continue
        files = content_files(category_dir)
        counts[category] = len(files)
        if not files:
            errors.append(f"category `{category}` contains no JSON content")
            continue
        for path in files:
            relative_path = path.relative_to(pack_dir)
            try:
                payload = load_json(path)
            except (OSError, ValueError, json.JSONDecodeError) as error:
                errors.append(f"{relative_path} is invalid JSON: {error}")
                continue

            item_id = payload.get("id")
            display_id = item_id if is_nonempty_string(item_id) else path.stem
            if not is_nonempty_string(item_id) or not ID_PATTERN.match(str(item_id)):
                errors.append(f"{relative_path} has invalid kebab-case id")
                continue
            if item_id != path.stem:
                warnings.append(f"{relative_path} id `{item_id}` does not match file stem `{path.stem}`")
            if item_id in ids[category]:
                errors.append(f"duplicate `{category}` id `{item_id}`")
                continue
            ids[category][str(item_id)] = payload

            if not is_nonempty_string(payload.get("name")):
                errors.append(f"{category} `{display_id}` missing non-empty `name`")
            if not isinstance(payload.get("version"), int) or payload["version"] <= 0:
                errors.append(f"{category} `{display_id}` version must be a positive integer")
            if category != "waves" and not is_nonempty_string(payload.get("description")):
                errors.append(f"{category} `{display_id}` missing non-empty `description`")

    return ids, counts, errors, warnings


def validate_manifest(pack_dir: Path, content_counts: dict[str, int]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    manifest_path = pack_dir / "metadata" / "manifest.json"
    if not manifest_path.exists():
        return ["missing metadata/manifest.json"], warnings

    try:
        manifest = load_json(manifest_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return [f"metadata/manifest.json is invalid: {error}"], warnings

    if manifest.get("batch_id") != pack_dir.name:
        errors.append("manifest batch_id must match candidate directory name")
    if manifest.get("candidate_kind") != "full_content_pack":
        errors.append("manifest candidate_kind must be `full_content_pack`")
    if not is_nonempty_string(manifest.get("generated_at")):
        errors.append("manifest generated_at must be non-empty")
    if not is_nonempty_string(manifest.get("source_patch")):
        warnings.append("manifest should record source_patch provenance")
    if not is_nonempty_string(manifest.get("base_content_dir")):
        warnings.append("manifest should record base_content_dir provenance")

    errors.extend(validate_project_rules("manifest", manifest.get("project_rules")))

    declared_counts = manifest.get("content_counts")
    if not isinstance(declared_counts, dict):
        errors.append("manifest content_counts must be an object")
    else:
        for category, actual_count in content_counts.items():
            if declared_counts.get(category) != actual_count:
                errors.append(
                    f"manifest content_counts.{category} is {declared_counts.get(category)}, expected {actual_count}"
                )

    return errors, warnings


def validate_materialization(pack_dir: Path, content_counts: dict[str, int]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    materialization_path = pack_dir / "metadata" / "materialization.json"
    if not materialization_path.exists():
        warnings.append("missing metadata/materialization.json; provenance should be reviewed manually")
        return errors, warnings

    try:
        materialization = load_json(materialization_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return [f"metadata/materialization.json is invalid: {error}"], warnings

    errors.extend(validate_project_rules("materialization", materialization.get("project_rules")))

    output_dir = materialization.get("output_dir")
    if is_nonempty_string(output_dir) and Path(output_dir).name != pack_dir.name:
        errors.append("materialization output_dir must point to this candidate directory")

    source_patch = materialization.get("source_patch")
    if not is_nonempty_string(source_patch):
        errors.append("materialization source_patch must be non-empty")
    elif not Path(source_patch).exists():
        warnings.append(f"materialization source_patch does not currently exist: {source_patch}")

    copied_counts = materialization.get("copied_counts")
    overlay_counts = materialization.get("overlay_counts")
    if not isinstance(copied_counts, dict):
        errors.append("materialization copied_counts must be an object")
    if not isinstance(overlay_counts, dict):
        errors.append("materialization overlay_counts must be an object")
    if isinstance(copied_counts, dict) and isinstance(overlay_counts, dict):
        for category, actual_count in content_counts.items():
            expected_count = copied_counts.get(category, 0) + overlay_counts.get(category, 0)
            if expected_count != actual_count:
                errors.append(
                    f"materialization counts for {category} total {expected_count}, expected {actual_count}"
                )

    source_manifest_path = pack_dir / "metadata" / "source_patch_manifest.json"
    if not source_manifest_path.exists():
        warnings.append("missing metadata/source_patch_manifest.json; patch provenance is incomplete")
    else:
        try:
            source_manifest = load_json(source_manifest_path)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            errors.append(f"metadata/source_patch_manifest.json is invalid: {error}")
        else:
            errors.extend(validate_project_rules("source_patch_manifest", source_manifest.get("project_rules")))

    return errors, warnings


def validate_references(ids: dict[str, dict[str, dict[str, Any]]]) -> list[str]:
    errors: list[str] = []

    for character_id, character in ids["characters"].items():
        loadout = character.get("initial_loadout")
        if not isinstance(loadout, dict):
            errors.append(f"character `{character_id}` initial_loadout must be an object")
            continue
        for weapon_id in string_list(loadout.get("weapons")):
            if weapon_id not in ids["weapons"]:
                errors.append(f"character `{character_id}` loadout references unknown weapon `{weapon_id}`")
        for passive_id in string_list(loadout.get("passives")):
            if passive_id not in ids["passives"]:
                errors.append(f"character `{character_id}` loadout references unknown passive `{passive_id}`")

    for evolution_id, evolution in ids["evolutions"].items():
        requirements = evolution.get("requirements")
        if not isinstance(requirements, dict):
            errors.append(f"evolution `{evolution_id}` requirements must be an object")
            continue
        weapon = requirements.get("weapon")
        passive = requirements.get("passive")
        if not isinstance(weapon, dict) or not is_nonempty_string(weapon.get("id")):
            errors.append(f"evolution `{evolution_id}` requirements.weapon.id must be non-empty")
        elif weapon["id"] not in ids["weapons"]:
            errors.append(f"evolution `{evolution_id}` references unknown weapon `{weapon['id']}`")
        if not isinstance(passive, dict) or not is_nonempty_string(passive.get("id")):
            errors.append(f"evolution `{evolution_id}` requirements.passive.id must be non-empty")
        elif passive["id"] not in ids["passives"]:
            errors.append(f"evolution `{evolution_id}` references unknown passive `{passive['id']}`")
        replaces_weapon = evolution.get("replaces_weapon")
        if is_nonempty_string(replaces_weapon) and replaces_weapon not in ids["weapons"]:
            errors.append(f"evolution `{evolution_id}` replaces unknown weapon `{replaces_weapon}`")

    for wave_id, wave in ids["waves"].items():
        map_id = wave.get("map_id")
        if not is_nonempty_string(map_id) or map_id not in ids["maps"]:
            errors.append(f"wave `{wave_id}` references unknown map `{map_id}`")

        segments = wave.get("segments")
        if not isinstance(segments, list) or not segments:
            errors.append(f"wave `{wave_id}` segments must be a non-empty list")
        else:
            for segment_index, segment in enumerate(segments):
                if not isinstance(segment, dict):
                    errors.append(f"wave `{wave_id}` segments[{segment_index}] must be an object")
                    continue
                enemy_pool = segment.get("enemy_pool")
                if not isinstance(enemy_pool, list) or not enemy_pool:
                    errors.append(f"wave `{wave_id}` segments[{segment_index}].enemy_pool must be non-empty")
                    continue
                for entry_index, entry in enumerate(enemy_pool):
                    if not isinstance(entry, dict):
                        errors.append(f"wave `{wave_id}` enemy_pool[{entry_index}] must be an object")
                        continue
                    enemy_id = entry.get("enemy_id")
                    if not is_nonempty_string(enemy_id) or enemy_id not in ids["enemies"]:
                        errors.append(f"wave `{wave_id}` references unknown enemy `{enemy_id}`")

        boss_events = wave.get("boss_events", [])
        if not isinstance(boss_events, list):
            errors.append(f"wave `{wave_id}` boss_events must be a list when present")
        else:
            for event_index, event in enumerate(boss_events):
                if not isinstance(event, dict):
                    errors.append(f"wave `{wave_id}` boss_events[{event_index}] must be an object")
                    continue
                boss_id = event.get("boss_id")
                if not is_nonempty_string(boss_id) or boss_id not in ids["bosses"]:
                    errors.append(f"wave `{wave_id}` references unknown boss `{boss_id}`")

    return errors


def validate_pack(pack_dir: Path) -> dict[str, Any]:
    ids, content_counts, errors, warnings = collect_content(pack_dir)
    errors.extend(validate_references(ids))
    manifest_errors, manifest_warnings = validate_manifest(pack_dir, content_counts)
    materialization_errors, materialization_warnings = validate_materialization(pack_dir, content_counts)
    errors.extend(manifest_errors)
    errors.extend(materialization_errors)
    warnings.extend(manifest_warnings)
    warnings.extend(materialization_warnings)

    if not (pack_dir / "README.md").exists():
        warnings.append("candidate is missing README.md")

    return {
        "id": pack_dir.name,
        "path": str(pack_dir),
        "decision": "valid" if not errors else "invalid",
        "content_counts": content_counts,
        "content_count": sum(content_counts.values()),
        "errors": errors,
        "warnings": warnings,
    }


def build_report(root: Path) -> dict[str, Any]:
    packs = discover_packs(root)
    reviews = [validate_pack(pack) for pack in packs]
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
    if not packs:
        errors.append(f"no materialized candidate packs found under {root}")

    return {
        "report_version": 1,
        "root": str(root),
        "decision": "materialized_content_packs_valid" if not errors else "materialized_content_packs_invalid",
        "candidate_count": len(reviews),
        "content_count": sum(review["content_count"] for review in reviews),
        "errors": errors,
        "warnings": warnings,
        "candidates": reviews,
        "limitations": [
            "This preflight checks generated candidate structure and references only.",
            "A passing report does not validate gameplay semantics, budgets, simulations, replay regression, or human review.",
            "Full promotion still requires game_harness validate-candidates when the Rust binary can launch.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Materialized Content Pack Preflight",
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
    parser = argparse.ArgumentParser(description="Validate materialized Soft Candy Storm content candidate packs.")
    parser.add_argument(
        "root",
        type=Path,
        nargs="?",
        default=Path("harness/generated_candidates"),
        help="Generated full-pack candidate root or a single candidate directory",
    )
    parser.add_argument("--report", type=Path, default=None, help="Write JSON validation report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown validation summary")
    args = parser.parse_args()

    report = build_report(args.root)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "materialized_content_packs_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
