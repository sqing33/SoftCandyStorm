#!/usr/bin/env python3
"""Create a Markdown packet for human legal/compliance review.

The packet gathers privacy policy, Runtime privacy settings, upload transport,
save contract, related manual review report references, jurisdiction TODOs, and
manual legal/compliance checks. It does not provide legal advice, platform
approval, upload approval, or release readiness.
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


def resolve_repo_path(repo_root: Path, value: Any) -> Path:
    if not is_nonempty_string(value):
        raise ValueError("expected non-empty repository path")
    path = Path(str(value))
    return path if path.is_absolute() else repo_root / path


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
        raise ValueError("manual legal review template checks must be a non-empty list")
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


def report_reference_status(repo_root: Path, value: Any) -> dict[str, Any]:
    if not is_nonempty_string(value):
        return {"path": "", "status": "missing", "decision": None}
    if has_todo(value):
        return {"path": str(value), "status": "draft_placeholder", "decision": None}
    path = resolve_repo_path(repo_root, value)
    if not path.exists():
        return {"path": str(value), "status": "missing_file", "decision": None}
    decision = None
    if path.suffix == ".json":
        try:
            payload = load_json_object(path)
            if is_nonempty_string(payload.get("decision")):
                decision = str(payload["decision"])
        except (OSError, ValueError, json.JSONDecodeError):
            decision = None
    return {"path": str(value), "status": "present", "decision": decision}


def build_packet(
    review_template: Path,
    repo_root: Path,
) -> dict[str, Any]:
    review = load_json_object(review_template)
    policy_path = resolve_repo_path(repo_root, review.get("policy_path"))
    runtime_contract_path = resolve_repo_path(repo_root, review.get("runtime_privacy_contract_path"))
    save_contract_path = resolve_repo_path(repo_root, review.get("save_contract_path"))
    upload_contract_path = resolve_repo_path(repo_root, review.get("upload_transport_contract_path"))

    policy = load_json_object(policy_path)
    runtime_contract = load_json_object(runtime_contract_path)
    save_contract = load_json_object(save_contract_path)
    upload_contract = load_json_object(upload_contract_path)

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
    crash = upload_contract.get("crash_reports") if isinstance(upload_contract.get("crash_reports"), dict) else {}
    transport = upload_contract.get("transport") if isinstance(upload_contract.get("transport"), dict) else {}
    transport_release = (
        upload_contract.get("release_requirements")
        if isinstance(upload_contract.get("release_requirements"), list)
        else []
    )

    report_refs = {
        field: report_reference_status(repo_root, review.get(field))
        for field in [
            "policy_validation_report",
            "runtime_contract_validation_report",
            "upload_transport_validation_report",
            "manual_privacy_review_report",
            "manual_platform_path_review_report",
        ]
    }

    return {
        "review_template": relative_repo_path(repo_root, review_template),
        "gate_decision": review.get("gate_decision", ""),
        "summary_status": "draft_todo" if has_todo(review.get("summary")) else "present",
        "reviewer_status": "draft_todo" if has_todo(review.get("reviewer")) else "present",
        "jurisdiction_scope": string_list(review.get("jurisdiction_scope")),
        "jurisdiction_status": "draft_todo" if has_todo(review.get("jurisdiction_scope")) else "present",
        "policy_path": relative_repo_path(repo_root, policy_path),
        "runtime_contract_path": relative_repo_path(repo_root, runtime_contract_path),
        "save_contract_path": relative_repo_path(repo_root, save_contract_path),
        "upload_contract_path": relative_repo_path(repo_root, upload_contract_path),
        "report_refs": report_refs,
        "policy_id": policy.get("policy_id", ""),
        "policy_scope": policy.get("scope", ""),
        "upload_enabled": upload.get("enabled"),
        "upload_default_enabled": upload.get("default_enabled"),
        "upload_requires_consent": upload.get("requires_explicit_consent"),
        "raw_replay_default_enabled": raw_replay.get("default_enabled"),
        "raw_replay_requires_consent": raw_replay.get("requires_explicit_consent"),
        "crash_report_default_enabled": crash.get("default_enabled"),
        "crash_report_requires_consent": crash.get("requires_explicit_consent"),
        "prohibited_fields": string_list(policy.get("prohibited_fields")),
        "retention_days": policy.get("storage", {}).get("retention_days") if isinstance(policy.get("storage"), dict) else None,
        "runtime_contract_id": runtime_contract.get("contract_id", ""),
        "save_contract_id": save_contract.get("contract_id", ""),
        "upload_contract_id": upload_contract.get("contract_id", ""),
        "upload_implementation_status": upload_contract.get("implementation_status", ""),
        "upload_transport_mode": transport.get("method"),
        "upload_release_requirements": [item for item in transport_release if isinstance(item, str)],
        "checks": checks,
        "check_count": len(checks),
        "draft_todo_check_count": sum(1 for check in checks if check["status"] == "draft_todo"),
        "limitations": [
            "This packet organizes manual legal/compliance review evidence only.",
            "It does not provide legal advice, platform approval, store approval, upload approval, or release approval.",
            "TODO review fields must be filled by a qualified human before manual legal validation can pass.",
            "Valid privacy, Runtime, upload, save, privacy-review, and platform-path evidence still does not prove release readiness.",
        ],
    }


def write_markdown(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Manual Legal Review Packet",
        "",
        f"- Review template: `{packet['review_template']}`",
        f"- Gate decision: `{packet['gate_decision']}`",
        f"- Summary status: `{packet['summary_status']}`",
        f"- Reviewer status: `{packet['reviewer_status']}`",
        f"- Jurisdiction status: `{packet['jurisdiction_status']}`",
        f"- Checks: {packet['check_count']}",
        f"- Draft TODO checks: {packet['draft_todo_check_count']}",
        "",
        "## Bound Evidence",
        "",
        f"- Policy: `{packet['policy_path']}`",
        f"- Runtime privacy contract: `{packet['runtime_contract_path']}`",
        f"- Save contract: `{packet['save_contract_path']}`",
        f"- Upload transport contract: `{packet['upload_contract_path']}`",
        "",
        "## Report References",
        "",
        "| Report | Path | Status | Decision |",
        "|---|---|---|---|",
    ]
    for field, ref in packet["report_refs"].items():
        lines.append(
            "| "
            + " | ".join(
                [
                    code(field),
                    code(ref["path"]),
                    code(ref["status"]),
                    code(ref["decision"] or ""),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Jurisdiction Scope", ""])
    if packet["jurisdiction_scope"]:
        lines.extend(f"- `{item}`" for item in packet["jurisdiction_scope"])
    else:
        lines.append("- None")

    lines.extend(["", "## Privacy And Upload Summary", ""])
    lines.extend(
        [
            f"- Policy id: `{packet['policy_id']}`",
            f"- Policy scope: `{packet['policy_scope']}`",
            f"- Upload enabled: `{packet['upload_enabled']}`",
            f"- Upload default enabled: `{packet['upload_default_enabled']}`",
            f"- Upload requires consent: `{packet['upload_requires_consent']}`",
            f"- Raw replay default enabled: `{packet['raw_replay_default_enabled']}`",
            f"- Raw replay requires consent: `{packet['raw_replay_requires_consent']}`",
            f"- Crash report default enabled: `{packet['crash_report_default_enabled']}`",
            f"- Crash report requires consent: `{packet['crash_report_requires_consent']}`",
            f"- Retention days: `{packet['retention_days']}`",
            f"- Runtime contract id: `{packet['runtime_contract_id']}`",
            f"- Save contract id: `{packet['save_contract_id']}`",
            f"- Upload contract id: `{packet['upload_contract_id']}`",
            f"- Upload implementation status: `{packet['upload_implementation_status']}`",
            f"- Upload transport mode: `{packet['upload_transport_mode']}`",
        ]
    )

    lines.extend(["", "## Prohibited Fields", ""])
    lines.extend(f"- `{field}`" for field in packet["prohibited_fields"])

    lines.extend(["", "## Upload Release Requirements", ""])
    if packet["upload_release_requirements"]:
        lines.extend(f"- `{item}`" for item in packet["upload_release_requirements"])
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
    parser = argparse.ArgumentParser(description="Create a Markdown packet for human legal/compliance review.")
    parser.add_argument(
        "--review-template",
        type=Path,
        default=Path("harness/telemetry_privacy/manual_legal_review_template.json"),
        help="Manual legal/compliance review template JSON",
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
