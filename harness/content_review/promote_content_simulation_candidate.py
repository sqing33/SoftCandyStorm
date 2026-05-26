#!/usr/bin/env python3
"""Promote reviewed content packs into simulation-candidate staging.

This command only creates a design-approved staging copy after a human design
review passes `validate_content_candidate_design_review.py` with gate_decision
`simulate_candidate`. It never writes to validated_candidates,
simulated_candidates, playtest_candidates, accepted_content, or Runtime.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from validate_content_candidate_design_review import TYPE_TO_CATEGORY, build_report, load_json_object


DEFAULT_PROMOTED_AT = "2026-05-26T00:00:00Z"
CONTENT_SIMULATION_CANDIDATE_MANIFEST_CONTRACT_ID = "content-simulation-candidate-manifest-v0"


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


def content_path_for_entry(candidate_pack: Path, entry: dict[str, Any]) -> Path:
    entry_path = entry.get("path")
    if is_nonempty_string(entry_path):
        return candidate_pack / str(entry_path)
    content_type = entry.get("type")
    content_id = entry.get("id")
    category = TYPE_TO_CATEGORY.get(str(content_type))
    if category is None or not is_nonempty_string(content_id):
        raise ValueError("content entry must include a supported type and id")
    return candidate_pack / category / f"{content_id}.json"


def read_source_contents(candidate_pack: Path, source_patch_manifest: Path) -> list[dict[str, Any]]:
    source_manifest = load_json_object(source_patch_manifest)
    contents = source_manifest.get("contents")
    if not isinstance(contents, list) or not contents:
        raise ValueError("source_patch_manifest.contents must be a non-empty list")

    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, entry in enumerate(contents):
        if not isinstance(entry, dict):
            raise ValueError(f"source_patch_manifest.contents[{index}] must be an object")
        content_id = entry.get("id")
        content_type = entry.get("type")
        if not is_nonempty_string(content_id):
            raise ValueError(f"source_patch_manifest.contents[{index}] missing id")
        if not is_nonempty_string(content_type) or str(content_type) not in TYPE_TO_CATEGORY:
            raise ValueError(f"{content_id}: unsupported content type")
        if str(content_id) in seen:
            raise ValueError(f"source_patch_manifest duplicate content id `{content_id}`")
        seen.add(str(content_id))
        content_path = content_path_for_entry(candidate_pack, entry)
        if not content_path.exists():
            raise ValueError(f"candidate pack missing content file for `{content_id}`: {content_path}")
        normalized.append(
            {
                "id": str(content_id),
                "type": str(content_type),
                "path": relative_repo_path(candidate_pack, content_path),
            }
        )
    return normalized


def promote_content_simulation_candidate(
    review_path: Path,
    repo_root: Path,
    out_dir: Path,
    promoted_at: str = DEFAULT_PROMOTED_AT,
) -> dict[str, Any]:
    validation = build_report(review_path, repo_root)
    if validation["decision"] != "content_candidate_design_review_valid":
        raise ValueError("design review must validate before simulation-candidate promotion")
    if validation["gate_decision"] != "simulate_candidate":
        raise ValueError("design review gate_decision must be `simulate_candidate`")

    review = load_json_object(review_path)
    candidate_pack_path = review.get("candidate_pack_path")
    source_patch_manifest_path = review.get("source_patch_manifest")
    if not is_nonempty_string(candidate_pack_path):
        raise ValueError("design review must include candidate_pack_path")
    if not is_nonempty_string(source_patch_manifest_path):
        raise ValueError("design review must include source_patch_manifest")

    source_candidate = resolve_repo_path(repo_root, str(candidate_pack_path))
    source_patch_manifest = resolve_repo_path(repo_root, str(source_patch_manifest_path))
    if not source_candidate.exists():
        raise ValueError(f"candidate pack does not exist: {candidate_pack_path}")
    if not source_patch_manifest.exists():
        raise ValueError(f"source_patch_manifest does not exist: {source_patch_manifest_path}")

    candidate_pack_id = str(review.get("candidate_pack_id") or source_candidate.name)
    destination = out_dir / candidate_pack_id
    if destination.exists():
        raise FileExistsError(f"Content simulation candidate already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_candidate, destination)

    review_copy = destination / "manual_design_review.json"
    shutil.copy2(review_path, review_copy)

    contents = read_source_contents(destination, destination / "metadata" / "source_patch_manifest.json")
    simulation_manifest = {
        "manifest_version": 1,
        "manifest_contract_id": CONTENT_SIMULATION_CANDIDATE_MANIFEST_CONTRACT_ID,
        "stage": "content_simulation_candidate",
        "candidate_pack_id": candidate_pack_id,
        "promoted_at": promoted_at,
        "source_candidate_pack": relative_repo_path(repo_root, source_candidate),
        "source_patch_manifest": relative_repo_path(repo_root, source_patch_manifest),
        "manual_design_review_file": relative_repo_path(repo_root, review_copy),
        "manual_gate_decision": "simulate_candidate",
        "candidate_preflight_report": review.get("candidate_preflight_report"),
        "content_count": len(contents),
        "contents": contents,
        "rules": {
            "accepted_content": False,
            "runtime_integrated": False,
            "validated_candidates_written": False,
            "simulated_candidates_written": False,
            "playtest_candidate": False,
            "release_ready": False,
            "requires_schema_validation": True,
            "requires_static_budget": True,
            "requires_bot_simulation": True,
            "requires_replay_regression": True,
            "requires_manual_playtest": True,
            "requires_final_human_acceptance": True,
        },
    }
    (destination / "simulation_candidate_manifest.json").write_text(
        json.dumps(simulation_manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return {
        "report_version": 1,
        "decision": "content_simulation_candidate_promoted",
        "candidate_pack_id": candidate_pack_id,
        "source_review": relative_repo_path(repo_root, review_path),
        "source_candidate_pack": relative_repo_path(repo_root, source_candidate),
        "destination": relative_repo_path(repo_root, destination),
        "content_count": len(contents),
        "manual_design_review_file": relative_repo_path(repo_root, review_copy),
        "simulation_candidate_manifest": relative_repo_path(
            repo_root, destination / "simulation_candidate_manifest.json"
        ),
        "limitations": [
            "Simulation candidate staging does not promote content into validated_candidates.",
            "Simulation candidate staging does not run Bot simulation or Replay regression.",
            "Simulation candidate staging does not write playtest_candidates, accepted_content, or Runtime content.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Content Simulation Candidate Promotion",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Candidate: `{report['candidate_pack_id']}`",
        f"- Destination: `{report['destination']}`",
        f"- Contents: {report['content_count']}",
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Promote a human-reviewed content pack into simulation-candidate staging."
    )
    parser.add_argument("review", type=Path, help="Validated content design review JSON")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("harness/content_review/simulation_candidates"),
        help="Output directory for design-approved simulation candidate packs",
    )
    parser.add_argument("--promoted-at", default=DEFAULT_PROMOTED_AT, help="Promotion timestamp")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown report")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    review_path = resolve_repo_path(repo_root, str(args.review))
    out_dir = resolve_repo_path(repo_root, str(args.out_dir))

    report = promote_content_simulation_candidate(
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
