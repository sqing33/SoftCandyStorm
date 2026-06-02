#!/usr/bin/env python3
"""List TODO fields that a human must fill before v25 evidence validation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DESIGN_DRAFT = Path("harness/content_review/drafts/2026-06-02_demo_buildcraft_repair_v25_full_pack_design_review_draft.json")
PLAYTEST_DRAFT = Path("harness/playtest/drafts/2026-06-02_demo_buildcraft_repair_v25_manual_playtest_review_draft.json")

NOTICE_KEYS = {"draft_notice"}


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def preview(value: str, limit: int = 140) -> str:
    normalized = " ".join(value.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3] + "..."


def collect_todos(value: Any, path: str = "$") -> list[dict[str, str]]:
    todos: list[dict[str, str]] = []
    if isinstance(value, str):
        if "TODO" in value:
            todos.append({"path": path, "value": preview(value)})
    elif isinstance(value, list):
        for index, item in enumerate(value):
            todos.extend(collect_todos(item, f"{path}[{index}]"))
    elif isinstance(value, dict):
        for key, item in value.items():
            if key in NOTICE_KEYS:
                continue
            todos.extend(collect_todos(item, f"{path}.{key}"))
    return todos


def design_item_todos(design: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for index, review in enumerate(design.get("content_reviews", [])):
        if not isinstance(review, dict):
            continue
        content_id = str(review.get("id", f"content_reviews[{index}]"))
        todos = collect_todos(review, f"$.content_reviews[{index}]")
        items.append(
            {
                "content_id": content_id,
                "content_type": review.get("content_type", ""),
                "todo_count": len(todos),
                "todos": todos,
            }
        )
    return items


def playtest_run_todos(playtest: dict[str, Any]) -> list[dict[str, Any]]:
    runs: list[dict[str, Any]] = []
    for index, run in enumerate(playtest.get("runs", [])):
        if not isinstance(run, dict):
            continue
        run_id = str(run.get("run_id", f"runs[{index}]"))
        todos = collect_todos(run, f"$.runs[{index}]")
        runs.append(
            {
                "run_id": run_id,
                "player_skill": run.get("player_skill", ""),
                "intent": run.get("intent", ""),
                "required_observations": run.get("required_observations", []),
                "todo_count": len(todos),
                "todos": todos,
            }
        )
    return runs


def build_report(
    repo_root: Path,
    design_draft: Path = DESIGN_DRAFT,
    playtest_draft: Path = PLAYTEST_DRAFT,
) -> dict[str, Any]:
    design_path = repo_root / design_draft
    playtest_path = repo_root / playtest_draft
    design = load_json_object(design_path)
    playtest = load_json_object(playtest_path)

    design_top_level = [
        item
        for item in collect_todos(design)
        if not item["path"].startswith("$.content_reviews")
    ]
    playtest_top_level = [
        item
        for item in collect_todos(playtest)
        if not item["path"].startswith("$.runs")
    ]
    design_items = design_item_todos(design)
    playtest_runs = playtest_run_todos(playtest)
    design_todo_count = len(design_top_level) + sum(item["todo_count"] for item in design_items)
    playtest_todo_count = len(playtest_top_level) + sum(run["todo_count"] for run in playtest_runs)
    decision = "human_evidence_todos_clear" if design_todo_count == 0 and playtest_todo_count == 0 else "human_evidence_todos_pending"

    return {
        "report_version": 1,
        "decision": decision,
        "design_draft": str(design_draft),
        "playtest_draft": str(playtest_draft),
        "summary": {
            "design_todo_count": design_todo_count,
            "playtest_todo_count": playtest_todo_count,
            "design_content_count": len(design_items),
            "playtest_run_count": len(playtest_runs),
        },
        "design_review": {
            "top_level_todos": design_top_level,
            "content_items": design_items,
        },
        "manual_playtest": {
            "top_level_todos": playtest_top_level,
            "runs": playtest_runs,
        },
        "next_actions": [
            "Fill every TODO field with concrete human observations before strict validation.",
            "Keep AI-generated content in generated_candidates until design review and manual playtest evidence pass.",
        ],
        "limitations": [
            "This report lists TODO fields only.",
            "It does not fill human evidence, validate ratings, run the game, judge fun, or promote content.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# v25 Human Evidence TODOs",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Design draft: `{report['design_draft']}`",
        f"- Playtest draft: `{report['playtest_draft']}`",
        f"- Design TODOs: `{summary['design_todo_count']}`",
        f"- Playtest TODOs: `{summary['playtest_todo_count']}`",
        "",
        "## Design Review",
        "",
    ]
    design = report["design_review"]
    if design["top_level_todos"]:
        lines.append("### Top Level")
        lines.append("")
        for item in design["top_level_todos"]:
            lines.append(f"- `{item['path']}`: {item['value']}")
        lines.append("")
    for item in design["content_items"]:
        lines.append(f"### {item['content_id']}")
        lines.append("")
        lines.append(f"- Type: `{item['content_type']}`")
        lines.append(f"- TODOs: `{item['todo_count']}`")
        for todo in item["todos"]:
            lines.append(f"- `{todo['path']}`: {todo['value']}")
        lines.append("")

    lines.extend(["## Manual Playtest", ""])
    playtest = report["manual_playtest"]
    if playtest["top_level_todos"]:
        lines.append("### Top Level")
        lines.append("")
        for item in playtest["top_level_todos"]:
            lines.append(f"- `{item['path']}`: {item['value']}")
        lines.append("")
    for run in playtest["runs"]:
        lines.append(f"### {run['run_id']}")
        lines.append("")
        lines.append(f"- Skill: `{run['player_skill']}`")
        lines.append(f"- Intent: {run['intent']}")
        lines.append(f"- TODOs: `{run['todo_count']}`")
        observations = run["required_observations"]
        if observations:
            lines.append("- Required observations:")
            lines.extend(f"  - {item}" for item in observations)
        for todo in run["todos"]:
            lines.append(f"- `{todo['path']}`: {todo['value']}")
        lines.append("")

    lines.extend(["## Next Actions", ""])
    lines.extend(f"- {item}" for item in report["next_actions"])
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="List v25 human evidence TODO fields.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--design-draft", type=Path, default=DESIGN_DRAFT)
    parser.add_argument("--playtest-draft", type=Path, default=PLAYTEST_DRAFT)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--markdown", type=Path, default=None)
    parser.add_argument("--allow-todos", action="store_true")
    args = parser.parse_args()

    report = build_report(args.repo_root, args.design_draft, args.playtest_draft)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))

    if report["decision"] == "human_evidence_todos_clear" or args.allow_todos:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
