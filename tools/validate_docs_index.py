#!/usr/bin/env python3
"""Validate Soft Candy Storm documentation index and required doc files."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


EXPECTED_DOCS = [
    "00_index.md",
    "01_游戏愿景与设计支柱.md",
    "02_核心玩法规格.md",
    "03_世界观与剧情大纲.md",
    "04_内容系统与素材库.md",
    "05_美术与音频素材计划.md",
    "06_Bevy技术架构计划.md",
    "07_Harness工程计划.md",
    "08_Bot测试计划.md",
    "09_AI_Bot训练计划.md",
    "10_AI内容生成流水线.md",
    "11_测试指标与上线门禁.md",
    "12_阶段路线图.md",
    "13_内容数据Schema设计.md",
    "14_GameCore接口规格.md",
    "15_经济与数值平衡模型.md",
    "16_Replay与遥测设计.md",
    "17_素材生成Prompt库.md",
    "18_完整游戏流程与局外成长.md",
    "19_Goal模式开发约定.md",
]

REQUIRED_AGENT_DOC_NUMBERS = [
    "00",
    "01",
    "02",
    "03",
    "04",
    "05",
    "06",
    "07",
    "08",
    "09",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15",
    "16",
    "17",
    "18",
    "19",
]

MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def is_local_markdown_link(link: str) -> bool:
    return not link.startswith(("http://", "https://", "#")) and link.endswith(".md")


def doc_by_number(docs_dir: Path, number: str) -> list[Path]:
    return sorted(docs_dir.glob(f"{number}_*.md")) if number != "00" else [docs_dir / "00_index.md"]


def extract_index_links(index_path: Path) -> list[str]:
    text = index_path.read_text(encoding="utf-8")
    return [
        match.group(1)
        for match in MARKDOWN_LINK_PATTERN.finditer(text)
        if is_local_markdown_link(match.group(1))
    ]


def build_report(repo_root: Path) -> dict[str, Any]:
    docs_dir = repo_root / "docs"
    index_path = docs_dir / "00_index.md"
    agents_path = repo_root / "AGENTS.md"
    errors: list[str] = []
    warnings: list[str] = []

    if not docs_dir.exists():
        errors.append("docs directory is missing")
        return {
            "report_version": 1,
            "repo_root": str(repo_root),
            "decision": "docs_index_invalid",
            "doc_count": 0,
            "index_link_count": 0,
            "errors": errors,
            "warnings": warnings,
            "limitations": [],
        }

    doc_files = sorted(path.name for path in docs_dir.glob("*.md"))
    expected_set = set(EXPECTED_DOCS)
    actual_set = set(doc_files)
    missing_docs = sorted(expected_set - actual_set)
    extra_docs = sorted(actual_set - expected_set)
    for doc in missing_docs:
        errors.append(f"missing expected doc `{doc}`")
    for doc in extra_docs:
        warnings.append(f"extra docs file not listed in expected 00-19 set: `{doc}`")

    if not index_path.exists():
        errors.append("docs/00_index.md is missing")
        index_links: list[str] = []
    else:
        index_links = extract_index_links(index_path)
        for link in index_links:
            resolved = (index_path.parent / link).resolve()
            if not resolved.exists():
                errors.append(f"docs/00_index.md link does not exist: `{link}`")
        linked_names = {Path(link).name for link in index_links}
        for doc in EXPECTED_DOCS:
            if doc == "00_index.md":
                continue
            if doc not in linked_names:
                errors.append(f"docs/00_index.md missing link to `{doc}`")

    if not agents_path.exists():
        errors.append("AGENTS.md is missing")
    else:
        agents_text = agents_path.read_text(encoding="utf-8")
        for number in REQUIRED_AGENT_DOC_NUMBERS:
            matches = doc_by_number(docs_dir, number)
            existing_matches = [path for path in matches if path.exists()]
            if not existing_matches:
                errors.append(f"AGENTS required doc number `{number}` has no matching docs file")
            if number not in agents_text:
                warnings.append(f"AGENTS.md does not mention doc number `{number}` explicitly")

    return {
        "report_version": 1,
        "repo_root": str(repo_root),
        "decision": "docs_index_valid" if not errors else "docs_index_invalid",
        "doc_count": len(doc_files),
        "expected_doc_count": len(EXPECTED_DOCS),
        "index_link_count": len(index_links),
        "missing_docs": missing_docs,
        "extra_docs": extra_docs,
        "errors": errors,
        "warnings": warnings,
        "limitations": [
            "This validator checks documentation inventory and local Markdown links only.",
            "It does not prove that each document's requirements are implemented in code or content.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Docs Index Validation",
        "",
        f"- Repo root: `{report['repo_root']}`",
        f"- Decision: `{report['decision']}`",
        f"- Docs: {report['doc_count']} / {report['expected_doc_count']}",
        f"- Index links: {report['index_link_count']}",
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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm docs index and required docs.")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON validation report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown validation summary")
    args = parser.parse_args()

    report = build_report(args.repo_root)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "docs_index_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
