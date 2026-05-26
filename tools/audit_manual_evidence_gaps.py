#!/usr/bin/env python3
"""Audit manual evidence gaps across review gates.

This cross-cutting audit keeps the long-running Goal work honest: it collects
human-required review reports from playtest, content, story/codex, assets,
privacy, platform paths, base UI, and release readiness, then reports which
ones are still missing or not passing. It does not run Runtime or replace any
human review.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_REQUIREMENTS: list[dict[str, Any]] = [
    {
        "id": "manual_playtest_acceptance",
        "domain": "playtest",
        "title": "9-run human playtest acceptance",
        "report": "harness/reports/2026-05-26_manual_playtest_acceptance_review_packet_001/manual_playtest_acceptance_review_packet.json",
        "summary": "harness/reports/2026-05-26_manual_playtest_acceptance_review_packet_001/summary.md",
        "pass_decisions": ["manual_playtest_acceptance_review_packet_ready_for_content_lock"],
        "required_action": "Replace TODO playtest draft values with real human ratings, notes, tags, and acceptance evidence.",
    },
    {
        "id": "content_acceptance_packet",
        "domain": "content",
        "title": "Content acceptance evidence packet",
        "report": "harness/reports/2026-05-26_phase4_content_acceptance_review_packet_001/content_acceptance_review_packet.json",
        "summary": "harness/reports/2026-05-26_phase4_content_acceptance_review_packet_001/summary.md",
        "pass_decisions": ["content_acceptance_review_packet_ready_for_validation"],
        "required_action": "Finish human design review, manual playtest acceptance, demo readiness, and accepted-content lock evidence before validation.",
    },
    {
        "id": "content_final_acceptance",
        "domain": "content",
        "title": "Final human content acceptance",
        "report": "harness/reports/2026-05-26_content_final_acceptance_template_001/content_final_acceptance.json",
        "summary": "harness/reports/2026-05-26_content_final_acceptance_template_001/summary.md",
        "pass_decisions": ["content_final_acceptance_valid"],
        "required_gate_decisions": ["accepted_content"],
        "required_action": "Bind a valid simulation candidate manifest and accepted-content lockfile, then record real final acceptance observations.",
    },
    {
        "id": "content_acceptance_manifest",
        "domain": "content",
        "title": "Accepted content manifest",
        "report": "harness/reports/2026-05-26_content_acceptance_manifest_template_001/content_acceptance_manifest.json",
        "summary": "harness/reports/2026-05-26_content_acceptance_manifest_template_001/summary.md",
        "pass_decisions": ["content_acceptance_manifest_valid"],
        "required_action": "Create a manifest backed by valid simulation-candidate, final human acceptance, and accepted-content lockfile reports.",
    },
    {
        "id": "asset_candidate_review_runtime_topdown_audio",
        "domain": "asset",
        "title": "Runtime top-down/audio candidate human review",
        "report": "harness/reports/2026-05-26_mmx_runtime_topdown_audio_plan_manual_review_draft_001/asset_candidate_manual_review.json",
        "summary": "harness/reports/2026-05-26_mmx_runtime_topdown_audio_plan_manual_review_draft_001/summary.md",
        "pass_decisions": ["asset_candidate_manual_review_valid"],
        "required_gate_decisions": ["asset_candidate"],
        "required_action": "Replace generated review draft ratings and TODO notes with real art/audio review observations.",
    },
    {
        "id": "asset_candidate_review_level_up_feedback",
        "domain": "asset",
        "title": "Level-up feedback candidate human review",
        "report": "harness/reports/2026-05-26_mmx_level_up_feedback_manual_review_draft_001/asset_manual_review.json",
        "summary": "harness/reports/2026-05-26_mmx_level_up_feedback_manual_review_draft_001/summary.md",
        "pass_decisions": ["asset_candidate_manual_review_valid"],
        "required_gate_decisions": ["asset_candidate"],
        "required_action": "Fill the level-up feedback review draft with human visual, listening, provenance, and technical-readiness observations.",
    },
    {
        "id": "asset_runtime_preview_review",
        "domain": "asset",
        "title": "Asset Runtime preview human review",
        "report": "harness/reports/2026-05-26_asset_runtime_preview_review_template_001/asset_runtime_preview_review.json",
        "summary": "harness/reports/2026-05-26_asset_runtime_preview_review_template_001/summary.md",
        "pass_decisions": ["asset_runtime_preview_review_valid"],
        "required_gate_decisions": ["runtime_preview_pass"],
        "required_action": "Preview staged runtime candidates in context and record concrete small-size/readability observations.",
    },
    {
        "id": "asset_audio_loudness_review",
        "domain": "asset",
        "title": "Audio loudness/listening human review",
        "report": "harness/reports/2026-05-26_asset_audio_loudness_review_template_001/asset_audio_loudness_review.json",
        "summary": "harness/reports/2026-05-26_asset_audio_loudness_review_template_001/summary.md",
        "pass_decisions": ["asset_audio_loudness_review_valid"],
        "required_gate_decisions": ["audio_loudness_pass"],
        "required_action": "Record real listening, clipping, loudness, dialogue clarity, and loop/duration-fit observations.",
    },
    {
        "id": "asset_final_acceptance",
        "domain": "asset",
        "title": "Final human asset acceptance",
        "report": "harness/reports/2026-05-26_asset_final_acceptance_template_001/asset_final_acceptance.json",
        "summary": "harness/reports/2026-05-26_asset_final_acceptance_template_001/summary.md",
        "pass_decisions": ["asset_final_acceptance_valid"],
        "required_gate_decisions": ["accepted_content"],
        "required_action": "Bind passing Runtime preview and audio loudness reviews before recording final asset acceptance.",
    },
    {
        "id": "asset_acceptance_manifest",
        "domain": "asset",
        "title": "Accepted asset manifest",
        "report": "harness/reports/2026-05-26_asset_acceptance_manifest_template_001/asset_acceptance_manifest.json",
        "summary": "harness/reports/2026-05-26_asset_acceptance_manifest_template_001/summary.md",
        "pass_decisions": ["asset_acceptance_manifest_valid"],
        "required_action": "Create a manifest backed by valid runtime-candidate, runtime preview, loudness, and final acceptance evidence.",
    },
    {
        "id": "story_codex_ui_candidate_manifest",
        "domain": "story",
        "title": "Story/codex UI candidate manifest",
        "report": "harness/reports/2026-05-26_story_codex_ui_candidate_manifest_template_001/story_codex_ui_candidate_manifest.json",
        "summary": "harness/reports/2026-05-26_story_codex_ui_candidate_manifest_template_001/summary.md",
        "pass_decisions": ["story_codex_ui_candidate_manifest_valid"],
        "required_action": "Complete real story/codex manual review before promoting the text pack to UI-candidate staging.",
    },
    {
        "id": "story_codex_runtime_ui_review",
        "domain": "story",
        "title": "Story/codex Runtime UI human review",
        "report": "harness/reports/2026-05-26_story_codex_runtime_ui_review_template_001/story_codex_runtime_ui_review.json",
        "summary": "harness/reports/2026-05-26_story_codex_runtime_ui_review_template_001/summary.md",
        "pass_decisions": ["story_codex_runtime_ui_review_valid"],
        "required_gate_decisions": ["runtime_ui_review_pass"],
        "required_action": "Review the F3 candidate metadata UI in Runtime and record concrete observations without loading generated body text.",
    },
    {
        "id": "story_codex_final_acceptance",
        "domain": "story",
        "title": "Final human story/codex acceptance",
        "report": "harness/reports/2026-05-26_story_codex_final_acceptance_template_001/story_codex_final_acceptance.json",
        "summary": "harness/reports/2026-05-26_story_codex_final_acceptance_template_001/summary.md",
        "pass_decisions": ["story_codex_final_acceptance_valid"],
        "required_gate_decisions": ["accepted_content"],
        "required_action": "Bind a passing Runtime UI review and record final human acceptance for story/codex text.",
    },
    {
        "id": "story_codex_acceptance_manifest",
        "domain": "story",
        "title": "Accepted story/codex manifest",
        "report": "harness/reports/2026-05-26_story_codex_acceptance_manifest_template_001/story_codex_acceptance_manifest.json",
        "summary": "harness/reports/2026-05-26_story_codex_acceptance_manifest_template_001/summary.md",
        "pass_decisions": ["story_codex_acceptance_manifest_valid"],
        "required_action": "Create a manifest backed by valid UI-candidate, Runtime UI review, and final human acceptance evidence.",
    },
    {
        "id": "manual_privacy_review",
        "domain": "privacy",
        "title": "Manual privacy review",
        "report": "harness/reports/2026-05-26_manual_privacy_review_template_001/manual_privacy_review.json",
        "summary": "harness/reports/2026-05-26_manual_privacy_review_template_001/summary.md",
        "pass_decisions": ["manual_privacy_review_valid"],
        "required_gate_decisions": ["pass"],
        "required_action": "Fill the privacy review with real checks for consent, prohibited fields, notices, retention, and local data controls.",
    },
    {
        "id": "manual_platform_path_review",
        "domain": "platform",
        "title": "Manual platform path review",
        "report": "harness/reports/2026-05-26_manual_platform_path_review_template_001/manual_platform_path_review.json",
        "summary": "harness/reports/2026-05-26_manual_platform_path_review_template_001/summary.md",
        "pass_decisions": ["manual_platform_path_review_valid"],
        "required_gate_decisions": ["pass"],
        "required_action": "Review logical roots, delete/export scope, migration retention, cloud sync limits, and Runtime evidence limits on the target platform.",
    },
    {
        "id": "manual_legal_review",
        "domain": "privacy",
        "title": "Manual legal/compliance review",
        "report": "harness/reports/2026-05-26_manual_legal_review_template_001/manual_legal_review.json",
        "summary": "harness/reports/2026-05-26_manual_legal_review_template_001/summary.md",
        "pass_decisions": ["manual_legal_review_valid"],
        "required_gate_decisions": ["pass"],
        "required_action": "Complete real legal/compliance review after privacy and platform-path reviews are passing.",
    },
    {
        "id": "telemetry_privacy_acceptance_packet",
        "domain": "privacy",
        "title": "Telemetry/privacy acceptance evidence packet",
        "report": "harness/reports/2026-05-26_telemetry_privacy_acceptance_review_packet_001/telemetry_privacy_acceptance_review_packet.json",
        "summary": "harness/reports/2026-05-26_telemetry_privacy_acceptance_review_packet_001/summary.md",
        "pass_decisions": ["telemetry_privacy_acceptance_review_packet_ready_for_release_gate"],
        "required_action": "Bring policy, runtime contract, upload transport, platform path, privacy, legal, and RC telemetry gate evidence to passing state.",
    },
    {
        "id": "base_ui_manual_review",
        "domain": "base_ui",
        "title": "Base UI manual review",
        "report": "harness/reports/2026-05-26_base_ui_manual_review_template_001/base_ui_manual_review.json",
        "summary": "harness/reports/2026-05-26_base_ui_manual_review_template_001/summary.md",
        "pass_decisions": ["base_ui_manual_review_valid"],
        "required_gate_decisions": ["base_ui_review_pass"],
        "required_action": "Review F1-F4 base UI flows, local data controls, candidate boundaries, and evidence limits with concrete human observations.",
    },
    {
        "id": "release_candidate_evidence",
        "domain": "release",
        "title": "Release candidate evidence",
        "report": "harness/reports/2026-05-26_release_candidate_evidence_current_local_004/release_candidate_evidence.json",
        "summary": "harness/reports/2026-05-26_release_candidate_evidence_current_local_004/summary.md",
        "pass_decisions": ["release_candidate_ready"],
        "required_action": "Clear every release gate, including compile, tests, Harness, Replay, performance, manual reviews, content, asset, privacy, and package gates.",
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


def load_requirements(path: Path | None) -> list[dict[str, Any]]:
    if path is None:
        return [dict(item) for item in DEFAULT_REQUIREMENTS]
    payload = load_json_object(path)
    requirements = payload.get("requirements")
    if not isinstance(requirements, list):
        raise ValueError(f"{path} must contain a `requirements` list")
    return [item for item in requirements if isinstance(item, dict)]


def compact_items(value: Any, limit: int = 5) -> list[str]:
    if not isinstance(value, list):
        return []
    items = [str(item) for item in value if isinstance(item, str) and item.strip()]
    return items[:limit]


def report_details(payload: dict[str, Any]) -> dict[str, Any]:
    detail_fields = {
        "errors": compact_items(payload.get("errors")),
        "blockers": compact_items(payload.get("blockers")),
        "warnings": compact_items(payload.get("warnings")),
        "required_next_steps": compact_items(payload.get("required_next_steps")),
        "limitations": compact_items(payload.get("limitations"), limit=3),
    }
    return {key: value for key, value in detail_fields.items() if value}


def audit_requirement(requirement: dict[str, Any], repo_root: Path) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    req_id = requirement.get("id")
    domain = requirement.get("domain")
    report_value = requirement.get("report")
    if not is_nonempty_string(req_id):
        errors.append("requirement id must be non-empty")
        req_id = "<missing-id>"
    if not is_nonempty_string(domain):
        errors.append(f"{req_id}: domain must be non-empty")
        domain = "unknown"
    if not is_nonempty_string(report_value):
        errors.append(f"{req_id}: report must be non-empty")
        report_value = ""

    pass_decisions = string_list(requirement.get("pass_decisions"))
    if not pass_decisions:
        errors.append(f"{req_id}: pass_decisions must be a non-empty list")
    required_gate_decisions = string_list(requirement.get("required_gate_decisions"))

    evidence_paths: list[dict[str, Any]] = []
    for field in ("report", "summary", "template"):
        value = requirement.get(field)
        if not is_nonempty_string(value):
            continue
        path = resolve_repo_path(repo_root, str(value))
        evidence_paths.append(
            {
                "kind": field,
                "path": relative_repo_path(repo_root, path),
                "exists": is_inside_repo(repo_root, path) and path.exists(),
            }
        )

    report_path = resolve_repo_path(repo_root, str(report_value)) if report_value else repo_root
    report_payload: dict[str, Any] | None = None
    report_error = ""
    if not report_value:
        report_status = "missing_report"
    elif not is_inside_repo(repo_root, report_path):
        report_status = "outside_repo"
        report_error = f"report path must stay inside repository: {report_value}"
    elif not report_path.exists():
        report_status = "missing_report"
    else:
        try:
            report_payload = load_json_object(report_path)
            report_status = "loaded"
        except (OSError, ValueError, json.JSONDecodeError) as error:
            report_status = "invalid_json"
            report_error = str(error)

    decision = ""
    gate_decision = ""
    satisfied = False
    if report_payload is not None:
        raw_decision = report_payload.get("decision")
        raw_gate_decision = report_payload.get("gate_decision")
        decision = str(raw_decision) if raw_decision is not None else ""
        gate_decision = str(raw_gate_decision) if raw_gate_decision is not None else ""
        satisfied = decision in pass_decisions and (
            not required_gate_decisions or gate_decision in required_gate_decisions
        )

    missing_evidence = [
        item["path"] for item in evidence_paths if item["kind"] in {"report", "summary"} and not item["exists"]
    ]
    if report_error:
        errors.append(f"{req_id}: {report_error}")

    status = "satisfied" if satisfied else "gap"
    if report_status in {"missing_report", "outside_repo", "invalid_json"}:
        status = report_status

    detail = report_details(report_payload or {})
    if missing_evidence:
        detail["missing_evidence_paths"] = missing_evidence

    return (
        {
            "id": str(req_id),
            "domain": str(domain),
            "title": str(requirement.get("title", req_id)),
            "status": status,
            "satisfied": satisfied,
            "decision": decision,
            "expected_decisions": pass_decisions,
            "gate_decision": gate_decision,
            "expected_gate_decisions": required_gate_decisions,
            "report_status": report_status,
            "report": relative_repo_path(repo_root, report_path) if report_value else "",
            "source": report_payload.get("source") if report_payload else None,
            "required_action": str(requirement.get("required_action", "")),
            "evidence_paths": evidence_paths,
            "details": detail,
        },
        errors,
    )


def build_report(
    repo_root: Path,
    requirements: list[dict[str, Any]] | None = None,
    *,
    focus_domain: str | None = None,
) -> dict[str, Any]:
    requirements = requirements if requirements is not None else [dict(item) for item in DEFAULT_REQUIREMENTS]
    errors: list[str] = []
    items: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for requirement in requirements:
        if focus_domain and requirement.get("domain") != focus_domain:
            continue
        item, item_errors = audit_requirement(requirement, repo_root)
        errors.extend(item_errors)
        if item["id"] in seen_ids:
            errors.append(f"duplicate requirement id `{item['id']}`")
        seen_ids.add(str(item["id"]))
        items.append(item)

    domain_counts: dict[str, dict[str, int]] = {}
    for item in items:
        domain = str(item["domain"])
        domain_counts.setdefault(domain, {"total": 0, "satisfied": 0, "gaps": 0})
        domain_counts[domain]["total"] += 1
        if item["satisfied"]:
            domain_counts[domain]["satisfied"] += 1
        else:
            domain_counts[domain]["gaps"] += 1

    gap_items = [item for item in items if not item["satisfied"]]
    missing_reports = [item["id"] for item in items if item["status"] == "missing_report"]
    invalid_reports = [item["id"] for item in items if item["status"] in {"outside_repo", "invalid_json"}]
    decision = "manual_evidence_ready" if not errors and not gap_items else "manual_evidence_gaps_present"
    if invalid_reports:
        decision = "manual_evidence_gap_audit_invalid"

    return {
        "report_version": 1,
        "repo_root": str(repo_root),
        "decision": decision,
        "scope": "manual evidence gates across playtest, content, story, asset, privacy, platform, base UI, and release",
        "requirement_count": len(items),
        "satisfied_count": len(items) - len(gap_items),
        "gap_count": len(gap_items),
        "missing_report_count": len(missing_reports),
        "domain_counts": dict(sorted(domain_counts.items())),
        "missing_reports": missing_reports,
        "invalid_reports": invalid_reports,
        "errors": errors,
        "gaps": [
            {
                "id": item["id"],
                "domain": item["domain"],
                "decision": item["decision"],
                "gate_decision": item["gate_decision"],
                "required_action": item["required_action"],
            }
            for item in gap_items
        ],
        "items": items,
        "limitations": [
            "This audit reads existing evidence reports only; it does not run Rust, Bevy, Harness simulations, Replay, performance tests, or manual reviews.",
            "A satisfied row means the referenced machine report has the expected passing decision; it still does not replace release candidate aggregation.",
            "Template reports and generated drafts with TODO placeholders must remain gaps until a real human fills and validates them.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Manual Evidence Gap Audit",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Requirements: {report['requirement_count']}",
        f"- Satisfied: {report['satisfied_count']}",
        f"- Gaps: {report['gap_count']}",
        f"- Missing reports: {report['missing_report_count']}",
        "",
        "## Domains",
        "",
        "| Domain | Satisfied | Gaps | Total |",
        "|---|---:|---:|---:|",
    ]
    for domain, counts in report["domain_counts"].items():
        lines.append(f"| `{domain}` | {counts['satisfied']} | {counts['gaps']} | {counts['total']} |")

    lines.extend(
        [
            "",
            "## Requirements",
            "",
            "| Domain | Requirement | Status | Decision | Gate |",
            "|---|---|---|---|---|",
        ]
    )
    for item in report["items"]:
        gate = item["gate_decision"] if item["gate_decision"] else "-"
        decision = item["decision"] if item["decision"] else "-"
        lines.append(
            f"| `{item['domain']}` | `{item['id']}` | `{item['status']}` | `{decision}` | `{gate}` |"
        )

    lines.extend(["", "## Gaps", ""])
    if report["gaps"]:
        for gap in report["gaps"]:
            lines.append(
                f"- `{gap['id']}` (`{gap['domain']}`): {gap['required_action']}"
            )
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
    parser = argparse.ArgumentParser(description="Audit Soft Candy Storm manual evidence gaps.")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--requirements", type=Path, default=None, help="Optional JSON requirements file")
    parser.add_argument("--focus-domain", type=str, default=None, help="Only audit one domain")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON audit report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown audit summary")
    parser.add_argument(
        "--allow-gaps",
        action="store_true",
        help="Exit 0 when gaps are present; useful for recording known manual work still pending",
    )
    args = parser.parse_args()

    requirements = load_requirements(args.requirements)
    report = build_report(args.repo_root, requirements, focus_domain=args.focus_domain)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))

    if report["decision"] == "manual_evidence_ready" or args.allow_gaps:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
