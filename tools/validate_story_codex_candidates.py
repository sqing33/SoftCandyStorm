#!/usr/bin/env python3
"""Validate generated story chapter and codex candidate packs.

This dependency-free validator is intentionally conservative. It checks that a
story/codex pack remains a generated candidate, references known base_demo
content, keeps chapter text short enough for future UI use, and avoids obvious
theme violations. A passing report does not promote the pack out of
generated_candidates.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ALLOWED_CODEX_CATEGORIES = {
    "world",
    "character",
    "enemy",
    "boss",
    "map",
    "weapon",
    "passive",
    "event",
    "evolution",
}
BASE_CONTENT_CATEGORIES = [
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
REQUIRED_PROJECT_RULES = {
    "candidate_only": True,
    "accepted_content": False,
    "runtime_integrated": False,
}
REQUIRED_SOURCE_DOCS = {
    "docs/03_世界观与剧情大纲.md",
    "docs/18_完整游戏流程与局外成长.md",
}
FORBIDDEN_TERMS = {
    "blood",
    "gore",
    "horror",
    "sci-fi",
    "gun",
    "zombie",
    "血腥",
    "恐怖",
    "枪械",
    "僵尸",
    "赛博",
    "暗黑",
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


def discover_candidates(root: Path) -> list[Path]:
    if (root / "metadata" / "manifest.json").exists():
        return [root]
    return sorted(path for path in root.iterdir() if path.is_dir()) if root.exists() else []


def collect_base_ids(base_content_dir: Path | None) -> dict[str, set[str]]:
    ids: dict[str, set[str]] = {category: set() for category in BASE_CONTENT_CATEGORIES}
    ids["all"] = set()
    if base_content_dir is None or not base_content_dir.exists():
        return ids

    for category in BASE_CONTENT_CATEGORIES:
        category_dir = base_content_dir / category
        if not category_dir.exists():
            continue
        for path in sorted(category_dir.glob("*.json")):
            try:
                payload = load_json_object(path)
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            item_id = payload.get("id")
            if is_nonempty_string(item_id):
                ids[category].add(str(item_id))
                ids["all"].add(str(item_id))
    return ids


def check_id(label: str, item_id: Any, path: Path, errors: list[str], warnings: list[str]) -> str:
    display_id = str(item_id) if is_nonempty_string(item_id) else path.stem
    if not is_nonempty_string(item_id) or not ID_PATTERN.match(str(item_id)):
        errors.append(f"{label} `{display_id}` has invalid kebab-case id")
    elif item_id != path.stem:
        warnings.append(f"{label} `{item_id}` id does not match file stem `{path.stem}`")
    return display_id


def validate_forbidden_terms(label: str, values: list[str], errors: list[str]) -> None:
    combined = "\n".join(values).lower()
    for term in sorted(FORBIDDEN_TERMS):
        if term.lower() in combined:
            errors.append(f"{label} contains forbidden theme term `{term}`")


def require_text(
    label: str,
    payload: dict[str, Any],
    field: str,
    errors: list[str],
    max_length: int | None = None,
) -> str:
    value = payload.get(field)
    if not is_nonempty_string(value):
        errors.append(f"{label} missing non-empty `{field}`")
        return ""
    text = str(value).strip()
    if max_length is not None and len(text) > max_length:
        errors.append(f"{label} `{field}` is too long: {len(text)} > {max_length}")
    return text


def validate_manifest(candidate_dir: Path) -> tuple[dict[str, Any] | None, list[str], list[str]]:
    manifest_path = candidate_dir / "metadata" / "manifest.json"
    errors: list[str] = []
    warnings: list[str] = []
    if not manifest_path.exists():
        return None, ["candidate is missing metadata/manifest.json"], warnings

    try:
        manifest = load_json_object(manifest_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return None, [f"metadata/manifest.json is invalid: {error}"], warnings

    if manifest.get("batch_id") != candidate_dir.name:
        warnings.append("manifest batch_id should match candidate directory name")
    if manifest.get("candidate_kind") != "story_codex_seed_pack":
        errors.append("manifest candidate_kind must be `story_codex_seed_pack`")
    if not is_nonempty_string(manifest.get("generated_at")):
        errors.append("manifest generated_at must be non-empty")

    source_docs = set(string_list(manifest.get("source_docs")))
    missing_docs = sorted(REQUIRED_SOURCE_DOCS - source_docs)
    if missing_docs:
        errors.append(f"manifest source_docs missing required docs: {', '.join(missing_docs)}")

    project_rules = manifest.get("project_rules")
    if not isinstance(project_rules, dict):
        errors.append("manifest project_rules must be an object")
    else:
        for key, expected in REQUIRED_PROJECT_RULES.items():
            if project_rules.get(key) is not expected:
                errors.append(f"manifest project_rules.{key} must be {json.dumps(expected)}")
        if not string_list(project_rules.get("required_next_steps")):
            errors.append("manifest project_rules.required_next_steps must be non-empty")

    content_counts = manifest.get("content_counts")
    if not isinstance(content_counts, dict):
        errors.append("manifest content_counts must be an object")
    else:
        for field in ("chapters", "codex_entries"):
            if not isinstance(content_counts.get(field), int) or content_counts[field] <= 0:
                errors.append(f"manifest content_counts.{field} must be a positive integer")

    return manifest, errors, warnings


def list_json_files(candidate_dir: Path, subdir: str, errors: list[str]) -> list[Path]:
    target_dir = candidate_dir / subdir
    if not target_dir.exists():
        errors.append(f"candidate is missing `{subdir}` directory")
        return []
    files = sorted(target_dir.glob("*.json"))
    if not files:
        errors.append(f"candidate `{subdir}` directory contains no JSON files")
    return files


def load_payloads(
    candidate_dir: Path,
    subdir: str,
    errors: list[str],
) -> dict[str, tuple[Path, dict[str, Any]]]:
    payloads: dict[str, tuple[Path, dict[str, Any]]] = {}
    for path in list_json_files(candidate_dir, subdir, errors):
        try:
            payload = load_json_object(path)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            errors.append(f"{path.relative_to(candidate_dir)} is invalid JSON: {error}")
            continue
        item_id = payload.get("id")
        key = str(item_id) if is_nonempty_string(item_id) else path.stem
        if key in payloads:
            errors.append(f"duplicate `{subdir}` id `{key}`")
        payloads[key] = (path, payload)
    return payloads


def validate_chapter(
    path: Path,
    payload: dict[str, Any],
    candidate_dir: Path,
    base_ids: dict[str, set[str]],
    codex_ids: set[str],
    errors: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    label = f"chapter `{path.stem}`"
    item_id = check_id("chapter", payload.get("id"), path, errors, warnings)
    text_values = [
        require_text(label, payload, "title", errors, 32),
        require_text(label, payload, "theme", errors, 40),
        require_text(label, payload, "unlock_summary", errors, 100),
        require_text(label, payload, "boss_intro_line", errors, 80),
        require_text(label, payload, "completion_summary", errors, 120),
    ]

    map_id = payload.get("map_id")
    if not is_nonempty_string(map_id):
        errors.append(f"{label} missing non-empty `map_id`")
    elif map_id not in base_ids["maps"]:
        errors.append(f"{label} map_id `{map_id}` does not exist in base content maps")

    boss_id = payload.get("boss_id")
    if not is_nonempty_string(boss_id):
        errors.append(f"{label} missing non-empty `boss_id`")
    elif boss_id not in base_ids["bosses"]:
        errors.append(f"{label} boss_id `{boss_id}` does not exist in base content bosses")

    pre_run_lines = payload.get("pre_run_lines")
    if not isinstance(pre_run_lines, list) or len(pre_run_lines) not in {2, 3}:
        errors.append(f"{label} pre_run_lines must contain 2 or 3 short strings")
        line_count = 0
    else:
        line_count = len(pre_run_lines)
        for index, line in enumerate(pre_run_lines):
            if not is_nonempty_string(line):
                errors.append(f"{label} pre_run_lines[{index}] must be non-empty")
                continue
            line_text = str(line).strip()
            text_values.append(line_text)
            if len(line_text) > 60:
                errors.append(f"{label} pre_run_lines[{index}] is too long: {len(line_text)} > 60")

    codex_unlocks = string_list(payload.get("codex_unlocks"))
    if not codex_unlocks or len(codex_unlocks) != len(payload.get("codex_unlocks", [])):
        errors.append(f"{label} codex_unlocks must be a non-empty list of strings")
    for codex_id in codex_unlocks:
        if codex_id not in codex_ids:
            errors.append(f"{label} codex_unlock `{codex_id}` does not exist in codex entries")

    validate_forbidden_terms(label, text_values, errors)
    return {
        "id": item_id,
        "path": str(path.relative_to(candidate_dir)),
        "map_id": map_id if is_nonempty_string(map_id) else None,
        "boss_id": boss_id if is_nonempty_string(boss_id) else None,
        "pre_run_line_count": line_count,
        "codex_unlock_count": len(codex_unlocks),
    }


def validate_codex_entry(
    path: Path,
    payload: dict[str, Any],
    candidate_dir: Path,
    known_reference_ids: set[str],
    errors: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    label = f"codex `{path.stem}`"
    item_id = check_id("codex", payload.get("id"), path, errors, warnings)
    category = payload.get("category")
    if category not in ALLOWED_CODEX_CATEGORIES:
        errors.append(f"{label} category must be one of {', '.join(sorted(ALLOWED_CODEX_CATEGORIES))}")
    elif is_nonempty_string(item_id) and not str(item_id).startswith(f"{category}-"):
        warnings.append(f"{label} id does not start with category prefix `{category}-`")

    text_values = [
        require_text(label, payload, "title", errors, 32),
        require_text(label, payload, "unlock_hint", errors, 60),
        require_text(label, payload, "entry", errors, 160),
    ]

    related_ids = string_list(payload.get("related_ids"))
    if not related_ids or len(related_ids) != len(payload.get("related_ids", [])):
        errors.append(f"{label} related_ids must be a non-empty list of strings")
    elif not any(related_id in known_reference_ids for related_id in related_ids):
        errors.append(f"{label} related_ids must reference at least one known base content or chapter id")
    else:
        for related_id in related_ids:
            if related_id not in known_reference_ids:
                warnings.append(f"{label} related_id `{related_id}` is not known locally")

    tone_tags = string_list(payload.get("tone_tags"))
    if not tone_tags or len(tone_tags) != len(payload.get("tone_tags", [])):
        errors.append(f"{label} tone_tags must be a non-empty list of strings")

    validate_forbidden_terms(label, text_values + tone_tags, errors)
    return {
        "id": item_id,
        "path": str(path.relative_to(candidate_dir)),
        "category": category if isinstance(category, str) else None,
        "related_count": len(related_ids),
        "tone_tag_count": len(tone_tags),
    }


def validate_candidate(
    candidate_dir: Path,
    base_ids: dict[str, set[str]],
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    manifest, manifest_errors, manifest_warnings = validate_manifest(candidate_dir)
    errors.extend(manifest_errors)
    warnings.extend(manifest_warnings)

    chapter_payloads = load_payloads(candidate_dir, "chapters", errors)
    codex_payloads = load_payloads(candidate_dir, "codex", errors)
    chapter_ids = set(chapter_payloads)
    codex_ids = set(codex_payloads)
    known_reference_ids = set(base_ids["all"]) | chapter_ids

    chapter_reports = [
        validate_chapter(path, payload, candidate_dir, base_ids, codex_ids, errors, warnings)
        for _, (path, payload) in sorted(chapter_payloads.items())
    ]
    codex_reports = [
        validate_codex_entry(path, payload, candidate_dir, known_reference_ids, errors, warnings)
        for _, (path, payload) in sorted(codex_payloads.items())
    ]

    if manifest is not None:
        content_counts = manifest.get("content_counts", {})
        expected_chapters = content_counts.get("chapters") if isinstance(content_counts, dict) else None
        expected_codex = content_counts.get("codex_entries") if isinstance(content_counts, dict) else None
        if isinstance(expected_chapters, int) and expected_chapters != len(chapter_reports):
            errors.append(f"manifest expects {expected_chapters} chapters but found {len(chapter_reports)}")
        if isinstance(expected_codex, int) and expected_codex != len(codex_reports):
            errors.append(f"manifest expects {expected_codex} codex entries but found {len(codex_reports)}")

    if not (candidate_dir / "README.md").exists():
        warnings.append("candidate is missing README.md")

    return {
        "id": candidate_dir.name,
        "path": str(candidate_dir),
        "decision": "valid" if not errors else "invalid",
        "chapter_count": len(chapter_reports),
        "codex_entry_count": len(codex_reports),
        "chapters": chapter_reports,
        "codex_entries": codex_reports,
        "errors": errors,
        "warnings": warnings,
    }


def build_report(root: Path, base_content_dir: Path | None) -> dict[str, Any]:
    candidates = discover_candidates(root)
    base_ids = collect_base_ids(base_content_dir)
    reviews = [validate_candidate(path, base_ids) for path in candidates]
    errors = [f"{review['id']}: {error}" for review in reviews for error in review["errors"]]
    warnings = [f"{review['id']}: {warning}" for review in reviews for warning in review["warnings"]]
    if not candidates:
        errors.append(f"no candidate directories found under {root}")

    return {
        "report_version": 1,
        "root": str(root),
        "base_content_dir": str(base_content_dir) if base_content_dir is not None else None,
        "decision": "story_codex_candidates_valid" if not errors else "story_codex_candidates_invalid",
        "candidate_count": len(reviews),
        "chapter_count": sum(review["chapter_count"] for review in reviews),
        "codex_entry_count": sum(review["codex_entry_count"] for review in reviews),
        "errors": errors,
        "warnings": warnings,
        "candidates": reviews,
        "limitations": [
            "This validator checks generated story/codex candidate structure, references, and text guardrails only.",
            "A passing report does not promote candidates beyond generated_candidates.",
            "Lore tone, spoiler pacing, UI fit, localization quality, and acceptance still require human review.",
            "Runtime integration is intentionally blocked until a future accepted candidate path exists.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Story Codex Candidate Validation",
        "",
        f"- Root: `{report['root']}`",
        f"- Decision: `{report['decision']}`",
        f"- Candidate count: {report['candidate_count']}",
        f"- Chapters: {report['chapter_count']}",
        f"- Codex entries: {report['codex_entry_count']}",
        "",
        "## Candidates",
        "",
        "| Candidate | Decision | Chapters | Codex | Errors | Warnings |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for candidate in report["candidates"]:
        lines.append(
            f"| `{candidate['id']}` | `{candidate['decision']}` | "
            f"{candidate['chapter_count']} | {candidate['codex_entry_count']} | "
            f"{len(candidate['errors'])} | {len(candidate['warnings'])} |"
        )

    lines.extend(["", "## Errors", ""])
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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm story/codex candidate packs.")
    parser.add_argument(
        "root",
        type=Path,
        nargs="?",
        default=Path("harness/generated_candidates"),
        help="Generated story/codex candidate root or a single candidate directory",
    )
    parser.add_argument("--base-content-dir", type=Path, default=Path("content/base_demo"))
    parser.add_argument("--report", type=Path, default=None, help="Write JSON validation report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown validation summary")
    args = parser.parse_args()

    report = build_report(args.root, args.base_content_dir)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "story_codex_candidates_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
