#!/usr/bin/env python3
"""Create a Markdown packet for human privacy review.

The packet gathers privacy policy, Runtime privacy contract, save contract
binding, validation reports, and TODO manual review checks. It does not approve
privacy, legal, platform, upload transport, or release readiness.
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


def has_todo(value: Any) -> bool:
    if isinstance(value, str):
        return "TODO" in value or "<" in value or ">" in value
    if isinstance(value, list):
        return any(has_todo(item) for item in value)
    if isinstance(value, dict):
        return any(has_todo(item) for item in value.values())
    return False


def check_status(check: dict[str, Any] | None) -> str:
    if check is None:
        return "missing"
    if has_todo(check):
        return "draft_todo"
    return str(check.get("decision", "present"))


def review_checks(review_payload: dict[str, Any]) -> list[dict[str, Any]]:
    checks = review_payload.get("checks")
    if not isinstance(checks, list) or not checks:
        raise ValueError("manual privacy review template checks must be a non-empty list")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            raise ValueError(f"checks[{index}] must be an object")
        check_id = check.get("id")
        if not is_nonempty_string(check_id):
            raise ValueError(f"checks[{index}] missing id")
        if str(check_id) in seen:
            raise ValueError(f"duplicate check id `{check_id}`")
        seen.add(str(check_id))
        result.append(check)
    return result


def build_packet(
    review_template: Path,
    repo_root: Path,
) -> dict[str, Any]:
    review = load_json_object(review_template)
    policy_path = repo_root / str(review.get("policy_path"))
    runtime_contract_path = repo_root / str(review.get("runtime_privacy_contract_path"))
    save_contract_path = repo_root / str(review.get("save_contract_path"))
    policy = load_json_object(policy_path)
    runtime_contract = load_json_object(runtime_contract_path)
    save_contract = load_json_object(save_contract_path)

    checks = []
    for check in review_checks(review):
        checks.append(
            {
                "id": str(check["id"]),
                "decision": check.get("decision", ""),
                "status": check_status(check),
                "notes": check.get("notes", ""),
                "required_change_count": len(string_list(check.get("required_changes"))),
            }
        )

    upload = policy.get("upload") if isinstance(policy.get("upload"), dict) else {}
    raw_replay = policy.get("raw_replay_upload") if isinstance(policy.get("raw_replay_upload"), dict) else {}
    privacy_notice = runtime_contract.get("privacy_notice") if isinstance(runtime_contract.get("privacy_notice"), dict) else {}

    return {
        "review_template": relative_repo_path(repo_root, review_template),
        "policy_path": relative_repo_path(repo_root, policy_path),
        "runtime_contract_path": relative_repo_path(repo_root, runtime_contract_path),
        "save_contract_path": relative_repo_path(repo_root, save_contract_path),
        "policy_validation_report": review.get("policy_validation_report", ""),
        "runtime_contract_validation_report": review.get("runtime_contract_validation_report", ""),
        "gate_decision": review.get("gate_decision", ""),
        "summary_status": "draft_todo" if has_todo(review.get("summary")) else "present",
        "policy_id": policy.get("policy_id", ""),
        "policy_scope": policy.get("scope", ""),
        "upload_enabled": upload.get("enabled"),
        "upload_default_enabled": upload.get("default_enabled"),
        "upload_requires_consent": upload.get("requires_explicit_consent"),
        "raw_replay_default_enabled": raw_replay.get("default_enabled"),
        "raw_replay_requires_consent": raw_replay.get("requires_explicit_consent"),
        "prohibited_fields": string_list(policy.get("prohibited_fields")),
        "allowed_event_fields": string_list(policy.get("allowed_event_fields")),
        "retention_days": policy.get("storage", {}).get("retention_days") if isinstance(policy.get("storage"), dict) else None,
        "runtime_contract_id": runtime_contract.get("contract_id", ""),
        "save_contract_id": save_contract.get("contract_id", ""),
        "ui_controls": [
            control
            for control in runtime_contract.get("ui_controls", [])
            if isinstance(control, dict)
        ],
        "data_action_controls": [
            control
            for control in runtime_contract.get("data_action_controls", [])
            if isinstance(control, dict)
        ],
        "privacy_notice_topics": string_list(privacy_notice.get("required_topics")),
        "privacy_notice_short_text": privacy_notice.get("short_text", ""),
        "checks": checks,
        "check_count": len(checks),
        "draft_todo_check_count": sum(1 for check in checks if check["status"] == "draft_todo"),
        "limitations": [
            "This packet organizes manual privacy review evidence only.",
            "It does not provide legal advice, platform approval, upload transport proof, or release approval.",
            "TODO review fields must be filled by a qualified human before manual privacy validation can pass.",
            "Valid policy and Runtime setting contracts do not prove executable Runtime behavior or network upload behavior.",
        ],
    }


def write_markdown(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Manual Privacy Review Packet",
        "",
        f"- Review template: `{packet['review_template']}`",
        f"- Gate decision: `{packet['gate_decision']}`",
        f"- Summary status: `{packet['summary_status']}`",
        f"- Policy: `{packet['policy_path']}`",
        f"- Runtime privacy contract: `{packet['runtime_contract_path']}`",
        f"- Save contract: `{packet['save_contract_path']}`",
        f"- Policy validation report: `{packet['policy_validation_report']}`",
        f"- Runtime contract validation report: `{packet['runtime_contract_validation_report']}`",
        f"- Checks: {packet['check_count']}",
        f"- Draft TODO checks: {packet['draft_todo_check_count']}",
        "",
        "## Policy Summary",
        "",
        f"- Policy id: `{packet['policy_id']}`",
        f"- Scope: `{packet['policy_scope']}`",
        f"- Upload enabled: `{packet['upload_enabled']}`",
        f"- Upload default enabled: `{packet['upload_default_enabled']}`",
        f"- Upload requires consent: `{packet['upload_requires_consent']}`",
        f"- Raw replay default enabled: `{packet['raw_replay_default_enabled']}`",
        f"- Raw replay requires consent: `{packet['raw_replay_requires_consent']}`",
        f"- Retention days: `{packet['retention_days']}`",
        "",
        "## Prohibited Fields",
        "",
    ]
    lines.extend(f"- `{field}`" for field in packet["prohibited_fields"])

    lines.extend(["", "## Allowed Event Fields", ""])
    lines.extend(f"- `{field}`" for field in packet["allowed_event_fields"])

    lines.extend(["", "## Runtime UI Controls", "", "| Control | Setting | Default | Consent |", "|---|---|---|---|"])
    for control in packet["ui_controls"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    code(control.get("id", "")),
                    code(control.get("setting", "")),
                    code(control.get("default_enabled", "")),
                    code(control.get("requires_explicit_consent", "")),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Data Action Controls", "", "| Control | Action | Visible |", "|---|---|---|"])
    for control in packet["data_action_controls"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    code(control.get("id", "")),
                    code(control.get("action", "")),
                    code(control.get("visible", "")),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Privacy Notice Topics", ""])
    lines.extend(f"- `{topic}`" for topic in packet["privacy_notice_topics"])
    lines.extend(["", "## Privacy Notice Text", "", markdown_escape(packet["privacy_notice_short_text"])])

    lines.extend(["", "## Manual Checks", "", "| Check | Decision | Status | Required changes |", "|---|---|---|---:|"])
    for check in packet["checks"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    code(check["id"]),
                    code(check["decision"]),
                    code(check["status"]),
                    str(check["required_change_count"]),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Check Details", ""])
    for check in packet["checks"]:
        lines.extend(
            [
                f"### {check['id']}",
                "",
                f"- Decision: `{check['decision']}`",
                f"- Status: `{check['status']}`",
                f"- Notes: {markdown_escape(check['notes'])}",
                "",
            ]
        )

    lines.extend(["## Limitations", ""])
    lines.extend(f"- {item}" for item in packet["limitations"])

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Markdown packet for human privacy review.")
    parser.add_argument(
        "--review-template",
        type=Path,
        default=Path("harness/telemetry_privacy/manual_privacy_review_template.json"),
        help="Manual privacy review template JSON",
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--out", type=Path, required=True, help="Output Markdown packet")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    review_template = (
        args.review_template if args.review_template.is_absolute() else repo_root / args.review_template
    )
    packet = build_packet(review_template, repo_root)
    write_markdown(packet, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
