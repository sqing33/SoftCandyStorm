#!/usr/bin/env python3
"""Validate Soft Candy Storm failure case records.

The project requires every bug, balance failure, bot exploit, training anomaly,
or replay regression to be recorded as a failure case. This validator checks
that those records have the required postmortem fields and can be audited later.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any


CANONICAL_CASE_ID_PATTERN = re.compile(r"^fail_\d{8}_\d{3}$")
REQUIRED_FIELDS = [
    "case_id",
    "category",
    "content_id",
    "seed",
    "bot",
    "time_seconds",
    "symptom",
    "root_cause",
    "fix",
    "validation",
]
REQUIRED_TEXT_FIELDS = [
    "case_id",
    "category",
    "content_id",
    "symptom",
    "root_cause",
    "fix",
    "validation",
]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_optional_number(value: Any) -> bool:
    if value is None:
        return True
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def discover_failure_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    return sorted(path for path in root.rglob("*.json") if path.is_file()) if root.exists() else []


def records_from_file(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    try:
        payload = load_json(path)
    except (OSError, json.JSONDecodeError) as error:
        return [], [f"{path}: invalid JSON: {error}"]

    if isinstance(payload, dict):
        return [payload], errors
    if isinstance(payload, list):
        records: list[dict[str, Any]] = []
        for index, item in enumerate(payload):
            if isinstance(item, dict):
                records.append(item)
            else:
                errors.append(f"{path}: records[{index}] must be an object")
        return records, errors
    return [], [f"{path}: must contain a JSON object or list of objects"]


def is_canonical_failed_case_path(path: Path) -> bool:
    return path.parent.name == "failed_cases" and path.name.startswith("fail_")


def validate_record(path: Path, record: dict[str, Any], index: int, strict_filename: bool) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    label = f"{path}:{index}" if index > 0 else str(path)

    for field in REQUIRED_FIELDS:
        if field not in record:
            errors.append(f"{label}: missing `{field}`")

    for field in REQUIRED_TEXT_FIELDS:
        if field in record and not is_nonempty_string(record.get(field)):
            errors.append(f"{label}: `{field}` must be a non-empty string")

    case_id = record.get("case_id")
    if is_nonempty_string(case_id):
        if strict_filename:
            if not CANONICAL_CASE_ID_PATTERN.match(str(case_id)):
                errors.append(f"{label}: canonical case_id must match fail_YYYYMMDD_NNN")
            if not path.stem.startswith(str(case_id)):
                errors.append(f"{label}: file name must start with case_id `{case_id}`")
        elif not CANONICAL_CASE_ID_PATTERN.match(str(case_id)):
            warnings.append(f"{label}: non-canonical report-local case_id `{case_id}`")

    if "time_seconds" in record and not is_optional_number(record.get("time_seconds")):
        errors.append(f"{label}: `time_seconds` must be finite number or null")

    seed = record.get("seed")
    if seed is not None and not isinstance(seed, (int, str)):
        errors.append(f"{label}: `seed` must be integer, string range, or null")

    bot = record.get("bot")
    if bot is not None and not is_nonempty_string(bot):
        errors.append(f"{label}: `bot` must be a non-empty string or null")

    if "diagnostics" in record and not isinstance(record["diagnostics"], list):
        errors.append(f"{label}: `diagnostics` must be a list when present")

    return errors, warnings


def build_report(root: Path) -> dict[str, Any]:
    files = discover_failure_files(root)
    errors: list[str] = []
    warnings: list[str] = []
    case_ids: dict[str, str] = {}
    file_reports: list[dict[str, Any]] = []
    category_counts: dict[str, int] = {}
    record_count = 0

    if not files:
        errors.append(f"no failure case JSON files found under {root}")

    for path in files:
        records, load_errors = records_from_file(path)
        errors.extend(load_errors)
        strict_filename = is_canonical_failed_case_path(path)
        file_errors: list[str] = []
        file_warnings: list[str] = []

        for index, record in enumerate(records):
            record_count += 1
            record_errors, record_warnings = validate_record(path, record, index, strict_filename)
            errors.extend(record_errors)
            warnings.extend(record_warnings)
            file_errors.extend(record_errors)
            file_warnings.extend(record_warnings)

            case_id = record.get("case_id")
            if is_nonempty_string(case_id):
                if case_id in case_ids:
                    duplicate = f"duplicate case_id `{case_id}` in {path} and {case_ids[case_id]}"
                    errors.append(duplicate)
                    file_errors.append(duplicate)
                else:
                    case_ids[str(case_id)] = str(path)

            category = record.get("category")
            if is_nonempty_string(category):
                category_counts[str(category)] = category_counts.get(str(category), 0) + 1

        file_reports.append(
            {
                "path": str(path),
                "record_count": len(records),
                "errors": file_errors,
                "warnings": file_warnings,
            }
        )

    return {
        "report_version": 1,
        "root": str(root),
        "decision": "failure_cases_valid" if not errors else "failure_cases_invalid",
        "file_count": len(files),
        "record_count": record_count,
        "category_counts": dict(sorted(category_counts.items())),
        "errors": errors,
        "warnings": warnings,
        "files": file_reports,
        "limitations": [
            "This validator checks failure case record structure and provenance fields only.",
            "It does not prove the fix is correct; validation commands or reports must still be reviewed.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Failure Case Validation",
        "",
        f"- Root: `{report['root']}`",
        f"- Decision: `{report['decision']}`",
        f"- File count: {report['file_count']}",
        f"- Record count: {report['record_count']}",
        "",
        "## Categories",
        "",
    ]
    if report["category_counts"]:
        for category, count in report["category_counts"].items():
            lines.append(f"- `{category}`: {count}")
    else:
        lines.append("- None")

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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm failure case records.")
    parser.add_argument(
        "root",
        type=Path,
        nargs="?",
        default=Path("harness/failed_cases"),
        help="Failure case JSON file or directory",
    )
    parser.add_argument("--report", type=Path, default=None, help="Write JSON validation report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown validation summary")
    args = parser.parse_args()

    report = build_report(args.root)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "failure_cases_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
