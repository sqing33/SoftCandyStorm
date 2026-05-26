#!/usr/bin/env python3
"""Create a Markdown packet for human runtime playtest review.

The packet gathers the 9-run template, current TODO review draft, required
observations, and validation limitations. It does not run the game or approve a
candidate.
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


def draft_run_index(draft_payload: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not draft_payload:
        return {}
    runs = draft_payload.get("runs")
    if not isinstance(runs, list):
        return {}
    indexed: dict[str, dict[str, Any]] = {}
    for run in runs:
        if isinstance(run, dict) and is_nonempty_string(run.get("run_id")):
            indexed[str(run["run_id"])] = run
    return indexed


def has_todo(value: Any) -> bool:
    if isinstance(value, str):
        return "TODO" in value
    if isinstance(value, list):
        return any(has_todo(item) for item in value)
    if isinstance(value, dict):
        return any(has_todo(item) for item in value.values())
    return False


def run_review_status(run: dict[str, Any] | None) -> str:
    if run is None:
        return "missing"
    if has_todo(run):
        return "draft_todo"
    return str(run.get("gate_decision", "present"))


def template_runs(template_payload: dict[str, Any]) -> list[dict[str, Any]]:
    runs = template_payload.get("runs")
    if not isinstance(runs, list) or not runs:
        raise ValueError("template runs must be a non-empty list")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, run in enumerate(runs):
        if not isinstance(run, dict):
            raise ValueError(f"template runs[{index}] must be an object")
        run_id = run.get("run_id")
        if not is_nonempty_string(run_id):
            raise ValueError(f"template runs[{index}] missing non-empty run_id")
        if str(run_id) in seen:
            raise ValueError(f"template duplicate run_id `{run_id}`")
        seen.add(str(run_id))
        result.append(run)
    return result


def rating_fields(template_payload: dict[str, Any]) -> list[str]:
    fields = template_payload.get("manual_review_fields")
    if not isinstance(fields, dict):
        raise ValueError("template manual_review_fields must be an object")
    return [
        field
        for field in fields
        if field.endswith("_rating")
        or field
        in {
            "projectile_readability",
            "hit_feedback",
            "xp_pickup_rhythm",
            "boss_spawn_clarity",
            "death_reason_clarity",
        }
    ]


def build_packet(
    template_path: Path,
    draft_path: Path | None,
    repo_root: Path,
) -> dict[str, Any]:
    template_payload = load_json_object(template_path)
    draft_payload = load_json_object(draft_path) if draft_path is not None else None
    draft_runs = draft_run_index(draft_payload)

    runs = []
    for template_run in template_runs(template_payload):
        run_id = str(template_run["run_id"])
        draft_run = draft_runs.get(run_id)
        runs.append(
            {
                "run_id": run_id,
                "player_skill": template_run.get("player_skill", ""),
                "intent": template_run.get("intent", ""),
                "required_observations": string_list(template_run.get("required_observations")),
                "review_status": run_review_status(draft_run),
                "gate_decision": draft_run.get("gate_decision", "") if draft_run else "",
            }
        )

    missing_draft_runs = sorted({run["run_id"] for run in runs} - set(draft_runs))
    return {
        "template": relative_repo_path(repo_root, template_path),
        "draft": relative_repo_path(repo_root, draft_path) if draft_path is not None else None,
        "candidate_id": draft_payload.get("candidate_id", "") if draft_payload else "",
        "content_hash": draft_payload.get("content_hash", "") if draft_payload else "",
        "acceptance_decision": draft_payload.get("acceptance_decision", "") if draft_payload else "",
        "minimum_run_count": template_payload.get("minimum_run_count", len(runs)),
        "run_count": len(runs),
        "missing_draft_run_count": len(missing_draft_runs),
        "missing_draft_runs": missing_draft_runs,
        "rating_fields": rating_fields(template_payload),
        "allowed_tags": string_list(template_payload.get("allowed_tags")),
        "allowed_gate_decisions": string_list(template_payload.get("allowed_gate_decisions")),
        "runs": runs,
        "limitations": [
            "This packet organizes manual playtest review evidence only.",
            "It does not run Runtime, inspect gameplay, fill ratings, or approve a candidate.",
            "TODO review fields must be filled by a human before strict acceptance validation can pass.",
            "Automated runtime capture reports cannot replace the human observations listed here.",
        ],
    }


def write_markdown(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Manual Playtest Review Packet",
        "",
        f"- Template: `{packet['template']}`",
        f"- Draft: `{packet['draft'] or 'None'}`",
        f"- Candidate id: `{packet['candidate_id']}`",
        f"- Content hash: `{packet['content_hash']}`",
        f"- Acceptance decision: `{packet['acceptance_decision']}`",
        f"- Runs: {packet['run_count']} / {packet['minimum_run_count']}",
        f"- Missing draft runs: {packet['missing_draft_run_count']}",
        "",
        "## Rating Fields",
        "",
    ]
    lines.extend(f"- `{field}`" for field in packet["rating_fields"])

    lines.extend(["", "## Runs", "", "| Run | Skill | Intent | Review | Gate |", "|---|---|---|---|---|"])
    for run in packet["runs"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    code(run["run_id"]),
                    code(run["player_skill"]),
                    markdown_escape(run["intent"]),
                    code(run["review_status"]),
                    code(run["gate_decision"] or "None"),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Run Details", ""])
    for run in packet["runs"]:
        lines.extend(
            [
                f"### {run['run_id']}",
                "",
                f"- Skill: `{run['player_skill']}`",
                f"- Intent: {markdown_escape(run['intent'])}",
                f"- Review status: `{run['review_status']}`",
                "- Required observations:",
            ]
        )
        lines.extend(f"  - {markdown_escape(item)}" for item in run["required_observations"])
        lines.append("")

    lines.extend(["## Allowed Tags", ""])
    lines.extend(f"- `{tag}`" for tag in packet["allowed_tags"])

    lines.extend(["", "## Allowed Run Gates", ""])
    lines.extend(f"- `{decision}`" for decision in packet["allowed_gate_decisions"])

    lines.extend(["", "## Missing Draft Runs", ""])
    if packet["missing_draft_runs"]:
        lines.extend(f"- `{run_id}`" for run_id in packet["missing_draft_runs"])
    else:
        lines.append("- None")

    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in packet["limitations"])

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Markdown packet for human playtest review.")
    parser.add_argument(
        "--template",
        type=Path,
        default=Path("harness/playtest/runtime_manual_review_template.json"),
        help="Runtime manual review template JSON",
    )
    parser.add_argument("--draft", type=Path, default=None, help="Manual review draft JSON")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--out", type=Path, required=True, help="Output Markdown packet")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    template_path = args.template if args.template.is_absolute() else repo_root / args.template
    draft_path = None
    if args.draft is not None:
        draft_path = args.draft if args.draft.is_absolute() else repo_root / args.draft

    packet = build_packet(template_path, draft_path, repo_root)
    write_markdown(packet, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
