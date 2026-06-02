#!/usr/bin/env python3
"""Summarize objective Runtime metrics for optional v25 content-tour runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from run_v25_content_tour import TOUR_RUNS
from run_v25_manual_playtest import CANDIDATE_ID, CONTENT_DIR, CONTENT_HASH
from summarize_v25_manual_playtest_reports import (
    automation_attention,
    content_dir_matches,
    format_value,
    load_json_object,
    objective_metrics,
)


DEFAULT_REPORT = Path(
    "harness/reports/2026-06-02_demo_buildcraft_repair_v25_content_tour_summary_001/content_tour_summary.json"
)
DEFAULT_MARKDOWN = Path("harness/reports/2026-06-02_demo_buildcraft_repair_v25_content_tour_summary_001/summary.md")


def summarize_run(repo_root: Path, run) -> dict[str, Any]:
    report_path = repo_root / run.report_path
    base = {
        "run_id": run.run_id,
        "character_id": run.character_id,
        "map_id": run.map_id,
        "seed": run.seed,
        "focus": run.focus,
        "report": str(run.report_path),
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
    if metrics.get("seed") != run.seed:
        errors.append(f"seed mismatch: expected {run.seed}, got {metrics.get('seed')}")
    if metrics.get("player_skill") != "tour":
        errors.append(f"player_skill mismatch: expected tour, got {metrics.get('player_skill')}")
    if metrics.get("character_id") != run.character_id:
        errors.append(f"character_id mismatch: expected {run.character_id}, got {metrics.get('character_id')}")
    if metrics.get("map_id") != run.map_id:
        errors.append(f"map_id mismatch: expected {run.map_id}, got {metrics.get('map_id')}")
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
    runs = [summarize_run(repo_root, run) for run in TOUR_RUNS]
    existing_report_count = sum(1 for run in runs if run["report_exists"])
    missing_reports = [run["report"] for run in runs if not run["report_exists"]]
    attention_items = [
        f"{run['run_id']}: {item}" for run in runs for item in [*run["attention"], *run["errors"]]
    ]
    if attention_items:
        decision = "content_tour_summary_needs_attention"
    elif existing_report_count == 0:
        decision = "content_tour_summary_no_reports"
    elif existing_report_count < len(TOUR_RUNS):
        decision = "content_tour_summary_partial"
    else:
        decision = "content_tour_summary_all_reports"

    return {
        "report_version": 1,
        "candidate_id": CANDIDATE_ID,
        "content_hash": CONTENT_HASH,
        "decision": decision,
        "summary": {
            "tour_run_count": len(TOUR_RUNS),
            "existing_report_count": existing_report_count,
            "missing_report_count": len(missing_reports),
            "attention_count": len(attention_items),
        },
        "missing_reports": missing_reports,
        "attention_items": attention_items,
        "runs": runs,
        "next_actions": [
            "用 `python3 harness/playtest/run_v25_content_tour.py --next` 继续运行缺失的内容巡游局。",
            "根据地图 / 角色表里的客观指标和真人感受，整理具体内容修复项：节奏、怪潮、构筑引导、Boss 可读性或性能。",
            "内容巡游只帮助发现问题；v25 是否接受仍必须走 9 局人工试玩、设计审查、最终接受和 lockfile 门禁。",
        ],
        "limitations": [
            "本工具只汇总可观测 Runtime 指标，不判断乐趣、清晰度或内容是否达标。",
            "这些 content-tour 报告是可选巡游记录，不计入 9 局人工 acceptance 证据。",
            "使用 demo input、simulation speed 或 auto-exit 生成的报告会被标记，不能作为真人试玩辅助证据。",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# v25 内容巡游客观摘要",
        "",
        f"- Candidate id: `{report['candidate_id']}`",
        f"- Content hash: `{report['content_hash']}`",
        f"- Decision: `{report['decision']}`",
        f"- Reports: `{summary['existing_report_count']}` / `{summary['tour_run_count']}`",
        f"- Attention items: `{summary['attention_count']}`",
        "",
        "## 巡游指标",
        "",
        "| Run | Character | Map | Report | Terminal | Time | Level | Kills | Damage Taken | Upgrades | Avg FPS | Attention |",
        "|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for run in report["runs"]:
        metrics = run["objective_metrics"]
        lines.append(
            f"| `{run['run_id']}` | `{run['character_id']}` | `{run['map_id']}` | "
            f"`{run['report_exists']}` | "
            f"`{format_value(metrics.get('terminal_kind'))}` | "
            f"{format_value(metrics.get('duration_seconds'))} | "
            f"{format_value(metrics.get('level'))} | "
            f"{format_value(metrics.get('kills'))} | "
            f"{format_value(metrics.get('damage_taken'))} | "
            f"{format_value(metrics.get('upgrade_choice_count'))} | "
            f"{format_value(metrics.get('average_fps'))} | "
            f"{len(run['attention']) + len(run['errors'])} |"
        )

    lines.extend(["", "## 巡游重点", ""])
    for run in report["runs"]:
        lines.append(f"- `{run['run_id']}`: {run['focus']}")

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
    parser = argparse.ArgumentParser(description="Summarize objective v25 content-tour Runtime reports.")
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

    if report["decision"] in {"content_tour_summary_partial", "content_tour_summary_all_reports"}:
        return 0
    if args.allow_incomplete and report["decision"] == "content_tour_summary_no_reports":
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
