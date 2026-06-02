#!/usr/bin/env python3
"""Audit playable-content coverage for the v25 candidate.

The audit checks whether the v25 candidate has a complete-enough playable
surface for human playtest preparation. It does not judge fun, run Runtime,
accept content, or move candidate files into the official content pool.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_v25_playable_content_guide import CATEGORIES, build_guide, collect_records
from run_v25_manual_playtest import CANDIDATE_ID, CONTENT_DIR, CONTENT_HASH


DEFAULT_REPORT = Path(
    "harness/reports/2026-06-02_demo_buildcraft_repair_v25_playable_content_coverage_001/"
    "playable_content_coverage.json"
)
DEFAULT_MARKDOWN = Path(
    "harness/reports/2026-06-02_demo_buildcraft_repair_v25_playable_content_coverage_001/summary.md"
)

EXPECTED_BUILD_ROLES = {
    "starter",
    "defense",
    "control",
    "summon",
    "boss-killer",
    "aoe-clear",
    "economy",
}
FIELD_CHECKS = {
    "characters": ("description", "visual_description", "sfx_description"),
    "weapons": ("description", "visual_description", "sfx_description", "balance_budget"),
    "passives": ("description", "visual_description", "sfx_description", "balance_budget"),
    "evolutions": ("description", "visual_description", "sfx_description", "requirements"),
    "enemies": ("description", "visual_description", "sfx_description", "counterplay"),
    "bosses": ("description", "visual_description", "sfx_description", "counterplay"),
    "maps": ("description", "visual_description", "music_theme"),
    "events": ("description", "visual_description", "sfx_description"),
}
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


def is_present(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value)
    if isinstance(value, dict):
        return bool(value)
    return value is not None


def markdown_escape(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def code(value: Any) -> str:
    text = str(value).strip() if value is not None else ""
    return f"`{markdown_escape(text or '-')}`"


def sort_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        items,
        key=lambda item: (
            PRIORITY_ORDER.get(str(item.get("priority", "P3")), 99),
            str(item.get("category", "")),
            str(item.get("id", "")),
        ),
    )


def content_ids(records: dict[str, dict[str, dict[str, Any]]], category: str) -> set[str]:
    return set(records.get(category, {}))


def referenced_evolution_weapons(records: dict[str, dict[str, dict[str, Any]]]) -> set[str]:
    weapon_ids: set[str] = set()
    for evolution in records["evolutions"].values():
        requirements = evolution.get("requirements") if isinstance(evolution.get("requirements"), dict) else {}
        weapon = requirements.get("weapon") if isinstance(requirements.get("weapon"), dict) else {}
        weapon_id = weapon.get("id")
        if isinstance(weapon_id, str) and weapon_id:
            weapon_ids.add(weapon_id)
    return weapon_ids


def referenced_evolution_passives(records: dict[str, dict[str, dict[str, Any]]]) -> set[str]:
    passive_ids: set[str] = set()
    for evolution in records["evolutions"].values():
        requirements = evolution.get("requirements") if isinstance(evolution.get("requirements"), dict) else {}
        passive = requirements.get("passive") if isinstance(requirements.get("passive"), dict) else {}
        passive_id = passive.get("id")
        if isinstance(passive_id, str) and passive_id:
            passive_ids.add(passive_id)
    return passive_ids


def collect_playable_sets(guide: dict[str, Any]) -> dict[str, set[str]]:
    quick_characters = {preset["character_id"] for preset in guide["quick_play_presets"]}
    quick_maps = {preset["map_id"] for preset in guide["quick_play_presets"]}
    tour_characters = {run["character_id"] for run in guide["content_tour_runs"]}
    tour_maps = {run["map_id"] for run in guide["content_tour_runs"]}
    return {
        "quick_characters": quick_characters,
        "quick_maps": quick_maps,
        "tour_characters": tour_characters,
        "tour_maps": tour_maps,
    }


def add_action(
    items: list[dict[str, Any]],
    *,
    item_id: str,
    priority: str,
    category: str,
    title: str,
    affected_ids: list[str],
    evidence: str,
    action: str,
) -> None:
    items.append(
        {
            "id": item_id,
            "priority": priority,
            "category": category,
            "title": title,
            "affected_ids": affected_ids,
            "evidence": evidence,
            "action": action,
            "candidate_only": True,
        }
    )


def audit_candidate_state(guide: dict[str, Any], items: list[dict[str, Any]]) -> None:
    state = guide["candidate_state"]
    if state.get("candidate_only") is not True:
        add_action(
            items,
            item_id="candidate_state_not_candidate_only",
            priority="P0",
            category="candidate_state",
            title="候选池标记异常",
            affected_ids=[guide["candidate_id"]],
            evidence="candidate_only is not true",
            action="检查 manifest，确保 v25 仍停留在 generated_candidates 候选池。",
        )
    if state.get("accepted_content") is True or state.get("runtime_integrated") is True:
        add_action(
            items,
            item_id="candidate_state_promoted_too_early",
            priority="P0",
            category="candidate_state",
            title="候选内容被提前晋级",
            affected_ids=[guide["candidate_id"]],
            evidence=f"accepted_content={state.get('accepted_content')}, runtime_integrated={state.get('runtime_integrated')}",
            action="撤回错误晋级路径，等待真人审查、人工试玩和 lockfile 通过后再进入正式内容池。",
        )


def audit_targets(guide: dict[str, Any], items: list[dict[str, Any]]) -> None:
    failures = guide["summary"]["target_count_failures"]
    if failures:
        add_action(
            items,
            item_id="demo_target_counts_missing",
            priority="P0",
            category="content_count",
            title="Demo 内容数量未达到目标",
            affected_ids=list(failures),
            evidence=f"target_count_failures={failures}",
            action="补足缺失类型的候选内容，并重新运行 playable content guide 和 coverage audit。",
        )


def audit_entrypoint_coverage(guide: dict[str, Any], items: list[dict[str, Any]]) -> None:
    sets = collect_playable_sets(guide)
    character_ids = {item["id"] for item in guide["characters"]}
    map_ids = {item["id"] for item in guide["maps"]}
    checks = [
        ("quick_play_missing_characters", "quick-play 缺少角色覆盖", character_ids - sets["quick_characters"]),
        ("quick_play_missing_maps", "quick-play 缺少地图覆盖", map_ids - sets["quick_maps"]),
        ("content_tour_missing_characters", "内容巡游缺少角色覆盖", character_ids - sets["tour_characters"]),
        ("content_tour_missing_maps", "内容巡游缺少地图覆盖", map_ids - sets["tour_maps"]),
    ]
    for item_id, title, missing in checks:
        if missing:
            add_action(
                items,
                item_id=item_id,
                priority="P0",
                category="entrypoint_coverage",
                title=title,
                affected_ids=sorted(missing),
                evidence=f"missing={sorted(missing)}",
                action="补充对应 quick-play 或 content-tour 入口，确保玩家能实际启动这些角色和地图。",
            )


def audit_character_starters(
    records: dict[str, dict[str, dict[str, Any]]],
    items: list[dict[str, Any]],
) -> None:
    evolved_weapons = referenced_evolution_weapons(records)
    weapon_ids = content_ids(records, "weapons")
    for character in records["characters"].values():
        loadout = character.get("initial_loadout") if isinstance(character.get("initial_loadout"), dict) else {}
        starters = [item for item in loadout.get("weapons", []) if isinstance(item, str)]
        if not starters:
            add_action(
                items,
                item_id=f"character_missing_initial_weapon_{character['id']}",
                priority="P0",
                category="character_starter",
                title="角色缺少初始武器",
                affected_ids=[character["id"]],
                evidence="initial_loadout.weapons is empty",
                action="为角色配置至少一个已存在的初始武器，否则玩家无法形成清晰开局。",
            )
            continue
        missing_refs = [weapon_id for weapon_id in starters if weapon_id not in weapon_ids]
        if missing_refs:
            add_action(
                items,
                item_id=f"character_initial_weapon_missing_ref_{character['id']}",
                priority="P0",
                category="character_starter",
                title="角色初始武器引用不存在",
                affected_ids=[character["id"], *missing_refs],
                evidence=f"missing weapon refs={missing_refs}",
                action="修正角色初始武器引用或补齐对应武器候选。",
            )
        non_evolving_starters = [weapon_id for weapon_id in starters if weapon_id not in evolved_weapons]
        if non_evolving_starters:
            add_action(
                items,
                item_id=f"character_starter_without_evolution_{character['id']}",
                priority="P1",
                category="character_starter",
                title="角色初始武器缺少进化路线",
                affected_ids=[character["id"], *non_evolving_starters],
                evidence=f"starter weapons without evolution={non_evolving_starters}",
                action="为该初始武器补一条进化路线，或明确改成短期无进化的候选风险并安排试玩验证。",
            )


def audit_build_routes(
    guide: dict[str, Any],
    records: dict[str, dict[str, dict[str, Any]]],
    items: list[dict[str, Any]],
) -> None:
    roles = {route["role"] for route in guide["build_routes"] if isinstance(route.get("role"), str) and route["role"]}
    missing_roles = sorted(EXPECTED_BUILD_ROLES - roles)
    if missing_roles:
        add_action(
            items,
            item_id="build_roles_missing",
            priority="P1",
            category="build_routes",
            title="构筑定位覆盖不足",
            affected_ids=missing_roles,
            evidence=f"missing roles={missing_roles}",
            action="补齐缺失定位的武器 / 被动 / 进化路线，或调整现有路线的 balance_budget.role。",
        )

    weapon_ids = content_ids(records, "weapons")
    passive_ids = content_ids(records, "passives")
    evolved_weapons = referenced_evolution_weapons(records)
    used_passives = referenced_evolution_passives(records)
    all_weapons_without_evolution = sorted(weapon_ids - evolved_weapons)
    if all_weapons_without_evolution:
        add_action(
            items,
            item_id="weapons_without_evolution_routes",
            priority="P2",
            category="build_routes",
            title="部分武器没有进化路线",
            affected_ids=all_weapons_without_evolution,
            evidence=f"weapons without evolution={all_weapons_without_evolution}",
            action="评估这些武器是否应补进化，尤其是玩家初始武器和主要流派入口。",
        )
    unused_passives = sorted(passive_ids - used_passives)
    if unused_passives:
        add_action(
            items,
            item_id="passives_without_evolution_usage",
            priority="P2",
            category="build_routes",
            title="部分被动没有参与进化配方",
            affected_ids=unused_passives,
            evidence=f"passives without evolution usage={unused_passives}",
            action="判断这些被动是否只是数值补强，还是需要绑定新进化以提高升级选择纠结感。",
        )


def audit_map_wave_coverage(guide: dict[str, Any], items: list[dict[str, Any]]) -> None:
    for game_map in guide["maps"]:
        map_id = game_map["id"]
        if game_map["duration_seconds"] != 600:
            add_action(
                items,
                item_id=f"map_duration_not_standard_{map_id}",
                priority="P1",
                category="map_wave",
                title="地图不是 10 分钟标准局",
                affected_ids=[map_id],
                evidence=f"duration_seconds={game_map['duration_seconds']}",
                action="调整地图波次为 600 秒标准局，或明确它不是当前 demo 标准内容。",
            )
        if game_map["segment_count"] < 5:
            add_action(
                items,
                item_id=f"map_wave_segments_low_{map_id}",
                priority="P1",
                category="map_wave",
                title="地图波次段落太少",
                affected_ids=[map_id],
                evidence=f"segment_count={game_map['segment_count']}",
                action="补足开局、成长期、Boss 前后、中后期和终局压力段。",
            )
        if not game_map["boss_events"]:
            add_action(
                items,
                item_id=f"map_missing_boss_{map_id}",
                priority="P1",
                category="map_wave",
                title="地图缺少 Boss 事件",
                affected_ids=[map_id],
                evidence="boss_events is empty",
                action="配置至少一个章节 Boss 或普通 Boss 事件，确保 10 分钟局有目标感。",
            )
        if not game_map["early_enemies"] or not game_map["late_enemies"]:
            add_action(
                items,
                item_id=f"map_missing_enemy_identity_{map_id}",
                priority="P1",
                category="map_wave",
                title="地图敌人身份不完整",
                affected_ids=[map_id],
                evidence=f"early={game_map['early_enemies']}, late={game_map['late_enemies']}",
                action="检查 wave enemy_pool，确保玩家能感到地图前后期节奏差异。",
            )


def audit_counterplay(guide: dict[str, Any], items: list[dict[str, Any]]) -> None:
    enemy_missing = sorted(enemy["id"] for enemy in guide["enemies"] if not enemy.get("counterplay"))
    if enemy_missing:
        add_action(
            items,
            item_id="enemies_missing_counterplay",
            priority="P1",
            category="counterplay",
            title="敌人缺少反制说明",
            affected_ids=enemy_missing,
            evidence=f"enemy counterplay missing={enemy_missing}",
            action="补充玩家能观察到的反制方式，便于试玩记录死亡是否可理解。",
        )
    boss_missing = sorted(
        boss["id"] for boss in guide["bosses"] if not boss.get("counterplay") or not boss.get("abilities")
    )
    if boss_missing:
        add_action(
            items,
            item_id="bosses_missing_readable_mechanics",
            priority="P1",
            category="counterplay",
            title="Boss 缺少可读机制或反制",
            affected_ids=boss_missing,
            evidence=f"boss readable mechanics missing={boss_missing}",
            action="为 Boss 补充阶段能力和反制提示，避免 Boss 只是血量检查。",
        )


def audit_required_fields(
    records: dict[str, dict[str, dict[str, Any]]],
    items: list[dict[str, Any]],
) -> None:
    for category in CATEGORIES:
        fields = FIELD_CHECKS.get(category, ())
        missing: list[str] = []
        for item_id, payload in records[category].items():
            for field in fields:
                if not is_present(payload.get(field)):
                    missing.append(f"{item_id}.{field}")
        if missing:
            add_action(
                items,
                item_id=f"{category}_missing_playable_descriptors",
                priority="P2",
                category="playable_descriptors",
                title=f"{category} 缺少可玩内容描述字段",
                affected_ids=missing,
                evidence=f"missing fields={missing}",
                action="补齐描述、视觉、音效、预算或需求字段，方便人工试玩前理解内容身份。",
            )


def build_audit(repo_root: Path, content_dir: Path = CONTENT_DIR) -> dict[str, Any]:
    guide = build_guide(repo_root, content_dir)
    records, record_errors = collect_records(repo_root / content_dir)
    items: list[dict[str, Any]] = []
    audit_candidate_state(guide, items)
    audit_targets(guide, items)
    audit_entrypoint_coverage(guide, items)
    audit_character_starters(records, items)
    audit_build_routes(guide, records, items)
    audit_map_wave_coverage(guide, items)
    audit_counterplay(guide, items)
    audit_required_fields(records, items)
    items = sort_items(items)

    priority_counts: dict[str, int] = {}
    category_counts: dict[str, int] = {}
    for item in items:
        priority_counts[item["priority"]] = priority_counts.get(item["priority"], 0) + 1
        category_counts[item["category"]] = category_counts.get(item["category"], 0) + 1
    hard_error_count = guide["summary"]["error_count"] + len(record_errors)
    decision = "v25_playable_content_coverage_invalid"
    if hard_error_count == 0:
        decision = (
            "v25_playable_content_coverage_needs_content_repair"
            if items
            else "v25_playable_content_coverage_ready_for_human_playtest"
        )

    return {
        "report_version": 1,
        "candidate_id": CANDIDATE_ID,
        "content_hash": CONTENT_HASH,
        "content_dir": str(content_dir),
        "decision": decision,
        "summary": {
            "action_item_count": len(items),
            "priority_counts": priority_counts,
            "category_counts": category_counts,
            "guide_error_count": guide["summary"]["error_count"],
            "record_error_count": len(record_errors),
            "quick_play_preset_count": len(guide["quick_play_presets"]),
            "content_tour_run_count": len(guide["content_tour_runs"]),
            "build_route_count": guide["summary"]["build_route_count"],
            "character_count": guide["summary"]["character_count"],
            "map_count": guide["summary"]["map_count"],
            "target_count_failures": guide["summary"]["target_count_failures"],
        },
        "candidate_state": guide["candidate_state"],
        "coverage": {
            "expected_build_roles": sorted(EXPECTED_BUILD_ROLES),
            "actual_build_roles": sorted(
                {
                    route["role"]
                    for route in guide["build_routes"]
                    if isinstance(route.get("role"), str) and route["role"]
                }
            ),
            "quick_play_characters": sorted(collect_playable_sets(guide)["quick_characters"]),
            "quick_play_maps": sorted(collect_playable_sets(guide)["quick_maps"]),
            "content_tour_characters": sorted(collect_playable_sets(guide)["tour_characters"]),
            "content_tour_maps": sorted(collect_playable_sets(guide)["tour_maps"]),
        },
        "action_items": items,
        "errors": [*guide["errors"], *record_errors],
        "limitations": [
            "这份审计只检查玩家可触达内容表面是否覆盖完整，不运行 Runtime、不判断乐趣、不接受候选。",
            "发现缺口只能进入 repair/playtest 讨论，不能绕过 Schema、Harness、人工审查和 lockfile。",
            "v25 仍是 generated candidate，不能复制到 content/base_demo、accepted_content 或 Runtime 正式内容目录。",
            "AI/RL 训练线不在本审计范围内。",
        ],
    }


def write_markdown(audit: dict[str, Any], path: Path) -> None:
    summary = audit["summary"]
    lines = [
        "# v25 可玩内容覆盖审计",
        "",
        f"- Candidate id: `{audit['candidate_id']}`",
        f"- Content hash: `{audit['content_hash']}`",
        f"- Content dir: `{audit['content_dir']}`",
        f"- Decision: `{audit['decision']}`",
        f"- Action items: `{summary['action_item_count']}`",
        f"- Build routes: `{summary['build_route_count']}`",
        f"- Quick-play presets: `{summary['quick_play_preset_count']}`",
        f"- Content-tour runs: `{summary['content_tour_run_count']}`",
        "",
        "## 覆盖摘要",
        "",
        f"- Characters: `{summary['character_count']}`",
        f"- Maps: `{summary['map_count']}`",
        f"- Expected build roles: `{', '.join(audit['coverage']['expected_build_roles'])}`",
        f"- Actual build roles: `{', '.join(audit['coverage']['actual_build_roles'])}`",
        f"- Quick-play characters: `{', '.join(audit['coverage']['quick_play_characters'])}`",
        f"- Quick-play maps: `{', '.join(audit['coverage']['quick_play_maps'])}`",
        f"- Content-tour characters: `{', '.join(audit['coverage']['content_tour_characters'])}`",
        f"- Content-tour maps: `{', '.join(audit['coverage']['content_tour_maps'])}`",
        "",
        "## 修复项",
        "",
    ]
    if audit["action_items"]:
        lines.extend(
            [
                "| Priority | Category | Item | Affected | Evidence | Action |",
                "|---|---|---|---|---|---|",
            ]
        )
        for item in audit["action_items"]:
            lines.append(
                "| "
                + " | ".join(
                    [
                        code(item["priority"]),
                        code(item["category"]),
                        code(item["id"]),
                        markdown_escape(", ".join(item["affected_ids"])),
                        markdown_escape(item["evidence"]),
                        markdown_escape(item["action"]),
                    ]
                )
                + " |"
            )
    else:
        lines.append("- 当前没有自动覆盖审计发现的内容缺口；下一步仍需要人工试玩和设计审查。")

    lines.extend(["", "## 错误", ""])
    if audit["errors"]:
        lines.extend(f"- {item}" for item in audit["errors"])
    else:
        lines.append("- None")

    lines.extend(["", "## 限制", ""])
    lines.extend(f"- {item}" for item in audit["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit v25 playable-content coverage.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--content-dir", type=Path, default=CONTENT_DIR)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--allow-repair", action="store_true")
    args = parser.parse_args()

    audit = build_audit(args.repo_root, args.content_dir)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(audit, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(audit, indent=2, ensure_ascii=False))

    if audit["decision"] == "v25_playable_content_coverage_ready_for_human_playtest":
        return 0
    if args.allow_repair and audit["decision"] == "v25_playable_content_coverage_needs_content_repair":
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
