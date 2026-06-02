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
            "## 设计审查",
            "",
            "- 草稿：`harness/content_review/drafts/2026-06-02_demo_buildcraft_repair_v25_full_pack_design_review_draft.json`",
            "- 内容项：`pudding-turret`",
            "- 当前门禁结论：`needs_more_review`",
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
            "- 具体设计观察：",
            "",
            "```text",
            "",
            "```",
            "- 必要修改或接受阻塞点：",
            "",
            "```text",
            "",
            "```",
            "",
            "### 批次备注",
            "",
            "- reviewer: ____________________",
            "- reviewed_at: YYYY-MM-DD",
            "- 总结：",
            "",
            "```text",
            "",
            "```",
            "- 批次风险：",
            "",
            "```text",
            "",
            "```",
            "- 后续行动：",
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
            "## 人工试玩局",
            "",
            "- 草稿：`harness/playtest/drafts/2026-06-02_demo_buildcraft_repair_v25_manual_playtest_review_draft.json`",
            "- 人工证据不得使用 `--demo-input`、`--simulation-speed` 或 `--auto-exit-after-report`。",
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
                f"- 玩家视角：`{run.skill}`",
                f"- 固定 seed：`{run.seed}`",
                f"- 试玩意图：{run.intent}",
                f"- 报告路径：`{run.report_path}`",
                f"- 本地报告已存在：`{report_exists}`",
                f"- 启动器：`{command}`",
                f"- Runtime 命令：`{runtime_command}`",
                "",
                "#### 必看观察项",
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
        lines.extend(["", "#### 评分", ""])
        for field in RATING_FIELDS:
            lines.append(f"- {field}: ____ / 5")
        lines.extend(
            [
                "- gate_decision: playtest_pass / repair / needs_more_runs",
                "- tags: __________________________________",
                "- 具体局内观察：",
                "",
                "```text",
                "",
                "```",
                "- 后续行动：",
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
        "# v25 人工审查表",
        "",
        f"- 候选 id：`{CANDIDATE_ID}`",
        f"- 内容 hash：`{CONTENT_HASH}`",
        f"- 设计审查 TODO 数：`{summary['design_todo_count']}`",
        f"- 人工试玩 TODO 数：`{summary['playtest_todo_count']}`",
        f"- 人工试玩局数：`{summary['playtest_run_count']}`",
        "",
        "## 规则",
        "",
        checkbox("v25 必须留在 generated_candidates，直到真人设计审查和人工试玩门禁通过。"),
        checkbox("填完这张表后，把具体观察写回 JSON 草稿，并运行对应校验。"),
        checkbox("不要用自动 demo-input 证据替代真人观察。"),
        "",
    ]
    write_design_section(lines)
    write_run_section(lines, repo_root)
    lines.extend(
        [
            "## 校验命令",
            "",
            "```bash",
            "python3 harness/content_review/check_v25_design_review_status.py --allow-incomplete",
            "python3 harness/playtest/check_v25_manual_playtest_status.py --allow-incomplete",
            "python3 harness/playtest/check_v25_candidate_readiness.py --allow-incomplete",
            "python3 harness/playtest/list_v25_human_evidence_todos.py --allow-todos",
            "```",
            "",
            "这张表本身不是接受证据；JSON 草稿仍是事实来源。",
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
