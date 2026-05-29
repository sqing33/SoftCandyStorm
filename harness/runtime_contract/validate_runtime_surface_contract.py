#!/usr/bin/env python3
"""Validate Runtime surface source-shape contracts.

This dependency-free gate checks the Rust Runtime source for local data
controls, save controls, meta panel tabs, privacy settings, and upload consent
placeholders. It does not compile or execute Bevy.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REQUIRED_SAFETY_FLAGS = {
    "local_data_delete_requires_explicit_root": True,
    "save_delete_requires_save_file": True,
    "upload_transport_marked_not_implemented": True,
}
REQUIRED_KNOWN_GAPS = {
    "source_shape_only_no_rust_compile",
    "no_bevy_runtime_smoke",
    "no_platform_path_runtime_resolution",
    "no_manual_playtest_or_privacy_review",
}


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


def string_set(value: Any) -> set[str]:
    return set(string_list(value))


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
    match = re.search(rf"\b(?:pub\s+)?struct\s+{re.escape(name)}\b", source)
    if not match:
        return None
    return brace_block(source, match.end())


def find_enum_block(source: str, name: str) -> str | None:
    match = re.search(rf"\b(?:pub\s+)?enum\s+{re.escape(name)}\b", source)
    if not match:
        return None
    return brace_block(source, match.end())


def parse_fields(block: str) -> set[str]:
    return set(re.findall(r"\b(?:pub\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*:", block))


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


def validate_metadata(contract: dict[str, Any], errors: list[str]) -> None:
    if not isinstance(contract.get("contract_version"), int) or contract["contract_version"] <= 0:
        errors.append("contract_version must be a positive integer")
    for field in ("contract_id", "ruleset_version", "status", "summary"):
        if not is_nonempty_string(contract.get(field)):
            errors.append(f"{field} must be non-empty")


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


def validate_structs(contract: dict[str, Any], sources: dict[str, str]) -> tuple[list[dict[str, Any]], list[str]]:
    reports: list[dict[str, Any]] = []
    errors: list[str] = []
    structs = contract.get("required_structs")
    if not isinstance(structs, list) or not structs:
        return reports, ["required_structs must be a non-empty list"]

    for index, item in enumerate(structs):
        if not isinstance(item, dict):
            errors.append(f"required_structs[{index}] must be an object")
            continue
        file_key = item.get("file")
        name = item.get("name")
        label = str(name) if is_nonempty_string(name) else f"required_structs[{index}]"
        if not is_nonempty_string(file_key) or file_key not in sources:
            errors.append(f"{label}: file must reference a known source_files key")
            continue
        if not is_nonempty_string(name):
            errors.append(f"{label}: name must be non-empty")
            continue

        block = find_struct_block(sources[str(file_key)], str(name))
        if block is None:
            errors.append(f"{label}: struct not found")
            fields: set[str] = set()
        else:
            fields = parse_fields(block)
        required_fields = string_list(item.get("required_fields"))
        missing_fields = sorted(set(required_fields) - fields)
        for field in missing_fields:
            errors.append(f"{label}: missing field `{field}`")
        reports.append(
            {
                "name": str(name),
                "file": str(file_key),
                "required_field_count": len(required_fields),
                "missing_field_count": len(missing_fields),
            }
        )
    return reports, errors


def validate_enums(contract: dict[str, Any], sources: dict[str, str]) -> tuple[list[dict[str, Any]], list[str]]:
    reports: list[dict[str, Any]] = []
    errors: list[str] = []
    enums = contract.get("required_enums")
    if not isinstance(enums, list) or not enums:
        return reports, ["required_enums must be a non-empty list"]

    for index, item in enumerate(enums):
        if not isinstance(item, dict):
            errors.append(f"required_enums[{index}] must be an object")
            continue
        file_key = item.get("file")
        name = item.get("name")
        label = str(name) if is_nonempty_string(name) else f"required_enums[{index}]"
        if not is_nonempty_string(file_key) or file_key not in sources:
            errors.append(f"{label}: file must reference a known source_files key")
            continue
        if not is_nonempty_string(name):
            errors.append(f"{label}: name must be non-empty")
            continue

        block = find_enum_block(sources[str(file_key)], str(name))
        if block is None:
            errors.append(f"{label}: enum not found")
            variants: set[str] = set()
        else:
            variants = parse_enum_variants(block)
        required_variants = string_list(item.get("required_variants"))
        missing_variants = sorted(set(required_variants) - variants)
        for variant in missing_variants:
            errors.append(f"{label}: missing variant `{variant}`")
        reports.append(
            {
                "name": str(name),
                "file": str(file_key),
                "required_variant_count": len(required_variants),
                "missing_variant_count": len(missing_variants),
            }
        )
    return reports, errors


def source_contains_function(source: str, name: str) -> bool:
    return bool(re.search(rf"\bfn\s+{re.escape(name)}\s*\(", source))


def validate_functions_and_fragments(contract: dict[str, Any], source: str) -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    reports: list[dict[str, Any]] = []

    required_functions = string_list(contract.get("required_functions"))
    missing_functions = [name for name in required_functions if not source_contains_function(source, name)]
    for name in missing_functions:
        errors.append(f"required_functions missing `{name}`")
    reports.append(
        {
            "kind": "functions",
            "required_count": len(required_functions),
            "missing_count": len(missing_functions),
        }
    )

    required_flags = string_list(contract.get("required_cli_flags"))
    missing_flags = [flag for flag in required_flags if flag not in source]
    for flag in missing_flags:
        errors.append(f"required_cli_flags missing `{flag}`")
    reports.append(
        {
            "kind": "cli_flags",
            "required_count": len(required_flags),
            "missing_count": len(missing_flags),
        }
    )

    required_fragments = string_list(contract.get("required_source_fragments"))
    missing_fragments = [fragment for fragment in required_fragments if fragment not in source]
    for fragment in missing_fragments:
        errors.append(f"required_source_fragments missing `{fragment}`")
    reports.append(
        {
            "kind": "source_fragments",
            "required_count": len(required_fragments),
            "missing_count": len(missing_fragments),
        }
    )
    return reports, errors


def validate_key_bindings(contract: dict[str, Any], source: str) -> tuple[list[dict[str, Any]], list[str]]:
    bindings = contract.get("required_key_bindings")
    if not isinstance(bindings, list) or not bindings:
        return [], ["required_key_bindings must be a non-empty list"]

    errors: list[str] = []
    reports: list[dict[str, Any]] = []
    for index, binding in enumerate(bindings):
        if not isinstance(binding, dict):
            errors.append(f"required_key_bindings[{index}] must be an object")
            continue
        key = binding.get("key")
        target = binding.get("target")
        label = f"required_key_bindings[{index}]"
        if not is_nonempty_string(key) or not is_nonempty_string(target):
            errors.append(f"{label}: key and target must be non-empty")
            continue
        key_present = str(key) in source
        target_present = str(target) in source
        if not key_present:
            errors.append(f"{label}: missing key `{key}`")
        if not target_present:
            errors.append(f"{label}: missing target `{target}`")
        reports.append(
            {
                "key": str(key),
                "target": str(target),
                "key_present": key_present,
                "target_present": target_present,
            }
        )
    return reports, errors


def validate_defaults_and_safety(contract: dict[str, Any], source: str) -> list[str]:
    errors: list[str] = []
    defaults = contract.get("default_privacy_settings")
    if not isinstance(defaults, dict):
        errors.append("default_privacy_settings must be an object")
    else:
        for field in ("telemetry_upload_enabled", "raw_replay_upload_enabled", "crash_report_upload_enabled"):
            if defaults.get(field) is not False:
                errors.append(f"default_privacy_settings.{field} must be false")

    safety = contract.get("required_data_safety")
    if not isinstance(safety, dict):
        errors.append("required_data_safety must be an object")
        return errors
    for field, expected in REQUIRED_SAFETY_FLAGS.items():
        if safety.get(field) is not expected:
            errors.append(f"required_data_safety.{field} must be {json.dumps(expected)}")
    if safety.get("local_data_export_format") != "json":
        errors.append("required_data_safety.local_data_export_format must be json")
    if safety.get("save_export_format") != "json":
        errors.append("required_data_safety.save_export_format must be json")

    source_guards = {
        "local_data_delete_requires_explicit_root": "explicit_local_data_dirs.is_empty()",
        "save_delete_requires_save_file": "delete save requires --save-file",
        "upload_transport_marked_not_implemented": "上传传输层: not_implemented",
    }
    for field, fragment in source_guards.items():
        if safety.get(field) is True and fragment not in source:
            errors.append(f"{field}: source missing guard `{fragment}`")
    return errors


def validate_known_gaps(contract: dict[str, Any], warnings: list[str]) -> None:
    missing = sorted(REQUIRED_KNOWN_GAPS - string_set(contract.get("known_gaps")))
    if missing:
        warnings.append(f"known_gaps missing recommended entries: {', '.join(missing)}")


def build_report(contract_path: Path, repo_root: Path) -> dict[str, Any]:
    contract = load_json_object(contract_path)
    errors: list[str] = []
    warnings: list[str] = []

    validate_metadata(contract, errors)
    resolved_paths, sources = validate_source_files(repo_root, contract.get("source_files"), errors)
    combined_source = "\n".join(sources.values())

    struct_reports, struct_errors = validate_structs(contract, sources)
    enum_reports, enum_errors = validate_enums(contract, sources)
    fragment_reports, fragment_errors = validate_functions_and_fragments(contract, combined_source)
    binding_reports, binding_errors = validate_key_bindings(contract, combined_source)
    safety_errors = validate_defaults_and_safety(contract, combined_source)
    validate_known_gaps(contract, warnings)

    errors.extend(struct_errors)
    errors.extend(enum_errors)
    errors.extend(fragment_errors)
    errors.extend(binding_errors)
    errors.extend(safety_errors)

    return {
        "report_version": 1,
        "source": str(contract_path),
        "repo_root": str(repo_root),
        "contract_id": contract.get("contract_id"),
        "ruleset_version": contract.get("ruleset_version"),
        "decision": "runtime_surface_contract_valid" if not errors else "runtime_surface_contract_invalid",
        "source_file_count": len(resolved_paths),
        "struct_count": len(struct_reports),
        "enum_count": len(enum_reports),
        "key_binding_count": len(binding_reports),
        "errors": errors,
        "warnings": warnings,
        "structs": struct_reports,
        "enums": enum_reports,
        "checks": fragment_reports,
        "key_bindings": binding_reports,
        "limitations": [
            "This validator checks Rust source shape only; it does not compile or execute Bevy Runtime.",
            "It cannot prove keyboard behavior, rendered UI, platform path resolution, save migration, or upload transport behavior.",
            "Runtime smoke, platform path review, and manual playtest remain required before docs/16 and docs/18 can be marked complete.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Runtime Surface Contract Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Contract: `{report['contract_id']}`",
        f"- Ruleset: `{report['ruleset_version']}`",
        f"- Decision: `{report['decision']}`",
        f"- Source files: {report['source_file_count']}",
        f"- Structs: {report['struct_count']}",
        f"- Enums: {report['enum_count']}",
        f"- Key bindings: {report['key_binding_count']}",
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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm Runtime surface contract source shape.")
    parser.add_argument(
        "contract",
        type=Path,
        nargs="?",
        default=Path("harness/runtime_contract/runtime_surface_contract_v0.json"),
        help="Runtime surface contract JSON",
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
    return 0 if report["decision"] == "runtime_surface_contract_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
