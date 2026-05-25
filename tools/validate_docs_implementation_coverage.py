#!/usr/bin/env python3
"""Validate documentation implementation coverage records.

This gate keeps the "implement every docs requirement" goal auditable. It does
not decide that a feature is complete by itself; it checks that each docs/00-19
entry has an explicit status, concrete evidence paths, and named gaps whenever
the implementation is not complete.
"""

from __future__ import annotations

import argparse
import json
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

DOC_STATUSES = {"complete", "partial", "blocked", "pending", "design_only"}
ITEM_STATUSES = {"complete", "partial", "blocked", "pending", "not_applicable"}


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]


def resolve_repo_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def is_inside_repo(repo_root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return False
    return True


def validate_evidence_paths(
    repo_root: Path,
    label: str,
    evidence: list[str],
    errors: list[str],
) -> None:
    for evidence_path in evidence:
        resolved = resolve_repo_path(repo_root, evidence_path)
        if not is_inside_repo(repo_root, resolved):
            errors.append(f"{label}: evidence path must stay inside repository: {evidence_path}")
        elif not resolved.exists():
            errors.append(f"{label}: evidence path does not exist: {evidence_path}")


def validate_coverage_item(
    repo_root: Path,
    doc_id: str,
    item: Any,
    index: int,
) -> tuple[dict[str, Any] | None, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(item, dict):
        return None, [f"{doc_id}.coverage[{index}] must be an object"], warnings

    item_id = item.get("id")
    label = f"{doc_id}.{item_id}" if is_nonempty_string(item_id) else f"{doc_id}.coverage[{index}]"
    if not is_nonempty_string(item_id):
        errors.append(f"{label}: id must be non-empty")
    if not is_nonempty_string(item.get("requirement")):
        errors.append(f"{label}: requirement must be non-empty")

    status = item.get("status")
    if status not in ITEM_STATUSES:
        errors.append(f"{label}: status must be one of {', '.join(sorted(ITEM_STATUSES))}")

    evidence = string_list(item.get("evidence"))
    gaps = string_list(item.get("gaps"))
    blockers = string_list(item.get("blockers"))
    if item.get("evidence") is not None and not isinstance(item.get("evidence"), list):
        errors.append(f"{label}: evidence must be a list")
    if item.get("gaps") is not None and not isinstance(item.get("gaps"), list):
        errors.append(f"{label}: gaps must be a list")
    if item.get("blockers") is not None and not isinstance(item.get("blockers"), list):
        errors.append(f"{label}: blockers must be a list")

    validate_evidence_paths(repo_root, label, evidence, errors)

    if status == "complete":
        if not evidence:
            errors.append(f"{label}: complete item requires at least one evidence path")
        if gaps:
            errors.append(f"{label}: complete item cannot list open gaps")
        if blockers:
            errors.append(f"{label}: complete item cannot list blockers")
    elif status in {"partial", "pending"} and not gaps:
        warnings.append(f"{label}: {status} item should list concrete gaps")
    elif status == "blocked" and not blockers:
        errors.append(f"{label}: blocked item requires at least one blocker")

    return (
        {
            "id": item_id if is_nonempty_string(item_id) else f"coverage[{index}]",
            "status": status,
            "evidence_count": len(evidence),
            "gap_count": len(gaps),
            "blocker_count": len(blockers),
        },
        errors,
        warnings,
    )


def validate_doc_entry(
    repo_root: Path,
    entry: Any,
    index: int,
) -> tuple[dict[str, Any] | None, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(entry, dict):
        return None, [f"docs[{index}] must be an object"], warnings

    doc_id = entry.get("doc_id")
    label = str(doc_id) if is_nonempty_string(doc_id) else f"docs[{index}]"
    if not is_nonempty_string(doc_id):
        errors.append(f"{label}: doc_id must be non-empty")

    doc_path = entry.get("doc_path")
    if not is_nonempty_string(doc_path):
        errors.append(f"{label}: doc_path must be non-empty")
    else:
        resolved_doc_path = resolve_repo_path(repo_root, str(doc_path))
        if not is_inside_repo(repo_root, resolved_doc_path):
            errors.append(f"{label}: doc_path must stay inside repository: {doc_path}")
        elif not resolved_doc_path.exists():
            errors.append(f"{label}: doc_path does not exist: {doc_path}")

    status = entry.get("status")
    if status not in DOC_STATUSES:
        errors.append(f"{label}: status must be one of {', '.join(sorted(DOC_STATUSES))}")
    if not is_nonempty_string(entry.get("summary")):
        errors.append(f"{label}: summary must be non-empty")

    coverage = entry.get("coverage")
    if not isinstance(coverage, list) or not coverage:
        errors.append(f"{label}: coverage must be a non-empty list")
        coverage = []

    item_reports: list[dict[str, Any]] = []
    item_status_counts: dict[str, int] = {}
    for item_index, item in enumerate(coverage):
        item_report, item_errors, item_warnings = validate_coverage_item(repo_root, label, item, item_index)
        errors.extend(item_errors)
        warnings.extend(item_warnings)
        if item_report is not None:
            item_reports.append(item_report)
            item_status = str(item_report["status"])
            item_status_counts[item_status] = item_status_counts.get(item_status, 0) + 1

    incomplete_items = [
        item
        for item in item_reports
        if item["status"] not in {"complete", "not_applicable"}
    ]
    if status == "complete" and incomplete_items:
        errors.append(f"{label}: complete doc cannot contain incomplete coverage items")
    if status != "complete" and not incomplete_items and item_reports:
        warnings.append(f"{label}: doc status is `{status}` but all coverage items are complete or not_applicable")

    return (
        {
            "doc_id": doc_id if is_nonempty_string(doc_id) else f"docs[{index}]",
            "doc_path": doc_path if is_nonempty_string(doc_path) else None,
            "status": status,
            "coverage_count": len(item_reports),
            "item_status_counts": dict(sorted(item_status_counts.items())),
            "incomplete_coverage_count": len(incomplete_items),
        },
        errors,
        warnings,
    )


def build_report(manifest_path: Path, repo_root: Path) -> dict[str, Any]:
    payload = load_json_object(manifest_path)
    errors: list[str] = []
    warnings: list[str] = []

    for field in ("updated_at", "scope", "summary"):
        if not is_nonempty_string(payload.get(field)):
            errors.append(f"`{field}` must be non-empty")

    docs = payload.get("docs")
    if not isinstance(docs, list):
        docs = []
        errors.append("`docs` must be a list")

    doc_reports: list[dict[str, Any]] = []
    seen_doc_paths: dict[str, str] = {}
    for index, entry in enumerate(docs):
        doc_report, doc_errors, doc_warnings = validate_doc_entry(repo_root, entry, index)
        errors.extend(doc_errors)
        warnings.extend(doc_warnings)
        if doc_report is None:
            continue
        doc_reports.append(doc_report)
        doc_path = doc_report.get("doc_path")
        doc_id = str(doc_report.get("doc_id"))
        if isinstance(doc_path, str):
            if doc_path in seen_doc_paths:
                errors.append(f"duplicate doc_path `{doc_path}` in {doc_id} and {seen_doc_paths[doc_path]}")
            seen_doc_paths[doc_path] = doc_id

    expected_paths = {f"docs/{name}" for name in EXPECTED_DOCS}
    actual_paths = {str(report.get("doc_path")) for report in doc_reports if report.get("doc_path")}
    missing_docs = sorted(expected_paths - actual_paths)
    extra_docs = sorted(actual_paths - expected_paths)
    for doc_path in missing_docs:
        errors.append(f"missing docs coverage entry for `{doc_path}`")
    for doc_path in extra_docs:
        warnings.append(f"coverage entry is not part of docs/00-19 expected set: `{doc_path}`")

    doc_status_counts: dict[str, int] = {}
    item_status_counts: dict[str, int] = {}
    incomplete_docs: list[str] = []
    for doc_report in doc_reports:
        doc_status = str(doc_report["status"])
        doc_status_counts[doc_status] = doc_status_counts.get(doc_status, 0) + 1
        if doc_status != "complete":
            incomplete_docs.append(str(doc_report["doc_path"]))
        for item_status, count in doc_report["item_status_counts"].items():
            item_status_counts[item_status] = item_status_counts.get(item_status, 0) + int(count)

    decision = (
        "docs_implementation_complete"
        if not errors and not incomplete_docs and item_status_counts.get("partial", 0) == 0
        and item_status_counts.get("blocked", 0) == 0
        and item_status_counts.get("pending", 0) == 0
        else "docs_implementation_incomplete"
    )

    return {
        "report_version": 1,
        "source": str(manifest_path),
        "repo_root": str(repo_root),
        "scope": payload.get("scope"),
        "decision": decision,
        "doc_count": len(doc_reports),
        "expected_doc_count": len(EXPECTED_DOCS),
        "doc_status_counts": dict(sorted(doc_status_counts.items())),
        "item_status_counts": dict(sorted(item_status_counts.items())),
        "incomplete_docs": incomplete_docs,
        "missing_docs": missing_docs,
        "errors": errors,
        "warnings": warnings,
        "docs": doc_reports,
        "limitations": [
            "This validator checks the coverage ledger and evidence path existence only.",
            "It does not execute Rust, Bevy, Harness simulations, Replay, performance tests, or manual playtests.",
            "A complete decision requires every docs/00-19 entry and every coverage item to be marked complete or not_applicable with existing evidence.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Docs Implementation Coverage Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Decision: `{report['decision']}`",
        f"- Docs: {report['doc_count']} / {report['expected_doc_count']}",
        f"- Incomplete docs: {len(report['incomplete_docs'])}",
        "",
        "## Doc Status",
        "",
        "| Status | Count |",
        "|---|---:|",
    ]
    for status, count in report["doc_status_counts"].items():
        lines.append(f"| `{status}` | {count} |")

    lines.extend(["", "## Item Status", "", "| Status | Count |", "|---|---:|"])
    for status, count in report["item_status_counts"].items():
        lines.append(f"| `{status}` | {count} |")

    lines.extend(["", "## Docs", "", "| Doc | Status | Coverage | Incomplete |", "|---|---|---:|---:|"])
    for doc_report in report["docs"]:
        lines.append(
            f"| `{doc_report['doc_path']}` | `{doc_report['status']}` | "
            f"{doc_report['coverage_count']} | {doc_report['incomplete_coverage_count']} |"
        )

    lines.extend(["", "## Errors", ""])
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
    parser = argparse.ArgumentParser(description="Validate docs implementation coverage records.")
    parser.add_argument("manifest", type=Path, help="Docs implementation coverage manifest JSON")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON validation report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown validation summary")
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="Exit 0 for an incomplete docs coverage report; useful while the long-running goal is active",
    )
    args = parser.parse_args()

    report = build_report(args.manifest, args.repo_root)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))

    if report["decision"] == "docs_implementation_complete" or args.allow_incomplete:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
