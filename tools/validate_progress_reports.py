#!/usr/bin/env python3
"""Validate progress report evidence references.

The long-running goal work uses harness/progress.json as a compact handoff
ledger. This validator checks that every recorded `report` path points to an
existing repository artifact, so progress claims remain auditable across agents.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PROGRESS_SECTIONS = ["completed", "current_findings", "next_recommended"]
SECTIONS_EXPECTED_TO_HAVE_EVIDENCE = {"completed", "current_findings"}


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def resolve_repo_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def is_inside_repo(repo_root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return False
    return True


def validate_item(
    repo_root: Path,
    section: str,
    item: Any,
    index: int,
    seen_ids: dict[str, list[str]],
) -> tuple[dict[str, Any] | None, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(item, dict):
        return None, [f"{section}[{index}] must be an object"], warnings

    item_id = item.get("id")
    label = f"{section}[{index}]"
    if is_nonempty_string(item_id):
        label = str(item_id)
        previous_locations = seen_ids.get(str(item_id), [])
        same_section_duplicate = any(location.startswith(f"{section}[") for location in previous_locations)
        if same_section_duplicate:
            errors.append(
                f"duplicate progress id `{item_id}` in {section}[{index}] and {', '.join(previous_locations)}"
            )
        elif previous_locations:
            warnings.append(
                f"progress id `{item_id}` appears in multiple sections: "
                f"{', '.join(previous_locations)}, {section}[{index}]"
            )
            previous_locations.append(f"{section}[{index}]")
            seen_ids[str(item_id)] = previous_locations
        else:
            seen_ids[str(item_id)] = [f"{section}[{index}]"]
    else:
        errors.append(f"{section}[{index}]: id must be non-empty")

    if not is_nonempty_string(item.get("summary")):
        errors.append(f"{label}: summary must be non-empty")

    report = item.get("report")
    has_report = report is not None
    report_exists = False
    if has_report:
        if not is_nonempty_string(report):
            errors.append(f"{label}: report must be a non-empty string when present")
        else:
            resolved = resolve_repo_path(repo_root, str(report))
            if not is_inside_repo(repo_root, resolved):
                errors.append(f"{label}: report path must stay inside the repository: {report}")
            elif not resolved.exists():
                errors.append(f"{label}: report path does not exist: {report}")
            else:
                report_exists = True
    elif section in SECTIONS_EXPECTED_TO_HAVE_EVIDENCE:
        warnings.append(f"{label}: no report evidence path recorded")

    return (
        {
            "section": section,
            "id": item_id if is_nonempty_string(item_id) else f"{section}[{index}]",
            "has_report": has_report,
            "report": report if is_nonempty_string(report) else None,
            "report_exists": report_exists,
        },
        errors,
        warnings,
    )


def build_report(progress_path: Path, repo_root: Path) -> dict[str, Any]:
    payload = load_json_object(progress_path)
    errors: list[str] = []
    warnings: list[str] = []
    items: list[dict[str, Any]] = []
    section_counts: dict[str, int] = {}
    seen_ids: dict[str, list[str]] = {}

    for field in ("updated_at", "phase"):
        if not is_nonempty_string(payload.get(field)):
            errors.append(f"`{field}` must be non-empty")

    for section in PROGRESS_SECTIONS:
        raw_items = payload.get(section)
        if not isinstance(raw_items, list):
            errors.append(f"`{section}` must be a list")
            section_counts[section] = 0
            continue
        section_counts[section] = len(raw_items)
        for index, item in enumerate(raw_items):
            item_report, item_errors, item_warnings = validate_item(repo_root, section, item, index, seen_ids)
            errors.extend(item_errors)
            warnings.extend(item_warnings)
            if item_report is not None:
                items.append(item_report)

    report_items = [item for item in items if item["has_report"]]
    missing_reports = [item for item in report_items if not item["report_exists"]]
    no_report_warnings = [warning for warning in warnings if "no report evidence path recorded" in warning]
    decision = "progress_reports_valid" if not errors and not missing_reports else "progress_reports_invalid"

    return {
        "report_version": 1,
        "source": str(progress_path),
        "repo_root": str(repo_root),
        "decision": decision,
        "section_counts": section_counts,
        "item_count": len(items),
        "report_reference_count": len(report_items),
        "existing_report_reference_count": len(report_items) - len(missing_reports),
        "missing_report_reference_count": len(missing_reports),
        "items_without_report_count": len(no_report_warnings),
        "errors": errors,
        "warnings": warnings,
        "items": items,
        "limitations": [
            "This validator checks progress ledger structure and local report path existence only.",
            "It does not prove the referenced report's conclusions are correct or still current.",
            "Older completed entries without a report are warnings, not errors, until backfilled.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Progress Report Reference Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Decision: `{report['decision']}`",
        f"- Items: {report['item_count']}",
        f"- Report references: {report['existing_report_reference_count']} / {report['report_reference_count']}",
        f"- Items without report: {report['items_without_report_count']}",
        "",
        "## Sections",
        "",
        "| Section | Items |",
        "|---|---:|",
    ]
    for section, count in report["section_counts"].items():
        lines.append(f"| `{section}` | {count} |")

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
    parser = argparse.ArgumentParser(description="Validate harness/progress.json report references.")
    parser.add_argument("progress", type=Path, nargs="?", default=Path("harness/progress.json"))
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON validation report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown validation summary")
    args = parser.parse_args()

    report = build_report(args.progress, args.repo_root)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "progress_reports_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
