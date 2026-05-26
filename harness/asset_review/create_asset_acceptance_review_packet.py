#!/usr/bin/env python3
"""Create a human-review packet for final asset acceptance evidence.

The packet gathers the final acceptance manifest, required Runtime preview,
audio loudness/listening, and final human acceptance evidence into one
Markdown/JSON report. It does not validate the manifest as accepted, copy
assets, integrate Runtime assets, or approve release readiness.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_EVIDENCE = [
    {
        "field": "source_runtime_candidate_manifest",
        "label": "Runtime candidate manifest",
        "expected_review_type": None,
        "expected_decision": "asset_runtime_candidate_manifest_valid",
        "required_checks": [],
    },
    {
        "field": "runtime_preview_review_file",
        "label": "Runtime preview review",
        "expected_review_type": "asset_runtime_preview_review",
        "expected_decision": "runtime_preview_pass",
        "required_checks": [
            "all_assets_visible_or_audible",
            "small_size_readable",
            "no_placeholder_leak",
            "no_runtime_integration_claim",
        ],
    },
    {
        "field": "audio_loudness_review_file",
        "label": "Audio loudness/listening review",
        "expected_review_type": "asset_audio_loudness_review",
        "expected_decision": "audio_loudness_pass",
        "required_checks": [
            "dialogue_clear_if_present",
            "loudness_review_passed",
            "no_clipping",
            "loop_or_duration_fit",
        ],
    },
    {
        "field": "final_human_acceptance_file",
        "label": "Final human acceptance",
        "expected_review_type": "asset_final_acceptance",
        "expected_decision": "accepted_content",
        "required_checks": [
            "accepts_asset_batch",
            "accepted_content_only_after_reviews",
            "release_ready",
            "runtime_integrated",
        ],
    },
]
TODO_MARKERS = ("TODO", "<", ">")


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


def is_inside_repo(repo_root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return False
    return True


def markdown_escape(text: Any) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def code(value: Any) -> str:
    return f"`{markdown_escape(value)}`"


def evidence_status(repo_root: Path, value: Any) -> tuple[str, str | None]:
    if not is_nonempty_string(value):
        return "missing", None
    text = str(value)
    if has_placeholder(text):
        return "placeholder", None
    path = resolve_repo_path(repo_root, text)
    if not is_inside_repo(repo_root, path):
        return "outside_repo", None
    if not path.exists():
        return "missing_file", relative_repo_path(repo_root, path)
    return "exists", relative_repo_path(repo_root, path)


def accepted_asset_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    assets = payload.get("accepted_assets")
    if not isinstance(assets, list):
        return []
    rows: list[dict[str, Any]] = []
    for index, asset in enumerate(assets):
        if not isinstance(asset, dict):
            rows.append(
                {
                    "id": f"accepted_assets[{index}]",
                    "type": "invalid",
                    "accepted_use": "invalid",
                    "source_path": "invalid",
                    "status": "invalid",
                }
            )
            continue
        rows.append(
            {
                "id": asset.get("id", f"accepted_assets[{index}]"),
                "type": asset.get("type", ""),
                "accepted_use": asset.get("accepted_use", ""),
                "source_path": asset.get("source_path", ""),
                "status": "placeholder" if has_placeholder(asset) else "listed",
            }
        )
    return rows


def build_packet(manifest_path: Path, repo_root: Path) -> dict[str, Any]:
    payload = load_json_object(manifest_path)
    evidence = []
    for requirement in REQUIRED_EVIDENCE:
        field = str(requirement["field"])
        status, resolved_path = evidence_status(repo_root, payload.get(field))
        evidence.append(
            {
                "field": field,
                "label": requirement["label"],
                "value": payload.get(field),
                "status": status,
                "resolved_path": resolved_path,
                "expected_review_type": requirement["expected_review_type"],
                "expected_decision": requirement["expected_decision"],
                "required_checks": requirement["required_checks"],
            }
        )

    accepted_assets = accepted_asset_rows(payload)
    placeholder_count = sum(1 for item in evidence if item["status"] == "placeholder")
    missing_count = sum(1 for item in evidence if item["status"] in {"missing", "missing_file"})
    outside_repo_count = sum(1 for item in evidence if item["status"] == "outside_repo")
    listed_asset_placeholders = sum(1 for item in accepted_assets if item["status"] == "placeholder")
    ready_for_validation = (
        placeholder_count == 0
        and missing_count == 0
        and outside_repo_count == 0
        and listed_asset_placeholders == 0
    )
    return {
        "report_version": 1,
        "source": relative_repo_path(repo_root, manifest_path),
        "repo_root": str(repo_root),
        "decision": "asset_acceptance_review_packet_ready_for_validation"
        if ready_for_validation
        else "asset_acceptance_review_packet_needs_evidence",
        "candidate_batch_id": payload.get("candidate_batch_id"),
        "asset_count": payload.get("asset_count"),
        "listed_asset_count": len(accepted_assets),
        "evidence_count": len(evidence),
        "existing_evidence_count": sum(1 for item in evidence if item["status"] == "exists"),
        "placeholder_evidence_count": placeholder_count,
        "missing_evidence_count": missing_count,
        "outside_repo_evidence_count": outside_repo_count,
        "placeholder_asset_count": listed_asset_placeholders,
        "evidence": evidence,
        "accepted_assets": accepted_assets,
        "required_next_steps": [
            "Fill or replace Runtime preview review evidence with concrete human observations.",
            "Fill or replace audio loudness/listening review evidence with concrete listening and clipping/loudness observations.",
            "Fill or replace final human acceptance evidence after prior reviews pass.",
            "Run harness/asset_review/validate_asset_acceptance_manifest.py after every TODO is removed.",
        ],
        "limitations": [
            "This packet organizes final asset acceptance evidence only.",
            "It does not validate the acceptance manifest as passing.",
            "It does not copy assets into Runtime, mark Runtime integration, or approve release readiness.",
        ],
    }


def write_markdown(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Asset Acceptance Review Packet",
        "",
        f"- Source: `{packet['source']}`",
        f"- Decision: `{packet['decision']}`",
        f"- Candidate batch: `{packet['candidate_batch_id']}`",
        f"- Assets: {packet['listed_asset_count']} / {packet['asset_count']}",
        f"- Evidence files: {packet['existing_evidence_count']} / {packet['evidence_count']}",
        f"- Placeholder evidence: {packet['placeholder_evidence_count']}",
        f"- Missing evidence: {packet['missing_evidence_count']}",
        "",
        "## Required Evidence",
        "",
        "| Field | Status | Expected | Required checks |",
        "|---|---|---|---|",
    ]
    for item in packet["evidence"]:
        expected = item["expected_decision"]
        if item["expected_review_type"]:
            expected = f"{item['expected_review_type']} / {expected}"
        checks = ", ".join(code(check) for check in item["required_checks"]) or "None"
        lines.append(
            "| "
            + " | ".join(
                [
                    code(item["field"]),
                    code(item["status"]),
                    code(expected),
                    checks,
                ]
            )
            + " |"
        )

    lines.extend(["", "## Evidence Paths", ""])
    for item in packet["evidence"]:
        value = item["value"] if item["value"] is not None else "None"
        resolved = item["resolved_path"] or "None"
        lines.append(f"- `{item['field']}`: {code(value)} -> {code(resolved)}")

    lines.extend(["", "## Accepted Assets", ""])
    if packet["accepted_assets"]:
        lines.extend(["| Asset | Type | Use | Source | Status |", "|---|---|---|---|---|"])
        for asset in packet["accepted_assets"]:
            lines.append(
                "| "
                + " | ".join(
                    [
                        code(asset["id"]),
                        code(asset["type"]),
                        code(asset["accepted_use"]),
                        code(asset["source_path"]),
                        code(asset["status"]),
                    ]
                )
                + " |"
            )
    else:
        lines.append("- None")

    lines.extend(["", "## Required Next Steps", ""])
    lines.extend(f"- {item}" for item in packet["required_next_steps"])

    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in packet["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a packet for final asset acceptance human review.")
    parser.add_argument("manifest", type=Path, help="Final asset acceptance manifest JSON")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON packet")
    parser.add_argument("--markdown", type=Path, required=True, help="Write Markdown packet")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    manifest_path = args.manifest if args.manifest.is_absolute() else repo_root / args.manifest
    packet = build_packet(manifest_path, repo_root)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(packet, args.markdown)
    if args.report is None:
        print(json.dumps(packet, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
