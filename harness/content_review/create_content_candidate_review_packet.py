#!/usr/bin/env python3
"""Create a Markdown packet for human content candidate design review.

The packet gathers source patch entries, generated content previews, preflight
evidence, and the current TODO design-review draft. It does not score, promote,
simulate, or accept content.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


TYPE_TO_CATEGORY = {
    "character": "characters",
    "weapon": "weapons",
    "passive": "passives",
    "evolution": "evolutions",
    "enemy": "enemies",
    "boss": "bosses",
    "wave": "waves",
    "map": "maps",
    "event": "events",
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


def relative_repo_path(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(path)


def markdown_escape(text: Any) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def code(value: Any) -> str:
    return f"`{markdown_escape(value)}`"


def text_preview(value: Any, limit: int = 120) -> str:
    if isinstance(value, list):
        text = " / ".join(str(item) for item in value)
    else:
        text = str(value or "")
    text = " ".join(text.split())
    if len(text) > limit:
        return text[: limit - 1] + "..."
    return text


def validate_project_rules(label: str, project_rules: Any) -> None:
    if not isinstance(project_rules, dict):
        raise ValueError(f"{label} project_rules must be an object")
    if project_rules.get("candidate_only") is not True:
        raise ValueError(f"{label} project_rules.candidate_only must stay true")
    if project_rules.get("accepted_content") is not False:
        raise ValueError(f"{label} project_rules.accepted_content must stay false")
    if project_rules.get("runtime_integrated") is not False:
        raise ValueError(f"{label} project_rules.runtime_integrated must stay false")


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


def review_index(review_payload: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not review_payload:
        return {}
    reviews = review_payload.get("content_reviews")
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


def source_patch_contents(source_manifest: dict[str, Any]) -> list[dict[str, Any]]:
    contents = source_manifest.get("contents")
    if not isinstance(contents, list) or not contents:
        raise ValueError("source_patch_manifest.contents must be a non-empty list")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, entry in enumerate(contents):
        if not isinstance(entry, dict):
            raise ValueError(f"source_patch_manifest.contents[{index}] must be an object")
        content_id = entry.get("id")
        content_type = entry.get("type")
        if not is_nonempty_string(content_id):
            raise ValueError(f"source_patch_manifest.contents[{index}] missing id")
        if str(content_id) in seen:
            raise ValueError(f"source_patch_manifest duplicate content id `{content_id}`")
        if not is_nonempty_string(content_type) or str(content_type) not in TYPE_TO_CATEGORY:
            raise ValueError(f"{content_id}: unsupported content type `{content_type}`")
        seen.add(str(content_id))
        result.append(entry)
    return result


def content_summary(content: dict[str, Any]) -> str:
    parts = []
    for field in ("description", "visual_description", "sfx_description"):
        if is_nonempty_string(content.get(field)):
            parts.append(str(content[field]))
    if not parts:
        parts.extend(string_list(content.get("tags")))
    return text_preview(parts, 160)


def balance_risk(entry: dict[str, Any]) -> str:
    budget = entry.get("balance_budget")
    if isinstance(budget, dict) and is_nonempty_string(budget.get("risk")):
        return str(budget["risk"])
    return ""


def gate_focus(entry: dict[str, Any]) -> str:
    budget = entry.get("balance_budget")
    if isinstance(budget, dict) and is_nonempty_string(budget.get("gate_focus")):
        return str(budget["gate_focus"])
    return ""


def build_packet(
    candidate_pack: Path,
    repo_root: Path,
    preflight_report: str,
    review_draft: Path | None,
) -> dict[str, Any]:
    manifest_path = candidate_pack / "metadata" / "manifest.json"
    source_manifest_path = candidate_pack / "metadata" / "source_patch_manifest.json"
    manifest = load_json_object(manifest_path)
    source_manifest = load_json_object(source_manifest_path)

    if manifest.get("candidate_kind") != "full_content_pack":
        raise ValueError(f"{manifest_path} candidate_kind must be full_content_pack")
    validate_project_rules("candidate manifest", manifest.get("project_rules"))
    validate_project_rules("source_patch_manifest", source_manifest.get("project_rules"))

    review_payload = load_json_object(review_draft) if review_draft is not None else None
    reviews = review_index(review_payload)

    items = []
    for entry in source_patch_contents(source_manifest):
        content_path = content_path_for_entry(candidate_pack, entry)
        if not content_path.exists():
            raise ValueError(f"{entry['id']}: candidate pack missing content file {content_path}")
        content = load_json_object(content_path)
        review = reviews.get(str(entry["id"]))
        items.append(
            {
                "id": str(entry["id"]),
                "type": str(entry["type"]),
                "role": entry.get("role", ""),
                "path": relative_repo_path(repo_root, content_path),
                "name": content.get("name", ""),
                "rarity": content.get("rarity", ""),
                "tags": string_list(content.get("tags")),
                "review_status": review_status(review),
                "summary": content_summary(content),
                "balance_risk": balance_risk(entry),
                "gate_focus": gate_focus(entry),
                "counterplay_or_limit": entry.get("counterplay_or_limit", ""),
            }
        )

    missing_review_ids = sorted({item["id"] for item in items} - set(reviews))
    type_counts: dict[str, int] = {}
    for item in items:
        type_counts[item["type"]] = type_counts.get(item["type"], 0) + 1

    return {
        "pack_id": manifest.get("batch_id", candidate_pack.name),
        "candidate_pack": relative_repo_path(repo_root, candidate_pack),
        "manifest": relative_repo_path(repo_root, manifest_path),
        "source_patch_manifest": relative_repo_path(repo_root, source_manifest_path),
        "preflight_report": preflight_report,
        "review_draft": relative_repo_path(repo_root, review_draft) if review_draft is not None else None,
        "content_count": len(items),
        "type_counts": dict(sorted(type_counts.items())),
        "missing_review_count": len(missing_review_ids),
        "missing_review_ids": missing_review_ids,
        "items": items,
        "limitations": [
            "This packet organizes content design review evidence only.",
            "It does not validate human ratings, run Schema or static budget gates, simulate content, or promote candidates.",
            "TODO review fields must be filled by a human before design-review validation can pass.",
            "A valid design review still does not write to validated_candidates, simulated_candidates, playtest_candidates, accepted_content, or Runtime.",
        ],
    }


def write_markdown(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Content Candidate Review Packet",
        "",
        f"- Pack: `{packet['pack_id']}`",
        f"- Candidate path: `{packet['candidate_pack']}`",
        f"- Manifest: `{packet['manifest']}`",
        f"- Source patch manifest: `{packet['source_patch_manifest']}`",
        f"- Preflight report: `{packet['preflight_report']}`",
        f"- Review draft: `{packet['review_draft'] or 'None'}`",
        f"- Contents: {packet['content_count']}",
        f"- Missing review entries: {packet['missing_review_count']}",
        "",
        "## Type Counts",
        "",
        "| Type | Count |",
        "|---|---:|",
    ]
    for content_type, count in packet["type_counts"].items():
        lines.append(f"| `{content_type}` | {count} |")

    lines.extend(
        [
            "",
            "## Contents",
            "",
            "| Content | Type | Name | Role | Review |",
            "|---|---|---|---|---|",
        ]
    )
    for item in packet["items"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    code(item["id"]),
                    code(item["type"]),
                    markdown_escape(item["name"]),
                    markdown_escape(item["role"]),
                    code(item["review_status"]),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Content Details", ""])
    for item in packet["items"]:
        tags = ", ".join(code(tag) for tag in item["tags"]) if item["tags"] else "None"
        lines.extend(
            [
                f"### {item['id']}",
                "",
                f"- File: `{item['path']}`",
                f"- Type: `{item['type']}`",
                f"- Rarity: `{item['rarity']}`",
                f"- Tags: {tags}",
                f"- Review status: `{item['review_status']}`",
                f"- Role: {markdown_escape(item['role'])}",
                f"- Balance risk: {markdown_escape(item['balance_risk'])}",
                f"- Gate focus: {markdown_escape(item['gate_focus'])}",
                f"- Counterplay or limit: {markdown_escape(item['counterplay_or_limit'])}",
                f"- Summary preview: {markdown_escape(item['summary'])}",
                "",
            ]
        )

    lines.extend(["## Missing Review Entries", ""])
    if packet["missing_review_ids"]:
        lines.extend(f"- `{item}`" for item in packet["missing_review_ids"])
    else:
        lines.append("- None")

    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in packet["limitations"])

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Markdown packet for content candidate design review.")
    parser.add_argument("candidate_pack", type=Path, help="Path to harness/generated_candidates/<full-pack>")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--preflight-report", required=True, help="Existing materialized content preflight summary path")
    parser.add_argument("--review-draft", type=Path, default=None, help="Design review draft JSON")
    parser.add_argument("--out", type=Path, required=True, help="Output Markdown packet")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    candidate_pack = args.candidate_pack if args.candidate_pack.is_absolute() else repo_root / args.candidate_pack
    review_draft = None
    if args.review_draft is not None:
        review_draft = args.review_draft if args.review_draft.is_absolute() else repo_root / args.review_draft

    packet = build_packet(candidate_pack, repo_root, args.preflight_report, review_draft)
    write_markdown(packet, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
