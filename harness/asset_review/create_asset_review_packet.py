#!/usr/bin/env python3
"""Create a human-readable packet for asset candidate review.

The packet gathers manifest assets, local file links, metadata validation, and
the current manual-review draft into one Markdown file. It does not score,
approve, promote, or modify any asset.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PATH_FIELDS = [
    "path",
    "source_path",
    "processed_path",
    "runtime_32_path",
    "postprocess_manifest",
]
PREVIEW_FIELDS = ["preview_paths"]


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


def relative_repo_path(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(path)


def resolve_candidate_file(candidate_batch: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else candidate_batch / path


def markdown_escape(text: Any) -> str:
    value = str(text)
    return value.replace("|", "\\|").replace("\n", " ")


def code(value: Any) -> str:
    return f"`{markdown_escape(value)}`"


def link_for_repo_path(repo_root: Path, path: Path) -> str:
    relative = relative_repo_path(repo_root, path)
    return f"[{relative}]({relative})"


def asset_file_entries(candidate_batch: Path, asset: dict[str, Any]) -> list[tuple[str, str, bool]]:
    entries: list[tuple[str, str, bool]] = []
    for field in PATH_FIELDS:
        value = asset.get(field)
        if is_nonempty_string(value):
            resolved = resolve_candidate_file(candidate_batch, str(value))
            entries.append((field, str(value), resolved.exists()))
    for field in PREVIEW_FIELDS:
        for value in string_list(asset.get(field)):
            resolved = resolve_candidate_file(candidate_batch, value)
            entries.append((field, value, resolved.exists()))
    return entries


def review_index(review_payload: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not review_payload:
        return {}
    reviews = review_payload.get("asset_reviews")
    if not isinstance(reviews, list):
        return {}
    indexed: dict[str, dict[str, Any]] = {}
    for review in reviews:
        if isinstance(review, dict) and is_nonempty_string(review.get("id")):
            indexed[str(review["id"])] = review
    return indexed


def review_status(review: dict[str, Any] | None) -> str:
    if review is None:
        return "missing"
    serialized = json.dumps(review, ensure_ascii=False)
    if "TODO" in serialized:
        return "draft_todo"
    return str(review.get("decision", "present"))


def build_packet(
    candidate_batch: Path,
    repo_root: Path,
    metadata_report: str,
    review_draft: Path | None,
) -> dict[str, Any]:
    manifest_path = candidate_batch / "metadata" / "manifest.json"
    manifest = load_json_object(manifest_path)
    assets = manifest.get("assets")
    if not isinstance(assets, list) or not assets:
        raise ValueError(f"{manifest_path} must contain a non-empty assets array")

    review_payload = load_json_object(review_draft) if review_draft is not None else None
    reviews = review_index(review_payload)

    asset_reports = []
    missing_files: list[str] = []
    for index, asset in enumerate(assets):
        if not isinstance(asset, dict):
            raise ValueError(f"{manifest_path}: assets[{index}] must be an object")
        asset_id = asset.get("id")
        if not is_nonempty_string(asset_id):
            raise ValueError(f"{manifest_path}: assets[{index}] missing id")
        files = asset_file_entries(candidate_batch, asset)
        for _, value, exists in files:
            if not exists:
                missing_files.append(f"{asset_id}: {value}")
        review = reviews.get(str(asset_id))
        asset_reports.append(
            {
                "id": str(asset_id),
                "type": asset.get("type", "unknown"),
                "qa_status": asset.get("qa_status", "unknown"),
                "file_count": len(files),
                "files": files,
                "review_status": review_status(review),
                "allowed_candidate_uses": string_list(review.get("allowed_candidate_uses")) if review else [],
                "qa_notes": string_list(asset.get("qa_notes")),
            }
        )

    missing_review_ids = sorted({str(asset["id"]) for asset in assets if isinstance(asset, dict)} - set(reviews))
    return {
        "batch_id": manifest.get("batch_id", candidate_batch.name),
        "candidate_batch": relative_repo_path(repo_root, candidate_batch),
        "manifest": relative_repo_path(repo_root, manifest_path),
        "metadata_report": metadata_report,
        "review_draft": relative_repo_path(repo_root, review_draft) if review_draft is not None else None,
        "asset_count": len(asset_reports),
        "missing_file_count": len(missing_files),
        "missing_review_count": len(missing_review_ids),
        "missing_files": missing_files,
        "missing_review_ids": missing_review_ids,
        "assets": asset_reports,
        "limitations": [
            "This packet organizes review evidence only.",
            "It does not validate human ratings, judge art/audio quality, promote Runtime candidates, or mark assets as accepted_content.",
            "TODO review fields must be filled by a human before manual review validation can pass.",
        ],
    }


def write_markdown(packet: dict[str, Any], repo_root: Path, path: Path) -> None:
    lines = [
        "# Asset Candidate Review Packet",
        "",
        f"- Batch: `{packet['batch_id']}`",
        f"- Candidate path: `{packet['candidate_batch']}`",
        f"- Manifest: `{packet['manifest']}`",
        f"- Metadata report: `{packet['metadata_report']}`",
        f"- Review draft: `{packet['review_draft'] or 'None'}`",
        f"- Assets: {packet['asset_count']}",
        f"- Missing files: {packet['missing_file_count']}",
        f"- Missing review entries: {packet['missing_review_count']}",
        "",
        "## Assets",
        "",
        "| Asset | Type | QA | Review | Files |",
        "|---|---|---|---|---:|",
    ]
    for asset in packet["assets"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    code(asset["id"]),
                    code(asset["type"]),
                    code(asset["qa_status"]),
                    code(asset["review_status"]),
                    str(asset["file_count"]),
                ]
            )
            + " |"
        )

    for asset in packet["assets"]:
        lines.extend(["", f"## {asset['id']}", ""])
        lines.append(f"- Type: `{asset['type']}`")
        lines.append(f"- QA status: `{asset['qa_status']}`")
        lines.append(f"- Review status: `{asset['review_status']}`")
        if asset["allowed_candidate_uses"]:
            lines.append("- Allowed candidate uses: " + ", ".join(code(item) for item in asset["allowed_candidate_uses"]))
        if asset["qa_notes"]:
            lines.extend(["", "### QA Notes", ""])
            lines.extend(f"- {note}" for note in asset["qa_notes"])
        lines.extend(["", "### Files", ""])
        for field, value, exists in asset["files"]:
            resolved = resolve_candidate_file(Path(packet["candidate_batch"]), value)
            repo_resolved = (repo_root / resolved).resolve() if not resolved.is_absolute() else resolved
            existence = "exists" if exists else "missing"
            lines.append(f"- `{field}` {code(existence)}: {link_for_repo_path(repo_root, repo_resolved)}")

    lines.extend(["", "## Missing Files", ""])
    if packet["missing_files"]:
        lines.extend(f"- {item}" for item in packet["missing_files"])
    else:
        lines.append("- None")

    lines.extend(["", "## Missing Review Entries", ""])
    if packet["missing_review_ids"]:
        lines.extend(f"- `{item}`" for item in packet["missing_review_ids"])
    else:
        lines.append("- None")

    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in packet["limitations"])

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Markdown packet for human asset candidate review.")
    parser.add_argument("candidate_batch", type=Path, help="Path to asset/generated_candidates/<batch>")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--metadata-report", required=True, help="Metadata validation report path")
    parser.add_argument("--review-draft", type=Path, default=None, help="Manual review draft JSON")
    parser.add_argument("--out", type=Path, required=True, help="Output Markdown packet")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    candidate_batch = args.candidate_batch if args.candidate_batch.is_absolute() else repo_root / args.candidate_batch
    review_draft = None
    if args.review_draft is not None:
        review_draft = args.review_draft if args.review_draft.is_absolute() else repo_root / args.review_draft

    packet = build_packet(candidate_batch, repo_root, args.metadata_report, review_draft)
    write_markdown(packet, repo_root, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
