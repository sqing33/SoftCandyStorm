#!/usr/bin/env python3
"""Create a candidate-only repair triage plan for v25 playable content.

This helper turns quick-play, content-tour, and manual-playtest objective
summaries into actionable repair work. It does not run Runtime, fill human
review fields, approve v25, or move candidate content into accepted content.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from audit_v25_playable_content_coverage import build_audit as build_playable_content_coverage_audit
from play_v25_candidate import QUICK_PLAY_PRESETS
from run_v25_content_tour import TOUR_RUNS
from run_v25_manual_playtest import CANDIDATE_ID, CONTENT_DIR, CONTENT_HASH, RUNS
from summarize_v25_content_tour_reports import build_report as build_content_tour_summary
from summarize_v25_manual_playtest_reports import build_report as build_manual_summary
from summarize_v25_quick_play_reports import build_report as build_quick_play_summary


DEFAULT_REPORT = Path(
    "harness/reports/2026-06-02_demo_buildcraft_repair_v25_content_repair_action_plan_001/"
    "content_repair_action_plan.json"
)
DEFAULT_MARKDOWN = Path(
    "harness/reports/2026-06-02_demo_buildcraft_repair_v25_content_repair_action_plan_001/summary.md"
)

PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
DOMAIN_ORDER = {"quick_play": 0, "manual_playtest": 1, "content_tour": 2, "coverage_audit": 3}
RUN_ORDER = {
    "quick_play": {preset.preset_id: index for index, preset in enumerate(QUICK_PLAY_PRESETS)},
    "content_tour": {run.run_id: index for index, run in enumerate(TOUR_RUNS)},
    "manual_playtest": {run.run_id: index for index, run in enumerate(RUNS)},
}


def finite_number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def markdown_escape(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def code(value: Any) -> str:
    text = str(value).strip() if value is not None else ""
    return f"`{markdown_escape(text or '-')}`"


def format_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def priority_sort_key(item: dict[str, Any]) -> tuple[int, int, int, str]:
    domain = str(item.get("domain", ""))
    run_id = str(item.get("run_id", ""))
    return (
        PRIORITY_ORDER.get(str(item.get("priority", "P3")), 99),
        DOMAIN_ORDER.get(domain, 99),
        RUN_ORDER.get(domain, {}).get(run_id, 999),
        str(item.get("id", "")),
    )


def command_for(domain: str, run_id: str) -> str:
    if domain == "quick_play":
        return f"python3 harness/playtest/play_v25_candidate.py {run_id}"
    if domain == "content_tour":
        return f"python3 harness/playtest/run_v25_content_tour.py {run_id}"
    if domain == "manual_playtest":
        return f"python3 harness/playtest/run_v25_manual_playtest.py {run_id}"
    return ""


def source_summary(name: str, summary: dict[str, Any]) -> dict[str, Any]:
    raw = summary.get("summary") if isinstance(summary.get("summary"), dict) else {}
    return {
        "name": name,
        "decision": str(summary.get("decision", "")),
        "existing_report_count": int(raw.get("existing_report_count", 0) or 0),
        "missing_report_count": int(raw.get("missing_report_count", 0) or 0),
        "attention_count": int(raw.get("attention_count", 0) or 0),
    }


def coverage_source_summary(summary: dict[str, Any]) -> dict[str, Any]:
    raw = summary.get("summary") if isinstance(summary.get("summary"), dict) else {}
    return {
        "name": "coverage_audit",
        "decision": str(summary.get("decision", "")),
        "existing_report_count": 0,
        "missing_report_count": 0,
        "attention_count": int(raw.get("action_item_count", 0) or 0),
    }


def coverage_audit_or_skip(repo_root: Path) -> dict[str, Any]:
    if not (repo_root / CONTENT_DIR).exists():
        return {
            "decision": "v25_playable_content_coverage_skipped_missing_content_dir",
            "summary": {
                "action_item_count": 0,
                "priority_counts": {},
                "category_counts": {},
            },
            "action_items": [],
        }
    return build_playable_content_coverage_audit(repo_root)


def missing_quick_play_items(summary: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for preset in summary.get("presets", []):
        if not isinstance(preset, dict) or preset.get("report_exists") is True:
            continue
        preset_id = str(preset.get("preset_id", "unknown"))
        priority = "P0" if preset_id == "default" else "P1"
        items.append(
            {
                "id": f"quick_play_missing_{preset_id}",
                "domain": "quick_play",
                "category": "missing_report",
                "priority": priority,
                "title": f"补跑快速试玩：{preset_id}",
                "run_id": preset_id,
                "character_id": preset.get("character_id", ""),
                "map_id": preset.get("map_id", ""),
                "focus": preset.get("focus", ""),
                "evidence_gap": f"缺少 `{preset.get('report', '')}`",
                "action": "运行对应 quick-play 局，获得一份本地 Runtime 指标报告，再刷新修复计划。",
                "command": command_for("quick_play", preset_id),
                "report": preset.get("report", ""),
                "candidate_only": True,
            }
        )
    return items


def missing_content_tour_items(summary: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for run in summary.get("runs", []):
        if not isinstance(run, dict) or run.get("report_exists") is True:
            continue
        run_id = str(run.get("run_id", "unknown"))
        items.append(
            {
                "id": f"content_tour_missing_{run_id}",
                "domain": "content_tour",
                "category": "missing_report",
                "priority": "P1",
                "title": f"补跑内容巡游：{run_id}",
                "run_id": run_id,
                "character_id": run.get("character_id", ""),
                "map_id": run.get("map_id", ""),
                "focus": run.get("focus", ""),
                "evidence_gap": f"缺少 `{run.get('report', '')}`",
                "action": "运行对应 content-tour 局，覆盖地图、角色和局内内容表面。",
                "command": command_for("content_tour", run_id),
                "report": run.get("report", ""),
                "candidate_only": True,
            }
        )
    return items


def missing_manual_items(summary: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for run in summary.get("runs", []):
        if not isinstance(run, dict) or run.get("report_exists") is True:
            continue
        run_id = str(run.get("run_id", "unknown"))
        items.append(
            {
                "id": f"manual_playtest_missing_{run_id}",
                "domain": "manual_playtest",
                "category": "missing_report",
                "priority": "P0",
                "title": f"补跑人工试玩矩阵：{run_id}",
                "run_id": run_id,
                "skill": run.get("skill", ""),
                "focus": run.get("intent", ""),
                "required_observations": run.get("required_observations", []),
                "evidence_gap": f"缺少 `{run.get('report', '')}`",
                "action": "运行对应人工试玩局，并由真人在草稿中填写具体观察、评分、tags 和 next_actions。",
                "command": command_for("manual_playtest", run_id),
                "report": run.get("report", ""),
                "candidate_only": True,
            }
        )
    return items


def attention_items(summary: dict[str, Any], domain: str, run_key: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    rows = summary.get("presets") if domain == "quick_play" else summary.get("runs")
    if not isinstance(rows, list):
        return items
    for row in rows:
        if not isinstance(row, dict) or row.get("report_exists") is not True:
            continue
        row_id = str(row.get(run_key, "unknown"))
        warnings = [item for item in row.get("attention", []) if isinstance(item, str)]
        errors = [item for item in row.get("errors", []) if isinstance(item, str)]
        if not warnings and not errors:
            continue
        priority = "P0" if errors else "P1"
        items.append(
            {
                "id": f"{domain}_attention_{row_id}",
                "domain": domain,
                "category": "report_attention",
                "priority": priority,
                "title": f"修复或重跑报告：{row_id}",
                "run_id": row_id,
                "focus": row.get("focus", row.get("intent", "")),
                "evidence_gap": "; ".join([*errors, *warnings]),
                "action": "修正报告不匹配问题，或用无自动化旗标的人工可玩命令重跑该局。",
                "command": command_for(domain, row_id),
                "report": row.get("report", ""),
                "candidate_only": True,
            }
        )
    return items


def metric_risk_items(summary: dict[str, Any], domain: str, run_key: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    rows = summary.get("presets") if domain == "quick_play" else summary.get("runs")
    if not isinstance(rows, list):
        return items
    for row in rows:
        if not isinstance(row, dict) or row.get("report_exists") is not True:
            continue
        if row.get("errors"):
            continue
        metrics = row.get("objective_metrics")
        if not isinstance(metrics, dict) or not metrics:
            continue
        row_id = str(row.get(run_key, "unknown"))
        base = {
            "domain": domain,
            "run_id": row_id,
            "focus": row.get("focus", row.get("intent", "")),
            "command": command_for(domain, row_id),
            "report": row.get("report", ""),
            "candidate_only": True,
            "metrics": {
                "terminal_kind": metrics.get("terminal_kind"),
                "duration_seconds": metrics.get("duration_seconds"),
                "level": metrics.get("level"),
                "kills": metrics.get("kills"),
                "damage_taken": metrics.get("damage_taken"),
                "upgrade_choice_count": metrics.get("upgrade_choice_count"),
                "average_fps": metrics.get("average_fps"),
            },
        }
        duration = finite_number(metrics.get("duration_seconds"))
        target_duration = finite_number(metrics.get("target_duration_seconds"))
        level = finite_number(metrics.get("level"))
        kills = finite_number(metrics.get("kills"))
        damage_taken = finite_number(metrics.get("damage_taken"))
        upgrade_count = finite_number(metrics.get("upgrade_choice_count"))
        average_fps = finite_number(metrics.get("average_fps"))
        terminal_kind = str(metrics.get("terminal_kind", ""))
        event_counts = metrics.get("event_counts") if isinstance(metrics.get("event_counts"), dict) else {}

        if terminal_kind and terminal_kind != "victory" and (
            target_duration is None or duration is None or duration < target_duration * 0.9
        ):
            items.append(
                {
                    **base,
                    "id": f"{domain}_risk_survival_{row_id}",
                    "category": "objective_metric_risk",
                    "priority": "P1",
                    "title": f"检查生存节奏：{row_id}",
                    "evidence_gap": f"终局 `{terminal_kind}`，时长 {format_value(duration)} 秒",
                    "action": "回看该局前中期压力、接触伤害、经验投放和 Boss 前铺垫，确认是否需要调波次或敌人预算。",
                }
            )
        if duration is not None and duration >= 300 and level is not None and level < 4:
            items.append(
                {
                    **base,
                    "id": f"{domain}_risk_level_curve_{row_id}",
                    "category": "objective_metric_risk",
                    "priority": "P1",
                    "title": f"检查升级节奏：{row_id}",
                    "evidence_gap": f"运行 {format_value(duration)} 秒后等级仅为 {format_value(level)}",
                    "action": "检查 XP 掉落、拾取半径、前期敌人密度和升级选择反馈，避免玩家长时间没有成长决策。",
                }
            )
        if duration is not None and duration >= 300 and upgrade_count is not None and upgrade_count < 2:
            items.append(
                {
                    **base,
                    "id": f"{domain}_risk_upgrade_choices_{row_id}",
                    "category": "objective_metric_risk",
                    "priority": "P1",
                    "title": f"检查升级选择频率：{row_id}",
                    "evidence_gap": f"升级选择次数仅为 {format_value(upgrade_count)}",
                    "action": "检查升级三选一触发、Build 成型速度和新手可见成长频率。",
                }
            )
        if damage_taken is not None and damage_taken >= 100:
            items.append(
                {
                    **base,
                    "id": f"{domain}_risk_contact_damage_{row_id}",
                    "category": "objective_metric_risk",
                    "priority": "P1",
                    "title": f"检查受伤压力：{row_id}",
                    "evidence_gap": f"受伤累计 {format_value(damage_taken)}",
                    "action": "检查快速怪伤害、地图路线阻挡和防御流救场能力，确认死亡是否可读且可避免。",
                }
            )
        if duration is not None and duration >= 300 and kills is not None and kills < 80:
            items.append(
                {
                    **base,
                    "id": f"{domain}_risk_weapon_feedback_{row_id}",
                    "category": "objective_metric_risk",
                    "priority": "P2",
                    "title": f"检查输出反馈：{row_id}",
                    "evidence_gap": f"击杀数仅为 {format_value(kills)}",
                    "action": "检查初始武器命中可靠性、清群窗口和玩家是否能看懂武器正在产生效果。",
                }
            )
        if duration is not None and duration >= 240 and int(event_counts.get("boss_spawned", 0) or 0) == 0:
            items.append(
                {
                    **base,
                    "id": f"{domain}_risk_boss_timing_{row_id}",
                    "category": "objective_metric_risk",
                    "priority": "P2",
                    "title": f"检查 Boss 触发：{row_id}",
                    "evidence_gap": "Runtime 事件中没有 Boss spawn 记录",
                    "action": "检查地图 wave、Boss 时间点和 report 采集，避免内容巡游没有覆盖 Boss 机制。",
                }
            )
        if average_fps is not None and average_fps < 55:
            items.append(
                {
                    **base,
                    "id": f"{domain}_risk_runtime_readability_{row_id}",
                    "category": "objective_metric_risk",
                    "priority": "P2",
                    "title": f"检查运行表现和可读性：{row_id}",
                    "evidence_gap": f"平均 FPS 为 {format_value(average_fps)}",
                    "action": "检查该地图或构筑的同屏敌人、投射物和特效压力；性能问题会直接影响玩家读局。",
                }
            )
    return items


def coverage_audit_items(coverage_audit: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for item in coverage_audit.get("action_items", []):
        if not isinstance(item, dict):
            continue
        affected = item.get("affected_ids")
        if not isinstance(affected, list):
            affected = []
        affected_ids = [str(value) for value in affected if isinstance(value, str)]
        item_id = str(item.get("id", "unknown"))
        items.append(
            {
                "id": f"coverage_{item_id}",
                "domain": "coverage_audit",
                "category": "content_coverage_gap",
                "priority": str(item.get("priority", "P2")),
                "title": str(item.get("title", item_id)),
                "focus": ", ".join(affected_ids),
                "affected_ids": affected_ids,
                "evidence_gap": str(item.get("evidence", "")),
                "action": str(item.get("action", "")),
                "command": "python3 harness/playtest/audit_v25_playable_content_coverage.py --allow-repair",
                "report": "harness/reports/2026-06-02_demo_buildcraft_repair_v25_playable_content_coverage_001/playable_content_coverage.json",
                "candidate_only": True,
            }
        )
    return items


def build_action_items(
    quick_summary: dict[str, Any],
    tour_summary: dict[str, Any],
    manual_summary: dict[str, Any],
    coverage_audit: dict[str, Any],
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    items.extend(missing_quick_play_items(quick_summary))
    items.extend(missing_content_tour_items(tour_summary))
    items.extend(missing_manual_items(manual_summary))
    items.extend(attention_items(quick_summary, "quick_play", "preset_id"))
    items.extend(attention_items(tour_summary, "content_tour", "run_id"))
    items.extend(attention_items(manual_summary, "manual_playtest", "run_id"))
    items.extend(metric_risk_items(quick_summary, "quick_play", "preset_id"))
    items.extend(metric_risk_items(tour_summary, "content_tour", "run_id"))
    items.extend(metric_risk_items(manual_summary, "manual_playtest", "run_id"))
    items.extend(coverage_audit_items(coverage_audit))
    items.sort(key=priority_sort_key)
    return items


def plan_decision(source_summaries: list[dict[str, Any]], action_items: list[dict[str, Any]]) -> str:
    total_existing = sum(source["existing_report_count"] for source in source_summaries)
    if total_existing == 0:
        return "v25_content_repair_action_plan_needs_playtest_reports"
    if any(
        item["category"] in {"report_attention", "objective_metric_risk", "content_coverage_gap"}
        for item in action_items
    ):
        return "v25_content_repair_action_plan_needs_repair_triage"
    if any(item["category"] == "missing_report" for item in action_items):
        return "v25_content_repair_action_plan_has_remaining_coverage"
    return "v25_content_repair_action_plan_ready_for_human_review"


def next_commands(action_items: list[dict[str, Any]]) -> list[str]:
    commands: list[str] = []
    for item in action_items:
        command = item.get("command")
        if isinstance(command, str) and command and command not in commands:
            commands.append(command)
        if len(commands) >= 5:
            break
    for command in [
        "python3 harness/playtest/audit_v25_playable_content_coverage.py --allow-repair",
        "python3 harness/playtest/summarize_v25_quick_play_reports.py --allow-incomplete",
        "python3 harness/playtest/summarize_v25_content_tour_reports.py --allow-incomplete",
        "python3 harness/playtest/summarize_v25_manual_playtest_reports.py --allow-incomplete",
        "python3 harness/playtest/create_v25_content_repair_action_plan.py",
    ]:
        if command not in commands:
            commands.append(command)
    return commands


def build_plan(repo_root: Path) -> dict[str, Any]:
    quick_summary = build_quick_play_summary(repo_root)
    tour_summary = build_content_tour_summary(repo_root)
    manual_summary = build_manual_summary(repo_root)
    coverage_audit = coverage_audit_or_skip(repo_root)
    sources = [
        source_summary("quick_play", quick_summary),
        source_summary("content_tour", tour_summary),
        source_summary("manual_playtest", manual_summary),
        coverage_source_summary(coverage_audit),
    ]
    action_items = build_action_items(quick_summary, tour_summary, manual_summary, coverage_audit)
    category_counts: dict[str, int] = {}
    priority_counts: dict[str, int] = {}
    domain_counts: dict[str, int] = {}
    for item in action_items:
        category_counts[item["category"]] = category_counts.get(item["category"], 0) + 1
        priority_counts[item["priority"]] = priority_counts.get(item["priority"], 0) + 1
        domain_counts[item["domain"]] = domain_counts.get(item["domain"], 0) + 1

    return {
        "report_version": 1,
        "candidate_id": CANDIDATE_ID,
        "content_hash": CONTENT_HASH,
        "decision": plan_decision(sources, action_items),
        "source_summaries": sources,
        "summary": {
            "action_item_count": len(action_items),
            "missing_report_count": category_counts.get("missing_report", 0),
            "report_attention_count": category_counts.get("report_attention", 0),
            "objective_metric_risk_count": category_counts.get("objective_metric_risk", 0),
            "content_coverage_gap_count": category_counts.get("content_coverage_gap", 0),
            "priority_counts": priority_counts,
            "domain_counts": domain_counts,
        },
        "action_items": action_items,
        "next_commands": next_commands(action_items),
        "limitations": [
            "这份计划只整理 v25 候选内容的试玩修复线索，不批准、不接受、不晋级内容。",
            "缺失报告、客观指标和自动 attention 只能告诉我们该看哪里，不能替代真人乐趣、清晰度和再来一局冲动判断。",
            "v25 仍必须通过设计审查、9 局人工试玩、最终接受和 lockfile 后，才能离开候选池。",
            "AI/RL 训练线不在本计划范围内。",
        ],
    }


def write_markdown(plan: dict[str, Any], path: Path) -> None:
    summary = plan["summary"]
    lines = [
        "# v25 内容修复行动计划",
        "",
        f"- Candidate id: `{plan['candidate_id']}`",
        f"- Content hash: `{plan['content_hash']}`",
        f"- Decision: `{plan['decision']}`",
        f"- Action items: `{summary['action_item_count']}`",
        f"- Missing reports: `{summary['missing_report_count']}`",
        f"- Report attention: `{summary['report_attention_count']}`",
        f"- Objective metric risks: `{summary['objective_metric_risk_count']}`",
        f"- Content coverage gaps: `{summary['content_coverage_gap_count']}`",
        "",
        "## 来源摘要",
        "",
        "| Source | Decision | Existing | Missing | Attention |",
        "|---|---|---:|---:|---:|",
    ]
    for source in plan["source_summaries"]:
        lines.append(
            f"| `{source['name']}` | `{source['decision']}` | "
            f"{source['existing_report_count']} | {source['missing_report_count']} | {source['attention_count']} |"
        )

    lines.extend(["", "## 优先修复项", ""])
    if plan["action_items"]:
        lines.extend(
            [
                "| Priority | Domain | Category | Item | Focus | Action | Command |",
                "|---|---|---|---|---|---|---|",
            ]
        )
        for item in plan["action_items"]:
            lines.append(
                "| "
                + " | ".join(
                    [
                        code(item["priority"]),
                        code(item["domain"]),
                        code(item["category"]),
                        code(item["id"]),
                        markdown_escape(item.get("focus", "")),
                        markdown_escape(item.get("action", "")),
                        code(item.get("command", "")),
                    ]
                )
                + " |"
            )
    else:
        lines.append("- 当前没有由客观摘要生成的修复项；下一步应由真人填写具体试玩观察。")

    lines.extend(["", "## 下一组命令", ""])
    lines.extend(f"- `{markdown_escape(command)}`" for command in plan["next_commands"])
    lines.extend(["", "## 限制", ""])
    lines.extend(f"- {item}" for item in plan["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a v25 candidate-only playable-content repair action plan.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()

    plan = build_plan(args.repo_root)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(plan, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(plan, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
