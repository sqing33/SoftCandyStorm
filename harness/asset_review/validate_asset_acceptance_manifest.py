#!/usr/bin/env python3
"""Validate final asset acceptance manifests.

This gate verifies that an asset batch has passed Runtime-candidate staging,
Runtime preview review, audio loudness/listening review, and final human
acceptance before it can be treated as accepted asset content. It does not copy
assets into Runtime, mark Runtime integration, or approve release readiness.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from validate_asset_runtime_candidate_manifest import (
    build_report as build_runtime_candidate_manifest_report,
    load_json_object,
)


EXPECTED_CONTRACT_ID = "asset-acceptance-manifest-v0"
EXPECTED_STAGE = "asset_acceptance"
TODO_MARKERS = ("TODO", "<", ">")
REQUIRED_RULES = {
    "accepted_content": True,
    "runtime_integrated": False,
    "release_ready": False,
    "requires_runtime_candidate_manifest": True,
    "requires_runtime_preview": True,
    "requires_audio_loudness_review": True,
    "requires_final_human_acceptance": True,
    "generated_candidate_direct_acceptance_allowed": False,
}
RUNTIME_PREVIEW_REQUIRED_FLAGS = {
    "all_assets_visible_or_audible": True,
    "small_size_readable": True,
    "no_placeholder_leak": True,
    "no_runtime_integration_claim": True,
}
AUDIO_LOUDNESS_REQUIRED_FLAGS = {
    "dialogue_clear_if_present": True,
    "loudness_review_passed": True,
    "no_clipping": True,
    "loop_or_duration_fit": True,
}
FINAL_ACCEPTANCE_REQUIRED_FLAGS = {
    "accepts_asset_batch": True,
    "accepted_content_only_after_reviews": True,
    "release_ready": False,
    "runtime_integrated": False,
}
FORBIDDEN_ACCEPTED_USES = {"runtime_integrated", "release_ready"}


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]


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
    }
    for field, expected in expected_strings.items():
        if payload.get(field) != expected:
            errors.append(f"{field} must be `{expected}`")
    for field in ("candidate_batch_id", "accepted_at"):
        if not is_nonempty_string(payload.get(field)):
            errors.append(f"{field} must be non-empty")
        elif has_placeholder(payload.get(field)):
            errors.append(f"{field} must not contain TODO or placeholder markers")
    if not isinstance(payload.get("asset_count"), int) or payload["asset_count"] <= 0:
        errors.append("asset_count must be a positive integer")


def validate_rules(payload: dict[str, Any], errors: list[str]) -> None:
    rules = payload.get("rules")
    if not isinstance(rules, dict):
        errors.append("rules must be an object")
        return
    for field, expected in REQUIRED_RULES.items():
        if rules.get(field) is not expected:
            errors.append(f"rules.{field} must be {json.dumps(expected)}")


def validate_runtime_candidate_manifest(
    path: Path | None,
    repo_root: Path,
    payload: dict[str, Any],
    errors: list[str],
) -> tuple[dict[str, Any] | None, dict[str, dict[str, Any]]]:
    if path is None:
        return None, {}
    runtime_payload = load_json_object(path)
    report = build_runtime_candidate_manifest_report(path, repo_root)
    if report["decision"] != "asset_runtime_candidate_manifest_valid":
        errors.append("source_runtime_candidate_manifest must validate")
    if report.get("candidate_batch_id") != payload.get("candidate_batch_id"):
        errors.append("candidate_batch_id must match source_runtime_candidate_manifest")
    if report.get("asset_count") != payload.get("asset_count"):
        errors.append("asset_count must match source_runtime_candidate_manifest")
    if report.get("manual_gate_decision") != "asset_candidate":
        errors.append("source_runtime_candidate_manifest manual_gate_decision must be asset_candidate")
    assets = {
        str(item["id"]): item
        for item in runtime_payload.get("assets", [])
        if isinstance(item, dict) and is_nonempty_string(item.get("id"))
    }
    return report, assets


def validate_required_flags(
    payload: dict[str, Any],
    field: str,
    expected_flags: dict[str, bool],
    label: str,
    errors: list[str],
) -> None:
    flags = payload.get(field)
    if not isinstance(flags, dict):
        errors.append(f"{label}.{field} must be an object")
        return
    for flag, expected in expected_flags.items():
        if flags.get(flag) is not expected:
            errors.append(f"{label}.{field}.{flag} must be {json.dumps(expected)}")


def validate_review_file(
    path: Path | None,
    manifest_payload: dict[str, Any],
    expected_review_type: str,
    expected_decision: str,
    required_flags: dict[str, bool],
    label: str,
    errors: list[str],
) -> dict[str, Any] | None:
    if path is None:
        return None
    try:
        payload = load_json_object(path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"{label} is invalid JSON: {error}")
        return None

    if not isinstance(payload.get("review_version"), int) or payload["review_version"] <= 0:
        errors.append(f"{label}.review_version must be a positive integer")
    if payload.get("review_type") != expected_review_type:
        errors.append(f"{label}.review_type must be `{expected_review_type}`")
    if payload.get("candidate_batch_id") != manifest_payload.get("candidate_batch_id"):
        errors.append(f"{label}.candidate_batch_id must match acceptance manifest")
    if payload.get("source_runtime_candidate_manifest") != manifest_payload.get("source_runtime_candidate_manifest"):
        errors.append(f"{label}.source_runtime_candidate_manifest must match acceptance manifest")
    if payload.get("decision") != expected_decision:
        errors.append(f"{label}.decision must be `{expected_decision}`")
    for field in ("reviewer", "reviewed_at", "summary"):
        if not is_nonempty_string(payload.get(field)):
            errors.append(f"{label}.{field} must be non-empty")
        elif has_placeholder(payload.get(field)):
            errors.append(f"{label}.{field} must not contain TODO or placeholder markers")
    concrete_observations = string_list(payload.get("concrete_observations"))
    if len(concrete_observations) < 2:
        errors.append(f"{label}.concrete_observations must contain at least two concrete items")
    unresolved_issues = string_list(payload.get("unresolved_issues"))
    if unresolved_issues:
        errors.append(f"{label}.unresolved_issues must be empty for {expected_decision}")
    validate_required_flags(payload, "checks", required_flags, label, errors)
    return payload


def validate_accepted_assets(
    payload: dict[str, Any],
    source_assets: dict[str, dict[str, Any]],
    errors: list[str],
) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    assets = payload.get("accepted_assets")
    if not isinstance(assets, list) or not assets:
        errors.append("accepted_assets must be a non-empty list")
        return reports
    if payload.get("asset_count") != len(assets):
        errors.append("asset_count must match accepted_assets length")

    seen: set[str] = set()
    for index, asset in enumerate(assets):
        label = f"accepted_assets[{index}]"
        if not isinstance(asset, dict):
            errors.append(f"{label} must be an object")
            continue
        asset_id = asset.get("id")
        display_id = str(asset_id) if is_nonempty_string(asset_id) else label
        if not is_nonempty_string(asset_id):
            errors.append(f"{label}.id must be non-empty")
            continue
        if has_placeholder(display_id):
            errors.append(f"{display_id}: id must not contain TODO or placeholder markers")
        if display_id in seen:
            errors.append(f"{display_id}: duplicate accepted asset id")
        seen.add(display_id)

        source_asset = source_assets.get(display_id)
        if source_assets and source_asset is None:
            errors.append(f"{display_id}: id does not exist in source Runtime candidate manifest")
            source_asset = {}
        elif source_asset is None:
            source_asset = {}

        accepted_use = asset.get("accepted_use")
        if not is_nonempty_string(accepted_use):
            errors.append(f"{display_id}: accepted_use must be non-empty")
        elif has_placeholder(accepted_use):
            errors.append(f"{display_id}: accepted_use must not contain TODO or placeholder markers")
        elif accepted_use in FORBIDDEN_ACCEPTED_USES:
            errors.append(f"{display_id}: accepted_use must not claim {accepted_use}")

        for field, source_field in (("type", "type"), ("source_path", "path")):
            value = asset.get(field)
            if not is_nonempty_string(value):
                errors.append(f"{display_id}: {field} must be non-empty")
            elif has_placeholder(value):
                errors.append(f"{display_id}: {field} must not contain TODO or placeholder markers")
            if source_asset and value != source_asset.get(source_field):
                errors.append(f"{display_id}: {field} must match source Runtime candidate manifest {source_field}")

        reports.append(
            {
                "id": display_id,
                "type": asset.get("type"),
                "accepted_use": asset.get("accepted_use"),
            }
        )

    missing_ids = sorted(set(source_assets) - seen)
    if missing_ids:
        errors.append(f"accepted_assets missing source Runtime candidate ids: {', '.join(missing_ids)}")
    return reports


def build_report(manifest_path: Path, repo_root: Path) -> dict[str, Any]:
    payload = load_json_object(manifest_path)
    errors: list[str] = []
    warnings: list[str] = []

    validate_top_level(payload, errors)
    validate_rules(payload, errors)
    runtime_manifest_path = require_existing_repo_path(payload, "source_runtime_candidate_manifest", repo_root, errors)
    runtime_preview_review_path = require_existing_repo_path(payload, "runtime_preview_review_file", repo_root, errors)
    audio_loudness_review_path = require_existing_repo_path(payload, "audio_loudness_review_file", repo_root, errors)
    final_acceptance_path = require_existing_repo_path(payload, "final_human_acceptance_file", repo_root, errors)

    runtime_manifest_report, source_assets = validate_runtime_candidate_manifest(
        runtime_manifest_path,
        repo_root,
        payload,
        errors,
    )
    runtime_preview_review = validate_review_file(
        runtime_preview_review_path,
        payload,
        "asset_runtime_preview_review",
        "runtime_preview_pass",
        RUNTIME_PREVIEW_REQUIRED_FLAGS,
        "runtime_preview_review_file",
        errors,
    )
    audio_loudness_review = validate_review_file(
        audio_loudness_review_path,
        payload,
        "asset_audio_loudness_review",
        "audio_loudness_pass",
        AUDIO_LOUDNESS_REQUIRED_FLAGS,
        "audio_loudness_review_file",
        errors,
    )
    final_acceptance = validate_review_file(
        final_acceptance_path,
        payload,
        "asset_final_acceptance",
        "accepted_content",
        FINAL_ACCEPTANCE_REQUIRED_FLAGS,
        "final_human_acceptance_file",
        errors,
    )
    accepted_asset_reports = validate_accepted_assets(payload, source_assets, errors)

    return {
        "report_version": 1,
        "source": relative_repo_path(repo_root, manifest_path),
        "repo_root": str(repo_root),
        "decision": "asset_acceptance_manifest_valid" if not errors else "asset_acceptance_manifest_invalid",
        "candidate_batch_id": payload.get("candidate_batch_id"),
        "asset_count": payload.get("asset_count"),
        "validated_asset_count": len(accepted_asset_reports),
        "runtime_candidate_manifest_decision": runtime_manifest_report["decision"]
        if runtime_manifest_report is not None
        else None,
        "runtime_preview_review_decision": runtime_preview_review.get("decision")
        if runtime_preview_review is not None
        else None,
        "audio_loudness_review_decision": audio_loudness_review.get("decision")
        if audio_loudness_review is not None
        else None,
        "final_acceptance_decision": final_acceptance.get("decision") if final_acceptance is not None else None,
        "errors": errors,
        "warnings": warnings,
        "accepted_assets": accepted_asset_reports,
        "limitations": [
            "This validator checks final asset acceptance evidence only.",
            "A valid acceptance manifest may mark assets accepted, but it does not prove Runtime integration.",
            "A valid acceptance manifest is not release readiness and cannot bypass future packaging, privacy, playtest, or Runtime smoke gates.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Asset Acceptance Manifest Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Decision: `{report['decision']}`",
        f"- Candidate batch: `{report['candidate_batch_id']}`",
        f"- Assets: {report['validated_asset_count']} / {report['asset_count']}",
        f"- Runtime candidate manifest: `{report['runtime_candidate_manifest_decision']}`",
        f"- Runtime preview review: `{report['runtime_preview_review_decision']}`",
        f"- Audio loudness review: `{report['audio_loudness_review_decision']}`",
        f"- Final acceptance: `{report['final_acceptance_decision']}`",
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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm final asset acceptance manifests.")
    parser.add_argument("manifest", type=Path, help="Final asset acceptance manifest JSON")
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
    return 0 if report["decision"] == "asset_acceptance_manifest_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
