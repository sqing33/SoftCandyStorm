#!/usr/bin/env python3
"""Validate human review records for generated asset candidate batches.

The validator checks review evidence completeness and candidate-pool discipline.
It does not decide whether art or audio is good enough, and a passing report
does not promote assets into Runtime or accepted content.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ALLOWED_GATE_DECISIONS = {"repair", "asset_candidate", "reject", "needs_more_review"}
FORBIDDEN_GATE_DECISIONS = {"accepted_content", "runtime_integrated", "release_ready", "accept_asset"}
ALLOWED_ITEM_DECISIONS = {"pass", "revise", "reject"}
COMMON_RATING_FIELDS = ["style_fit", "gameplay_readability", "provenance_confidence", "technical_readiness"]
IMAGE_RATING_FIELDS = ["small_size_readability", "alpha_edge_quality"]
AUDIO_RATING_FIELDS = ["audio_clarity", "loudness_readiness", "duration_fit"]
AUDIO_TYPES = {"audio", "speech", "music", "sfx", "voice"}
IMAGE_TYPES = {"image", "sprite", "ui", "icon", "background"}
REQUIRED_PROJECT_RULES = {
    "candidate_only": True,
    "accepted_content": False,
    "runtime_integrated": False,
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


def validate_rating(value: Any) -> bool:
    return isinstance(value, int) and 1 <= value <= 5


def resolve_repo_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def is_inside_repo(repo_root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return False
    return True


def load_candidate_manifest(
    repo_root: Path,
    payload: dict[str, Any],
    errors: list[str],
) -> dict[str, dict[str, Any]]:
    candidate_path = payload.get("candidate_batch_path")
    if not is_nonempty_string(candidate_path):
        errors.append("candidate_batch_path must be non-empty")
        return {}

    resolved = resolve_repo_path(repo_root, str(candidate_path))
    if not is_inside_repo(repo_root, resolved):
        errors.append(f"candidate_batch_path must stay inside repository: {candidate_path}")
        return {}
    if not resolved.exists():
        errors.append(f"candidate_batch_path does not exist: {candidate_path}")
        return {}

    candidate_id = payload.get("candidate_batch_id")
    if is_nonempty_string(candidate_id) and resolved.name != candidate_id:
        errors.append("candidate_batch_id must match candidate_batch_path directory name")

    manifest_path = resolved / "metadata" / "manifest.json"
    if not manifest_path.exists():
        errors.append("candidate batch missing metadata/manifest.json")
        return {}

    try:
        manifest = load_json_object(manifest_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"candidate manifest is invalid: {error}")
        return {}

    project_rules = manifest.get("project_rules")
    if not isinstance(project_rules, dict):
        errors.append("candidate manifest project_rules must be an object")
    else:
        for key, expected in REQUIRED_PROJECT_RULES.items():
            if project_rules.get(key) is not expected:
                errors.append(f"candidate manifest project_rules.{key} must be {json.dumps(expected)}")

    assets = manifest.get("assets")
    if not isinstance(assets, list) or not assets:
        errors.append("candidate manifest assets must be a non-empty list")
        return {}

    asset_index: dict[str, dict[str, Any]] = {}
    for index, asset in enumerate(assets):
        if not isinstance(asset, dict):
            errors.append(f"candidate manifest assets[{index}] must be an object")
            continue
        asset_id = asset.get("id")
        if not is_nonempty_string(asset_id):
            errors.append(f"candidate manifest assets[{index}] missing id")
            continue
        if asset_id in asset_index:
            errors.append(f"candidate manifest duplicate asset id `{asset_id}`")
            continue
        asset_index[str(asset_id)] = asset

    return asset_index


def validate_existing_report(repo_root: Path, payload: dict[str, Any], errors: list[str]) -> None:
    report_path = payload.get("candidate_metadata_report")
    if not is_nonempty_string(report_path):
        errors.append("candidate_metadata_report must be non-empty")
        return
    resolved = resolve_repo_path(repo_root, str(report_path))
    if not is_inside_repo(repo_root, resolved):
        errors.append(f"candidate_metadata_report must stay inside repository: {report_path}")
    elif not resolved.exists():
        errors.append(f"candidate_metadata_report does not exist: {report_path}")


def expected_rating_fields(asset_type: str | None) -> list[str]:
    fields = list(COMMON_RATING_FIELDS)
    if asset_type in AUDIO_TYPES:
        fields.extend(AUDIO_RATING_FIELDS)
    elif asset_type in IMAGE_TYPES:
        fields.extend(IMAGE_RATING_FIELDS)
    return fields


def validate_asset_reviews(
    reviews: Any,
    asset_index: dict[str, dict[str, Any]],
    gate_decision: str | None,
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    reports: list[dict[str, Any]] = []
    if not isinstance(reviews, list):
        return reports, ["asset_reviews must be a list"], warnings

    seen: set[str] = set()
    for index, review in enumerate(reviews):
        if not isinstance(review, dict):
            errors.append(f"asset_reviews[{index}] must be an object")
            continue
        asset_id = review.get("id")
        display_id = str(asset_id) if is_nonempty_string(asset_id) else f"asset_reviews[{index}]"
        if not is_nonempty_string(asset_id):
            errors.append(f"{display_id}: id must be non-empty")
            manifest_asset: dict[str, Any] = {}
        elif asset_id not in asset_index:
            errors.append(f"{display_id}: id does not exist in candidate manifest")
            manifest_asset = {}
        elif asset_id in seen:
            errors.append(f"{display_id}: duplicate review id")
            manifest_asset = asset_index[str(asset_id)]
        else:
            seen.add(str(asset_id))
            manifest_asset = asset_index[str(asset_id)]

        manifest_type = manifest_asset.get("type") if isinstance(manifest_asset.get("type"), str) else None
        review_type = review.get("asset_type")
        if review_type is not None and not is_nonempty_string(review_type):
            errors.append(f"{display_id}: asset_type must be non-empty when present")
        if is_nonempty_string(review_type) and manifest_type and review_type != manifest_type:
            warnings.append(f"{display_id}: asset_type `{review_type}` differs from manifest type `{manifest_type}`")
        asset_type = str(review_type) if is_nonempty_string(review_type) else manifest_type

        decision = review.get("decision")
        if decision not in ALLOWED_ITEM_DECISIONS:
            errors.append(f"{display_id}: decision must be one of {', '.join(sorted(ALLOWED_ITEM_DECISIONS))}")

        low_fields: list[str] = []
        missing_fields: list[str] = []
        for field in expected_rating_fields(asset_type):
            if not validate_rating(review.get(field)):
                errors.append(f"{display_id}: {field} must be an integer from 1 to 5")
                missing_fields.append(field)
            elif int(review[field]) < 4:
                low_fields.append(field)

        allowed_uses = string_list(review.get("allowed_candidate_uses"))
        if not allowed_uses or len(allowed_uses) != len(review.get("allowed_candidate_uses", [])):
            errors.append(f"{display_id}: allowed_candidate_uses must be a non-empty list of strings")

        if not is_nonempty_string(review.get("notes")):
            errors.append(f"{display_id}: notes must contain a concrete human observation")

        required_changes = review.get("required_changes")
        if not isinstance(required_changes, list) or not all(isinstance(item, str) for item in required_changes):
            errors.append(f"{display_id}: required_changes must be a list of strings")
            required_change_count = 0
        else:
            required_change_count = len([item for item in required_changes if item.strip()])

        if decision in {"revise", "reject"} and required_change_count == 0:
            errors.append(f"{display_id}: {decision} requires at least one required_changes item")
        if low_fields and decision == "pass":
            warnings.append(f"{display_id}: pass decision has ratings below 4 for {', '.join(low_fields)}")
        if gate_decision == "asset_candidate":
            if decision != "pass":
                errors.append(f"{display_id}: asset_candidate gate requires every item decision to be pass")
            if low_fields:
                errors.append(f"{display_id}: asset_candidate gate requires all ratings to be at least 4")
            if required_change_count:
                errors.append(f"{display_id}: asset_candidate gate cannot have required_changes")

        reports.append(
            {
                "id": asset_id if is_nonempty_string(asset_id) else display_id,
                "asset_type": asset_type,
                "decision": decision,
                "low_rating_count": len(low_fields),
                "missing_rating_count": len(missing_fields),
                "required_change_count": required_change_count,
            }
        )

    missing_ids = sorted(set(asset_index) - seen)
    if missing_ids:
        errors.append(f"asset_reviews missing candidate asset ids: {', '.join(missing_ids)}")

    return reports, errors, warnings


def build_report(review_path: Path, repo_root: Path) -> dict[str, Any]:
    payload = load_json_object(review_path)
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(payload.get("review_version"), int) or payload["review_version"] <= 0:
        errors.append("review_version must be a positive integer")
    for field in ("candidate_batch_id", "reviewer", "reviewed_at", "summary"):
        if not is_nonempty_string(payload.get(field)):
            errors.append(f"{field} must be non-empty")

    gate_decision = payload.get("gate_decision")
    if gate_decision in FORBIDDEN_GATE_DECISIONS:
        errors.append(f"forbidden gate_decision `{gate_decision}`")
    elif gate_decision not in ALLOWED_GATE_DECISIONS:
        errors.append(f"gate_decision must be one of {', '.join(sorted(ALLOWED_GATE_DECISIONS))}")

    validate_existing_report(repo_root, payload, errors)
    asset_index = load_candidate_manifest(repo_root, payload, errors)
    asset_reports, asset_errors, asset_warnings = validate_asset_reviews(
        payload.get("asset_reviews"),
        asset_index,
        str(gate_decision) if isinstance(gate_decision, str) else None,
    )
    errors.extend(asset_errors)
    warnings.extend(asset_warnings)

    global_risks = string_list(payload.get("global_risks"))
    next_actions = string_list(payload.get("next_actions"))
    if payload.get("global_risks") is not None and not isinstance(payload.get("global_risks"), list):
        errors.append("global_risks must be a list")
    if payload.get("next_actions") is not None and not isinstance(payload.get("next_actions"), list):
        errors.append("next_actions must be a list")
    if gate_decision == "asset_candidate" and global_risks:
        errors.append("asset_candidate gate cannot list unresolved global_risks")
    if gate_decision in {"repair", "reject", "needs_more_review"} and not next_actions:
        errors.append(f"{gate_decision} gate requires non-empty next_actions")

    repair_item_count = sum(
        1
        for item in asset_reports
        if item["decision"] in {"revise", "reject"} or item["required_change_count"] > 0
    )
    if gate_decision == "repair" and repair_item_count == 0 and not global_risks:
        errors.append("repair gate requires at least one item issue or global_risks entry")

    return {
        "report_version": 1,
        "source": str(review_path),
        "repo_root": str(repo_root),
        "decision": "asset_candidate_manual_review_valid" if not errors else "asset_candidate_manual_review_invalid",
        "gate_decision": gate_decision,
        "asset_review_count": len(asset_reports),
        "expected_asset_count": len(asset_index),
        "repair_item_count": repair_item_count,
        "global_risk_count": len(global_risks),
        "next_action_count": len(next_actions),
        "errors": errors,
        "warnings": warnings,
        "limitations": [
            "This validator checks manual review record completeness only.",
            "It cannot judge visual quality, listening quality, licensing, or in-engine feel.",
            "An asset_candidate decision does not promote assets into Runtime, accepted_content, or release assets.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Asset Candidate Manual Review Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Decision: `{report['decision']}`",
        f"- Gate decision: `{report['gate_decision']}`",
        f"- Assets reviewed: {report['asset_review_count']} / {report['expected_asset_count']}",
        f"- Repair items: {report['repair_item_count']}",
        f"- Global risks: {report['global_risk_count']}",
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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm asset candidate manual reviews.")
    parser.add_argument("review", type=Path, help="Asset candidate manual review JSON file")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON validation report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown validation summary")
    args = parser.parse_args()

    report = build_report(args.review, args.repo_root)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "asset_candidate_manual_review_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
