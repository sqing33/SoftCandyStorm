#!/usr/bin/env python3
"""Create a human-review packet for final story/codex acceptance evidence.

The packet gathers the final acceptance manifest, required UI-candidate
manifest, Runtime UI review, and final human acceptance evidence into one
Markdown/JSON report. It does not validate the manifest as accepted, copy
story/codex text, integrate Runtime UI, or approve release readiness.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_EVIDENCE = [
    {
        "field": "source_ui_candidate_manifest",
        "label": "UI candidate manifest",
        "expected_review_type": None,
        "expected_decision": "story_codex_ui_candidate_manifest_valid",
        "required_checks": [],
    },
    {
        "field": "runtime_ui_review_file",
        "label": "Runtime UI review",
        "expected_review_type": "story_codex_runtime_ui_review",
        "expected_decision": "runtime_ui_review_pass",
        "required_checks": [
            "f3_entry_visible",
            "no_generated_candidate_text_loaded",
            "no_runtime_integration_claim",
            "layout_readable",
        ],
    },
    {
        "field": "final_human_acceptance_file",
        "label": "Final human acceptance",
        "expected_review_type": "story_codex_final_acceptance",
        "expected_decision": "accepted_content",
        "required_checks": [
            "accepts_story_codex_text",
            "accepted_content_only_after_reviews",
            "release_ready",
            "runtime_integrated",
        ],
    },
]
TOP_LEVEL_EVIDENCE_FIELDS = [
    "candidate_pack_id",
    "accepted_at",
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


def value_status(value: Any) -> str:
    if not is_nonempty_string(value):
        return "missing"
    if has_placeholder(value):
        return "placeholder"
    return "filled"


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


def build_packet(manifest_path: Path, repo_root: Path) -> dict[str, Any]:
    payload = load_json_object(manifest_path)
    top_level_fields = [
        {
            "field": field,
            "value": payload.get(field),
            "status": value_status(payload.get(field)),
        }
        for field in TOP_LEVEL_EVIDENCE_FIELDS
    ]

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

    placeholder_evidence_count = sum(1 for item in evidence if item["status"] == "placeholder")
    missing_evidence_count = sum(1 for item in evidence if item["status"] in {"missing", "missing_file"})
    outside_repo_evidence_count = sum(1 for item in evidence if item["status"] == "outside_repo")
    placeholder_manifest_field_count = sum(1 for item in top_level_fields if item["status"] == "placeholder")
    missing_manifest_field_count = sum(1 for item in top_level_fields if item["status"] == "missing")
    ready_for_validation = (
        placeholder_evidence_count == 0
        and missing_evidence_count == 0
        and outside_repo_evidence_count == 0
        and placeholder_manifest_field_count == 0
        and missing_manifest_field_count == 0
    )

    return {
        "report_version": 1,
        "source": relative_repo_path(repo_root, manifest_path),
        "repo_root": str(repo_root),
        "decision": "story_codex_acceptance_review_packet_ready_for_validation"
        if ready_for_validation
        else "story_codex_acceptance_review_packet_needs_evidence",
        "candidate_pack_id": payload.get("candidate_pack_id"),
        "chapter_count": payload.get("chapter_count"),
        "codex_entry_count": payload.get("codex_entry_count"),
        "evidence_count": len(evidence),
        "existing_evidence_count": sum(1 for item in evidence if item["status"] == "exists"),
        "placeholder_evidence_count": placeholder_evidence_count,
        "missing_evidence_count": missing_evidence_count,
        "outside_repo_evidence_count": outside_repo_evidence_count,
        "placeholder_manifest_field_count": placeholder_manifest_field_count,
        "missing_manifest_field_count": missing_manifest_field_count,
        "top_level_fields": top_level_fields,
        "evidence": evidence,
        "required_next_steps": [
            "Fill or replace the UI candidate manifest evidence after human story/codex review passes.",
            "Fill or replace Runtime UI review evidence with concrete F3 visibility and text-loading observations.",
            "Fill or replace final human acceptance evidence only after prior reviews pass.",
            "Run harness/story_review/validate_story_codex_acceptance_manifest.py after every TODO is removed.",
        ],
        "limitations": [
            "This packet organizes final story/codex acceptance evidence only.",
            "It does not validate the acceptance manifest as passing.",
            "It does not copy candidate story/codex text, mark Runtime integration, or approve release readiness.",
        ],
    }


def write_markdown(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Story Codex Acceptance Review Packet",
        "",
        f"- Source: `{packet['source']}`",
        f"- Decision: `{packet['decision']}`",
        f"- Candidate pack: `{packet['candidate_pack_id']}`",
        f"- Chapters: {packet['chapter_count']}",
        f"- Codex entries: {packet['codex_entry_count']}",
        f"- Evidence files: {packet['existing_evidence_count']} / {packet['evidence_count']}",
        f"- Placeholder evidence: {packet['placeholder_evidence_count']}",
        f"- Missing evidence: {packet['missing_evidence_count']}",
        f"- Placeholder manifest fields: {packet['placeholder_manifest_field_count']}",
        "",
        "## Manifest Fields",
        "",
        "| Field | Status | Value |",
        "|---|---|---|",
    ]
    for item in packet["top_level_fields"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    code(item["field"]),
                    code(item["status"]),
                    code(item["value"]),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Required Evidence", "", "| Field | Status | Expected | Required checks |", "|---|---|---|---|"])
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

    lines.extend(["", "## Required Next Steps", ""])
    lines.extend(f"- {item}" for item in packet["required_next_steps"])

    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in packet["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a packet for final story/codex acceptance human review.")
    parser.add_argument("manifest", type=Path, help="Final story/codex acceptance manifest JSON")
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
