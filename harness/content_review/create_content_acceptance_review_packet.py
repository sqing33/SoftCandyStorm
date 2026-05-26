#!/usr/bin/env python3
"""Create a final content-acceptance evidence packet.

This packet gathers the evidence required before a generated content pack can
eventually move toward accepted_content. It does not validate human reviews,
run Harness simulation, promote candidates, write accepted_content, or approve
release readiness.
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
TODO_MARKERS = ("TODO", "<", ">")
REQUIRED_EVIDENCE = [
    {
        "field": "candidate_preflight_report",
        "label": "Candidate preflight",
        "expected": "materialized full pack preflight exists",
        "blocking_if_missing": True,
    },
    {
        "field": "static_budget_report",
        "label": "Static budget",
        "expected": "pure Python static budget exists",
        "blocking_if_missing": True,
    },
    {
        "field": "design_review_draft",
        "label": "Design review draft",
        "expected": "human-filled design review must replace TODO values",
        "blocking_if_missing": True,
    },
    {
        "field": "design_review_packet",
        "label": "Design review packet",
        "expected": "review packet exists for human review",
        "blocking_if_missing": True,
    },
    {
        "field": "demo_readiness_report",
        "label": "Demo readiness",
        "expected": "demo readiness must not be demo_ready until gates pass",
        "blocking_if_missing": True,
    },
    {
        "field": "manual_playtest_draft",
        "label": "Manual playtest draft",
        "expected": "9-run human playtest must be filled by a human",
        "blocking_if_missing": True,
    },
    {
        "field": "accepted_content_lockfile_report",
        "label": "Accepted content lockfile",
        "expected": "non-empty lockfile only after strict human acceptance",
        "blocking_if_missing": True,
    },
]


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


def evidence_status(repo_root: Path, value: str | None) -> tuple[str, str | None]:
    if not is_nonempty_string(value):
        return "missing", None
    path = resolve_repo_path(repo_root, str(value))
    if not is_inside_repo(repo_root, path):
        return "outside_repo", None
    if not path.exists():
        return "missing_file", relative_repo_path(repo_root, path)
    return "exists", relative_repo_path(repo_root, path)


def validate_project_rules(label: str, rules: Any, errors: list[str]) -> None:
    if not isinstance(rules, dict):
        errors.append(f"{label} project_rules must be an object")
        return
    expected = {
        "candidate_only": True,
        "accepted_content": False,
        "runtime_integrated": False,
    }
    for field, expected_value in expected.items():
        if rules.get(field) is not expected_value:
            errors.append(f"{label} project_rules.{field} must be {json.dumps(expected_value)}")


def source_patch_contents(source_manifest: dict[str, Any]) -> list[dict[str, Any]]:
    contents = source_manifest.get("contents")
    if not isinstance(contents, list):
        return []
    return [item for item in contents if isinstance(item, dict)]


def content_path_for_entry(candidate_pack: Path, entry: dict[str, Any]) -> Path:
    entry_path = entry.get("path")
    if is_nonempty_string(entry_path):
        return candidate_pack / str(entry_path)
    content_type = entry.get("type")
    content_id = entry.get("id")
    category = TYPE_TO_CATEGORY.get(str(content_type))
    if category is None or not is_nonempty_string(content_id):
        return candidate_pack / "__missing__"
    return candidate_pack / category / f"{content_id}.json"


def item_summary(candidate_pack: Path, repo_root: Path, entry: dict[str, Any]) -> dict[str, Any]:
    content_path = content_path_for_entry(candidate_pack, entry)
    payload: dict[str, Any] = {}
    if content_path.exists():
        try:
            payload = load_json_object(content_path)
        except (OSError, ValueError, json.JSONDecodeError):
            payload = {}
    return {
        "id": entry.get("id"),
        "type": entry.get("type"),
        "role": entry.get("role", ""),
        "path": relative_repo_path(repo_root, content_path),
        "name": payload.get("name", ""),
        "tags": string_list(payload.get("tags")),
        "balance_risk": entry.get("balance_budget", {}).get("risk", "")
        if isinstance(entry.get("balance_budget"), dict)
        else "",
        "gate_focus": entry.get("balance_budget", {}).get("gate_focus", "")
        if isinstance(entry.get("balance_budget"), dict)
        else "",
    }


def review_draft_status(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {
            "decision": None,
            "gate_decision": None,
            "content_review_count": 0,
            "todo_count": 0,
            "status": "missing",
        }
    try:
        payload = load_json_object(path)
    except (OSError, ValueError, json.JSONDecodeError):
        return {
            "decision": None,
            "gate_decision": None,
            "content_review_count": 0,
            "todo_count": 0,
            "status": "invalid_json",
        }
    serialized = json.dumps(payload, ensure_ascii=False)
    reviews = payload.get("content_reviews")
    review_count = len(reviews) if isinstance(reviews, list) else 0
    todo_count = serialized.count("TODO")
    return {
        "decision": payload.get("decision"),
        "gate_decision": payload.get("gate_decision"),
        "content_review_count": review_count,
        "todo_count": todo_count,
        "status": "draft_todo" if todo_count else "filled",
    }


def manual_playtest_status(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {"acceptance_decision": None, "run_count": 0, "todo_count": 0, "status": "missing"}
    try:
        payload = load_json_object(path)
    except (OSError, ValueError, json.JSONDecodeError):
        return {"acceptance_decision": None, "run_count": 0, "todo_count": 0, "status": "invalid_json"}
    runs = payload.get("runs")
    run_count = len(runs) if isinstance(runs, list) else 0
    todo_count = json.dumps(payload, ensure_ascii=False).count("TODO")
    return {
        "acceptance_decision": payload.get("acceptance_decision"),
        "run_count": run_count,
        "todo_count": todo_count,
        "status": "draft_todo" if todo_count else "filled",
    }


def decision_from_report(path: Path | None) -> str | None:
    if path is None or not path.exists():
        return None
    try:
        payload = load_json_object(path)
    except (OSError, ValueError, json.JSONDecodeError):
        return None
    return payload.get("decision") if is_nonempty_string(payload.get("decision")) else None


def build_packet(
    candidate_pack: Path,
    repo_root: Path,
    evidence_paths: dict[str, str],
) -> dict[str, Any]:
    errors: list[str] = []
    manifest_path = candidate_pack / "metadata/manifest.json"
    source_manifest_path = candidate_pack / "metadata/source_patch_manifest.json"
    manifest = load_json_object(manifest_path)
    source_manifest = load_json_object(source_manifest_path)
    validate_project_rules("candidate manifest", manifest.get("project_rules"), errors)
    validate_project_rules("source_patch_manifest", source_manifest.get("project_rules"), errors)

    evidence = []
    resolved_paths: dict[str, Path | None] = {}
    for requirement in REQUIRED_EVIDENCE:
        field = str(requirement["field"])
        status, resolved_text = evidence_status(repo_root, evidence_paths.get(field))
        resolved_paths[field] = resolve_repo_path(repo_root, evidence_paths[field]) if status == "exists" else None
        evidence.append(
            {
                "field": field,
                "label": requirement["label"],
                "value": evidence_paths.get(field),
                "status": status,
                "resolved_path": resolved_text,
                "expected": requirement["expected"],
                "blocking_if_missing": requirement["blocking_if_missing"],
            }
        )
        if status != "exists" and requirement["blocking_if_missing"]:
            errors.append(f"{field} evidence must exist")

    items = [
        item_summary(candidate_pack, repo_root, entry)
        for entry in source_patch_contents(source_manifest)
    ]
    type_counts: dict[str, int] = {}
    for item in items:
        item_type = str(item.get("type"))
        type_counts[item_type] = type_counts.get(item_type, 0) + 1

    design_status = review_draft_status(resolved_paths.get("design_review_draft"))
    manual_status = manual_playtest_status(resolved_paths.get("manual_playtest_draft"))
    demo_decision = decision_from_report(resolved_paths.get("demo_readiness_report"))
    lock_decision = decision_from_report(resolved_paths.get("accepted_content_lockfile_report"))

    blockers: list[str] = []
    if design_status["todo_count"]:
        blockers.append("design review draft still contains TODO placeholders")
    if design_status["gate_decision"] != "simulate_candidate":
        blockers.append("design review has not reached simulate_candidate")
    if manual_status["todo_count"]:
        blockers.append("manual playtest draft still contains TODO placeholders")
    if manual_status["acceptance_decision"] != "accept_candidate":
        blockers.append("manual playtest has not accepted the candidate")
    if demo_decision != "demo_ready":
        blockers.append(f"demo readiness is `{demo_decision}`")
    if lock_decision != "accepted_content_lockfile_valid":
        blockers.append(f"accepted content lockfile is `{lock_decision}`")

    if errors:
        decision = "content_acceptance_review_packet_invalid"
    elif blockers:
        decision = "content_acceptance_review_packet_needs_evidence"
    else:
        decision = "content_acceptance_review_packet_ready_for_validation"

    return {
        "report_version": 1,
        "source": relative_repo_path(repo_root, candidate_pack),
        "repo_root": str(repo_root),
        "decision": decision,
        "candidate_pack_id": manifest.get("batch_id", candidate_pack.name),
        "candidate_kind": manifest.get("candidate_kind"),
        "content_count": len(items),
        "type_counts": dict(sorted(type_counts.items())),
        "evidence_count": len(evidence),
        "existing_evidence_count": sum(1 for item in evidence if item["status"] == "exists"),
        "errors": errors,
        "blockers": blockers,
        "evidence": evidence,
        "design_review_status": design_status,
        "manual_playtest_status": manual_status,
        "demo_readiness_decision": demo_decision,
        "accepted_content_lockfile_decision": lock_decision,
        "items": items,
        "required_next_steps": [
            "Replace design review TODO values with a real human design review and validate it.",
            "After binary recovery, run formal Harness validate-candidates, budget-content, Bot simulation, and replay regression.",
            "Run and fill the 9-run manual playtest review with human ratings and notes.",
            "Only after strict human acceptance, generate a non-empty accepted content lockfile.",
        ],
        "limitations": [
            "This packet organizes content acceptance evidence only.",
            "It does not validate human reviews, simulate content, promote candidates, write accepted_content, or approve release readiness.",
            "Candidate content remains generated_candidates until every required gate passes.",
        ],
    }


def write_markdown(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Content Acceptance Review Packet",
        "",
        f"- Source: `{packet['source']}`",
        f"- Decision: `{packet['decision']}`",
        f"- Candidate pack: `{packet['candidate_pack_id']}`",
        f"- Candidate kind: `{packet['candidate_kind']}`",
        f"- Contents: {packet['content_count']}",
        f"- Evidence files: {packet['existing_evidence_count']} / {packet['evidence_count']}",
        f"- Demo readiness: `{packet['demo_readiness_decision']}`",
        f"- Accepted content lockfile: `{packet['accepted_content_lockfile_decision']}`",
        "",
        "## Evidence",
        "",
        "| Field | Status | Expected | Path |",
        "|---|---|---|---|",
    ]
    for item in packet["evidence"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    code(item["field"]),
                    code(item["status"]),
                    markdown_escape(item["expected"]),
                    code(item["resolved_path"] or item["value"]),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Review Status", ""])
    lines.append(f"- Design review status: `{packet['design_review_status']['status']}`")
    lines.append(f"- Design review gate: `{packet['design_review_status']['gate_decision']}`")
    lines.append(f"- Design review TODO count: `{packet['design_review_status']['todo_count']}`")
    lines.append(f"- Manual playtest status: `{packet['manual_playtest_status']['status']}`")
    lines.append(f"- Manual playtest decision: `{packet['manual_playtest_status']['acceptance_decision']}`")
    lines.append(f"- Manual playtest TODO count: `{packet['manual_playtest_status']['todo_count']}`")

    lines.extend(["", "## Type Counts", "", "| Type | Count |", "|---|---:|"])
    for item_type, count in packet["type_counts"].items():
        lines.append(f"| `{item_type}` | {count} |")

    lines.extend(["", "## Contents", "", "| Content | Type | Name | Tags | Gate Focus |", "|---|---|---|---|---|"])
    for item in packet["items"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    code(item["id"]),
                    code(item["type"]),
                    markdown_escape(item["name"]),
                    ", ".join(code(tag) for tag in item["tags"]) or "-",
                    markdown_escape(item["gate_focus"] or "-"),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Blockers", ""])
    if packet["blockers"]:
        lines.extend(f"- {blocker}" for blocker in packet["blockers"])
    else:
        lines.append("- None")

    lines.extend(["", "## Errors", ""])
    if packet["errors"]:
        lines.extend(f"- {error}" for error in packet["errors"])
    else:
        lines.append("- None")

    lines.extend(["", "## Required Next Steps", ""])
    lines.extend(f"- {item}" for item in packet["required_next_steps"])
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in packet["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def default_evidence_paths() -> dict[str, str]:
    return {
        "candidate_preflight_report": "harness/reports/2026-05-26_phase4_roster_full_pack_preflight_001/summary.md",
        "static_budget_report": "harness/reports/2026-05-26_static_balance_budget_phase4_full_pack_001/summary.md",
        "design_review_draft": "harness/content_review/drafts/2026-05-26_phase4_roster_gap_full_pack_design_review_draft.json",
        "design_review_packet": "harness/reports/2026-05-26_phase4_roster_content_review_packet_001/summary.md",
        "demo_readiness_report": "harness/reports/2026-05-26_demo_readiness_current_local_001/demo_readiness.json",
        "manual_playtest_draft": "harness/playtest/drafts/2026-05-26_runtime_manual_playtest_review_draft.json",
        "accepted_content_lockfile_report": "harness/reports/2026-05-26_accepted_content_lockfile_current_local_001/accepted_content_lockfile.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a content acceptance evidence review packet.")
    parser.add_argument(
        "candidate_pack",
        type=Path,
        nargs="?",
        default=Path("harness/generated_candidates/2026-05-26_phase4_roster_gap_full_pack"),
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--markdown", type=Path, default=None)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    candidate_pack = args.candidate_pack if args.candidate_pack.is_absolute() else repo_root / args.candidate_pack
    packet = build_packet(candidate_pack, repo_root, default_evidence_paths())
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(packet, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(packet, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
