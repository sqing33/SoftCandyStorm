#!/usr/bin/env python3
"""Create a Markdown packet for human platform path review.

The packet gathers the platform save path policy, save contract bindings, local
data roots, validation report references, and TODO manual review checks. It
does not approve platform paths, cloud sync, Runtime behavior, or release
readiness.
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
        raise ValueError("manual platform path review template checks must be a non-empty list")
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


def resolve_repo_path(repo_root: Path, value: Any) -> Path:
    if not is_nonempty_string(value):
        raise ValueError("expected non-empty repository path")
    path = Path(str(value))
    return path if path.is_absolute() else repo_root / path


def build_packet(
    review_template: Path,
    repo_root: Path,
) -> dict[str, Any]:
    review = load_json_object(review_template)
    path_policy_path = resolve_repo_path(repo_root, review.get("path_policy_path"))
    path_policy = load_json_object(path_policy_path)

    save_contracts = []
    for value in string_list(review.get("save_contract_paths")):
        contract_path = resolve_repo_path(repo_root, value)
        contract = load_json_object(contract_path)
        save_contracts.append(
            {
                "path": relative_repo_path(repo_root, contract_path),
                "contract_id": contract.get("contract_id", ""),
                "schema_version": contract.get("schema_version", ""),
                "summary": contract.get("summary", ""),
            }
        )

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

    storage_roots = [
        root
        for root in path_policy.get("storage_roots", [])
        if isinstance(root, dict)
    ]
    path_rules = path_policy.get("path_rules") if isinstance(path_policy.get("path_rules"), dict) else {}

    return {
        "review_template": relative_repo_path(repo_root, review_template),
        "path_policy_path": relative_repo_path(repo_root, path_policy_path),
        "path_policy_validation_report": review.get("path_policy_validation_report", ""),
        "save_contract_validation_reports": string_list(review.get("save_contract_validation_reports")),
        "gate_decision": review.get("gate_decision", ""),
        "summary_status": "draft_todo" if has_todo(review.get("summary")) else "present",
        "policy_id": path_policy.get("policy_id", ""),
        "policy_status": path_policy.get("status", ""),
        "policy_scope": path_policy.get("scope", ""),
        "storage_roots": storage_roots,
        "storage_root_count": len(storage_roots),
        "path_rules": path_rules,
        "prohibited_path_fragments": string_list(path_policy.get("prohibited_path_fragments")),
        "release_requirements": string_list(path_policy.get("release_requirements")),
        "blockers": string_list(path_policy.get("blockers")),
        "next_actions": string_list(path_policy.get("next_actions")),
        "save_contracts": save_contracts,
        "save_contract_count": len(save_contracts),
        "checks": checks,
        "check_count": len(checks),
        "draft_todo_check_count": sum(1 for check in checks if check["status"] == "draft_todo"),
        "limitations": [
            "This packet organizes manual platform path review evidence only.",
            "It does not provide legal advice, platform approval, cloud save approval, Runtime implementation proof, or release approval.",
            "TODO review fields must be filled by a qualified human before manual platform path validation can pass.",
            "A valid path policy does not prove executable Runtime platform-native path behavior.",
        ],
    }


def write_markdown(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Manual Platform Path Review Packet",
        "",
        f"- Review template: `{packet['review_template']}`",
        f"- Gate decision: `{packet['gate_decision']}`",
        f"- Summary status: `{packet['summary_status']}`",
        f"- Path policy: `{packet['path_policy_path']}`",
        f"- Path policy validation report: `{packet['path_policy_validation_report']}`",
        f"- Save contracts: {packet['save_contract_count']}",
        f"- Storage roots: {packet['storage_root_count']}",
        f"- Checks: {packet['check_count']}",
        f"- Draft TODO checks: {packet['draft_todo_check_count']}",
        "",
        "## Policy Summary",
        "",
        f"- Policy id: `{packet['policy_id']}`",
        f"- Scope: `{packet['policy_scope']}`",
        f"- Status: `{packet['policy_status']}`",
        "",
        "## Storage Roots",
        "",
        "| Root | Purpose | Logical path | Delete | Export | Cloud sync |",
        "|---|---|---|---|---|---|",
    ]
    for root in packet["storage_roots"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    code(root.get("id", "")),
                    code(root.get("purpose", "")),
                    code(root.get("logical_path", "")),
                    code(root.get("delete_supported", "")),
                    code(root.get("export_supported", "")),
                    code(root.get("cloud_sync_allowed", "")),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Path Rules", ""])
    for key, value in sorted(packet["path_rules"].items()):
        lines.append(f"- `{key}`: `{value}`")

    lines.extend(["", "## Prohibited Path Fragments", ""])
    lines.extend(f"- `{fragment}`" for fragment in packet["prohibited_path_fragments"])

    lines.extend(["", "## Save Contracts", "", "| Contract | Schema | Path |", "|---|---|---|"])
    for contract in packet["save_contracts"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    code(contract["contract_id"]),
                    code(contract["schema_version"]),
                    code(contract["path"]),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Release Requirements", ""])
    lines.extend(f"- `{item}`" for item in packet["release_requirements"])

    lines.extend(["", "## Policy Blockers", ""])
    if packet["blockers"]:
        lines.extend(f"- {item}" for item in packet["blockers"])
    else:
        lines.append("- None")

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
    parser = argparse.ArgumentParser(description="Create a Markdown packet for human platform path review.")
    parser.add_argument(
        "--review-template",
        type=Path,
        default=Path("harness/save_contract/manual_platform_path_review_template.json"),
        help="Manual platform path review template JSON",
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
