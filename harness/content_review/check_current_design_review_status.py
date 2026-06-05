#!/usr/bin/env python3
"""Check local evidence status for the current content design-review draft."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from validate_content_candidate_design_review import has_placeholder, load_json_object


SCRIPT_DIR = Path(__file__).resolve().parent
PLAYTEST_DIR = SCRIPT_DIR.parent / "playtest"
if str(PLAYTEST_DIR) not in sys.path:
    sys.path.insert(0, str(PLAYTEST_DIR))

from current_candidate import CANDIDATE_ID, CANDIDATE_LABEL, CONTENT_DIR  # noqa: E402


DEFAULT_DRAFT = Path(f"harness/content_review/drafts/{CANDIDATE_ID}_design_review_draft.json")


def load_expected_content_ids(repo_root: Path, draft: dict[str, Any], errors: list[str]) -> list[str]:
    source_patch_manifest = draft.get("source_patch_manifest")
    if not isinstance(source_patch_manifest, str) or not source_patch_manifest.strip():
        errors.append("source_patch_manifest is missing")
        return []
    manifest_path = repo_root / source_patch_manifest
    if not manifest_path.exists():
        errors.append(f"source_patch_manifest does not exist: {source_patch_manifest}")
        return []
    try:
        manifest = load_json_object(manifest_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"source_patch_manifest is invalid: {error}")
        return []
    contents = manifest.get("contents")
    if not isinstance(contents, list):
        errors.append("source_patch_manifest.contents must be a list")
        return []
    expected: list[str] = []
    for index, entry in enumerate(contents):
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
            errors.append(f"source_patch_manifest.contents[{index}] missing id")
            continue
        expected.append(entry["id"])
    return sorted(expected)


def review_index(draft: dict[str, Any]) -> dict[str, dict[str, Any]]:
    reviews = draft.get("content_reviews")
    if not isinstance(reviews, list):
        return {}
    indexed: dict[str, dict[str, Any]] = {}
    for review in reviews:
        if isinstance(review, dict) and isinstance(review.get("id"), str):
            indexed[review["id"]] = review
    return indexed


def build_report(repo_root: Path, draft_path: Path = DEFAULT_DRAFT) -> dict[str, Any]:
    resolved_draft = repo_root / draft_path
    draft_exists = resolved_draft.exists()
    errors: list[str] = []
    draft = load_json_object(resolved_draft) if draft_exists else {}
    if not draft_exists:
        errors.append(f"review draft missing: {draft_path}")

    if draft.get("candidate_pack_id") != CANDIDATE_ID:
        errors.append("review draft candidate_pack_id does not match current candidate")
    if draft.get("candidate_pack_path") != str(CONTENT_DIR):
        errors.append("review draft candidate_pack_path does not match current candidate")

    expected_ids = load_expected_content_ids(repo_root, draft, errors) if draft_exists else []
    reviews = review_index(draft)
    missing_reviews = sorted(content_id for content_id in expected_ids if content_id not in reviews)
    extra_reviews = sorted(content_id for content_id in reviews if expected_ids and content_id not in expected_ids)
    placeholder_reviews = sorted(content_id for content_id, review in reviews.items() if has_placeholder(review))
    if missing_reviews:
        errors.append(f"{len(missing_reviews)} content reviews are missing")
    if extra_reviews:
        errors.append(f"{len(extra_reviews)} content reviews are not in source_patch_manifest")

    draft_has_placeholder = has_placeholder(draft) if draft_exists else True
    if draft_has_placeholder:
        errors.append("review draft still contains TODO or placeholder markers")

    decision = "design_review_ready_for_validation" if not errors else "design_review_incomplete"
    return {
        "report_version": 1,
        "candidate_label": CANDIDATE_LABEL,
        "candidate_id": CANDIDATE_ID,
        "candidate_path": str(CONTENT_DIR),
        "draft": str(draft_path),
        "decision": decision,
        "summary": {
            "expected_content_count": len(expected_ids),
            "reviewed_content_count": len(reviews),
            "missing_review_count": len(missing_reviews),
            "draft_exists": draft_exists,
            "draft_has_placeholder": draft_has_placeholder,
            "gate_decision": draft.get("gate_decision", ""),
        },
        "expected_content_ids": expected_ids,
        "missing_reviews": missing_reviews,
        "extra_reviews": extra_reviews,
        "placeholder_reviews": placeholder_reviews,
        "errors": errors,
        "limitations": [
            "This checker only inspects local design-review draft completeness.",
            "It does not judge theme, fun, balance, readability, or production quality.",
            "Formal validation still requires validate_content_candidate_design_review.py.",
            "A valid design review still does not promote content into accepted_content or Runtime.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    summary = report["summary"]
    lines = [
        f"# {report['candidate_label']} Content Design Review Status",
        "",
        f"- Candidate id: `{report['candidate_id']}`",
        f"- Candidate path: `{report['candidate_path']}`",
        f"- Draft: `{report['draft']}`",
        f"- Decision: `{report['decision']}`",
        f"- Reviews: `{summary['reviewed_content_count']}` / `{summary['expected_content_count']}`",
        f"- Draft has placeholder: `{summary['draft_has_placeholder']}`",
        f"- Gate decision: `{summary['gate_decision']}`",
        "",
        "## Expected Contents",
        "",
    ]
    if report["expected_content_ids"]:
        lines.extend(f"- `{content_id}`" for content_id in report["expected_content_ids"])
    else:
        lines.append("- None")

    lines.extend(["", "## Missing Reviews", ""])
    if report["missing_reviews"]:
        lines.extend(f"- `{content_id}`" for content_id in report["missing_reviews"])
    else:
        lines.append("- None")

    lines.extend(["", "## Placeholder Reviews", ""])
    if report["placeholder_reviews"]:
        lines.extend(f"- `{content_id}`" for content_id in report["placeholder_reviews"])
    else:
        lines.append("- None")

    lines.extend(["", "## Errors", ""])
    if report["errors"]:
        lines.extend(f"- {error}" for error in report["errors"])
    else:
        lines.append("- None")

    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=f"Check {CANDIDATE_LABEL} content design-review draft status.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--draft", type=Path, default=DEFAULT_DRAFT)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--markdown", type=Path, default=None)
    parser.add_argument("--allow-incomplete", action="store_true")
    args = parser.parse_args()

    report = build_report(args.repo_root, args.draft)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))

    if report["decision"] == "design_review_ready_for_validation" or args.allow_incomplete:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
