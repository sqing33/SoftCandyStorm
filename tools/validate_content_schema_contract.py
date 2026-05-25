#!/usr/bin/env python3
"""Validate content packs against the docs/13 JSON Schema contract.

This dependency-free validator supports the JSON Schema subset used by
content/schemas/*.schema.json. It is not a replacement for the Rust GameCore
loader or Harness simulation gates; it provides a portable first pass for
schema shape, required fields, enums, id patterns, and simple numeric bounds.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any


DEFAULT_SCHEMA_MANIFEST = Path("content/schemas/manifest.json")
CONTENT_CATEGORIES = [
    "characters",
    "weapons",
    "passives",
    "evolutions",
    "enemies",
    "bosses",
    "maps",
    "waves",
    "events",
]
ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def content_files(content_dir: Path, category: str) -> list[Path]:
    category_dir = content_dir / category
    return sorted(path for path in category_dir.glob("*.json") if path.is_file()) if category_dir.exists() else []


def type_matches(value: Any, expected_type: str) -> bool:
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    if expected_type == "boolean":
        return isinstance(value, bool)
    return True


def validate_value(schema: dict[str, Any], value: Any, label: str) -> list[str]:
    errors: list[str] = []
    expected_type = schema.get("type")
    if isinstance(expected_type, str):
        if not type_matches(value, expected_type):
            return [f"{label}: expected {expected_type}, got {type(value).__name__}"]
    elif isinstance(expected_type, list):
        if not any(type_matches(value, item) for item in expected_type if isinstance(item, str)):
            return [f"{label}: expected one of {expected_type}, got {type(value).__name__}"]

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{label}: value `{value}` is not in enum {schema['enum']}")

    if isinstance(value, str):
        min_length = schema.get("minLength")
        if isinstance(min_length, int) and len(value) < min_length:
            errors.append(f"{label}: string length {len(value)} is below {min_length}")
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and not re.match(pattern, value):
            errors.append(f"{label}: value `{value}` does not match pattern `{pattern}`")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        minimum = schema.get("minimum")
        if isinstance(minimum, (int, float)) and value < minimum:
            errors.append(f"{label}: value {value} is below minimum {minimum}")
        exclusive_minimum = schema.get("exclusiveMinimum")
        if isinstance(exclusive_minimum, (int, float)) and value <= exclusive_minimum:
            errors.append(f"{label}: value {value} must be greater than {exclusive_minimum}")

    if isinstance(value, list):
        min_items = schema.get("minItems")
        if isinstance(min_items, int) and len(value) < min_items:
            errors.append(f"{label}: array length {len(value)} is below {min_items}")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                errors.extend(validate_value(item_schema, item, f"{label}[{index}]"))

    if isinstance(value, dict):
        required = schema.get("required", [])
        if isinstance(required, list):
            for field in required:
                if isinstance(field, str) and field not in value:
                    errors.append(f"{label}: missing required `{field}`")
        properties = schema.get("properties", {})
        if isinstance(properties, dict):
            for field, field_schema in properties.items():
                if field in value and isinstance(field_schema, dict):
                    errors.extend(validate_value(field_schema, value[field], f"{label}.{field}"))

    return errors


def validate_schema_shape(category: str, schema_path: Path, schema: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    label = f"schema `{category}`"
    if not is_nonempty_string(schema.get("$schema")):
        errors.append(f"{label}: missing `$schema`")
    if schema.get("type") != "object":
        errors.append(f"{label}: top-level type must be object")
    if not isinstance(schema.get("required"), list) or not schema["required"]:
        errors.append(f"{label}: required must be a non-empty list")
    if not isinstance(schema.get("properties"), dict) or not schema["properties"]:
        errors.append(f"{label}: properties must be a non-empty object")
    if schema.get("additionalProperties") is not True:
        warnings.append(f"{label}: additionalProperties should be true for forward-compatible content")
    if schema_path.name != f"{category}.schema.json":
        warnings.append(f"{label}: schema file name is `{schema_path.name}`, expected `{category}.schema.json`")
    return errors, warnings


def load_schema_manifest(schema_manifest: Path) -> tuple[dict[str, dict[str, Any]], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    schemas: dict[str, dict[str, Any]] = {}
    try:
        manifest = load_json_object(schema_manifest)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return schemas, [f"{schema_manifest}: invalid schema manifest: {error}"], warnings

    categories = manifest.get("categories")
    if not isinstance(categories, dict):
        return schemas, ["schema manifest categories must be an object"], warnings

    for category in CONTENT_CATEGORIES:
        schema_file = categories.get(category)
        if not is_nonempty_string(schema_file):
            errors.append(f"schema manifest missing category `{category}`")
            continue
        schema_path = schema_manifest.parent / str(schema_file)
        try:
            schema = load_json_object(schema_path)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            errors.append(f"{schema_path}: invalid schema JSON: {error}")
            continue
        schema_errors, schema_warnings = validate_schema_shape(category, schema_path, schema)
        errors.extend(schema_errors)
        warnings.extend(schema_warnings)
        schemas[category] = schema

    unknown_categories = sorted(set(categories) - set(CONTENT_CATEGORIES))
    for category in unknown_categories:
        warnings.append(f"schema manifest includes unknown category `{category}`")

    return schemas, errors, warnings


def validate_content_dir(content_dir: Path, schemas: dict[str, dict[str, Any]]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    category_counts: dict[str, int] = {}
    seen_ids: dict[str, str] = {}

    for category in CONTENT_CATEGORIES:
        schema = schemas.get(category)
        if schema is None:
            errors.append(f"{content_dir}: no schema loaded for category `{category}`")
            continue
        category_dir = content_dir / category
        if not category_dir.exists():
            errors.append(f"{content_dir}: missing category directory `{category}`")
            category_counts[category] = 0
            continue
        files = content_files(content_dir, category)
        category_counts[category] = len(files)
        if not files:
            errors.append(f"{content_dir}: category `{category}` contains no JSON files")
            continue
        for path in files:
            relative_path = path.relative_to(content_dir)
            try:
                payload = load_json_object(path)
            except (OSError, ValueError, json.JSONDecodeError) as error:
                errors.append(f"{content_dir}/{relative_path}: invalid JSON: {error}")
                continue
            label = f"{content_dir}/{relative_path}"
            errors.extend(validate_value(schema, payload, label))

            item_id = payload.get("id")
            if is_nonempty_string(item_id):
                if not ID_PATTERN.match(str(item_id)):
                    errors.append(f"{label}: id `{item_id}` is not kebab-case")
                if item_id != path.stem:
                    errors.append(f"{label}: id `{item_id}` must match file stem `{path.stem}`")
                qualified_id = f"{category}:{item_id}"
                if qualified_id in seen_ids:
                    errors.append(f"{label}: duplicate id also found in {seen_ids[qualified_id]}")
                else:
                    seen_ids[qualified_id] = str(relative_path)

    return {
        "content_dir": str(content_dir),
        "decision": "content_schema_contract_valid" if not errors else "content_schema_contract_invalid",
        "category_counts": category_counts,
        "errors": errors,
        "warnings": warnings,
    }


def build_report(schema_manifest: Path, content_dirs: list[Path]) -> dict[str, Any]:
    schemas, schema_errors, schema_warnings = load_schema_manifest(schema_manifest)
    content_reports = [validate_content_dir(content_dir, schemas) for content_dir in content_dirs] if not schema_errors else []
    errors = list(schema_errors)
    warnings = list(schema_warnings)
    for content_report in content_reports:
        errors.extend(content_report["errors"])
        warnings.extend(content_report["warnings"])

    return {
        "report_version": 1,
        "schema_manifest": str(schema_manifest),
        "decision": "content_schema_contract_valid" if not errors else "content_schema_contract_invalid",
        "schema_count": len(schemas),
        "expected_schema_count": len(CONTENT_CATEGORIES),
        "content_pack_count": len(content_reports),
        "errors": errors,
        "warnings": warnings,
        "content_packs": content_reports,
        "limitations": [
            "This validator supports the JSON Schema subset used in content/schemas only.",
            "It checks structural contract, required fields, enums, id patterns, and simple numeric bounds.",
            "It does not run GameCore loading, static budget gates, Bot simulation, Replay regression, or human review.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Content Schema Contract Validation",
        "",
        f"- Schema manifest: `{report['schema_manifest']}`",
        f"- Decision: `{report['decision']}`",
        f"- Schemas: {report['schema_count']} / {report['expected_schema_count']}",
        f"- Content packs: {report['content_pack_count']}",
        "",
        "## Content Packs",
        "",
        "| Content Dir | Decision | Items |",
        "|---|---|---:|",
    ]
    for content_report in report["content_packs"]:
        total_items = sum(content_report["category_counts"].values())
        lines.append(f"| `{content_report['content_dir']}` | `{content_report['decision']}` | {total_items} |")

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
    parser = argparse.ArgumentParser(description="Validate content packs against the docs/13 schema contract.")
    parser.add_argument("content_dirs", type=Path, nargs="+", help="Content pack directories to validate")
    parser.add_argument("--schema-manifest", type=Path, default=DEFAULT_SCHEMA_MANIFEST)
    parser.add_argument("--report", type=Path, default=None, help="Write JSON validation report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown validation summary")
    args = parser.parse_args()

    report = build_report(args.schema_manifest, args.content_dirs)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "content_schema_contract_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
