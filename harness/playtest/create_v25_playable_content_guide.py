#!/usr/bin/env python3
"""Create a human-readable playable content guide for the v25 candidate.

The guide is evidence support for manual playtests only. It reads the
generated candidate pack and summarizes what a human can try, without
promoting the candidate or filling any human review fields.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from run_v25_content_tour import TOUR_RUNS, build_tour_command, shell_quote
from run_v25_manual_playtest import CANDIDATE_ID, CONTENT_DIR, CONTENT_HASH


DEFAULT_REPORT = Path("harness/reports/2026-06-02_demo_buildcraft_repair_v25_playable_content_guide_001/guide.json")
DEFAULT_MARKDOWN = Path("harness/reports/2026-06-02_demo_buildcraft_repair_v25_playable_content_guide_001/summary.md")

CATEGORIES = ("characters", "maps", "weapons", "passives", "evolutions", "enemies", "bosses", "waves", "events")
DEMO_TARGETS = {
    "characters": 1,
    "maps": 1,
    "weapons": 12,
    "passives": 8,
    "enemies": 12,
    "bosses": 3,
    "waves": 1,
}


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def content_files(content_dir: Path, category: str) -> list[Path]:
    category_dir = content_dir / category
    if not category_dir.exists():
        return []
    return sorted(path for path in category_dir.glob("*.json") if path.is_file())


def collect_records(content_dir: Path) -> tuple[dict[str, dict[str, dict[str, Any]]], list[str]]:
    errors: list[str] = []
    records: dict[str, dict[str, dict[str, Any]]] = {}
    for category in CATEGORIES:
        category_records: dict[str, dict[str, Any]] = {}
        for path in content_files(content_dir, category):
            try:
                payload = load_json_object(path)
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                errors.append(f"{category}/{path.name} could not be read: {exc}")
                continue
            item_id = payload.get("id")
            if not isinstance(item_id, str) or not item_id.strip():
                errors.append(f"{category}/{path.name} missing non-empty id")
                continue
            category_records[item_id] = payload
        records[category] = category_records
    return records, errors


def name_for(records: dict[str, dict[str, Any]], item_id: str | None) -> str:
    if item_id is None:
        return ""
    payload = records.get(item_id)
    if not payload:
        return item_id
    name = payload.get("name")
    return f"{name} (`{item_id}`)" if isinstance(name, str) and name else f"`{item_id}`"


def short_tags(payload: dict[str, Any]) -> list[str]:
    tags = payload.get("tags")
    return [tag for tag in tags if isinstance(tag, str)] if isinstance(tags, list) else []


def summarize_characters(records: dict[str, dict[str, dict[str, Any]]]) -> list[dict[str, Any]]:
    weapons = records["weapons"]
    passives = records["passives"]
    characters = []
    for character in records["characters"].values():
        loadout = character.get("initial_loadout") if isinstance(character.get("initial_loadout"), dict) else {}
        weapon_ids = [item for item in loadout.get("weapons", []) if isinstance(item, str)]
        passive_ids = [item for item in loadout.get("passives", []) if isinstance(item, str)]
        trait = character.get("trait") if isinstance(character.get("trait"), dict) else {}
        characters.append(
            {
                "id": character["id"],
                "name": character.get("name", character["id"]),
                "tags": short_tags(character),
                "initial_weapons": [name_for(weapons, item) for item in weapon_ids],
                "initial_passives": [name_for(passives, item) for item in passive_ids],
                "trait": trait.get("description", ""),
                "description": character.get("description", ""),
            }
        )
    return sorted(characters, key=lambda item: item["id"])


def summarize_build_routes(records: dict[str, dict[str, dict[str, Any]]]) -> list[dict[str, Any]]:
    weapons = records["weapons"]
    passives = records["passives"]
    routes: list[dict[str, Any]] = []
    for evolution in records["evolutions"].values():
        requirements = evolution.get("requirements") if isinstance(evolution.get("requirements"), dict) else {}
        weapon_req = requirements.get("weapon") if isinstance(requirements.get("weapon"), dict) else {}
        passive_req = requirements.get("passive") if isinstance(requirements.get("passive"), dict) else {}
        weapon_id = weapon_req.get("id") if isinstance(weapon_req.get("id"), str) else None
        passive_id = passive_req.get("id") if isinstance(passive_req.get("id"), str) else None
        weapon = weapons.get(weapon_id or "", {})
        role = ""
        budget = weapon.get("balance_budget") if isinstance(weapon.get("balance_budget"), dict) else {}
        if isinstance(budget.get("role"), str):
            role = budget["role"]
        routes.append(
            {
                "id": evolution["id"],
                "name": evolution.get("name", evolution["id"]),
                "weapon": name_for(weapons, weapon_id),
                "weapon_id": weapon_id,
                "weapon_min_level": weapon_req.get("min_level"),
                "passive": name_for(passives, passive_id),
                "passive_id": passive_id,
                "passive_min_level": passive_req.get("min_level"),
                "trigger": requirements.get("trigger", ""),
                "role": role,
                "tags": short_tags(evolution),
                "description": evolution.get("description", ""),
            }
        )
    return sorted(routes, key=lambda item: item["id"])


def summarize_maps(records: dict[str, dict[str, dict[str, Any]]]) -> list[dict[str, Any]]:
    maps = records["maps"]
    enemies = records["enemies"]
    bosses = records["bosses"]
    by_map: dict[str, dict[str, Any]] = {}
    for map_id, game_map in maps.items():
        by_map[map_id] = {
            "id": map_id,
            "name": game_map.get("name", map_id),
            "tags": short_tags(game_map),
            "description": game_map.get("description", ""),
            "music_theme": game_map.get("music_theme", ""),
            "duration_seconds": None,
            "segment_count": 0,
            "boss_events": [],
            "early_enemies": [],
            "late_enemies": [],
        }

    for wave in records["waves"].values():
        map_id = wave.get("map_id")
        if not isinstance(map_id, str) or map_id not in by_map:
            continue
        segments = wave.get("segments") if isinstance(wave.get("segments"), list) else []
        by_map[map_id]["duration_seconds"] = wave.get("duration_seconds")
        by_map[map_id]["segment_count"] = len(segments)
        boss_events = []
        for event in wave.get("boss_events", []) if isinstance(wave.get("boss_events"), list) else []:
            if not isinstance(event, dict):
                continue
            boss_id = event.get("boss_id") if isinstance(event.get("boss_id"), str) else None
            boss_events.append(
                {
                    "time_second": event.get("time_second"),
                    "boss": name_for(bosses, boss_id),
                    "boss_id": boss_id,
                }
            )
        by_map[map_id]["boss_events"] = boss_events
        if segments:
            by_map[map_id]["early_enemies"] = enemy_names_from_segment(segments[0], enemies)
            by_map[map_id]["late_enemies"] = enemy_names_from_segment(segments[-1], enemies)
    return sorted(by_map.values(), key=lambda item: item["id"])


def enemy_names_from_segment(segment: Any, enemies: dict[str, dict[str, Any]]) -> list[str]:
    if not isinstance(segment, dict):
        return []
    pool = segment.get("enemy_pool") if isinstance(segment.get("enemy_pool"), list) else []
    names = []
    for entry in pool:
        if not isinstance(entry, dict):
            continue
        enemy_id = entry.get("enemy_id")
        if isinstance(enemy_id, str):
            names.append(name_for(enemies, enemy_id))
    return names


def summarize_enemies(records: dict[str, dict[str, dict[str, Any]]]) -> list[dict[str, Any]]:
    enemies = []
    for enemy in records["enemies"].values():
        behavior = enemy.get("behavior") if isinstance(enemy.get("behavior"), dict) else {}
        stats = enemy.get("stats") if isinstance(enemy.get("stats"), dict) else {}
        enemies.append(
            {
                "id": enemy["id"],
                "name": enemy.get("name", enemy["id"]),
                "tags": short_tags(enemy),
                "behavior": behavior.get("type", ""),
                "health": stats.get("health"),
                "move_speed": stats.get("move_speed"),
                "counterplay": enemy.get("counterplay", ""),
            }
        )
    return sorted(enemies, key=lambda item: item["id"])


def summarize_bosses(records: dict[str, dict[str, dict[str, Any]]]) -> list[dict[str, Any]]:
    bosses = []
    for boss in records["bosses"].values():
        abilities = []
        for phase in boss.get("phases", []) if isinstance(boss.get("phases"), list) else []:
            if isinstance(phase, dict) and isinstance(phase.get("abilities"), list):
                abilities.extend(item for item in phase["abilities"] if isinstance(item, str))
        bosses.append(
            {
                "id": boss["id"],
                "name": boss.get("name", boss["id"]),
                "tags": short_tags(boss),
                "abilities": sorted(set(abilities)),
                "counterplay": boss.get("counterplay", ""),
            }
        )
    return sorted(bosses, key=lambda item: item["id"])


def summarize_events(records: dict[str, dict[str, dict[str, Any]]]) -> list[dict[str, Any]]:
    return [
        {
            "id": event["id"],
            "name": event.get("name", event["id"]),
            "tags": short_tags(event),
            "description": event.get("description", ""),
        }
        for event in sorted(records["events"].values(), key=lambda item: item["id"])
    ]


def load_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return load_json_object(path)
    except (OSError, ValueError, json.JSONDecodeError):
        return {}


def build_guide(repo_root: Path, content_dir: Path = CONTENT_DIR) -> dict[str, Any]:
    resolved_content_dir = repo_root / content_dir
    records, errors = collect_records(resolved_content_dir)
    counts = {category: len(records[category]) for category in CATEGORIES}
    manifest = load_optional_json(resolved_content_dir / "metadata" / "manifest.json")
    materialization = load_optional_json(resolved_content_dir / "metadata" / "materialization.json")
    source_patch = load_optional_json(resolved_content_dir / "metadata" / "source_patch_manifest.json")

    project_rules = manifest.get("project_rules") if isinstance(manifest.get("project_rules"), dict) else {}
    target_status = {
        category: {
            "actual": counts.get(category, 0),
            "target": target,
            "meets_target": counts.get(category, 0) >= target,
        }
        for category, target in DEMO_TARGETS.items()
    }
    routes = summarize_build_routes(records)
    guide = {
        "report_version": 1,
        "candidate_id": CANDIDATE_ID,
        "content_hash": CONTENT_HASH,
        "content_dir": str(content_dir),
        "decision": "playable_content_guide_invalid" if errors else "playable_content_guide_candidate_only",
        "candidate_state": {
            "candidate_only": project_rules.get("candidate_only", True),
            "accepted_content": project_rules.get("accepted_content", False),
            "runtime_integrated": project_rules.get("runtime_integrated", False),
            "source_patch": manifest.get("source_patch", materialization.get("source_patch")),
            "overlay_counts": materialization.get("overlay_counts", {}),
            "overridden_counts": materialization.get("overridden_counts", {}),
            "source_patch_contents": source_patch.get("contents", []),
        },
        "counts": counts,
        "demo_targets": target_status,
        "summary": {
            "character_count": counts["characters"],
            "map_count": counts["maps"],
            "weapon_count": counts["weapons"],
            "passive_count": counts["passives"],
            "evolution_count": counts["evolutions"],
            "enemy_count": counts["enemies"],
            "boss_count": counts["bosses"],
            "wave_count": counts["waves"],
            "event_count": counts["events"],
            "build_route_count": len(routes),
            "target_count_failures": [
                category for category, status in target_status.items() if not status["meets_target"]
            ],
            "error_count": len(errors),
        },
        "characters": summarize_characters(records),
        "build_routes": routes,
        "maps": summarize_maps(records),
        "enemies": summarize_enemies(records),
        "bosses": summarize_bosses(records),
        "events": summarize_events(records),
        "playtest_entrypoints": [
            "python3 harness/playtest/run_v25_manual_playtest.py --status",
            "python3 harness/playtest/run_v25_manual_playtest.py --next --dry-run",
            "python3 harness/playtest/run_v25_manual_playtest.py --next",
        ],
        "content_tour_entrypoints": [
            "python3 harness/playtest/run_v25_content_tour.py --list",
            "python3 harness/playtest/run_v25_content_tour.py --next --dry-run",
            "python3 harness/playtest/run_v25_content_tour.py --next",
            "python3 harness/playtest/summarize_v25_content_tour_reports.py --allow-incomplete",
        ],
        "content_tour_runs": [
            {
                "run_id": run.run_id,
                "character_id": run.character_id,
                "map_id": run.map_id,
                "seed": run.seed,
                "focus": run.focus,
                "report": str(run.report_path),
                "command": f"python3 harness/playtest/run_v25_content_tour.py {run.run_id}",
                "runtime_command": shell_quote(build_tour_command(run)),
            }
            for run in TOUR_RUNS
        ],
        "human_review_blockers": [
            "design_review_incomplete",
            "manual_playtest_incomplete",
            "final_acceptance_missing",
            "accepted_content_lockfile_blocked",
        ],
        "errors": errors,
        "limitations": [
            "This guide summarizes generated candidate content for human playtest preparation only.",
            "It does not approve content, fill human review fields, or move files into accepted_content.",
            "v25 must remain out of content/base_demo and Runtime official content until human gates pass.",
        ],
    }
    return guide


def join_list(items: list[str]) -> str:
    return ", ".join(items) if items else "-"


def write_markdown(guide: dict[str, Any], path: Path) -> None:
    summary = guide["summary"]
    state = guide["candidate_state"]
    lines = [
        "# v25 可玩内容导览",
        "",
        f"- Candidate id: `{guide['candidate_id']}`",
        f"- Content hash: `{guide['content_hash']}`",
        f"- Content dir: `{guide['content_dir']}`",
        f"- Decision: `{guide['decision']}`",
        f"- Candidate only: `{state['candidate_only']}`",
        f"- Accepted content: `{state['accepted_content']}`",
        f"- Runtime integrated: `{state['runtime_integrated']}`",
        "",
        "## 内容数量",
        "",
        "| 类型 | 当前数量 | Demo 目标 | 达标 |",
        "|---|---:|---:|---|",
    ]
    for category, target in guide["demo_targets"].items():
        lines.append(
            f"| `{category}` | {target['actual']} | {target['target']} | `{target['meets_target']}` |"
        )
    lines.extend(
        [
            f"| `evolutions` | {summary['evolution_count']} | - | - |",
            f"| `events` | {summary['event_count']} | - | - |",
            "",
            "## 9 局人工试玩入口",
            "",
        ]
    )
    lines.extend(f"- `{command}`" for command in guide["playtest_entrypoints"])

    lines.extend(["", "## 角色 / 地图巡游入口", ""])
    lines.extend(f"- `{command}`" for command in guide["content_tour_entrypoints"])
    lines.extend(["", "| Run | Character | Map | Seed | Focus | Launcher |", "|---|---|---|---:|---|---|"])
    for run in guide["content_tour_runs"]:
        lines.append(
            f"| `{run['run_id']}` | `{run['character_id']}` | `{run['map_id']}` | "
            f"{run['seed']} | {run['focus']} | `{run['command']}` |"
        )

    lines.extend(["", "## 角色入口", "", "| 角色 | 标签 | 初始武器 | 初始被动 | 特性 |", "|---|---|---|---|---|"])
    for character in guide["characters"]:
        lines.append(
            f"| {character['name']} (`{character['id']}`) | {join_list(character['tags'])} | "
            f"{join_list(character['initial_weapons'])} | {join_list(character['initial_passives'])} | "
            f"{character['trait'] or '-'} |"
        )

    lines.extend(["", "## 构筑路线", "", "| 进化 | 基础武器 | 搭配被动 | 触发 | 角色定位 | 说明 |", "|---|---|---|---|---|---|"])
    for route in guide["build_routes"]:
        weapon_req = f"{route['weapon']} Lv.{route['weapon_min_level']}"
        passive_req = f"{route['passive']} Lv.{route['passive_min_level']}"
        lines.append(
            f"| {route['name']} (`{route['id']}`) | {weapon_req} | {passive_req} | "
            f"`{route['trigger']}` | `{route['role'] or '-'} / {join_list(route['tags'])}` | "
            f"{route['description']} |"
        )

    lines.extend(["", "## 地图与波次身份", "", "| 地图 | 时长 | 段数 | Boss | 开局敌人 | 终局敌人 |", "|---|---:|---:|---|---|---|"])
    for game_map in guide["maps"]:
        boss_text = ", ".join(
            f"{event['boss']} @ {event['time_second']}s" for event in game_map["boss_events"]
        ) or "-"
        lines.append(
            f"| {game_map['name']} (`{game_map['id']}`) | {game_map['duration_seconds'] or '-'} | "
            f"{game_map['segment_count']} | {boss_text} | "
            f"{join_list(game_map['early_enemies'])} | {join_list(game_map['late_enemies'])} |"
        )

    lines.extend(["", "## 敌人反制", "", "| 敌人 | 行为 | 标签 | 反制提示 |", "|---|---|---|---|"])
    for enemy in guide["enemies"]:
        lines.append(
            f"| {enemy['name']} (`{enemy['id']}`) | `{enemy['behavior']}` | "
            f"{join_list(enemy['tags'])} | {enemy['counterplay'] or '-'} |"
        )

    lines.extend(["", "## Boss 机制", "", "| Boss | 能力 | 反制提示 |", "|---|---|---|"])
    for boss in guide["bosses"]:
        lines.append(
            f"| {boss['name']} (`{boss['id']}`) | {join_list(boss['abilities'])} | {boss['counterplay'] or '-'} |"
        )

    lines.extend(["", "## 随机事件", ""])
    if guide["events"]:
        lines.extend(f"- {event['name']} (`{event['id']}`)：{event['description']}" for event in guide["events"])
    else:
        lines.append("- None")

    lines.extend(["", "## 阻塞项", ""])
    lines.extend(f"- `{item}`" for item in guide["human_review_blockers"])
    lines.extend(["", "## 限制", ""])
    lines.extend(f"- {item}" for item in guide["limitations"])
    if guide["errors"]:
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {error}" for error in guide["errors"])

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a v25 playable content guide.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--content-dir", type=Path, default=CONTENT_DIR)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()

    guide = build_guide(args.repo_root, args.content_dir)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(guide, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(guide, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(guide, indent=2, ensure_ascii=False))
    return 0 if not guide["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
