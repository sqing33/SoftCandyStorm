#!/usr/bin/env python3
"""Promote reviewed asset batches into Runtime candidate staging.

This command only creates a Runtime-candidate staging copy after a human review
file passes `validate_asset_candidate_manual_review.py` with gate_decision
`asset_candidate`. It never writes to accepted_content and never marks assets
as Runtime-integrated or release-ready.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from validate_asset_candidate_manual_review import build_report, load_json_object


DEFAULT_PROMOTED_AT = "2026-05-26T00:00:00Z"


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def resolve_repo_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def relative_repo_path(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(path)


def read_manifest_assets(candidate_dir: Path) -> list[dict[str, Any]]:
    manifest_path = candidate_dir / "metadata" / "manifest.json"
    manifest = load_json_object(manifest_path)
    assets = manifest.get("assets")
    if not isinstance(assets, list):
        raise ValueError("candidate manifest assets must be a list")

    normalized: list[dict[str, Any]] = []
    for index, asset in enumerate(assets):
        if not isinstance(asset, dict):
            raise ValueError(f"candidate manifest assets[{index}] must be an object")
        asset_id = asset.get("id")
        if not is_nonempty_string(asset_id):
            raise ValueError(f"candidate manifest assets[{index}] missing id")
        normalized.append(
            {
                "id": str(asset_id),
                "type": asset.get("type"),
                "path": asset.get("path"),
                "qa_status": asset.get("qa_status"),
            }
        )
    return normalized


def read_review_allowed_uses(review: dict[str, Any]) -> dict[str, list[str]]:
    allowed: dict[str, list[str]] = {}
    reviews = review.get("asset_reviews")
    if not isinstance(reviews, list):
        return allowed
    for item in reviews:
        if not isinstance(item, dict):
            continue
        asset_id = item.get("id")
        uses = item.get("allowed_candidate_uses")
        if is_nonempty_string(asset_id) and isinstance(uses, list):
            allowed[str(asset_id)] = [use for use in uses if is_nonempty_string(use)]
    return allowed


def promote_asset_runtime_candidate(
    review_path: Path,
    repo_root: Path,
    out_dir: Path,
    promoted_at: str = DEFAULT_PROMOTED_AT,
) -> dict[str, Any]:
    validation = build_report(review_path, repo_root)
    if validation["decision"] != "asset_candidate_manual_review_valid":
        raise ValueError("manual review must validate before Runtime candidate promotion")
    if validation["gate_decision"] != "asset_candidate":
        raise ValueError("manual review gate_decision must be `asset_candidate`")

    review = load_json_object(review_path)
    candidate_batch_path = review.get("candidate_batch_path")
    if not is_nonempty_string(candidate_batch_path):
        raise ValueError("manual review must include candidate_batch_path")
    source_candidate = resolve_repo_path(repo_root, str(candidate_batch_path))
    if not source_candidate.exists():
        raise ValueError(f"candidate batch does not exist: {candidate_batch_path}")

    candidate_batch_id = str(review.get("candidate_batch_id") or source_candidate.name)
    destination = out_dir / candidate_batch_id
    if destination.exists():
        raise FileExistsError(f"Runtime candidate already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_candidate, destination)

    review_copy = destination / "manual_review.json"
    shutil.copy2(review_path, review_copy)

    assets = read_manifest_assets(destination)
    allowed_uses = read_review_allowed_uses(review)
    for asset in assets:
        asset["allowed_candidate_uses"] = allowed_uses.get(asset["id"], [])

    runtime_manifest = {
        "manifest_version": 1,
        "stage": "asset_runtime_candidate",
        "candidate_batch_id": candidate_batch_id,
        "promoted_at": promoted_at,
        "source_candidate_batch": relative_repo_path(repo_root, source_candidate),
        "manual_review_file": relative_repo_path(repo_root, review_copy),
        "candidate_metadata_report": review.get("candidate_metadata_report"),
        "asset_count": len(assets),
        "assets": assets,
        "rules": {
            "accepted_content": False,
            "runtime_integrated": False,
            "release_ready": False,
            "requires_runtime_preview": True,
            "requires_audio_loudness_review": True,
            "requires_final_human_acceptance": True,
        },
    }
    (destination / "runtime_candidate_manifest.json").write_text(
        json.dumps(runtime_manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return {
        "report_version": 1,
        "decision": "asset_runtime_candidate_promoted",
        "candidate_batch_id": candidate_batch_id,
        "source_review": relative_repo_path(repo_root, review_path),
        "source_candidate_batch": relative_repo_path(repo_root, source_candidate),
        "destination": relative_repo_path(repo_root, destination),
        "asset_count": len(assets),
        "manual_review_file": relative_repo_path(repo_root, review_copy),
        "runtime_candidate_manifest": relative_repo_path(
            repo_root, destination / "runtime_candidate_manifest.json"
        ),
        "limitations": [
            "Runtime candidate staging does not promote assets into accepted_content.",
            "Runtime candidate staging does not integrate assets into Runtime.",
            "Runtime preview, audio checks, source review, and final human acceptance are still required.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Asset Runtime Candidate Promotion",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Candidate batch: `{report['candidate_batch_id']}`",
        f"- Destination: `{report['destination']}`",
        f"- Assets: {report['asset_count']}",
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Promote a human-reviewed asset batch into Runtime candidate staging."
    )
    parser.add_argument("review", type=Path, help="Validated asset candidate manual review JSON")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("harness/asset_review/runtime_candidates"),
        help="Output directory for Runtime candidate asset batches",
    )
    parser.add_argument("--promoted-at", default=DEFAULT_PROMOTED_AT, help="Promotion timestamp")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown report")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    review_path = resolve_repo_path(repo_root, str(args.review))
    out_dir = resolve_repo_path(repo_root, str(args.out_dir))

    report = promote_asset_runtime_candidate(
        review_path,
        repo_root,
        out_dir,
        args.promoted_at,
    )
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
