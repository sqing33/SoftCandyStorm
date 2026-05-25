#!/usr/bin/env python3
"""Validate generated asset candidate metadata.

The validator is dependency-free and intentionally conservative: it checks that
AI or post-processed asset batches stay in candidate-only state, keep provenance
records, and reference files that actually exist. It does not decide whether art
or audio is good enough for the game.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PATH_FIELDS = [
    "path",
    "processed_path",
    "runtime_32_path",
    "postprocess_manifest",
]

REQUIRED_PROJECT_RULES = {
    "candidate_only": True,
    "accepted_content": False,
    "runtime_integrated": False,
}


def load_json(path: Path) -> dict[str, Any]:
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


def discover_manifests(root: Path) -> list[Path]:
    if (root / "metadata" / "manifest.json").exists():
        return [root / "metadata" / "manifest.json"]
    return sorted(root.glob("*/metadata/manifest.json"))


def resolve_candidate_path(batch_dir: Path, value: str) -> Path:
    return (batch_dir / value).resolve()


def validate_referenced_paths(batch_dir: Path, asset: dict[str, Any], asset_id: str) -> list[str]:
    errors: list[str] = []
    referenced = False

    for field in PATH_FIELDS:
        value = asset.get(field)
        if value is None:
            continue
        if not is_nonempty_string(value):
            errors.append(f"{asset_id}: `{field}` must be a non-empty string")
            continue
        referenced = True
        if not resolve_candidate_path(batch_dir, value).exists():
            errors.append(f"{asset_id}: referenced `{field}` does not exist: {value}")

    for field in ("source_path",):
        value = asset.get(field)
        if value is None:
            continue
        if not is_nonempty_string(value):
            errors.append(f"{asset_id}: `{field}` must be a non-empty string")
            continue
        referenced = True
        if not resolve_candidate_path(batch_dir, value).exists():
            errors.append(f"{asset_id}: referenced `{field}` does not exist: {value}")

    preview_paths = asset.get("preview_paths")
    if preview_paths is not None:
        if not isinstance(preview_paths, list):
            errors.append(f"{asset_id}: `preview_paths` must be a list")
        else:
            for preview_path in preview_paths:
                if not is_nonempty_string(preview_path):
                    errors.append(f"{asset_id}: `preview_paths` entries must be non-empty strings")
                    continue
                referenced = True
                if not resolve_candidate_path(batch_dir, preview_path).exists():
                    errors.append(f"{asset_id}: preview path does not exist: {preview_path}")

    if not referenced:
        errors.append(f"{asset_id}: asset must reference at least one candidate file")
    return errors


def validate_asset(batch_dir: Path, asset: Any, index: int) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(asset, dict):
        return [f"assets[{index}] must be an object"], warnings

    asset_id = asset.get("id", f"assets[{index}]")
    if not is_nonempty_string(asset_id):
        errors.append(f"assets[{index}]: `id` must be a non-empty string")
        asset_id = f"assets[{index}]"

    if not is_nonempty_string(asset.get("type")):
        warnings.append(f"{asset_id}: missing optional `type` field")

    errors.extend(validate_referenced_paths(batch_dir, asset, str(asset_id)))

    if not is_nonempty_string(asset.get("qa_status")):
        errors.append(f"{asset_id}: `qa_status` must be a non-empty string")

    qa_notes = string_list(asset.get("qa_notes"))
    if not qa_notes:
        errors.append(f"{asset_id}: `qa_notes` must be a non-empty list of strings")

    if not (
        is_nonempty_string(asset.get("prompt"))
        or is_nonempty_string(asset.get("source_path"))
        or is_nonempty_string(asset.get("postprocess_manifest"))
    ):
        warnings.append(f"{asset_id}: missing prompt/source/postprocess provenance field")

    return errors, warnings


def validate_manifest(manifest_path: Path, require_commands: bool) -> dict[str, Any]:
    payload = load_json(manifest_path)
    batch_dir = manifest_path.parents[1]
    errors: list[str] = []
    warnings: list[str] = []

    batch_id = payload.get("batch_id")
    if not is_nonempty_string(batch_id):
        errors.append("`batch_id` must be a non-empty string")
        batch_id = batch_dir.name
    elif batch_id != batch_dir.name:
        warnings.append(f"`batch_id` `{batch_id}` does not match directory `{batch_dir.name}`")

    if not is_nonempty_string(payload.get("generated_at")):
        errors.append("`generated_at` must be a non-empty string")

    project_rules = payload.get("project_rules")
    if not isinstance(project_rules, dict):
        errors.append("`project_rules` must be an object")
        project_rules = {}
    for key, expected in REQUIRED_PROJECT_RULES.items():
        if project_rules.get(key) is not expected:
            errors.append(f"`project_rules.{key}` must be {json.dumps(expected)}")

    required_next_steps = string_list(project_rules.get("required_next_steps"))
    if not required_next_steps:
        errors.append("`project_rules.required_next_steps` must be a non-empty list of strings")

    generator = payload.get("generator")
    is_mmx_batch = "mmx" in str(batch_id)
    if is_mmx_batch:
        if not isinstance(generator, dict) or generator.get("tool") != "mmx-cli":
            errors.append("mmx batch requires `generator.tool` to be `mmx-cli`")
    elif generator is not None and not isinstance(generator, dict):
        errors.append("`generator` must be an object when present")

    commands = string_list(payload.get("commands"))
    if is_mmx_batch and not commands:
        message = "mmx batch should record generation commands"
        if require_commands:
            errors.append(message)
        else:
            warnings.append(message)

    assets = payload.get("assets")
    if not isinstance(assets, list) or not assets:
        errors.append("`assets` must be a non-empty list")
        assets = []

    for index, asset in enumerate(assets):
        asset_errors, asset_warnings = validate_asset(batch_dir, asset, index)
        errors.extend(asset_errors)
        warnings.extend(asset_warnings)

    if not (batch_dir / "README.md").exists():
        warnings.append("batch is missing README.md")
    if not list((batch_dir / "metadata").glob("review_*.md")):
        warnings.append("batch is missing metadata/review_*.md")

    return {
        "batch_id": batch_id,
        "manifest": str(manifest_path),
        "asset_count": len(assets),
        "errors": errors,
        "warnings": warnings,
    }


def build_report(root: Path, require_commands: bool) -> dict[str, Any]:
    manifests = discover_manifests(root)
    batches = [validate_manifest(path, require_commands) for path in manifests]
    errors = [
        f"{batch['batch_id']}: {error}"
        for batch in batches
        for error in batch["errors"]
    ]
    warnings = [
        f"{batch['batch_id']}: {warning}"
        for batch in batches
        for warning in batch["warnings"]
    ]
    if not manifests:
        errors.append(f"no asset candidate manifests found under {root}")
    return {
        "report_version": 1,
        "root": str(root),
        "require_commands": require_commands,
        "decision": "asset_candidates_valid" if not errors else "asset_candidates_invalid",
        "batch_count": len(batches),
        "asset_count": sum(batch["asset_count"] for batch in batches),
        "errors": errors,
        "warnings": warnings,
        "batches": batches,
        "limitations": [
            "This validator checks metadata and referenced files only; it does not judge visual or audio quality.",
            "A passing report does not promote assets out of generated_candidates or replace human review.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Asset Candidate Metadata Validation",
        "",
        f"- Root: `{report['root']}`",
        f"- Decision: `{report['decision']}`",
        f"- Batch count: {report['batch_count']}",
        f"- Asset count: {report['asset_count']}",
        f"- Require commands: {report['require_commands']}",
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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm generated asset candidates.")
    parser.add_argument(
        "root",
        type=Path,
        nargs="?",
        default=Path("asset/generated_candidates"),
        help="Generated asset candidate root or a single batch directory",
    )
    parser.add_argument(
        "--require-commands",
        action="store_true",
        help="Fail mmx batches that do not record the exact generation commands",
    )
    parser.add_argument("--report", type=Path, default=None, help="Write JSON validation report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown validation summary")
    args = parser.parse_args()

    report = build_report(args.root, args.require_commands)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "asset_candidates_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
