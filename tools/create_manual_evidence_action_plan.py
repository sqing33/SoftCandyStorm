#!/usr/bin/env python3
"""Create a human-action plan from the manual evidence gap audit.

This helper turns the cross-domain manual evidence audit into a compact
checklist for the human reviewer. It does not run Runtime, fill review fields,
or convert any gate to pass.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DOMAIN_ORDER = ["playtest", "content", "asset", "story", "privacy", "platform", "base_ui", "release"]


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


def markdown_escape(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def code(value: Any) -> str:
    text = str(value).strip() if value is not None else ""
    return f"`{markdown_escape(text or '-')}`"


def evidence_paths(item: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for entry in item.get("evidence_paths", []):
        if isinstance(entry, dict) and is_nonempty_string(entry.get("path")):
            paths.append(str(entry["path"]))
    report = item.get("report")
    if is_nonempty_string(report) and str(report) not in paths:
        paths.insert(0, str(report))
    return paths


def required_next_steps(item: dict[str, Any]) -> list[str]:
    details = item.get("details")
    if isinstance(details, dict):
        steps = string_list(details.get("required_next_steps"))
        if steps:
            return steps
    action = item.get("required_action")
    return [str(action)] if is_nonempty_string(action) else []


def domain_sort_key(domain: str) -> tuple[int, str]:
    if domain in DOMAIN_ORDER:
        return DOMAIN_ORDER.index(domain), domain
    return len(DOMAIN_ORDER), domain


def item_sort_key(item: dict[str, Any]) -> tuple[int, str]:
    domain = str(item.get("domain", ""))
    return domain_sort_key(domain)[0], str(item.get("id", ""))


def normalize_item(item: dict[str, Any]) -> dict[str, Any]:
    status = str(item.get("status", "unknown"))
    satisfied = bool(item.get("satisfied"))
    return {
        "id": str(item.get("id", "")),
        "domain": str(item.get("domain", "unknown")),
        "title": str(item.get("title", item.get("id", ""))),
        "status": status,
        "satisfied": satisfied,
        "decision": str(item.get("decision", "")),
        "gate_decision": str(item.get("gate_decision", "")),
        "required_action": str(item.get("required_action", "")),
        "report": str(item.get("report", "")),
        "summary": str(item.get("summary", "")),
        "evidence_paths": evidence_paths(item),
        "required_next_steps": required_next_steps(item),
    }


def build_plan(audit_path: Path, repo_root: Path, domain_filter: str | None = None) -> dict[str, Any]:
    audit = load_json_object(audit_path)
    raw_items = audit.get("items")
    if not isinstance(raw_items, list):
        raise ValueError("manual evidence audit must contain an `items` list")

    items = [normalize_item(item) for item in raw_items if isinstance(item, dict)]
    if domain_filter:
        items = [item for item in items if item["domain"] == domain_filter]
    items.sort(key=item_sort_key)

    domains: dict[str, dict[str, Any]] = {}
    for item in items:
        domain = item["domain"]
        domain_entry = domains.setdefault(
            domain,
            {
                "domain": domain,
                "total": 0,
                "gaps": 0,
                "satisfied": 0,
                "items": [],
                "next_steps": [],
            },
        )
        domain_entry["total"] += 1
        if item["satisfied"]:
            domain_entry["satisfied"] += 1
        else:
            domain_entry["gaps"] += 1
        domain_entry["items"].append(item)
        for step in item["required_next_steps"]:
            if step not in domain_entry["next_steps"]:
                domain_entry["next_steps"].append(step)

    ordered_domains = [
        domains[name]
        for name in sorted(domains, key=domain_sort_key)
    ]
    gap_items = [item for item in items if not item["satisfied"]]
    return {
        "report_version": 1,
        "decision": "manual_evidence_action_plan_ready",
        "source_audit": relative_repo_path(repo_root, audit_path),
        "source_decision": str(audit.get("decision", "")),
        "domain_filter": domain_filter or "",
        "item_count": len(items),
        "gap_count": len(gap_items),
        "satisfied_count": len(items) - len(gap_items),
        "domain_count": len(ordered_domains),
        "domains": ordered_domains,
        "limitations": [
            "This action plan organizes human-required evidence gaps only.",
            "It does not run Runtime, inspect gameplay, fill review fields, approve content, or change release gates.",
            "Every gap remains blocked until a real human review source passes its validator.",
        ],
    }


def write_markdown(plan: dict[str, Any], path: Path) -> None:
    lines = [
        "# Manual Evidence Action Plan",
        "",
        f"- Source audit: `{plan['source_audit']}`",
        f"- Source decision: `{plan['source_decision']}`",
        f"- Decision: `{plan['decision']}`",
        f"- Items: {plan['item_count']}",
        f"- Gaps: {plan['gap_count']}",
        f"- Satisfied: {plan['satisfied_count']}",
        "",
        "## Domains",
        "",
        "| Domain | Gaps | Satisfied | Total |",
        "|---|---:|---:|---:|",
    ]
    for domain in plan["domains"]:
        lines.append(
            f"| `{domain['domain']}` | {domain['gaps']} | {domain['satisfied']} | {domain['total']} |"
        )

    lines.extend(["", "## Gap Checklist", ""])
    for domain in plan["domains"]:
        lines.extend([f"### {domain['domain']}", ""])
        lines.extend(["| Requirement | Status | Decision | Required action | Source |", "|---|---|---|---|---|"])
        for item in domain["items"]:
            source = item["report"] or item["summary"] or "-"
            lines.append(
                "| "
                + " | ".join(
                    [
                        code(item["id"]),
                        code(item["status"]),
                        code(item["decision"]),
                        markdown_escape(item["required_action"] or "-"),
                        code(source),
                    ]
                )
                + " |"
            )
        lines.append("")
        if domain["next_steps"]:
            lines.append("Next steps:")
            for step in domain["next_steps"]:
                lines.append(f"- {markdown_escape(step)}")
            lines.append("")

    lines.extend(["## Evidence Sources", ""])
    for domain in plan["domains"]:
        lines.extend([f"### {domain['domain']}", ""])
        for item in domain["items"]:
            lines.append(f"- {code(item['id'])}")
            paths = item["evidence_paths"] or [item["report"]]
            for source in paths:
                if is_nonempty_string(source):
                    lines.append(f"  - `{markdown_escape(source)}`")
        lines.append("")

    lines.extend(["## Limitations", ""])
    lines.extend(f"- {item}" for item in plan["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a manual evidence action plan.")
    parser.add_argument(
        "audit",
        type=Path,
        nargs="?",
        default=Path("harness/reports/2026-05-26_manual_evidence_gap_audit_001/manual_evidence_gap_audit.json"),
        help="Manual evidence gap audit JSON",
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--domain", default=None, help="Optional domain filter such as playtest or asset")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON action plan")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown action plan")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    audit_path = args.audit if args.audit.is_absolute() else repo_root / args.audit
    plan = build_plan(audit_path, repo_root, args.domain)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(plan, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(plan, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
