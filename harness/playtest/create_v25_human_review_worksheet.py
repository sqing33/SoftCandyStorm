#!/usr/bin/env python3
"""Create a human-fillable worksheet for v25 design review and playtests."""

from __future__ import annotations

import argparse
from pathlib import Path

from list_v25_human_evidence_todos import build_report as build_todo_report
from run_v25_manual_playtest import CANDIDATE_ID, CONTENT_HASH, RUNS, build_runtime_command, shell_quote


DEFAULT_OUT = Path("harness/reports/2026-06-02_demo_buildcraft_repair_v25_human_review_worksheet_001/worksheet.md")

RATING_FIELDS = [
    "fun_rating",
    "clarity_rating",
    "difficulty_rating",
    "projectile_readability",
    "hit_feedback",
    "xp_pickup_rhythm",
    "boss_spawn_clarity",
    "death_reason_clarity",
]

DESIGN_RATING_FIELDS = [
    "theme_fit",
    "novelty",
    "build_potential",
    "counterplay_clarity",
    "visual_audio_fit",
]


def checkbox(label: str) -> str:
    return f"- [ ] {label}"


def write_design_section(lines: list[str]) -> None:
    lines.extend(
        [
            "## Design Review",
            "",
            "- Draft: `harness/content_review/drafts/2026-06-02_demo_buildcraft_repair_v25_full_pack_design_review_draft.json`",
            "- Content item: `pudding-turret`",
            "- Current gate decision: `needs_more_review`",
            "",
            "### pudding-turret",
            "",
        ]
    )
    for field in DESIGN_RATING_FIELDS:
        lines.append(f"- {field}: ____ / 5")
    lines.extend(
        [
            "- balance_risk: low / medium / high",
            "- decision: pass / revise / reject",
            "- concrete design observation:",
            "",
            "```text",
            "",
            "```",
            "- required changes or acceptance blocker:",
            "",
            "```text",
            "",
            "```",
            "",
            "### Batch Notes",
            "",
            "- reviewer: ____________________",
            "- reviewed_at: YYYY-MM-DD",
            "- summary:",
            "",
            "```text",
            "",
            "```",
            "- batch risks:",
            "",
            "```text",
            "",
            "```",
            "- next actions:",
            "",
            "```text",
            "",
            "```",
            "",
        ]
    )


def write_run_section(lines: list[str], repo_root: Path) -> None:
    lines.extend(
        [
            "## Manual Playtest Runs",
            "",
            "- Draft: `harness/playtest/drafts/2026-06-02_demo_buildcraft_repair_v25_manual_playtest_review_draft.json`",
            "- Human evidence must not use `--demo-input`, `--simulation-speed`, or `--auto-exit-after-report`.",
            "",
        ]
    )
    for run in RUNS:
        command = f"python3 harness/playtest/run_v25_manual_playtest.py {run.run_id}"
        runtime_command = shell_quote(build_runtime_command(run))
        report_exists = (repo_root / run.report_path).exists()
        lines.extend(
            [
                f"### {run.run_id}",
                "",
                f"- skill: `{run.skill}`",
                f"- seed: `{run.seed}`",
                f"- intent: {run.intent}",
                f"- report: `{run.report_path}`",
                f"- report exists: `{report_exists}`",
                f"- launcher: `{command}`",
                f"- runtime command: `{runtime_command}`",
                "",
                "#### Required Observations",
                "",
            ]
        )
        required_observations = {
            "new_001": ["是否理解移动", "是否理解拾取糖晶", "是否理解升级三选一"],
            "new_002": ["是否知道为什么受伤", "如果死亡是否知道主要原因", "XP 节奏是否诱导过度冒险"],
            "new_003": ["前 2 分钟是否至少看到 2-3 次升级机会", "保守玩法是否太无聊", "怪潮压力是否逐步增加"],
            "skilled_001": ["命中反馈是否清楚", "XP 拾取是否顺畅", "升级选择是否有纠结"],
            "skilled_002": ["Boss 出场是否明显", "Boss 威胁方向是否明确", "Boss 战是否拖沓"],
            "skilled_003": ["屏幕压力是否压迫但不烦", "受伤反馈是否及时", "性能体感是否稳定"],
            "build_001": ["projectile 可读性", "单体输出反馈", "远程 Build 是否有明确优势和代价"],
            "build_002": ["受伤反馈", "逃生空间", "容错感"],
            "build_003": ["地面效果可读性", "敌群可读性", "性能体感"],
        }[run.run_id]
        lines.extend(checkbox(item) for item in required_observations)
        lines.extend(["", "#### Ratings", ""])
        for field in RATING_FIELDS:
            lines.append(f"- {field}: ____ / 5")
        lines.extend(
            [
                "- gate_decision: playtest_pass / repair / needs_more_runs",
                "- tags: __________________________________",
                "- concrete moment-to-moment observation:",
                "",
                "```text",
                "",
                "```",
                "- next actions:",
                "",
                "```text",
                "",
                "```",
                "",
            ]
        )


def build_markdown(repo_root: Path) -> str:
    todo_report = build_todo_report(repo_root)
    summary = todo_report["summary"]
    lines = [
        "# v25 Human Review Worksheet",
        "",
        f"- Candidate id: `{CANDIDATE_ID}`",
        f"- Content hash: `{CONTENT_HASH}`",
        f"- Design TODOs: `{summary['design_todo_count']}`",
        f"- Playtest TODOs: `{summary['playtest_todo_count']}`",
        f"- Playtest runs: `{summary['playtest_run_count']}`",
        "",
        "## Rules",
        "",
        checkbox("Keep v25 in generated_candidates until human design review and manual playtest gates pass."),
        checkbox("After filling this worksheet, copy concrete observations into the JSON drafts and run validators."),
        checkbox("Do not replace human observations with automated demo-input evidence."),
        "",
    ]
    write_design_section(lines)
    write_run_section(lines, repo_root)
    lines.extend(
        [
            "## Validation Commands",
            "",
            "```bash",
            "python3 harness/content_review/check_v25_design_review_status.py --allow-incomplete",
            "python3 harness/playtest/check_v25_manual_playtest_status.py --allow-incomplete",
            "python3 harness/playtest/check_v25_candidate_readiness.py --allow-incomplete",
            "python3 harness/playtest/list_v25_human_evidence_todos.py --allow-todos",
            "```",
            "",
            "This worksheet is not acceptance evidence by itself; the JSON drafts remain the source of truth.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a v25 human review worksheet.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    markdown = build_markdown(args.repo_root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(markdown, encoding="utf-8")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
