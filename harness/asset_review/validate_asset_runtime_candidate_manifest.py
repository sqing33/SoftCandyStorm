#!/usr/bin/env python3
"""Validate asset Runtime candidate manifests.

This gate checks manifests produced after a human `asset_candidate` review. It
does not accept generated assets into accepted_content and does not prove
Runtime integration, listening quality, licensing, or final art acceptance.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from validate_asset_candidate_manual_review import build_report as build_manual_review_report


EXPECTED_CONTRACT_ID = "asset-runtime-candidate-manifest-v0"
EXPECTED_STAGE = "asset_runtime_candidate"
TODO_MARKERS = ("TODO", "<", ">")
REQUIRED_PROJECT_RULES = {
    "candidate_only": True,
    "accepted_content": False,
    "runtime_integrated": False,
}
REQUIRED_RULES = {
    "accepted_content": False,
    "runtime_integrated": False,
    "release_ready": False,
    "requires_runtime_preview": True,
    "requires_audio_loudness_review": True,
    "requires_final_human_acceptance": True,
}


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def has_placeholder(value: Any) -> bool:
    if isinstance(value, str):
        return any(marker in value for marker in TODO_MARKERS)
    if isinstance(value, list):
        return any(has_placeholder(item) for item in value)
    if isinstance(value, dict):
        return any(has_placeholder(item) for item in value.values())
    return False


def resolve_repo_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def relative_repo_path(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(path)


def is_inside(base_dir: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(base_dir.resolve())
    except ValueError:
        return False
    return True


def require_existing_repo_path(
    payload: dict[str, Any],
    field: str,
    repo_root: Path,
    errors: list[str],
) -> Path | None:
    value = payload.get(field)
    if not is_nonempty_string(value):
        errors.append(f"{field} must be non-empty")
        return None
    if has_placeholder(value):
        errors.append(f"{field} must not contain TODO or placeholder markers")
        return None
    path = resolve_repo_path(repo_root, str(value))
    if not is_inside(repo_root, path):
        errors.append(f"{field} must stay inside repository: {value}")
        return None
    if not path.exists():
        errors.append(f"{field} does not exist: {value}")
        return None
    return path


def validate_top_level(payload: dict[str, Any], errors: list[str]) -> None:
    if not isinstance(payload.get("manifest_version"), int) or payload["manifest_version"] <= 0:
        errors.append("manifest_version must be a positive integer")
    expected_strings = {
        "manifest_contract_id": EXPECTED_CONTRACT_ID,
        "stage": EXPECTED_STAGE,
        "manual_gate_decision": "asset_candidate",
    }
    for field, expected in expected_strings.items():
        if payload.get(field) != expected:
            errors.append(f"{field} must be `{expected}`")
    for field in ("candidate_batch_id", "promoted_at"):
        if not is_nonempty_string(payload.get(field)):
            errors.append(f"{field} must be non-empty")
        elif has_placeholder(payload.get(field)):
            errors.append(f"{field} must not contain TODO or placeholder markers")


def validate_rules(payload: dict[str, Any], errors: list[str]) -> None:
    rules = payload.get("rules")
    if not isinstance(rules, dict):
        errors.append("rules must be an object")
        return
    for field, expected in REQUIRED_RULES.items():
        if rules.get(field) is not expected:
            errors.append(f"rules.{field} must be {json.dumps(expected)}")


def validate_source_candidate(
    candidate_dir: Path | None,
    payload: dict[str, Any],
    errors: list[str],
) -> dict[str, dict[str, Any]]:
    if candidate_dir is None:
        return {}
    if payload.get("candidate_batch_id") != candidate_dir.name:
        errors.append("candidate_batch_id must match source_candidate_batch directory name")

    manifest_path = candidate_dir / "metadata" / "manifest.json"
    if not manifest_path.exists():
        errors.append("source_candidate_batch missing metadata/manifest.json")
        return {}

    try:
        manifest = load_json_object(manifest_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"source candidate manifest is invalid: {error}")
        return {}

    manifest_batch_id = manifest.get("batch_id")
    if is_nonempty_string(manifest_batch_id) and manifest_batch_id != candidate_dir.name:
        errors.append("source candidate manifest batch_id must match source_candidate_batch directory name")

    project_rules = manifest.get("project_rules")
    if not isinstance(project_rules, dict):
        errors.append("source candidate manifest project_rules must be an object")
    else:
        for field, expected in REQUIRED_PROJECT_RULES.items():
            if project_rules.get(field) is not expected:
                errors.append(f"source candidate project_rules.{field} must be {json.dumps(expected)}")

    source_assets = manifest.get("assets")
    if not isinstance(source_assets, list) or not source_assets:
        errors.append("source candidate manifest assets must be a non-empty list")
        return {}

    source_index: dict[str, dict[str, Any]] = {}
    for index, asset in enumerate(source_assets):
        if not isinstance(asset, dict):
            errors.append(f"source candidate manifest assets[{index}] must be an object")
            continue
        asset_id = asset.get("id")
        if not is_nonempty_string(asset_id):
            errors.append(f"source candidate manifest assets[{index}] missing id")
            continue
        if asset_id in source_index:
            errors.append(f"source candidate manifest duplicate asset id `{asset_id}`")
            continue
        source_index[str(asset_id)] = asset
    return source_index


def validate_manual_review(
    manual_review_path: Path | None,
    repo_root: Path,
    payload: dict[str, Any],
    errors: list[str],
) -> dict[str, Any] | None:
    if manual_review_path is None:
        return None
    report = build_manual_review_report(manual_review_path, repo_root)
    if report["decision"] != "asset_candidate_manual_review_valid":
        errors.append("manual_review_file must validate")
    if report.get("gate_decision") != "asset_candidate":
        errors.append("manual_review_file gate_decision must be asset_candidate")
    if report.get("asset_review_count") != payload.get("asset_count"):
        errors.append("asset_count must match manual review asset count")
    return report


def validate_asset_path(root_dir: Path, asset_path: str, label: str, errors: list[str]) -> None:
    path = Path(asset_path)
    if path.is_absolute():
        errors.append(f"{label} path must be relative to the candidate directory")
        return
    resolved = root_dir / path
    if not is_inside(root_dir, resolved):
        errors.append(f"{label} path must stay inside the candidate directory: {asset_path}")
    elif not resolved.exists():
        errors.append(f"{label} path does not exist: {asset_path}")


def validate_assets(
    payload: dict[str, Any],
    runtime_dir: Path,
    source_candidate_dir: Path | None,
    source_assets: dict[str, dict[str, Any]],
    errors: list[str],
) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    assets = payload.get("assets")
    if not isinstance(assets, list) or not assets:
        errors.append("assets must be a non-empty list")
        return reports
    if payload.get("asset_count") != len(assets):
        errors.append("asset_count must match assets length")
    if source_assets and payload.get("asset_count") != len(source_assets):
        errors.append("asset_count must match source candidate asset count")

    seen: set[str] = set()
    for index, asset in enumerate(assets):
        label = f"assets[{index}]"
        if not isinstance(asset, dict):
            errors.append(f"{label} must be an object")
            continue
        asset_id = asset.get("id")
        if not is_nonempty_string(asset_id):
            errors.append(f"{label}.id must be non-empty")
            continue
        display_id = str(asset_id)
        if has_placeholder(display_id):
            errors.append(f"{display_id}: id must not contain TODO or placeholder markers")
        if display_id in seen:
            errors.append(f"{display_id}: duplicate asset id")
        seen.add(display_id)

        source_asset = source_assets.get(display_id)
        if source_assets and source_asset is None:
            errors.append(f"{display_id}: id does not exist in source candidate manifest")
            source_asset = {}
        elif source_asset is None:
            source_asset = {}

        for field in ("type", "path", "qa_status"):
            value = asset.get(field)
            if not is_nonempty_string(value):
                errors.append(f"{display_id}: {field} must be non-empty")
            elif has_placeholder(value):
                errors.append(f"{display_id}: {field} must not contain TODO or placeholder markers")
            if source_asset and value != source_asset.get(field):
                errors.append(f"{display_id}: {field} must match source candidate manifest")

        asset_path = asset.get("path")
        if is_nonempty_string(asset_path):
            validate_asset_path(runtime_dir, str(asset_path), display_id, errors)
            if source_candidate_dir is not None:
                validate_asset_path(source_candidate_dir, str(asset_path), f"{display_id} source", errors)

        allowed_uses = asset.get("allowed_candidate_uses")
        if not isinstance(allowed_uses, list) or not allowed_uses:
            errors.append(f"{display_id}: allowed_candidate_uses must be a non-empty list")
            allowed_use_count = 0
        else:
            invalid_uses = [
                item for item in allowed_uses if not is_nonempty_string(item) or has_placeholder(item)
            ]
            if invalid_uses:
                errors.append(f"{display_id}: allowed_candidate_uses must contain only concrete strings")
            allowed_use_count = len(allowed_uses) - len(invalid_uses)

        reports.append(
            {
                "id": display_id,
                "type": asset.get("type"),
                "qa_status": asset.get("qa_status"),
                "allowed_candidate_use_count": allowed_use_count,
            }
        )

    missing_ids = sorted(set(source_assets) - seen)
    if missing_ids:
        errors.append(f"assets missing source candidate ids: {', '.join(missing_ids)}")
    return reports


def build_report(manifest_path: Path, repo_root: Path) -> dict[str, Any]:
    payload = load_json_object(manifest_path)
    errors: list[str] = []
    warnings: list[str] = []

    validate_top_level(payload, errors)
    validate_rules(payload, errors)
    source_candidate_dir = require_existing_repo_path(payload, "source_candidate_batch", repo_root, errors)
    manual_review_path = require_existing_repo_path(payload, "manual_review_file", repo_root, errors)
    metadata_report_path = require_existing_repo_path(payload, "candidate_metadata_report", repo_root, errors)

    source_assets = validate_source_candidate(source_candidate_dir, payload, errors)
    manual_review_report = validate_manual_review(manual_review_path, repo_root, payload, errors)
    asset_reports = validate_assets(payload, manifest_path.parent, source_candidate_dir, source_assets, errors)

    return {
        "report_version": 1,
        "source": relative_repo_path(repo_root, manifest_path),
        "repo_root": str(repo_root),
        "decision": "asset_runtime_candidate_manifest_valid" if not errors else "asset_runtime_candidate_manifest_invalid",
        "candidate_batch_id": payload.get("candidate_batch_id"),
        "asset_count": payload.get("asset_count"),
        "validated_asset_count": len(asset_reports),
        "candidate_metadata_report": relative_repo_path(repo_root, metadata_report_path)
        if metadata_report_path is not None
        else None,
        "manual_review_decision": manual_review_report["decision"] if manual_review_report is not None else None,
        "manual_gate_decision": manual_review_report["gate_decision"] if manual_review_report is not None else None,
        "errors": errors,
        "warnings": warnings,
        "assets": asset_reports,
        "limitations": [
            "This validator checks Runtime candidate manifest completeness only.",
            "A valid asset Runtime candidate manifest does not promote assets into accepted_content.",
            "A valid asset Runtime candidate manifest does not prove Runtime integration, listening quality, licensing, or release readiness.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Asset Runtime Candidate Manifest Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Decision: `{report['decision']}`",
        f"- Candidate batch: `{report['candidate_batch_id']}`",
        f"- Assets: {report['validated_asset_count']} / {report['asset_count']}",
        f"- Manual review: `{report['manual_review_decision']}` / `{report['manual_gate_decision']}`",
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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm asset Runtime candidate manifests.")
    parser.add_argument("manifest", type=Path, help="Asset Runtime candidate manifest JSON")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown summary")
    args = parser.parse_args()

    report = build_report(args.manifest, args.repo_root)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "asset_runtime_candidate_manifest_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
