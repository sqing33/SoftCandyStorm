#!/usr/bin/env python3
"""Materialize a partial content candidate patch into a full content pack.

The generated output remains a candidate. This tool copies an existing base
content pack and overlays supported candidate categories so the result can later
be passed to `game_harness validate-candidates` when the local Rust binary is
available.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any


CONTENT_CATEGORIES = [
    "characters",
    "weapons",
    "passives",
    "evolutions",
    "enemies",
    "bosses",
    "waves",
    "maps",
    "events",
]
SUPPORTED_PATCH_CATEGORIES = {"weapons", "passives", "evolutions", "enemies", "waves"}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def content_files(directory: Path) -> list[Path]:
    return sorted(path for path in directory.glob("*.json") if path.is_file()) if directory.exists() else []


def copy_category(base_content_dir: Path, output_dir: Path, category: str) -> int:
    source_dir = base_content_dir / category
    target_dir = output_dir / category
    target_dir.mkdir(parents=True, exist_ok=True)
    copied = 0
    if not source_dir.exists():
        return copied
    for source_path in content_files(source_dir):
        shutil.copy2(source_path, target_dir / source_path.name)
        copied += 1
    return copied


def overlay_category(
    patch_dir: Path,
    output_dir: Path,
    category: str,
    allow_overrides: bool,
) -> tuple[int, int, list[str]]:
    source_dir = patch_dir / category
    target_dir = output_dir / category
    errors: list[str] = []
    overlaid = 0
    overridden = 0
    if not source_dir.exists():
        return overlaid, overridden, errors
    target_dir.mkdir(parents=True, exist_ok=True)
    for source_path in content_files(source_dir):
        target_path = target_dir / source_path.name
        if target_path.exists():
            if not allow_overrides:
                errors.append(
                    f"{category}/{source_path.name} already exists in base pack; use --allow-overrides only for explicit repairs"
                )
                continue
            overridden += 1
        shutil.copy2(source_path, target_path)
        overlaid += 1
    return overlaid, overridden, errors


def manifest_batch_id(candidate_dir: Path) -> str:
    manifest_path = candidate_dir / "metadata" / "manifest.json"
    if not manifest_path.exists():
        return candidate_dir.name
    try:
        manifest = load_json(manifest_path)
    except (OSError, ValueError, json.JSONDecodeError):
        return candidate_dir.name
    batch_id = manifest.get("batch_id")
    return batch_id if isinstance(batch_id, str) and batch_id.strip() else candidate_dir.name


def manifest_generated_at(candidate_dir: Path) -> str:
    manifest_path = candidate_dir / "metadata" / "manifest.json"
    if not manifest_path.exists():
        return "unknown"
    try:
        manifest = load_json(manifest_path)
    except (OSError, ValueError, json.JSONDecodeError):
        return "unknown"
    generated_at = manifest.get("generated_at")
    return generated_at if isinstance(generated_at, str) and generated_at.strip() else "unknown"


def materialize_pack(
    patch_dir: Path,
    base_content_dir: Path,
    output_dir: Path,
    allow_overrides: bool,
) -> dict[str, Any]:
    if output_dir.exists():
        raise FileExistsError(f"output directory already exists: {output_dir}")
    if not base_content_dir.exists():
        raise FileNotFoundError(f"base content directory not found: {base_content_dir}")
    if not patch_dir.exists():
        raise FileNotFoundError(f"candidate patch directory not found: {patch_dir}")

    output_dir.mkdir(parents=True)
    copied_counts = {
        category: copy_category(base_content_dir, output_dir, category)
        for category in CONTENT_CATEGORIES
    }

    overlay_counts: dict[str, int] = {}
    overridden_counts: dict[str, int] = {}
    errors: list[str] = []
    for category in sorted(SUPPORTED_PATCH_CATEGORIES):
        count, overridden, category_errors = overlay_category(patch_dir, output_dir, category, allow_overrides)
        overlay_counts[category] = count
        overridden_counts[category] = overridden
        errors.extend(category_errors)

    if errors:
        shutil.rmtree(output_dir)
        raise ValueError("; ".join(errors))

    source_manifest_path = patch_dir / "metadata" / "manifest.json"
    if source_manifest_path.exists():
        metadata_dir = output_dir / "metadata"
        metadata_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_manifest_path, metadata_dir / "source_patch_manifest.json")

    source_batch_id = manifest_batch_id(patch_dir)
    generated_at = manifest_generated_at(patch_dir)
    materialization = {
        "source_patch": str(patch_dir),
        "source_patch_batch_id": source_batch_id,
        "base_content_dir": str(base_content_dir),
        "output_dir": str(output_dir),
        "allow_overrides": allow_overrides,
        "copied_counts": copied_counts,
        "overlay_counts": overlay_counts,
        "overridden_counts": overridden_counts,
        "project_rules": {
            "candidate_only": True,
            "accepted_content": False,
            "runtime_integrated": False,
            "required_next_steps": [
                "game_harness validate-candidates",
                "static budget review",
                "Bot simulation",
                "Replay regression",
                "human review before acceptance",
            ],
        },
    }
    write_json(output_dir / "metadata" / "materialization.json", materialization)
    write_json(
        output_dir / "metadata" / "manifest.json",
        {
            "batch_id": output_dir.name,
            "candidate_kind": "full_content_pack",
            "generated_at": generated_at,
            "source_patch": source_batch_id,
            "base_content_dir": str(base_content_dir),
            "project_rules": materialization["project_rules"],
            "content_counts": {
                category: len(content_files(output_dir / category))
                for category in CONTENT_CATEGORIES
            },
            "overlay_counts": overlay_counts,
            "overridden_counts": overridden_counts,
        },
    )
    (output_dir / "README.md").write_text(
        "\n".join(
            [
                "# Materialized Content Candidate Pack",
                "",
                f"- Source patch: `{patch_dir}`",
                f"- Base content: `{base_content_dir}`",
                "- Status: generated candidate only",
                "- Accepted content: false",
                "- Runtime integrated: false",
                "",
                "Next required gate: `game_harness validate-candidates` after local binary launch is recovered.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return materialization


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Materialized Content Candidate Pack",
        "",
        f"- Source patch: `{report['source_patch']}`",
        f"- Base content: `{report['base_content_dir']}`",
        f"- Output: `{report['output_dir']}`",
        f"- Allow overrides: {report['allow_overrides']}",
        "",
        "## Overlay Counts",
        "",
    ]
    for category, count in sorted(report["overlay_counts"].items()):
        overridden = report.get("overridden_counts", {}).get(category, 0)
        suffix = f" ({overridden} overrides)" if overridden else ""
        lines.append(f"- `{category}`: {count}{suffix}")
    lines.extend(["", "## Copied Base Counts", ""])
    for category, count in sorted(report["copied_counts"].items()):
        lines.append(f"- `{category}`: {count}")
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "- This command only materializes a generated candidate pack; it does not validate, simulate, accept, or runtime-integrate the content.",
            "- Full validation still requires `game_harness validate-candidates`.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Materialize a partial Soft Candy Storm content candidate patch.")
    parser.add_argument("patch_dir", type=Path)
    parser.add_argument("--base-content-dir", type=Path, default=Path("content/base_demo"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--allow-overrides", action="store_true")
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--markdown", type=Path, default=None)
    args = parser.parse_args()

    try:
        report = materialize_pack(
            args.patch_dir,
            args.base_content_dir,
            args.output_dir,
            args.allow_overrides,
        )
    except (OSError, ValueError) as error:
        print(f"error: {error}")
        return 1

    if args.report is not None:
        write_json(args.report, report)
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
