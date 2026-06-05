#!/usr/bin/env python3
"""Create a human-fillable worksheet for the current candidate."""

from __future__ import annotations

import argparse
from pathlib import Path

from check_current_manual_playtest_status import build_report as build_manual_status_report
from create_current_manual_playtest_review_draft import DEFAULT_OUT as DEFAULT_PLAYTEST_DRAFT
from current_candidate import CANDIDATE_ID, CANDIDATE_LABEL, CONTENT_HASH, MANUAL_PLAYTEST_RUNS, shell_quote
from run_current_manual_playtest import build_manual_playtest_command


DEFAULT_OUT = Path("harness/reports/2026-06-05_demo_buildcraft_repair_v61_human_review_worksheet_001/worksheet.md")
DESIGN_DRAFT = Path("harness/content_review/drafts/2026-06-05_demo_buildcraft_repair_v61_full_pack_design_review_draft.json")
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
            f"- 草稿：`{DESIGN_DRAFT}`",
            "- 内容项：`route-memory-caramel-ring`",
            "- 当前门禁结论：`draft_todo`",
            "",
            "### route-memory-caramel-ring",
            "",
        ]
    )
    for field in DESIGN_RATING_FIELDS:
        lines.append(f"- {field}: ____ / 5")
    lines.extend(
        [
            "- balance_risk: low / medium / high",
            "- decision: pass / revise / reject",
            "- 重点观察：212-232 秒焦糖旧路环印是否能提示玩家换线，同时不让新手觉得突然不公平。",
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
        ]
    )


def write_manual_section(lines: list[str], repo_root: Path) -> None:
    lines.extend(
        [
            "## 人工试玩局",
            "",
            f"- 草稿：`{DEFAULT_PLAYTEST_DRAFT}`",
            "- 人工证据不得使用 `--demo-input`、`--simulation-speed` 或 `--auto-exit-after-report`。",
            "- 6 局覆盖首发 5 个角色和 6 张地图；每局报告只是辅助，评分和结论必须由真人填写。",
            "",
        ]
    )
    for run in MANUAL_PLAYTEST_RUNS:
        command = f"python3 harness/playtest/run_current_manual_playtest.py {run.run_id}"
        runtime_command = shell_quote(build_manual_playtest_command(run))
        report_exists = (repo_root / run.report_path).exists()
        lines.extend(
            [
                f"### {run.run_id}",
                "",
                f"- 玩家视角：`{run.skill}`",
                f"- 角色：`{run.character_id}`",
                f"- 地图：`{run.map_id}`",
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
        lines.extend(checkbox(item) for item in run.required_observations)
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
    manual_status = build_manual_status_report(repo_root)
    summary = manual_status["summary"]
    lines = [
        f"# {CANDIDATE_LABEL} 人工审查表",
        "",
        f"- 候选 id：`{CANDIDATE_ID}`",
        f"- 内容 hash：`{CONTENT_HASH}`",
        f"- 人工试玩报告：`{summary['existing_report_count']}` / `{summary['required_run_count']}`",
        f"- 人工试玩草稿仍有 TODO：`{summary['draft_has_todo']}`",
        "",
        "## 规则",
        "",
        checkbox("当前候选必须留在 generated_candidates，直到真人设计审查和人工试玩门禁通过。"),
        checkbox("填完这张表后，把具体观察写回 JSON 草稿，并运行对应校验。"),
        checkbox("不要用自动 demo-input、加速或 auto-exit 证据替代真人观察。"),
        checkbox("Runtime GUI 当前环境如遇 GPU 不可用，只能记录阻塞，不能当作内容失败或人工试玩通过。"),
        "",
    ]
    write_design_section(lines)
    write_manual_section(lines, repo_root)
    lines.extend(
        [
            "## 校验命令",
            "",
            "```bash",
            "python3 harness/playtest/check_current_manual_playtest_status.py --allow-incomplete",
            f"python3 harness/playtest/validate_manual_review.py {DEFAULT_PLAYTEST_DRAFT} --strict-acceptance",
            "python3 harness/content_review/validate_content_candidate_design_review.py harness/content_review/drafts/2026-06-05_demo_buildcraft_repair_v61_full_pack_design_review_draft.json --repo-root .",
            "```",
            "",
            "这张表本身不是接受证据；JSON 草稿和 Runtime 报告才是后续校验的事实来源。",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=f"Create a {CANDIDATE_LABEL} human review worksheet.")
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
