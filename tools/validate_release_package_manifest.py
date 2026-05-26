#!/usr/bin/env python3
"""Validate release package manifests.

This gate checks the shape and evidence for a packaged release candidate. It
does not build archives, launch Runtime, run Harness, or approve a release by
itself. A ready package must point to concrete package files, checksums,
release notes, lockfiles, asset manifests, and final smoke evidence.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PACKAGE_STATUSES = {"ready", "blocked", "draft"}
CHECK_STATUSES = {"pass", "fail", "blocked", "waiting"}
PASS_STATUS = "pass"
REQUIRED_READY_ITEM_KINDS = {
    "runtime_bundle",
    "release_archive",
    "checksum_manifest",
    "release_notes",
    "content_lockfile",
    "asset_manifest",
}
REQUIRED_READY_CHECKS = {
    "package_created",
    "checksum_recorded",
    "content_lock_verified",
    "asset_manifest_verified",
    "final_smoke",
    "release_notes_reviewed",
}
OPTIONAL_ITEM_KINDS = {
    "debug_symbols",
    "license_notice",
    "privacy_notice",
    "store_assets",
    "manual",
}
TODO_MARKERS = ("TODO", "<", ">")


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


def is_sha256_hex(value: str) -> bool:
    return len(value) == 64 and all(char in "0123456789abcdefABCDEF" for char in value)


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


def is_inside_repo(repo_root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return False
    return True


def validate_existing_repo_path(repo_root: Path, label: str, value: Any, errors: list[str]) -> None:
    if not is_nonempty_string(value):
        errors.append(f"{label} must be non-empty")
        return
    if has_placeholder(value):
        errors.append(f"{label} must not contain TODO or placeholder markers")
        return
    resolved = resolve_repo_path(repo_root, str(value))
    if not is_inside_repo(repo_root, resolved):
        errors.append(f"{label} must stay inside repository: {value}")
    elif not resolved.exists():
        errors.append(f"{label} does not exist: {value}")


def validate_package_item(
    repo_root: Path,
    item: Any,
    index: int,
    package_status: str | None,
) -> tuple[str | None, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(item, dict):
        return None, [f"package_items[{index}] must be an object"], warnings

    item_id = item.get("id")
    label = str(item_id) if is_nonempty_string(item_id) else f"package_items[{index}]"
    if not is_nonempty_string(item_id):
        errors.append(f"{label}: id must be non-empty")
    elif has_placeholder(item_id):
        errors.append(f"{label}: id must not contain TODO or placeholder markers")

    kind = item.get("kind")
    allowed_kinds = REQUIRED_READY_ITEM_KINDS | OPTIONAL_ITEM_KINDS
    if not is_nonempty_string(kind):
        errors.append(f"{label}: kind must be non-empty")
        kind_value = None
    elif kind not in allowed_kinds:
        errors.append(f"{label}: kind must be one of {', '.join(sorted(allowed_kinds))}")
        kind_value = str(kind)
    else:
        kind_value = str(kind)

    validate_existing_repo_path(repo_root, f"{label}: path", item.get("path"), errors)

    sha256 = item.get("sha256")
    if package_status == "ready":
        if not is_nonempty_string(sha256):
            errors.append(f"{label}: ready package item requires sha256")
        elif has_placeholder(sha256):
            errors.append(f"{label}: sha256 must not contain TODO or placeholder markers")
        elif not is_sha256_hex(str(sha256)):
            errors.append(f"{label}: sha256 must be a 64-character hexadecimal digest")
    elif sha256 is not None and not is_nonempty_string(sha256):
        errors.append(f"{label}: sha256 must be non-empty when provided")
    elif is_nonempty_string(sha256) and not is_sha256_hex(str(sha256)):
        errors.append(f"{label}: sha256 must be a 64-character hexadecimal digest")

    if item.get("synthetic") is True and package_status == "ready":
        errors.append(f"{label}: synthetic package item cannot be part of a ready package")
    if item.get("synthetic") is True and package_status != "ready":
        warnings.append(f"{label}: synthetic package item is recorded but cannot satisfy readiness")

    notes = item.get("notes")
    if notes is not None and has_placeholder(notes):
        errors.append(f"{label}: notes must not contain TODO or placeholder markers")

    return kind_value, errors, warnings


def validate_package_check(
    repo_root: Path,
    check: Any,
    index: int,
) -> tuple[str | None, list[str], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    blockers: list[str] = []
    if not isinstance(check, dict):
        return None, [f"checks[{index}] must be an object"], warnings, blockers

    check_id = check.get("id")
    label = str(check_id) if is_nonempty_string(check_id) else f"checks[{index}]"
    if not is_nonempty_string(check_id):
        errors.append(f"{label}: id must be non-empty")
        check_value = None
    elif has_placeholder(check_id):
        errors.append(f"{label}: id must not contain TODO or placeholder markers")
        check_value = str(check_id)
    else:
        check_value = str(check_id)

    status = check.get("status")
    if status not in CHECK_STATUSES:
        errors.append(f"{label}: status must be one of {', '.join(sorted(CHECK_STATUSES))}")
    elif status != PASS_STATUS:
        blockers.append(f"{label}: check status is `{status}`")

    summary = check.get("summary")
    if not is_nonempty_string(summary):
        errors.append(f"{label}: summary must be non-empty")
    elif has_placeholder(summary):
        errors.append(f"{label}: summary must not contain TODO or placeholder markers")

    evidence_paths = string_list(check.get("evidence_paths"))
    if check.get("evidence_paths") is not None and not isinstance(check.get("evidence_paths"), list):
        errors.append(f"{label}: evidence_paths must be a list")
    if status == PASS_STATUS and not evidence_paths:
        errors.append(f"{label}: pass check requires evidence_paths")
    if status in {"fail", "blocked"} and not evidence_paths:
        errors.append(f"{label}: {status} check requires evidence explaining the condition")
    for evidence_path in evidence_paths:
        validate_existing_repo_path(repo_root, f"{label}: evidence path", evidence_path, errors)

    if check.get("synthetic") is True and status == PASS_STATUS:
        errors.append(f"{label}: synthetic evidence cannot satisfy a release package check")
    if check.get("synthetic") is True and status != PASS_STATUS:
        warnings.append(f"{label}: synthetic evidence is recorded but does not satisfy the check")

    return check_value, errors, warnings, blockers


def build_report(manifest_path: Path, repo_root: Path) -> dict[str, Any]:
    payload = load_json_object(manifest_path)
    errors: list[str] = []
    warnings: list[str] = []
    blockers: list[str] = []

    if payload.get("manifest_version") != 1:
        errors.append("manifest_version must be 1")
    for field in ("package_id", "candidate_id", "created_at", "release_stage", "summary"):
        value = payload.get(field)
        if not is_nonempty_string(value):
            errors.append(f"{field} must be non-empty")
        elif has_placeholder(value):
            errors.append(f"{field} must not contain TODO or placeholder markers")

    package_status = payload.get("package_status")
    if package_status not in PACKAGE_STATUSES:
        errors.append(f"package_status must be one of {', '.join(sorted(PACKAGE_STATUSES))}")
        package_status_value = None
    else:
        package_status_value = str(package_status)
        if package_status_value != "ready":
            blockers.append(f"package_status is `{package_status_value}`")

    validate_existing_repo_path(repo_root, "candidate_evidence", payload.get("candidate_evidence"), errors)

    package_items = payload.get("package_items")
    if not isinstance(package_items, list):
        package_items = []
        errors.append("package_items must be a list")
    item_kinds: set[str] = set()
    item_reports: list[dict[str, Any]] = []
    seen_item_ids: set[str] = set()
    for index, item in enumerate(package_items):
        kind, item_errors, item_warnings = validate_package_item(repo_root, item, index, package_status_value)
        errors.extend(item_errors)
        warnings.extend(item_warnings)
        if isinstance(item, dict):
            item_id = item.get("id")
            if is_nonempty_string(item_id):
                if str(item_id) in seen_item_ids:
                    errors.append(f"duplicate package item id `{item_id}`")
                seen_item_ids.add(str(item_id))
            if kind is not None:
                item_kinds.add(kind)
            item_reports.append(
                {
                    "id": item.get("id", f"package_items[{index}]"),
                    "kind": item.get("kind"),
                    "synthetic": item.get("synthetic", False),
                    "has_sha256": is_nonempty_string(item.get("sha256")),
                }
            )

    missing_ready_item_kinds = sorted(REQUIRED_READY_ITEM_KINDS - item_kinds)
    if package_status_value == "ready":
        for kind in missing_ready_item_kinds:
            blockers.append(f"ready package is missing `{kind}` item")

    checks = payload.get("checks")
    if not isinstance(checks, list):
        checks = []
        errors.append("checks must be a list")
    check_reports: list[dict[str, Any]] = []
    seen_check_ids: set[str] = set()
    for index, check in enumerate(checks):
        check_id, check_errors, check_warnings, check_blockers = validate_package_check(repo_root, check, index)
        errors.extend(check_errors)
        warnings.extend(check_warnings)
        blockers.extend(check_blockers)
        if check_id is not None:
            if check_id in seen_check_ids:
                errors.append(f"duplicate check id `{check_id}`")
            seen_check_ids.add(check_id)
        if isinstance(check, dict):
            check_reports.append(
                {
                    "id": check.get("id", f"checks[{index}]"),
                    "status": check.get("status"),
                    "synthetic": check.get("synthetic", False),
                    "evidence_count": len(string_list(check.get("evidence_paths"))),
                }
            )

    missing_ready_checks = sorted(REQUIRED_READY_CHECKS - seen_check_ids)
    if package_status_value == "ready":
        for check_id in missing_ready_checks:
            blockers.append(f"ready package is missing `{check_id}` check")

    package_blockers = string_list(payload.get("blockers"))
    next_actions = string_list(payload.get("next_actions"))
    if payload.get("blockers") is not None and not isinstance(payload.get("blockers"), list):
        errors.append("blockers must be a list")
    if payload.get("next_actions") is not None and not isinstance(payload.get("next_actions"), list):
        errors.append("next_actions must be a list")
    if has_placeholder(payload.get("blockers")):
        errors.append("blockers must not contain TODO or placeholder markers")
    if has_placeholder(payload.get("next_actions")):
        errors.append("next_actions must not contain TODO or placeholder markers")
    if package_status_value == "ready":
        if package_blockers:
            errors.append("ready package cannot list blockers")
    else:
        if not package_blockers:
            errors.append("non-ready package must list blockers")
        if not next_actions:
            errors.append("non-ready package must list next_actions")
    blockers.extend(f"package blocker: {item}" for item in package_blockers)

    if errors:
        decision = "release_package_manifest_invalid"
    elif package_status_value == "ready" and not blockers:
        decision = "release_package_ready"
    else:
        decision = "release_package_not_ready"

    return {
        "report_version": 1,
        "source": str(manifest_path),
        "repo_root": str(repo_root),
        "package_id": payload.get("package_id"),
        "candidate_id": payload.get("candidate_id"),
        "release_stage": payload.get("release_stage"),
        "package_status": package_status,
        "decision": decision,
        "required_ready_item_kinds": sorted(REQUIRED_READY_ITEM_KINDS),
        "provided_item_kinds": sorted(item_kinds),
        "missing_ready_item_kinds": missing_ready_item_kinds,
        "required_ready_checks": sorted(REQUIRED_READY_CHECKS),
        "provided_checks": sorted(seen_check_ids),
        "missing_ready_checks": missing_ready_checks,
        "package_item_count": len(item_reports),
        "check_count": len(check_reports),
        "errors": errors,
        "warnings": warnings,
        "blockers": blockers,
        "package_items": item_reports,
        "checks": check_reports,
        "limitations": [
            "This validator checks release package evidence only; it does not build, sign, launch, or upload packages.",
            "A ready package still needs the release candidate evidence manifest to pass every release gate.",
            "Draft or blocked package manifests are allowed as honest not-ready evidence, not as release approval.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Release Package Manifest Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Package: `{report['package_id']}`",
        f"- Candidate: `{report['candidate_id']}`",
        f"- Release stage: `{report['release_stage']}`",
        f"- Package status: `{report['package_status']}`",
        f"- Decision: `{report['decision']}`",
        "",
        "## Package Items",
        "",
        "| Item | Kind | SHA-256 | Synthetic |",
        "|---|---|---|---|",
    ]
    for item in report["package_items"]:
        lines.append(
            f"| `{item['id']}` | `{item['kind']}` | {item['has_sha256']} | {item['synthetic']} |"
        )

    lines.extend(["", "## Checks", "", "| Check | Status | Evidence | Synthetic |", "|---|---|---:|---|"])
    for check in report["checks"]:
        lines.append(
            f"| `{check['id']}` | `{check['status']}` | {check['evidence_count']} | {check['synthetic']} |"
        )

    lines.extend(["", "## Missing Ready Items", ""])
    if report["missing_ready_item_kinds"]:
        lines.extend(f"- `{item}`" for item in report["missing_ready_item_kinds"])
    else:
        lines.append("- None")

    lines.extend(["", "## Missing Ready Checks", ""])
    if report["missing_ready_checks"]:
        lines.extend(f"- `{item}`" for item in report["missing_ready_checks"])
    else:
        lines.append("- None")

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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm release package manifests.")
    parser.add_argument("manifest", type=Path, help="Release package manifest JSON")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON validation report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown validation summary")
    parser.add_argument(
        "--allow-not-ready",
        action="store_true",
        help="Exit 0 for structurally valid not-ready manifests",
    )
    args = parser.parse_args()

    report = build_report(args.manifest, args.repo_root)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))

    if report["decision"] == "release_package_ready":
        return 0
    if args.allow_not_ready and report["decision"] == "release_package_not_ready":
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
