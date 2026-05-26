#!/usr/bin/env python3
"""Validate static balance budgets without launching the Rust harness.

This mirrors the first-pass budget checks from `game_harness budget-content` for
docs/15: weapon theoretical DPS, enemy threat, boss HP/XP ranges, and wave
pressure envelopes. It is intentionally conservative and does not replace Bot
simulation, replay regression, or human playtest balance review.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


PERFORMANCE_COST_LABELS = {"low", "medium", "high"}


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def number_at(payload: dict[str, Any], path: str, errors: list[str], label: str) -> float:
    current: Any = payload
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            errors.append(f"{label}: missing `{path}`")
            return 0.0
        current = current[part]
    if not is_number(current):
        errors.append(f"{label}: `{path}` must be a finite number")
        return 0.0
    return float(current)


def string_at(payload: dict[str, Any], path: str, errors: list[str], label: str) -> str:
    current: Any = payload
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            errors.append(f"{label}: missing `{path}`")
            return ""
        current = current[part]
    if not isinstance(current, str) or not current.strip():
        errors.append(f"{label}: `{path}` must be a non-empty string")
        return ""
    return current


def load_category(content_dir: Path, category: str, errors: list[str]) -> dict[str, dict[str, Any]]:
    directory = content_dir / category
    items: dict[str, dict[str, Any]] = {}
    if not directory.exists():
        errors.append(f"missing `{category}` directory")
        return items
    for path in sorted(directory.glob("*.json")):
        try:
            payload = load_json_object(path)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            errors.append(f"{category}/{path.name}: invalid JSON: {error}")
            continue
        item_id = payload.get("id")
        if not isinstance(item_id, str) or not item_id.strip():
            errors.append(f"{category}/{path.name}: missing non-empty id")
            continue
        if item_id in items:
            errors.append(f"{category}/{path.name}: duplicate id `{item_id}`")
        items[item_id] = payload
    return items


def computed_enemy_threat(health: float, move_speed: float, contact_damage_per_second: float) -> float:
    health_factor = max(math.sqrt(max(health, 0.0) / 18.0), 0.4)
    speed_factor = max(move_speed / 60.0, 0.35)
    damage_factor = max(contact_damage_per_second / 4.5, 0.25)
    return health_factor * speed_factor * damage_factor


def pressure_level_for_time(start_second: float) -> str:
    if start_second < 90.0:
        return "early"
    if start_second < 210.0:
        return "mid_low"
    if start_second < 300.0:
        return "boss"
    if start_second < 480.0:
        return "mid_high"
    return "late"


def pressure_budget_allows(level: str, spawn_pressure: float, alive_pressure: float) -> bool:
    limits = {
        "early": (1.2, 45.0),
        "mid_low": (3.2, 85.0),
        "boss": (3.8, 130.0),
        "mid_high": (6.5, 180.0),
        "late": (8.0, 260.0),
    }
    spawn_limit, alive_limit = limits[level]
    return spawn_pressure <= spawn_limit and alive_pressure <= alive_limit


def validate_weapons(weapons: dict[str, dict[str, Any]], errors: list[str], warnings: list[str]) -> list[dict[str, Any]]:
    reviews: list[dict[str, Any]] = []
    for weapon_id, weapon in sorted(weapons.items()):
        local_errors: list[str] = []
        notes: list[str] = []
        damage = number_at(weapon, "base_stats.damage", local_errors, weapon_id)
        cooldown_ms = number_at(weapon, "base_stats.cooldown_ms", local_errors, weapon_id)
        projectile_count = number_at(weapon, "base_stats.projectile_count", local_errors, weapon_id)
        area_radius = number_at(weapon, "base_stats.area_radius", local_errors, weapon_id)
        single_target_budget = number_at(weapon, "balance_budget.single_target_dps", local_errors, weapon_id)
        group_dps = number_at(weapon, "balance_budget.group_dps", local_errors, weapon_id)
        role = string_at(weapon, "balance_budget.role", local_errors, weapon_id)
        performance_cost = string_at(weapon, "balance_budget.performance_cost", local_errors, weapon_id)

        theoretical_dps = damage * projectile_count / max(cooldown_ms / 1000.0, 0.001)
        lower_bound = single_target_budget * 0.65
        upper_bound = single_target_budget * 1.35
        failed = bool(local_errors)

        if theoretical_dps > upper_bound:
            failed = True
            notes.append(
                f"理论单体 DPS {theoretical_dps:.2f} 高于声明预算 {single_target_budget:.2f} 的 1.35 倍上限 {upper_bound:.2f}"
            )
        if theoretical_dps < lower_bound:
            failed = True
            notes.append(
                f"理论单体 DPS {theoretical_dps:.2f} 低于声明预算 {single_target_budget:.2f} 的 0.65 倍下限 {lower_bound:.2f}"
            )
        if group_dps > single_target_budget * 2.5:
            warnings.append(
                f"weapon `{weapon_id}` group DPS budget {group_dps:.2f} is much higher than single-target budget {single_target_budget:.2f}"
            )
            notes.append("群体 DPS 预算显著高于单体预算，需要后续 Bot 仿真确认")
        if performance_cost not in PERFORMANCE_COST_LABELS:
            failed = True
            notes.append(f"performance_cost `{performance_cost}` 非法，应为 low/medium/high")
        if projectile_count > 12:
            failed = True
            notes.append(f"projectile_count {projectile_count:.0f} 超过首版静态性能上限 12")
        if area_radius > 180.0:
            warnings.append(f"weapon `{weapon_id}` area radius {area_radius:.1f} is high")
            notes.append("范围半径较大，后续需要可读性和性能复查")

        if local_errors:
            notes.extend(local_errors)
        if failed:
            errors.append(f"weapon `{weapon_id}` failed static budget: {'; '.join(notes)}")

        reviews.append(
            {
                "id": weapon_id,
                "role": role,
                "theoretical_single_target_dps": round(theoretical_dps, 4),
                "declared_single_target_dps": single_target_budget,
                "declared_group_dps": group_dps,
                "performance_cost": performance_cost,
                "status": "failed" if failed else "ok",
                "notes": notes,
            }
        )
    return reviews


def validate_enemy_like(
    item_id: str,
    payload: dict[str, Any],
    is_boss: bool,
    errors: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    local_errors: list[str] = []
    notes: list[str] = []
    health = number_at(payload, "stats.health", local_errors, item_id)
    move_speed = number_at(payload, "stats.move_speed", local_errors, item_id)
    contact_damage = number_at(payload, "stats.contact_damage_per_second", local_errors, item_id)
    xp_value = number_at(payload, "stats.xp_value", local_errors, item_id)
    computed_threat = computed_enemy_threat(health, move_speed, contact_damage)
    speed_damage_pressure = move_speed * contact_damage / 100.0
    failed = bool(local_errors)

    if is_boss:
        declared_threat = computed_threat
        performance_cost: float | str = 4.0
        if not (450.0 <= health <= 2400.0):
            failed = True
            notes.append(f"Boss HP {health:.1f} 超出首版静态范围 450-2400")
        if not (60.0 <= xp_value <= 160.0):
            failed = True
            notes.append(f"Boss XP {xp_value:.1f} 超出文档建议范围 60-160")
    else:
        declared_threat = number_at(payload, "spawn_budget.threat", local_errors, item_id)
        performance_cost = number_at(payload, "spawn_budget.performance_cost", local_errors, item_id)
        if declared_threat <= 0.0 or not math.isfinite(declared_threat):
            failed = True
            notes.append(f"declared threat {declared_threat:.2f} 非正或非有限")
        if declared_threat > computed_threat * 1.8 or declared_threat < computed_threat * 0.45:
            warnings.append(
                f"enemy `{item_id}` declared threat {declared_threat:.2f} differs from computed threat {computed_threat:.2f}"
            )
            notes.append(f"声明威胁 {declared_threat:.2f} 与计算威胁 {computed_threat:.2f} 差异较大")
        if not (0.5 <= float(performance_cost) <= 5.0):
            failed = True
            notes.append(f"performance_cost {float(performance_cost):.2f} 超出首版静态范围 0.5-5.0")

    if move_speed >= 85.0 and contact_damage >= 6.0:
        failed = True
        notes.append(f"高速 {move_speed:.1f} + 高接触伤害 {contact_damage:.1f} 组合超过首版安全线")
    if speed_damage_pressure > 8.0:
        failed = True
        notes.append(f"speed_damage_pressure {speed_damage_pressure:.2f} 超过首版上限 8.0")

    if local_errors:
        notes.extend(local_errors)
    if failed:
        label = "boss" if is_boss else "enemy"
        errors.append(f"{label} `{item_id}` failed static budget: {'; '.join(notes)}")

    return {
        "id": item_id,
        "threat": declared_threat,
        "computed_threat": round(computed_threat, 4),
        "speed_damage_pressure": round(speed_damage_pressure, 4),
        "performance_cost": performance_cost,
        "status": "failed" if failed else "ok",
        "notes": notes,
    }


def validate_enemies_and_bosses(
    enemies: dict[str, dict[str, Any]],
    bosses: dict[str, dict[str, Any]],
    errors: list[str],
    warnings: list[str],
) -> list[dict[str, Any]]:
    reviews = [
        validate_enemy_like(enemy_id, enemy, False, errors, warnings)
        for enemy_id, enemy in sorted(enemies.items())
    ]
    reviews.extend(
        validate_enemy_like(boss_id, boss, True, errors, warnings)
        for boss_id, boss in sorted(bosses.items())
    )
    return reviews


def weighted_average_threat(
    enemies: dict[str, dict[str, Any]],
    enemy_pool: Any,
    wave_id: str,
    errors: list[str],
) -> float:
    if not isinstance(enemy_pool, list) or not enemy_pool:
        errors.append(f"wave `{wave_id}` segment enemy_pool must be a non-empty list")
        return 0.0
    weighted = 0.0
    total_weight = 0.0
    for entry in enemy_pool:
        if not isinstance(entry, dict):
            errors.append(f"wave `{wave_id}` enemy_pool entry must be an object")
            continue
        enemy_id = entry.get("enemy_id")
        weight = entry.get("weight")
        if not isinstance(enemy_id, str) or enemy_id not in enemies:
            errors.append(f"wave `{wave_id}` references unknown enemy `{enemy_id}`")
            continue
        if not is_number(weight) or float(weight) <= 0.0:
            errors.append(f"wave `{wave_id}` enemy `{enemy_id}` weight must be positive")
            continue
        threat = number_at(enemies[enemy_id], "spawn_budget.threat", errors, enemy_id)
        weighted += threat * float(weight)
        total_weight += float(weight)
    return weighted / total_weight if total_weight > 0.0 else 0.0


def validate_waves(
    waves: dict[str, dict[str, Any]],
    enemies: dict[str, dict[str, Any]],
    errors: list[str],
    warnings: list[str],
) -> list[dict[str, Any]]:
    reviews: list[dict[str, Any]] = []
    for wave_id, wave in sorted(waves.items()):
        notes: list[str] = []
        failed = False
        max_spawn_pressure = 0.0
        max_alive_pressure = 0.0
        max_alive = 0
        segments = wave.get("segments")
        if not isinstance(segments, list) or not segments:
            failed = True
            notes.append("segments must be a non-empty list")
            errors.append(f"wave `{wave_id}` failed static budget: {'; '.join(notes)}")
        else:
            for index, segment in enumerate(segments):
                if not isinstance(segment, dict):
                    failed = True
                    notes.append(f"segments[{index}] must be an object")
                    continue
                local_errors: list[str] = []
                start_second = number_at(segment, "start_second", local_errors, wave_id)
                end_second = number_at(segment, "end_second", local_errors, wave_id)
                spawn_interval_ms = number_at(segment, "spawn_interval_ms", local_errors, wave_id)
                spawn_count = number_at(segment, "spawn_count", local_errors, wave_id)
                segment_max_alive = int(number_at(segment, "max_alive", local_errors, wave_id))
                average_threat = weighted_average_threat(enemies, segment.get("enemy_pool"), wave_id, local_errors)
                if local_errors:
                    failed = True
                    notes.extend(local_errors)
                    continue
                if end_second <= start_second:
                    failed = True
                    notes.append(f"{start_second:.0f}-{end_second:.0f}s segment end must be after start")
                spawn_pressure = spawn_count / max(spawn_interval_ms / 1000.0, 0.001) * average_threat
                alive_pressure = segment_max_alive * average_threat
                max_spawn_pressure = max(max_spawn_pressure, spawn_pressure)
                max_alive_pressure = max(max_alive_pressure, alive_pressure)
                max_alive = max(max_alive, segment_max_alive)
                expected_level = pressure_level_for_time(start_second)
                if not pressure_budget_allows(expected_level, spawn_pressure, alive_pressure):
                    failed = True
                    notes.append(
                        f"{start_second:.0f}-{end_second:.0f}s {expected_level} pressure 超出首版静态预算: spawn {spawn_pressure:.2f}, alive {alive_pressure:.2f}"
                    )

        if max_alive > 140:
            failed = True
            notes.append(f"max_alive {max_alive} 超过首版静态性能上限 140")
        elif max_alive > 105:
            warnings.append(f"wave `{wave_id}` max_alive {max_alive} is near the prototype performance ceiling")
            notes.append("同屏敌人数接近性能风险线，需要 Bot 仿真确认")

        if failed and not any(error.startswith(f"wave `{wave_id}` failed") for error in errors):
            errors.append(f"wave `{wave_id}` failed static budget: {'; '.join(notes)}")

        reviews.append(
            {
                "id": wave_id,
                "max_spawn_pressure": round(max_spawn_pressure, 4),
                "max_alive_pressure": round(max_alive_pressure, 4),
                "max_alive": max_alive,
                "status": "failed" if failed else "ok",
                "notes": notes,
            }
        )
    return reviews


def build_report(content_dir: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    weapons = load_category(content_dir, "weapons", errors)
    enemies = load_category(content_dir, "enemies", errors)
    bosses = load_category(content_dir, "bosses", errors)
    waves = load_category(content_dir, "waves", errors)

    weapon_budgets = validate_weapons(weapons, errors, warnings)
    enemy_budgets = validate_enemies_and_bosses(enemies, bosses, errors, warnings)
    wave_budgets = validate_waves(waves, enemies, errors, warnings)

    return {
        "report_version": 1,
        "source": str(content_dir),
        "decision": "static_balance_budget_valid" if not errors else "static_balance_budget_invalid",
        "weapon_count": len(weapons),
        "enemy_count": len(enemies),
        "boss_count": len(bosses),
        "wave_count": len(waves),
        "weapon_budgets": weapon_budgets,
        "enemy_budgets": enemy_budgets,
        "wave_budgets": wave_budgets,
        "errors": errors,
        "warnings": warnings,
        "limitations": [
            "This validator mirrors first-pass static budget checks only.",
            "It does not run GameCore, Bot simulations, replay regression, performance tests, or human playtests.",
            "A valid static budget report is not sufficient to promote content into accepted_content.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Static Balance Budget Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Decision: `{report['decision']}`",
        f"- Weapons: {report['weapon_count']}",
        f"- Enemies: {report['enemy_count']}",
        f"- Bosses: {report['boss_count']}",
        f"- Waves: {report['wave_count']}",
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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm static balance budgets.")
    parser.add_argument("content_dir", type=Path, help="Content pack directory with weapons/enemies/bosses/waves")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON validation report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown validation summary")
    args = parser.parse_args()

    report = build_report(args.content_dir)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "static_balance_budget_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
