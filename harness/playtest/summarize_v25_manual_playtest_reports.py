#!/usr/bin/env python3
"""Summarize objective Runtime report metrics for v25 manual playtests."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from run_v25_manual_playtest import CANDIDATE_ID, CONTENT_DIR, CONTENT_HASH, RUNS


DEFAULT_REPORT = Path(
    "harness/reports/2026-06-02_demo_buildcraft_repair_v25_manual_report_summary_001/manual_report_summary.json"
)
DEFAULT_MARKDOWN = Path("harness/reports/2026-06-02_demo_buildcraft_repair_v25_manual_report_summary_001/summary.md")
DEFAULT_DRAFT = Path("harness/playtest/drafts/2026-06-02_demo_buildcraft_repair_v25_manual_playtest_review_draft.json")


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def finite_number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def draft_required_observations(repo_root: Path, draft_path: Path) -> dict[str, list[str]]:
    resolved = repo_root / draft_path
    if not resolved.exists():
        return {}
    try:
        draft = load_json_object(resolved)
    except (OSError, ValueError, json.JSONDecodeError):
        return {}
    observations: dict[str, list[str]] = {}
    runs = draft.get("runs")
    if not isinstance(runs, list):
        return observations
    for run in runs:
        if not isinstance(run, dict) or not isinstance(run.get("run_id"), str):
            continue
        raw_items = run.get("required_observations")
        observations[run["run_id"]] = [item for item in raw_items if isinstance(item, str)] if isinstance(raw_items, list) else []
    return observations


def content_dir_matches(raw_content_dir: Any) -> bool:
    if not isinstance(raw_content_dir, str) or not raw_content_dir:
        return False
    normalized = raw_content_dir.replace("\\", "/")
    expected = CONTENT_DIR.as_posix()
    return normalized == expected or normalized.endswith(f"/{expected}")


def objective_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    final_metrics = payload.get("final_metrics") if isinstance(payload.get("final_metrics"), dict) else {}
    terminal = final_metrics.get("terminal") if isinstance(final_metrics.get("terminal"), dict) else {}
    frame_metrics = payload.get("frame_metrics") if isinstance(payload.get("frame_metrics"), dict) else {}
    event_counts = payload.get("event_counts") if isinstance(payload.get("event_counts"), dict) else {}
    run_config = payload.get("run_config") if isinstance(payload.get("run_config"), dict) else {}
    samples = payload.get("samples") if isinstance(payload.get("samples"), list) else []
    upgrade_choices = final_metrics.get("upgrade_choices")
    if not isinstance(upgrade_choices, list):
        upgrade_choices = []

    return {
        "input_mode": payload.get("input_mode"),
        "simulation_speed": payload.get("simulation_speed"),
        "auto_exit_after_report": payload.get("auto_exit_after_report"),
        "player_skill": payload.get("player_skill"),
        "seed": final_metrics.get("seed", run_config.get("seed")),
        "map_id": run_config.get("map_id"),
        "character_id": run_config.get("character_id"),
        "target_duration_seconds": run_config.get("duration_seconds"),
        "duration_seconds": final_metrics.get("duration_seconds"),
        "terminal_kind": terminal.get("kind"),
        "terminal_reason": terminal.get("reason"),
        "terminal_time_seconds": terminal.get("time_seconds"),
        "kills": final_metrics.get("kills"),
        "level": final_metrics.get("level"),
        "xp_collected": final_metrics.get("xp_collected"),
        "xp_dropped": final_metrics.get("xp_dropped"),
        "damage_taken": final_metrics.get("damage_taken"),
        "max_enemy_count": final_metrics.get("max_enemy_count"),
        "max_projectile_count": final_metrics.get("max_projectile_count"),
        "upgrade_choice_count": len(upgrade_choices),
        "upgrade_choices": upgrade_choices,
        "average_fps": frame_metrics.get("average_fps"),
        "slow_frame_count_30fps": frame_metrics.get("slow_frame_count_30fps"),
        "frame_count": frame_metrics.get("frame_count"),
        "sample_count": len(samples),
        "event_counts": {
            "boss_spawned": event_counts.get("boss_spawned", 0),
            "player_damaged": event_counts.get("player_damaged", 0),
            "xp_collected": event_counts.get("xp_collected", 0),
            "level_up": event_counts.get("level_up", 0),
            "upgrade_offered": event_counts.get("upgrade_offered", 0),
            "upgrade_chosen": event_counts.get("upgrade_chosen", 0),
            "run_ended": event_counts.get("run_ended", 0),
        },
    }


def automation_attention(metrics: dict[str, Any]) -> list[str]:
    attention: list[str] = []
    if metrics.get("input_mode") == "demo":
        attention.append("input_mode is demo; this cannot be used as human playtest evidence")
    simulation_speed = finite_number(metrics.get("simulation_speed"))
    if simulation_speed is not None and not math.isclose(simulation_speed, 1.0):
        attention.append(f"simulation_speed is {simulation_speed:g}; human evidence must use normal speed")
    if metrics.get("auto_exit_after_report") is True:
        attention.append("auto_exit_after_report is true; human evidence must not use auto-exit")
    return attention


def summarize_run(repo_root: Path, run, required_observations: list[str]) -> dict[str, Any]:
    report_path = repo_root / run.report_path
    if not report_path.exists():
        return {
            "run_id": run.run_id,
            "skill": run.skill,
            "seed": run.seed,
            "intent": run.intent,
            "report": str(run.report_path),
            "report_exists": False,
            "required_observations": required_observations,
            "attention": [],
            "errors": [],
            "objective_metrics": {},
        }

    errors: list[str] = []
    attention: list[str] = []
    try:
        payload = load_json_object(report_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {
            "run_id": run.run_id,
            "skill": run.skill,
            "seed": run.seed,
            "intent": run.intent,
            "report": str(run.report_path),
            "report_exists": True,
            "required_observations": required_observations,
            "attention": [f"report could not be parsed: {exc}"],
            "errors": [f"invalid report JSON: {exc}"],
            "objective_metrics": {},
        }

    metrics = objective_metrics(payload)
    if metrics.get("seed") != run.seed:
        errors.append(f"seed mismatch: expected {run.seed}, got {metrics.get('seed')}")
    if metrics.get("player_skill") != run.skill:
        errors.append(f"player_skill mismatch: expected {run.skill}, got {metrics.get('player_skill')}")
    if not content_dir_matches(payload.get("content_dir")):
        errors.append(f"content_dir mismatch: expected {CONTENT_DIR}, got {payload.get('content_dir')}")
    attention.extend(automation_attention(metrics))

    return {
        "run_id": run.run_id,
        "skill": run.skill,
        "seed": run.seed,
        "intent": run.intent,
        "report": str(run.report_path),
        "report_exists": True,
        "required_observations": required_observations,
        "attention": attention,
        "errors": errors,
        "objective_metrics": metrics,
    }


def build_report(repo_root: Path, draft_path: Path = DEFAULT_DRAFT) -> dict[str, Any]:
    required_observations = draft_required_observations(repo_root, draft_path)
    runs = [
        summarize_run(repo_root, run, required_observations.get(run.run_id, []))
        for run in RUNS
    ]
    existing_report_count = sum(1 for run in runs if run["report_exists"])
    missing_reports = [run["report"] for run in runs if not run["report_exists"]]
    attention_items = [
        f"{run['run_id']}: {item}" for run in runs for item in [*run["attention"], *run["errors"]]
    ]
    if attention_items:
        decision = "manual_report_summary_needs_attention"
    elif existing_report_count == 0:
        decision = "manual_report_summary_no_reports"
    elif existing_report_count < len(RUNS):
        decision = "manual_report_summary_partial"
    else:
        decision = "manual_report_summary_all_reports"

    return {
        "report_version": 1,
        "candidate_id": CANDIDATE_ID,
        "content_hash": CONTENT_HASH,
        "draft": str(draft_path),
        "decision": decision,
        "summary": {
            "required_run_count": len(RUNS),
            "existing_report_count": existing_report_count,
            "missing_report_count": len(missing_reports),
            "attention_count": len(attention_items),
        },
        "missing_reports": missing_reports,
        "attention_items": attention_items,
        "runs": runs,
        "next_actions": [
            "用 `python3 harness/playtest/run_v25_manual_playtest.py --next` 继续运行缺失的人工试玩局。",
            "这份客观摘要只能作为填写参考；评分、notes、tags 和 next_actions 必须来自真人观察。",
            "9 份报告和真人填写后的 JSON 草稿都准备好后，再运行 `check_v25_manual_playtest_status.py` 和 strict validation。",
        ],
        "limitations": [
            "本工具只汇总 Runtime report 中的客观指标。",
            "它不判断乐趣、清晰度、可读性、死亡原因或是否接受候选。",
            "使用 demo input、simulation speed 或 auto-exit 生成的报告会被标记，且不得作为人工证据。",
        ],
    }


def format_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def write_markdown(report: dict[str, Any], path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# v25 人工试玩报告客观摘要",
        "",
        f"- Candidate id: `{report['candidate_id']}`",
        f"- Content hash: `{report['content_hash']}`",
        f"- Draft: `{report['draft']}`",
        f"- Decision: `{report['decision']}`",
        f"- Reports: `{summary['existing_report_count']}` / `{summary['required_run_count']}`",
        f"- Attention items: `{summary['attention_count']}`",
        "",
        "## 运行指标",
        "",
        "| Run | Report | Terminal | Time | Level | Kills | Damage Taken | Upgrades | Avg FPS | Attention |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for run in report["runs"]:
        metrics = run["objective_metrics"]
        lines.append(
            f"| `{run['run_id']}` | `{run['report_exists']}` | "
            f"`{format_value(metrics.get('terminal_kind'))}` | "
            f"{format_value(metrics.get('duration_seconds'))} | "
            f"{format_value(metrics.get('level'))} | "
            f"{format_value(metrics.get('kills'))} | "
            f"{format_value(metrics.get('damage_taken'))} | "
            f"{format_value(metrics.get('upgrade_choice_count'))} | "
            f"{format_value(metrics.get('average_fps'))} | "
            f"`{len(run['attention']) + len(run['errors'])}` |"
        )

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

    lines.extend(
        [
            "",
            "## 填写提示",
            "",
            "- 这份摘要只能帮真人回忆客观局面，不能替代 `fun_rating`、`clarity_rating`、可读性、死亡原因或是否想再来一局的判断。",
            "- 若某局出现 `demo`、加速或 auto-exit 标记，请重新用人工 launcher 跑该局。",
            "- 填写 JSON 草稿时，优先写具体瞬间，例如“第 3 次升级时远程投射物反馈不够明显”。",
            "",
            "## 后续行动",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["next_actions"])
    lines.extend(["", "## 限制", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize objective v25 manual playtest Runtime reports.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--draft", type=Path, default=DEFAULT_DRAFT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--allow-incomplete", action="store_true")
    args = parser.parse_args()

    report = build_report(args.repo_root, args.draft)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))

    if report["decision"] in {"manual_report_summary_partial", "manual_report_summary_all_reports"}:
        return 0
    if args.allow_incomplete and report["decision"] == "manual_report_summary_no_reports":
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
