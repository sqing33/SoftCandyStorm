#!/usr/bin/env python3
"""Validate the GameCore public API source-shape contract.

This is a dependency-free source inspection gate for docs/14. It checks that the
declared public structs, fields, enums, variants, methods, re-exports, and
compatibility policy are present in current source files. It does not compile or
execute Rust code.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REQUIRED_COMPATIBILITY_FLAGS = [
    "breaking_change_requires_contract_bump",
    "breaking_change_requires_migration_note",
    "breaking_change_requires_replay_compatibility_note",
    "runtime_must_not_mutate_game_state_directly",
    "harness_and_runtime_must_use_same_gamecore",
]


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


def brace_block(source: str, start_index: int) -> str | None:
    open_index = source.find("{", start_index)
    if open_index == -1:
        return None
    depth = 0
    for index in range(open_index, len(source)):
        char = source[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[open_index + 1:index]
    return None


def find_struct_block(source: str, name: str) -> str | None:
    match = re.search(rf"\bpub\s+struct\s+{re.escape(name)}\b", source)
    if not match:
        return None
    return brace_block(source, match.end())


def find_enum_block(source: str, name: str) -> str | None:
    match = re.search(rf"\bpub\s+enum\s+{re.escape(name)}\b", source)
    if not match:
        return None
    return brace_block(source, match.end())


def find_impl_block(source: str, name: str) -> str | None:
    match = re.search(rf"\bimpl\s+{re.escape(name)}\b", source)
    if not match:
        return None
    return brace_block(source, match.end())


def parse_pub_fields(block: str) -> set[str]:
    return set(re.findall(r"\bpub\s+([A-Za-z_][A-Za-z0-9_]*)\s*:", block))


def parse_methods(block: str) -> set[str]:
    return set(re.findall(r"\bpub\s+(?:const\s+)?fn\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", block))


def parse_enum_variants(block: str) -> set[str]:
    variants: set[str] = set()
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("//") or stripped.startswith("#"):
            continue
        match = re.match(r"([A-Z][A-Za-z0-9_]*)\b", stripped)
        if match:
            variants.add(match.group(1))
    return variants


def validate_source_files(
    repo_root: Path,
    source_files: Any,
    errors: list[str],
) -> tuple[dict[str, Path], dict[str, str]]:
    if not isinstance(source_files, dict) or not source_files:
        errors.append("source_files must be a non-empty object")
        return {}, {}

    resolved_paths: dict[str, Path] = {}
    sources: dict[str, str] = {}
    for key, value in source_files.items():
        if not is_nonempty_string(key) or not is_nonempty_string(value):
            errors.append("source_files entries must map non-empty keys to non-empty paths")
            continue
        resolved = resolve_repo_path(repo_root, str(value))
        if not is_inside_repo(repo_root, resolved):
            errors.append(f"source_files.{key} must stay inside repository: {value}")
            continue
        if not resolved.exists():
            errors.append(f"source_files.{key} does not exist: {value}")
            continue
        resolved_paths[str(key)] = resolved
        sources[str(key)] = resolved.read_text(encoding="utf-8")
    return resolved_paths, sources


def validate_structs(contract: dict[str, Any], sources: dict[str, str]) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    reports: list[dict[str, Any]] = []
    errors: list[str] = []
    warnings: list[str] = []
    structs = contract.get("public_structs")
    if not isinstance(structs, list) or not structs:
        return reports, ["public_structs must be a non-empty list"], warnings

    for index, item in enumerate(structs):
        if not isinstance(item, dict):
            errors.append(f"public_structs[{index}] must be an object")
            continue
        file_key = item.get("file")
        name = item.get("name")
        label = str(name) if is_nonempty_string(name) else f"public_structs[{index}]"
        if not is_nonempty_string(file_key) or file_key not in sources:
            errors.append(f"{label}: file must reference a known source_files key")
            continue
        if not is_nonempty_string(name):
            errors.append(f"{label}: name must be non-empty")
            continue

        source = sources[str(file_key)]
        block = find_struct_block(source, str(name))
        impl_block = find_impl_block(source, str(name))
        if block is None:
            errors.append(f"{label}: pub struct not found")
            fields: set[str] = set()
        else:
            fields = parse_pub_fields(block)
        methods = parse_methods(impl_block or "")

        required_fields = string_list(item.get("required_fields"))
        required_methods = string_list(item.get("required_methods"))
        missing_fields = sorted(set(required_fields) - fields)
        missing_methods = sorted(set(required_methods) - methods)
        for field in missing_fields:
            errors.append(f"{label}: missing public field `{field}`")
        for method in missing_methods:
            errors.append(f"{label}: missing public method `{method}`")
        if not required_fields and not required_methods:
            warnings.append(f"{label}: has no required fields or methods")

        reports.append(
            {
                "name": str(name),
                "file": str(file_key),
                "required_field_count": len(required_fields),
                "missing_field_count": len(missing_fields),
                "required_method_count": len(required_methods),
                "missing_method_count": len(missing_methods),
            }
        )

    return reports, errors, warnings


def validate_enums(contract: dict[str, Any], sources: dict[str, str]) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    reports: list[dict[str, Any]] = []
    errors: list[str] = []
    warnings: list[str] = []
    enums = contract.get("public_enums")
    if not isinstance(enums, list) or not enums:
        return reports, ["public_enums must be a non-empty list"], warnings

    for index, item in enumerate(enums):
        if not isinstance(item, dict):
            errors.append(f"public_enums[{index}] must be an object")
            continue
        file_key = item.get("file")
        name = item.get("name")
        label = str(name) if is_nonempty_string(name) else f"public_enums[{index}]"
        if not is_nonempty_string(file_key) or file_key not in sources:
            errors.append(f"{label}: file must reference a known source_files key")
            continue
        if not is_nonempty_string(name):
            errors.append(f"{label}: name must be non-empty")
            continue

        block = find_enum_block(sources[str(file_key)], str(name))
        if block is None:
            errors.append(f"{label}: pub enum not found")
            variants: set[str] = set()
        else:
            variants = parse_enum_variants(block)
        required_variants = string_list(item.get("required_variants"))
        missing_variants = sorted(set(required_variants) - variants)
        for variant in missing_variants:
            errors.append(f"{label}: missing variant `{variant}`")
        if not required_variants:
            warnings.append(f"{label}: has no required variants")
        reports.append(
            {
                "name": str(name),
                "file": str(file_key),
                "required_variant_count": len(required_variants),
                "missing_variant_count": len(missing_variants),
            }
        )

    return reports, errors, warnings


def validate_reexports(contract: dict[str, Any], sources: dict[str, str]) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    reports: list[dict[str, Any]] = []
    errors: list[str] = []
    warnings: list[str] = []
    reexports = contract.get("reexports", [])
    if not isinstance(reexports, list):
        return reports, ["reexports must be a list when present"], warnings
    for index, item in enumerate(reexports):
        if not isinstance(item, dict):
            errors.append(f"reexports[{index}] must be an object")
            continue
        file_key = item.get("file")
        label = f"reexports[{index}]"
        if not is_nonempty_string(file_key) or file_key not in sources:
            errors.append(f"{label}: file must reference a known source_files key")
            continue
        symbols = string_list(item.get("symbols"))
        source = sources[str(file_key)]
        missing = [symbol for symbol in symbols if not re.search(rf"\b{re.escape(symbol)}\b", source)]
        for symbol in missing:
            errors.append(f"{label}: missing re-export symbol `{symbol}`")
        reports.append(
            {
                "file": str(file_key),
                "symbol_count": len(symbols),
                "missing_symbol_count": len(missing),
            }
        )
    return reports, errors, warnings


def validate_contract_metadata(contract: dict[str, Any], errors: list[str]) -> None:
    if not isinstance(contract.get("contract_version"), int) or contract["contract_version"] <= 0:
        errors.append("contract_version must be a positive integer")
    for field in ("contract_id", "ruleset_version", "status", "summary"):
        if not is_nonempty_string(contract.get(field)):
            errors.append(f"{field} must be non-empty")
    compatibility = contract.get("compatibility_policy")
    if not isinstance(compatibility, dict):
        errors.append("compatibility_policy must be an object")
        return
    for field in REQUIRED_COMPATIBILITY_FLAGS:
        if compatibility.get(field) is not True:
            errors.append(f"compatibility_policy.{field} must be true")


def build_report(contract_path: Path, repo_root: Path) -> dict[str, Any]:
    contract = load_json_object(contract_path)
    errors: list[str] = []
    warnings: list[str] = []
    validate_contract_metadata(contract, errors)
    resolved_paths, sources = validate_source_files(repo_root, contract.get("source_files"), errors)

    struct_reports, struct_errors, struct_warnings = validate_structs(contract, sources)
    enum_reports, enum_errors, enum_warnings = validate_enums(contract, sources)
    reexport_reports, reexport_errors, reexport_warnings = validate_reexports(contract, sources)
    errors.extend(struct_errors)
    errors.extend(enum_errors)
    errors.extend(reexport_errors)
    warnings.extend(struct_warnings)
    warnings.extend(enum_warnings)
    warnings.extend(reexport_warnings)

    known_gaps = string_list(contract.get("known_gaps"))
    if not known_gaps:
        warnings.append("known_gaps should document source-shape validation limitations")

    return {
        "report_version": 1,
        "source": str(contract_path),
        "repo_root": str(repo_root),
        "contract_id": contract.get("contract_id"),
        "ruleset_version": contract.get("ruleset_version"),
        "decision": "gamecore_api_contract_valid" if not errors else "gamecore_api_contract_invalid",
        "source_file_count": len(resolved_paths),
        "struct_count": len(struct_reports),
        "enum_count": len(enum_reports),
        "reexport_group_count": len(reexport_reports),
        "known_gap_count": len(known_gaps),
        "errors": errors,
        "warnings": warnings,
        "structs": struct_reports,
        "enums": enum_reports,
        "reexports": reexport_reports,
        "limitations": [
            "This validator checks Rust source shape only; it does not compile or execute GameCore.",
            "It cannot prove deterministic semantics, replay compatibility, runtime integration, or Gym behavior.",
            "Recovering local binary launch remains required before cargo test and Harness validation can prove docs/14 complete.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# GameCore API Contract Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Contract: `{report['contract_id']}`",
        f"- Ruleset: `{report['ruleset_version']}`",
        f"- Decision: `{report['decision']}`",
        f"- Source files: {report['source_file_count']}",
        f"- Structs: {report['struct_count']}",
        f"- Enums: {report['enum_count']}",
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
    lines.extend(["", "## Known Gaps", ""])
    lines.append(f"- Count: {report['known_gap_count']}")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm GameCore API contract source shape.")
    parser.add_argument(
        "contract",
        type=Path,
        nargs="?",
        default=Path("harness/interface_contract/gamecore_api_contract_v0.json"),
        help="GameCore API contract JSON",
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON validation report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown validation summary")
    args = parser.parse_args()

    report = build_report(args.contract, args.repo_root)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "gamecore_api_contract_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
