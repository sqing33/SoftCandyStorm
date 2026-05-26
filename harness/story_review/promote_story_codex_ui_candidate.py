#!/usr/bin/env python3
"""Promote reviewed story/codex packs into UI candidate staging.

This command only creates a UI-candidate staging copy after a human review file
passes `validate_story_codex_manual_review.py` with gate_decision
`ui_candidate`. It never writes to accepted_content and never marks content as
Runtime-integrated.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from validate_story_codex_manual_review import build_report, load_json_object


DEFAULT_PROMOTED_AT = "2026-05-26T00:00:00Z"
UI_CANDIDATE_MANIFEST_CONTRACT_ID = "story-codex-ui-candidate-manifest-v0"


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


def read_candidate_counts(candidate_dir: Path) -> tuple[int, int]:
    return (
        len(list((candidate_dir / "chapters").glob("*.json"))),
        len(list((candidate_dir / "codex").glob("*.json"))),
    )


def promote_story_codex_ui_candidate(
    review_path: Path,
    repo_root: Path,
    out_dir: Path,
    promoted_at: str = DEFAULT_PROMOTED_AT,
) -> dict[str, Any]:
    validation = build_report(review_path, repo_root)
    if validation["decision"] != "story_codex_manual_review_valid":
        raise ValueError("manual review must validate before UI candidate promotion")
    if validation["gate_decision"] != "ui_candidate":
        raise ValueError("manual review gate_decision must be `ui_candidate`")

    review = load_json_object(review_path)
    candidate_pack_path = review.get("candidate_pack_path")
    if not is_nonempty_string(candidate_pack_path):
        raise ValueError("manual review must include candidate_pack_path")
    source_candidate = resolve_repo_path(repo_root, str(candidate_pack_path))
    if not source_candidate.exists():
        raise ValueError(f"candidate pack does not exist: {candidate_pack_path}")

    candidate_pack_id = str(review.get("candidate_pack_id") or source_candidate.name)
    destination = out_dir / candidate_pack_id
    if destination.exists():
        raise FileExistsError(f"UI candidate already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_candidate, destination)

    review_copy = destination / "manual_review.json"
    shutil.copy2(review_path, review_copy)

    chapter_count, codex_count = read_candidate_counts(destination)
    ui_manifest = {
        "manifest_version": 1,
        "manifest_contract_id": UI_CANDIDATE_MANIFEST_CONTRACT_ID,
        "stage": "story_codex_ui_candidate",
        "candidate_pack_id": candidate_pack_id,
        "promoted_at": promoted_at,
        "source_candidate_pack": relative_repo_path(repo_root, source_candidate),
        "manual_review_file": relative_repo_path(repo_root, review_copy),
        "manual_gate_decision": "ui_candidate",
        "candidate_validation_report": review.get("candidate_validation_report"),
        "chapter_count": chapter_count,
        "codex_entry_count": codex_count,
        "rules": {
            "accepted_content": False,
            "runtime_integrated": False,
            "requires_runtime_ui_review": True,
            "requires_final_human_acceptance": True,
        },
    }
    (destination / "ui_candidate_manifest.json").write_text(
        json.dumps(ui_manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return {
        "report_version": 1,
        "decision": "story_codex_ui_candidate_promoted",
        "candidate_pack_id": candidate_pack_id,
        "source_review": relative_repo_path(repo_root, review_path),
        "source_candidate_pack": relative_repo_path(repo_root, source_candidate),
        "destination": relative_repo_path(repo_root, destination),
        "chapter_count": chapter_count,
        "codex_entry_count": codex_count,
        "manual_review_file": relative_repo_path(repo_root, review_copy),
        "ui_candidate_manifest": relative_repo_path(
            repo_root, destination / "ui_candidate_manifest.json"
        ),
        "limitations": [
            "UI candidate staging does not promote content into accepted_content.",
            "UI candidate staging does not integrate story/codex text into Runtime.",
            "Runtime UI review and final human acceptance are still required.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Story Codex UI Candidate Promotion",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Candidate: `{report['candidate_pack_id']}`",
        f"- Destination: `{report['destination']}`",
        f"- Chapters: {report['chapter_count']}",
        f"- Codex entries: {report['codex_entry_count']}",
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Promote a human-reviewed story/codex pack into UI candidate staging."
    )
    parser.add_argument("review", type=Path, help="Validated story/codex manual review JSON")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("harness/story_review/ui_candidates"),
        help="Output directory for UI candidate packs",
    )
    parser.add_argument("--promoted-at", default=DEFAULT_PROMOTED_AT, help="Promotion timestamp")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown report")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    review_path = resolve_repo_path(repo_root, str(args.review))
    out_dir = resolve_repo_path(repo_root, str(args.out_dir))

    report = promote_story_codex_ui_candidate(
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
