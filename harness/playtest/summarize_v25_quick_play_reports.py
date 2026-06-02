#!/usr/bin/env python3
"""Summarize objective Runtime metrics for v25 quick-play sessions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from play_v25_candidate import QUICK_PLAY_PRESETS
from run_v25_manual_playtest import CANDIDATE_ID, CONTENT_DIR, CONTENT_HASH
from summarize_v25_manual_playtest_reports import (
    automation_attention,
    content_dir_matches,
    format_value,
    load_json_object,
    objective_metrics,
)


DEFAULT_REPORT = Path(
    "harness/reports/2026-06-02_demo_buildcraft_repair_v25_quick_play_summary_001/quick_play_summary.json"
)
DEFAULT_MARKDOWN = Path("harness/reports/2026-06-02_demo_buildcraft_repair_v25_quick_play_summary_001/summary.md")


def summarize_preset(repo_root: Path, preset) -> dict[str, Any]:
    report_path = repo_root / preset.report_path
    base = {
        "preset_id": preset.preset_id,
        "title": preset.title,
        "character_id": preset.character_id,
        "map_id": preset.map_id,
        "seed": preset.seed,
        "focus": preset.focus,
        "report": str(preset.report_path),
    }
    if not report_path.exists():
        return {
            **base,
            "report_exists": False,
            "attention": [],
            "errors": [],
            "objective_metrics": {},
        }

    try:
        payload = load_json_object(report_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {
            **base,
            "report_exists": True,
            "attention": [f"report could not be parsed: {exc}"],
            "errors": [f"invalid report JSON: {exc}"],
            "objective_metrics": {},
        }

    metrics = objective_metrics(payload)
    errors: list[str] = []
    if metrics.get("seed") != preset.seed:
        errors.append(f"seed mismatch: expected {preset.seed}, got {metrics.get('seed')}")
    if metrics.get("player_skill") != "quickplay":
        errors.append(f"player_skill mismatch: expected quickplay, got {metrics.get('player_skill')}")
    if metrics.get("character_id") != preset.character_id:
        errors.append(f"character_id mismatch: expected {preset.character_id}, got {metrics.get('character_id')}")
    if metrics.get("map_id") != preset.map_id:
        errors.append(f"map_id mismatch: expected {preset.map_id}, got {metrics.get('map_id')}")
    if not content_dir_matches(payload.get("content_dir")):
        errors.append(f"content_dir mismatch: expected {CONTENT_DIR}, got {payload.get('content_dir')}")

    return {
        **base,
        "report_exists": True,
        "attention": automation_attention(metrics),
        "errors": errors,
        "objective_metrics": metrics,
    }


def build_report(repo_root: Path) -> dict[str, Any]:
    presets = [summarize_preset(repo_root, preset) for preset in QUICK_PLAY_PRESETS]
    existing_report_count = sum(1 for preset in presets if preset["report_exists"])
    missing_reports = [preset["report"] for preset in presets if not preset["report_exists"]]
    attention_items = [
        f"{preset['preset_id']}: {item}"
        for preset in presets
        for item in [*preset["attention"], *preset["errors"]]
    ]
    if attention_items:
        decision = "quick_play_summary_needs_attention"
    elif existing_report_count == 0:
        decision = "quick_play_summary_no_reports"
    elif existing_report_count < len(QUICK_PLAY_PRESETS):
        decision = "quick_play_summary_partial"
    else:
        decision = "quick_play_summary_all_reports"

    return {
        "report_version": 1,
        "candidate_id": CANDIDATE_ID,
        "content_hash": CONTENT_HASH,
        "decision": decision,
        "summary": {
            "preset_count": len(QUICK_PLAY_PRESETS),
            "existing_report_count": existing_report_count,
            "missing_report_count": len(missing_reports),
            "attention_count": len(attention_items),
        },
        "missing_reports": missing_reports,
        "attention_items": attention_items,
        "presets": presets,
        "next_actions": [
            "用 `python3 harness/playtest/play_v25_candidate.py` 运行默认新手局，或用 `--list` 选择其它 quick-play 预设。",
            "根据 quick-play 客观指标和真人感受，整理默认体验、构筑引导、地图节奏、Boss 可读性或性能修复项。",
            "quick-play 只帮助快速试玩和记录；v25 是否接受仍必须走 9 局人工试玩、设计审查、最终接受和 lockfile 门禁。",
        ],
        "limitations": [
            "本工具只汇总可观测 Runtime 指标，不判断乐趣、清晰度或内容是否达标。",
            "这些 quick-play 报告是便利试玩记录，不计入 9 局人工 acceptance 证据。",
            "使用 demo input、simulation speed 或 auto-exit 生成的报告会被标记，不能作为真人试玩辅助证据。",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# v25 快速试玩客观摘要",
        "",
        f"- Candidate id: `{report['candidate_id']}`",
        f"- Content hash: `{report['content_hash']}`",
        f"- Decision: `{report['decision']}`",
        f"- Reports: `{summary['existing_report_count']}` / `{summary['preset_count']}`",
        f"- Attention items: `{summary['attention_count']}`",
        "",
        "## 快速试玩指标",
        "",
        "| Preset | Character | Map | Report | Terminal | Time | Level | Kills | Damage Taken | Upgrades | Avg FPS | Attention |",
        "|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for preset in report["presets"]:
        metrics = preset["objective_metrics"]
        lines.append(
            f"| `{preset['preset_id']}` | `{preset['character_id']}` | `{preset['map_id']}` | "
            f"`{preset['report_exists']}` | "
            f"`{format_value(metrics.get('terminal_kind'))}` | "
            f"{format_value(metrics.get('duration_seconds'))} | "
            f"{format_value(metrics.get('level'))} | "
            f"{format_value(metrics.get('kills'))} | "
            f"{format_value(metrics.get('damage_taken'))} | "
            f"{format_value(metrics.get('upgrade_choice_count'))} | "
            f"{format_value(metrics.get('average_fps'))} | "
            f"{len(preset['attention']) + len(preset['errors'])} |"
        )

    lines.extend(["", "## 试玩重点", ""])
    for preset in report["presets"]:
        lines.append(f"- `{preset['preset_id']}`: {preset['focus']}")

    lines.extend(["", "## 缺失报告", ""])
    if report["missing_reports"]:
        lines.extend(f"- `{item}`" for item in report["missing_reports"])
    else:
        lines.append("- None")

    lines.extend(["", "## 需要注意", ""])
    if report["attention_items"]:
        lines.extend(f"- {item}" for item in report["attention_items"])
    else:
        lines.append("- 无")

    lines.extend(["", "## 后续行动", ""])
    lines.extend(f"- {item}" for item in report["next_actions"])
    lines.extend(["", "## 限制", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize objective v25 quick-play Runtime reports.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--allow-incomplete", action="store_true")
    args = parser.parse_args()

    report = build_report(args.repo_root)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))

    if report["decision"] in {"quick_play_summary_partial", "quick_play_summary_all_reports"}:
        return 0
    if args.allow_incomplete and report["decision"] == "quick_play_summary_no_reports":
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
