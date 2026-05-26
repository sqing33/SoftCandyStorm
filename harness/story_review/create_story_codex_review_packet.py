#!/usr/bin/env python3
"""Create a Markdown packet for human story/codex review.

The packet gathers generated chapter/codex entries, validation evidence, and the
current TODO review draft. It does not score writing quality or promote content.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


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


def markdown_escape(text: Any) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def code(value: Any) -> str:
    return f"`{markdown_escape(value)}`"


def text_preview(value: Any, limit: int = 96) -> str:
    if isinstance(value, list):
        text = " / ".join(str(item) for item in value)
    else:
        text = str(value or "")
    text = " ".join(text.split())
    if len(text) > limit:
        return text[: limit - 1] + "..."
    return text


def read_items(candidate_pack: Path, subdir: str) -> list[dict[str, Any]]:
    directory = candidate_pack / subdir
    if not directory.exists():
        raise ValueError(f"{candidate_pack} is missing `{subdir}` directory")
    items: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path in sorted(directory.glob("*.json")):
        payload = load_json_object(path)
        item_id = payload.get("id")
        if not is_nonempty_string(item_id):
            raise ValueError(f"{path} missing non-empty id")
        if str(item_id) in seen:
            raise ValueError(f"{path}: duplicate id `{item_id}`")
        seen.add(str(item_id))
        payload["_path"] = path
        items.append(payload)
    if not items:
        raise ValueError(f"{directory} contains no JSON items")
    return items


def review_index(review_payload: dict[str, Any] | None, field: str) -> dict[str, dict[str, Any]]:
    if not review_payload:
        return {}
    reviews = review_payload.get(field)
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


def chapter_summary(chapter: dict[str, Any]) -> str:
    parts = []
    for field in ("unlock_summary", "boss_intro_line", "completion_summary"):
        if is_nonempty_string(chapter.get(field)):
            parts.append(str(chapter[field]))
    parts.extend(string_list(chapter.get("pre_run_lines")))
    return text_preview(parts, 140)


def codex_summary(codex: dict[str, Any]) -> str:
    parts = []
    for field in ("unlock_hint", "entry"):
        if is_nonempty_string(codex.get(field)):
            parts.append(str(codex[field]))
    return text_preview(parts, 140)


def build_packet(
    candidate_pack: Path,
    repo_root: Path,
    candidate_validation_report: str,
    review_draft: Path | None,
) -> dict[str, Any]:
    manifest_path = candidate_pack / "metadata" / "manifest.json"
    manifest = load_json_object(manifest_path)
    project_rules = manifest.get("project_rules")
    if not isinstance(project_rules, dict):
        raise ValueError(f"{manifest_path} must contain project_rules object")
    if project_rules.get("candidate_only") is not True:
        raise ValueError(f"{manifest_path} project_rules.candidate_only must stay true")
    if project_rules.get("accepted_content") is not False:
        raise ValueError(f"{manifest_path} project_rules.accepted_content must stay false")
    if project_rules.get("runtime_integrated") is not False:
        raise ValueError(f"{manifest_path} project_rules.runtime_integrated must stay false")

    review_payload = load_json_object(review_draft) if review_draft is not None else None
    chapter_reviews = review_index(review_payload, "chapter_reviews")
    codex_reviews = review_index(review_payload, "codex_reviews")

    chapters = []
    for item in read_items(candidate_pack, "chapters"):
        review = chapter_reviews.get(str(item["id"]))
        chapters.append(
            {
                "id": str(item["id"]),
                "title": item.get("title", ""),
                "map_id": item.get("map_id", ""),
                "boss_id": item.get("boss_id", ""),
                "theme": item.get("theme", ""),
                "path": relative_repo_path(repo_root, item["_path"]),
                "review_status": review_status(review),
                "summary": chapter_summary(item),
                "codex_unlock_count": len(string_list(item.get("codex_unlocks"))),
            }
        )

    codex_entries = []
    for item in read_items(candidate_pack, "codex"):
        review = codex_reviews.get(str(item["id"]))
        codex_entries.append(
            {
                "id": str(item["id"]),
                "title": item.get("title", ""),
                "category": item.get("category", ""),
                "path": relative_repo_path(repo_root, item["_path"]),
                "review_status": review_status(review),
                "summary": codex_summary(item),
                "related_count": len(string_list(item.get("related_ids"))),
                "tone_tags": string_list(item.get("tone_tags")),
            }
        )

    missing_chapter_reviews = sorted({item["id"] for item in chapters} - set(chapter_reviews))
    missing_codex_reviews = sorted({item["id"] for item in codex_entries} - set(codex_reviews))
    return {
        "pack_id": manifest.get("batch_id", candidate_pack.name),
        "candidate_pack": relative_repo_path(repo_root, candidate_pack),
        "manifest": relative_repo_path(repo_root, manifest_path),
        "candidate_validation_report": candidate_validation_report,
        "review_draft": relative_repo_path(repo_root, review_draft) if review_draft is not None else None,
        "chapter_count": len(chapters),
        "codex_count": len(codex_entries),
        "missing_chapter_review_count": len(missing_chapter_reviews),
        "missing_codex_review_count": len(missing_codex_reviews),
        "missing_chapter_reviews": missing_chapter_reviews,
        "missing_codex_reviews": missing_codex_reviews,
        "chapters": chapters,
        "codex_entries": codex_entries,
        "limitations": [
            "This packet organizes story/codex review evidence only.",
            "It does not validate human ratings, judge writing quality, promote UI candidates, or mark content as accepted_content.",
            "TODO review fields must be filled by a human before manual review validation can pass.",
        ],
    }


def write_markdown(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Story Codex Review Packet",
        "",
        f"- Pack: `{packet['pack_id']}`",
        f"- Candidate path: `{packet['candidate_pack']}`",
        f"- Manifest: `{packet['manifest']}`",
        f"- Candidate validation report: `{packet['candidate_validation_report']}`",
        f"- Review draft: `{packet['review_draft'] or 'None'}`",
        f"- Chapters: {packet['chapter_count']}",
        f"- Codex entries: {packet['codex_count']}",
        f"- Missing chapter reviews: {packet['missing_chapter_review_count']}",
        f"- Missing codex reviews: {packet['missing_codex_review_count']}",
        "",
        "## Chapters",
        "",
        "| Chapter | Title | Theme | Review | Unlocks |",
        "|---|---|---|---|---:|",
    ]
    for chapter in packet["chapters"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    code(chapter["id"]),
                    markdown_escape(chapter["title"]),
                    markdown_escape(chapter["theme"]),
                    code(chapter["review_status"]),
                    str(chapter["codex_unlock_count"]),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Codex", "", "| Entry | Category | Title | Review | Related |", "|---|---|---|---|---:|"])
    for codex in packet["codex_entries"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    code(codex["id"]),
                    code(codex["category"]),
                    markdown_escape(codex["title"]),
                    code(codex["review_status"]),
                    str(codex["related_count"]),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Chapter Details", ""])
    for chapter in packet["chapters"]:
        lines.extend(
            [
                f"### {chapter['id']}",
                "",
                f"- File: `{chapter['path']}`",
                f"- Map: `{chapter['map_id']}`",
                f"- Boss: `{chapter['boss_id']}`",
                f"- Review status: `{chapter['review_status']}`",
                f"- Summary preview: {chapter['summary']}",
                "",
            ]
        )

    lines.extend(["", "## Codex Details", ""])
    for codex in packet["codex_entries"]:
        tone = ", ".join(code(item) for item in codex["tone_tags"]) if codex["tone_tags"] else "None"
        lines.extend(
            [
                f"### {codex['id']}",
                "",
                f"- File: `{codex['path']}`",
                f"- Category: `{codex['category']}`",
                f"- Review status: `{codex['review_status']}`",
                f"- Tone tags: {tone}",
                f"- Summary preview: {codex['summary']}",
                "",
            ]
        )

    lines.extend(["## Missing Chapter Reviews", ""])
    if packet["missing_chapter_reviews"]:
        lines.extend(f"- `{item}`" for item in packet["missing_chapter_reviews"])
    else:
        lines.append("- None")

    lines.extend(["", "## Missing Codex Reviews", ""])
    if packet["missing_codex_reviews"]:
        lines.extend(f"- `{item}`" for item in packet["missing_codex_reviews"])
    else:
        lines.append("- None")

    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in packet["limitations"])

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Markdown packet for human story/codex review.")
    parser.add_argument("candidate_pack", type=Path, help="Path to harness/generated_candidates/<pack>")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--candidate-validation-report", required=True, help="Candidate validation summary path")
    parser.add_argument("--review-draft", type=Path, default=None, help="Manual review draft JSON")
    parser.add_argument("--out", type=Path, required=True, help="Output Markdown packet")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    candidate_pack = args.candidate_pack if args.candidate_pack.is_absolute() else repo_root / args.candidate_pack
    review_draft = None
    if args.review_draft is not None:
        review_draft = args.review_draft if args.review_draft.is_absolute() else repo_root / args.review_draft

    packet = build_packet(candidate_pack, repo_root, args.candidate_validation_report, review_draft)
    write_markdown(packet, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
