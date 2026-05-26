#!/usr/bin/env python3
"""Validate first-demo readiness evidence for Soft Candy Storm.

This gate maps the Demo target from docs/01 to repository evidence. It is a
pure Python audit: it counts content, inspects existing manifests/reports, and
keeps the decision conservative. It does not run Rust, Bevy, Harness
simulation, Replay, performance tests, or human playtests.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


CONTENT_CATEGORIES = [
    "characters",
    "weapons",
    "passives",
    "enemies",
    "bosses",
    "maps",
    "waves",
    "evolutions",
]
DEMO_CONTENT_TARGETS = {
    "characters": 1,
    "maps": 1,
    "weapons": 12,
    "passives": 8,
    "enemies": 12,
    "bosses": 3,
}
DEMO_TAG_GROUPS = {
    "projectile": {"projectile", "pierce", "single-target"},
    "defense": {"defense", "orbit", "close", "health", "recovery"},
    "control": {"control", "slow", "cold", "zone"},
    "burst": {"burst", "aoe", "area", "trap", "knockback"},
    "summon": {"summon", "turret", "auto-fire"},
    "boss": {"boss-killer", "beam"},
    "economy": {"economy", "xp", "pickup"},
}
REQUIRED_MANUAL_RUN_IDS = {
    "new_001",
    "new_002",
    "new_003",
    "skilled_001",
    "skilled_002",
    "skilled_003",
    "build_001",
    "build_002",
    "build_003",
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


def resolve_repo_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def relative_repo_path(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(path)


def evidence_exists(repo_root: Path, value: str) -> bool:
    return resolve_repo_path(repo_root, value).exists()


def content_files(content_dir: Path, category: str) -> list[Path]:
    category_dir = content_dir / category
    return sorted(path for path in category_dir.glob("*.json") if path.is_file()) if category_dir.exists() else []


def collect_content(content_dir: Path) -> tuple[dict[str, dict[str, dict[str, Any]]], list[str]]:
    errors: list[str] = []
    records: dict[str, dict[str, dict[str, Any]]] = {}
    for category in CONTENT_CATEGORIES:
        records[category] = {}
        for path in content_files(content_dir, category):
            try:
                payload = load_json_object(path)
            except (OSError, ValueError, json.JSONDecodeError) as error:
                errors.append(f"{category}/{path.name} invalid JSON: {error}")
                continue
            item_id = payload.get("id")
            if not is_nonempty_string(item_id):
                errors.append(f"{category}/{path.name} missing id")
                continue
            records[category][str(item_id)] = payload
    return records, errors


def tag_set(payload: dict[str, Any]) -> set[str]:
    return set(string_list(payload.get("tags")))


def content_counts(records: dict[str, dict[str, dict[str, Any]]]) -> dict[str, int]:
    return {category: len(records.get(category, {})) for category in CONTENT_CATEGORIES}


def build_tag_groups(records: dict[str, dict[str, dict[str, Any]]]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for group, tags in DEMO_TAG_GROUPS.items():
        matching = []
        for item_id, payload in records.get("weapons", {}).items():
            if tag_set(payload) & tags:
                matching.append(item_id)
        for item_id, payload in records.get("passives", {}).items():
            if tag_set(payload) & tags:
                matching.append(item_id)
        groups[group] = sorted(set(matching))
    return groups


def count_600_second_waves(records: dict[str, dict[str, dict[str, Any]]]) -> tuple[list[str], list[str]]:
    valid: list[str] = []
    invalid: list[str] = []
    for wave_id, payload in records.get("waves", {}).items():
        duration = payload.get("duration_seconds")
        boss_events = payload.get("boss_events")
        if duration == 600 and isinstance(boss_events, list) and boss_events:
            valid.append(wave_id)
        else:
            invalid.append(wave_id)
    return sorted(valid), sorted(invalid)


def content_gate(label: str, content_dir: Path, repo_root: Path, *, candidate: bool) -> dict[str, Any]:
    if not content_dir.exists():
        return {
            "id": label,
            "status": "blocked",
            "candidate": candidate,
            "content_dir": relative_repo_path(repo_root, content_dir),
            "summary": "content directory is missing",
            "counts": {},
            "targets": DEMO_CONTENT_TARGETS,
            "valid_600_second_waves": [],
            "invalid_waves": [],
            "build_tag_groups": {},
            "present_build_group_count": 0,
            "readiness_gaps": [],
            "errors": [f"content_dir does not exist: {relative_repo_path(repo_root, content_dir)}"],
            "evidence": [relative_repo_path(repo_root, content_dir)],
        }
    records, errors = collect_content(content_dir)
    counts = content_counts(records)
    readiness_gaps = [
        f"{category} count {counts.get(category, 0)} is below target {target}"
        for category, target in DEMO_CONTENT_TARGETS.items()
        if counts.get(category, 0) < target
    ]
    valid_waves, invalid_waves = count_600_second_waves(records)
    if not valid_waves:
        readiness_gaps.append("no 600-second wave with boss event")
    tag_groups = build_tag_groups(records)
    present_groups = sorted(group for group, items in tag_groups.items() if items)
    if len(present_groups) < 4:
        readiness_gaps.append("fewer than 4 build tag groups have supporting weapons/passives")

    status = "pass" if not errors and not readiness_gaps else ("waiting" if candidate else "blocked")
    summary = (
        "content counts and build tags satisfy docs/01 demo shape"
        if status == "pass"
        else "content shape is not sufficient for a demo-ready formal content pack"
    )
    return {
        "id": label,
        "status": status,
        "candidate": candidate,
        "content_dir": relative_repo_path(repo_root, content_dir),
        "summary": summary,
        "counts": counts,
        "targets": DEMO_CONTENT_TARGETS,
        "valid_600_second_waves": valid_waves,
        "invalid_waves": invalid_waves,
        "build_tag_groups": tag_groups,
        "present_build_group_count": len(present_groups),
        "readiness_gaps": readiness_gaps,
        "errors": errors,
        "evidence": [relative_repo_path(repo_root, content_dir)],
    }


def report_gate(
    gate_id: str,
    status: str,
    summary: str,
    evidence: list[str],
    repo_root: Path,
    *,
    errors: list[str] | None = None,
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    gate_errors = list(errors or [])
    for path in evidence:
        if not evidence_exists(repo_root, path):
            gate_errors.append(f"evidence path does not exist: {path}")
    if status == "pass" and gate_errors:
        status = "blocked"
    return {
        "id": gate_id,
        "status": status,
        "summary": summary,
        "evidence": evidence,
        "errors": gate_errors,
        "warnings": list(warnings or []),
    }


def candidate_manifest_gate(repo_root: Path, manifest_path: Path) -> dict[str, Any]:
    evidence = [relative_repo_path(repo_root, manifest_path)]
    try:
        payload = load_json_object(manifest_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return report_gate("candidate_full_pack", "blocked", "candidate manifest is unreadable", evidence, repo_root, errors=[str(error)])
    rules = payload.get("project_rules")
    errors: list[str] = []
    if not isinstance(rules, dict):
        errors.append("project_rules must be an object")
    else:
        if rules.get("candidate_only") is not True:
            errors.append("candidate_only must be true")
        if rules.get("accepted_content") is not False:
            errors.append("accepted_content must be false")
        if rules.get("runtime_integrated") is not False:
            errors.append("runtime_integrated must be false")
    counts = payload.get("content_counts")
    if not isinstance(counts, dict):
        errors.append("content_counts must be an object")
        counts = {}
    for category, target in DEMO_CONTENT_TARGETS.items():
        value = counts.get(category)
        if not isinstance(value, int) or isinstance(value, bool) or value < target:
            errors.append(f"candidate {category} count is below target {target}")
    return report_gate(
        "candidate_full_pack",
        "waiting" if not errors else "blocked",
        "Phase 4 full pack candidate reaches demo roster shape but remains candidate-only",
        evidence,
        repo_root,
        errors=errors,
    )


def runtime_asset_gate(repo_root: Path, manifest_path: Path) -> dict[str, Any]:
    evidence = [relative_repo_path(repo_root, manifest_path)]
    try:
        payload = load_json_object(manifest_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return report_gate("prototype_assets", "blocked", "prototype asset manifest is unreadable", evidence, repo_root, errors=[str(error)])
    assets = payload.get("assets")
    errors: list[str] = []
    if not isinstance(assets, list):
        errors.append("assets must be a list")
        assets = []
    asset_ids = {
        str(item.get("id"))
        for item in assets
        if isinstance(item, dict) and is_nonempty_string(item.get("id"))
    }
    required_assets = {
        "player_jar_keeper",
        "enemy_bouncy_gummy",
        "enemy_sour_gummy",
        "boss_runaway_sugar_mixer",
        "pickup_candy_crystal",
        "projectile_rainbow_candy_shot",
        "map_frosting_grassland_tile",
    }
    missing = sorted(required_assets - asset_ids)
    if missing:
        errors.append(f"missing prototype assets: {', '.join(missing)}")
    if payload.get("candidate_only") is not False:
        errors.append("prototype asset manifest must be runtime usable, not candidate-only")
    return report_gate(
        "prototype_assets",
        "pass" if not errors else "blocked",
        "programmatic top-down prototype assets cover core demo readability placeholders",
        evidence,
        repo_root,
        errors=errors,
    )


def manual_playtest_gate(
    repo_root: Path,
    draft_path: Path,
    packet_path: Path,
    strict_validation_path: Path,
    acceptance_packet_path: Path,
) -> dict[str, Any]:
    evidence = [
        relative_repo_path(repo_root, draft_path),
        relative_repo_path(repo_root, packet_path),
        relative_repo_path(repo_root, strict_validation_path),
        relative_repo_path(repo_root, acceptance_packet_path),
    ]
    errors: list[str] = []
    warnings: list[str] = []
    try:
        payload = load_json_object(draft_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return report_gate("manual_playtest", "blocked", "manual playtest draft is unreadable", evidence, repo_root, errors=[str(error)])
    runs = payload.get("runs")
    seen = set()
    if not isinstance(runs, list):
        errors.append("runs must be a list")
    else:
        for run in runs:
            if isinstance(run, dict) and is_nonempty_string(run.get("run_id")):
                seen.add(str(run["run_id"]))
    missing = sorted(REQUIRED_MANUAL_RUN_IDS - seen)
    if missing:
        errors.append(f"manual playtest draft is missing runs: {', '.join(missing)}")
    decision = payload.get("acceptance_decision")
    if decision != "needs_more_runs":
        warnings.append("manual playtest draft should remain needs_more_runs until real human review exists")
    try:
        strict_validation = load_json_object(strict_validation_path)
        if strict_validation.get("decision") != "manual_review_invalid":
            warnings.append("current local strict validation should stay invalid until real human review exists")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"strict manual review validation report unreadable: {error}")
    try:
        acceptance_packet = load_json_object(acceptance_packet_path)
        if acceptance_packet.get("decision") != "manual_playtest_acceptance_review_packet_needs_evidence":
            warnings.append("manual playtest acceptance packet should stay needs_evidence until real human review exists")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"manual playtest acceptance packet unreadable: {error}")
    return report_gate(
        "manual_playtest",
        "waiting" if not errors else "blocked",
        "9-run manual playtest draft, packet, strict validation, and acceptance evidence packet exist, but TODO ratings are not acceptance evidence",
        evidence,
        repo_root,
        errors=errors,
        warnings=warnings,
    )


def release_gate(repo_root: Path, rc_report_path: Path, lock_report_path: Path) -> dict[str, Any]:
    evidence = [relative_repo_path(repo_root, rc_report_path), relative_repo_path(repo_root, lock_report_path)]
    errors: list[str] = []
    status = "blocked"
    summary = "release candidate is not ready and accepted content lockfile is empty/blocked"
    try:
        rc_report = load_json_object(rc_report_path)
        if rc_report.get("decision") == "release_candidate_ready":
            errors.append("demo readiness expected current RC not-ready evidence, but RC is ready")
            status = "pass"
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"release candidate report unreadable: {error}")
    try:
        lock_report = load_json_object(lock_report_path)
        if lock_report.get("decision") == "accepted_content_lockfile_valid":
            errors.append("accepted content lockfile is valid; update demo readiness expectations")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"accepted content lockfile report unreadable: {error}")
    return report_gate("release_state", status, summary, evidence, repo_root, errors=errors)


def build_report(repo_root: Path, formal_content_dir: Path, candidate_content_dir: Path) -> dict[str, Any]:
    formal_gate = content_gate("formal_content_pack", formal_content_dir, repo_root, candidate=False)
    candidate_gate = content_gate("candidate_content_pack", candidate_content_dir, repo_root, candidate=True)
    gates = [
        formal_gate,
        candidate_gate,
        candidate_manifest_gate(
            repo_root,
            repo_root / "harness/generated_candidates/2026-05-26_phase4_roster_gap_full_pack/metadata/manifest.json",
        ),
        report_gate(
            "schema_preflight",
            "waiting",
            "candidate full pack preflight exists; formal Rust/GameCore schema gate remains blocked by local binary launch",
            [
                "harness/reports/2026-05-26_phase4_roster_full_pack_preflight_001/summary.md",
                "harness/reports/2026-05-26_content_schema_contract_001/summary.md",
            ],
            repo_root,
        ),
        report_gate(
            "static_budget",
            "waiting",
            "pure Python static budgets exist for base_demo and full pack; game_harness budget-content still needs binary recovery",
            [
                "harness/reports/2026-05-26_static_balance_budget_base_demo_001/summary.md",
                "harness/reports/2026-05-26_static_balance_budget_phase4_full_pack_001/summary.md",
            ],
            repo_root,
        ),
        report_gate(
            "historical_bot_matrix",
            "waiting",
            "historical 9-bot 20-seed matrix and replay regression exist, but current binary blocker prevents fresh release evidence",
            [
                "harness/reports/2026-05-25_bot_matrix_nightly_001/summary.md",
                "harness/reports/2026-05-25_bot_matrix_nightly_regression_001/summary.md",
            ],
            repo_root,
        ),
        report_gate(
            "runtime_capture",
            "waiting",
            "historical Runtime captures prove wiring but not current playable demo readiness",
            [
                "harness/reports/2026-05-25_runtime_demo_input_001/summary.md",
                "harness/reports/2026-05-25_runtime_boss_capture_001/summary.md",
                "harness/reports/2026-05-25_runtime_meta_panel_smoke_001/summary.md",
            ],
            repo_root,
        ),
        runtime_asset_gate(repo_root, repo_root / "assets/prototype_topdown/manifest.json"),
        report_gate(
            "meta_progression",
            "waiting",
            "meta progression smoke and save contracts exist, but complete base UI and fresh runtime validation remain missing",
            [
                "harness/reports/2026-05-25_meta_progression_smoke_001/summary.md",
                "harness/reports/2026-05-25_runtime_meta_panel_smoke_001/summary.md",
                "harness/reports/2026-05-26_save_state_contract_v1_001/summary.md",
            ],
            repo_root,
        ),
        manual_playtest_gate(
            repo_root,
            repo_root / "harness/playtest/drafts/2026-05-26_runtime_manual_playtest_review_draft.json",
            repo_root / "harness/reports/2026-05-26_runtime_manual_playtest_review_packet_001/summary.md",
            repo_root / "harness/reports/2026-05-26_runtime_manual_playtest_strict_validation_current_local_001/manual_review_validation.json",
            repo_root / "harness/reports/2026-05-26_manual_playtest_acceptance_review_packet_001/manual_playtest_acceptance_review_packet.json",
        ),
        release_gate(
            repo_root,
            repo_root / "harness/reports/2026-05-26_release_candidate_evidence_current_local_003/release_candidate_evidence.json",
            repo_root / "harness/reports/2026-05-26_accepted_content_lockfile_current_local_001/accepted_content_lockfile.json",
        ),
    ]

    errors = [f"{gate['id']}: {error}" for gate in gates for error in gate.get("errors", [])]
    warnings = [f"{gate['id']}: {warning}" for gate in gates for warning in gate.get("warnings", [])]
    blockers = [
        f"{gate['id']}: {gate['summary']}"
        for gate in gates
        if gate["status"] in {"blocked", "waiting"}
    ]
    status_counts: dict[str, int] = {}
    for gate in gates:
        status = str(gate["status"])
        status_counts[status] = status_counts.get(status, 0) + 1

    if errors:
        decision = "demo_readiness_invalid"
    elif blockers:
        decision = "demo_not_ready"
    else:
        decision = "demo_ready"

    return {
        "report_version": 1,
        "source": "docs/01 first-demo target",
        "repo_root": str(repo_root),
        "decision": decision,
        "status_counts": dict(sorted(status_counts.items())),
        "gate_count": len(gates),
        "errors": errors,
        "warnings": warnings,
        "blockers": blockers,
        "gates": gates,
        "limitations": [
            "This audit checks repository evidence for the docs/01 demo target only.",
            "It does not execute Rust, Bevy, Harness simulation, Replay, performance tests, or manual playtests.",
            "Candidate content and historical smoke reports cannot prove a release-ready demo.",
            "A demo_ready decision requires every gate to pass with current, non-candidate evidence.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Demo Readiness Audit",
        "",
        f"- Source: `{report['source']}`",
        f"- Decision: `{report['decision']}`",
        f"- Gates: {report['gate_count']}",
        "",
        "## Status Counts",
        "",
        "| Status | Count |",
        "|---|---:|",
    ]
    for status, count in report["status_counts"].items():
        lines.append(f"| `{status}` | {count} |")

    lines.extend(["", "## Gates", "", "| Gate | Status | Summary | Evidence |", "|---|---|---|---:|"])
    for gate in report["gates"]:
        lines.append(f"| `{gate['id']}` | `{gate['status']}` | {gate['summary']} | {len(gate['evidence'])} |")

    formal_gate = next((gate for gate in report["gates"] if gate["id"] == "formal_content_pack"), None)
    candidate_gate = next((gate for gate in report["gates"] if gate["id"] == "candidate_content_pack"), None)
    if formal_gate and candidate_gate:
        lines.extend(["", "## Content Counts", "", "| Category | Formal | Candidate | Target |", "|---|---:|---:|---:|"])
        targets = formal_gate["targets"]
        for category in DEMO_CONTENT_TARGETS:
            lines.append(
                f"| `{category}` | {formal_gate['counts'].get(category, 0)} | "
                f"{candidate_gate['counts'].get(category, 0)} | {targets[category]} |"
            )
        lines.extend(["", "## Build Groups", "", "| Group | Formal Items | Candidate Items |", "|---|---|---|"])
        for group in DEMO_TAG_GROUPS:
            formal_items = ", ".join(formal_gate["build_tag_groups"].get(group, [])) or "-"
            candidate_items = ", ".join(candidate_gate["build_tag_groups"].get(group, [])) or "-"
            lines.append(f"| `{group}` | {formal_items} | {candidate_items} |")

    lines.extend(["", "## Blockers", ""])
    if report["blockers"]:
        lines.extend(f"- {blocker}" for blocker in report["blockers"])
    else:
        lines.append("- None")

    lines.extend(["", "## Errors", ""])
    if report["errors"]:
        lines.extend(f"- {error}" for error in report["errors"])
    else:
        lines.append("- None")

    lines.extend(["", "## Warnings", ""])
    if report["warnings"]:
        lines.extend(f"- {warning}" for warning in report["warnings"])
    else:
        lines.append("- None")

    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm first-demo readiness.")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--content-dir", type=Path, default=Path("content/base_demo"), help="Formal content pack")
    parser.add_argument(
        "--candidate-dir",
        type=Path,
        default=Path("harness/generated_candidates/2026-05-26_phase4_roster_gap_full_pack"),
        help="Candidate full content pack",
    )
    parser.add_argument("--report", type=Path, default=None, help="Write JSON report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown summary")
    parser.add_argument("--allow-not-ready", action="store_true", help="Exit 0 for honest demo_not_ready reports")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    content_dir = args.content_dir if args.content_dir.is_absolute() else repo_root / args.content_dir
    candidate_dir = args.candidate_dir if args.candidate_dir.is_absolute() else repo_root / args.candidate_dir
    report = build_report(repo_root, content_dir, candidate_dir)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))

    if report["decision"] == "demo_ready":
        return 0
    if args.allow_not_ready and report["decision"] == "demo_not_ready":
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
