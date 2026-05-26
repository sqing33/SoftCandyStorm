#!/usr/bin/env python3
"""Create a recovery handoff packet for the local Mach-O launch blocker.

The packet consolidates the existing diagnostic report, failure case, progress
ledger, and docs coverage blockers. It does not repair the host policy and must
not be used as evidence that Rust, Bevy, Harness, Runtime, or Gym can run.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


BINARY_BLOCKER = "local_binary_launch_blocked"

DEFAULT_DIAGNOSTIC = Path(
    "harness/reports/2026-05-26_local_binary_launch_diagnostic_001/local_binary_launch_diagnostic.json"
)
DEFAULT_FAILURE_CASE = Path("harness/failed_cases/fail_20260526_024_local_binary_launch_blocked.json")
DEFAULT_PROGRESS = Path("harness/progress.json")
DEFAULT_DOCS_COVERAGE = Path("harness/docs_implementation_coverage.json")

POST_RECOVERY_COMMANDS = [
    "python3 tools/diagnose_local_binary_launch.py --repo-root . --report harness/reports/<report-id>/local_binary_launch_diagnostic.json --markdown harness/reports/<report-id>/summary.md --timeout 5",
    "spctl -a -vv target/debug/game_harness",
    "target/debug/game_harness --help",
    "cargo fmt --check",
    "cargo clippy --workspace --all-targets",
    "cargo test --workspace",
    "target/debug/game_harness simulate --bot kite --seed 12345 --seconds 300 --out harness/reports/<report-id>",
    "target/debug/game_harness matrix --bots all --seed-start <seed> --seeds <count> --seconds 300 --out harness/reports/<report-id>",
    "target/debug/game_harness replay-batch --input harness/reports/<baseline-replay-dir> --out harness/reports/<report-id>",
    "uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --behavior-clone-model <context3-model> --compare-rule-bots --compare-map-preset high-pressure --eval-seconds 60 --report harness/reports/<report-id>/run_output.json",
    "uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --behavior-clone-model <context3-model> --compare-rule-bots --compare-map-preset high-pressure --eval-seconds 300 --report harness/reports/<report-id>/run_output.json",
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


def relative_repo_path(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(path)


def resolve_repo_path(repo_root: Path, value: Path) -> Path:
    return value if value.is_absolute() else repo_root / value


def markdown_escape(text: Any) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def code(value: Any) -> str:
    return f"`{markdown_escape(value)}`"


def signal_rows(signals: dict[str, Any]) -> list[dict[str, str]]:
    ordered = [
        ("system_binary_runs", "System binary runs"),
        ("hello_compiled", "Minimal hello compiled"),
        ("hello_runs", "Minimal hello runs"),
        ("hello_timed_out", "Minimal hello timed out"),
        ("developer_mode_disabled", "Developer Mode disabled"),
        ("spctl_rejected", "spctl rejected hello"),
        ("provenance_xattr_present", "com.apple.provenance present"),
        ("amfi_no_cms_blob", "AMFI no CMS blob signal"),
        ("security_policy_would_not_allow", "Security policy denial signal"),
    ]
    rows: list[dict[str, str]] = []
    for key, label in ordered:
        rows.append({"id": key, "label": label, "value": str(bool(signals.get(key)))})
    return rows


def extract_check_summary(diagnostic: dict[str, Any]) -> dict[str, dict[str, Any]]:
    checks = diagnostic.get("checks") if isinstance(diagnostic.get("checks"), dict) else {}
    summary: dict[str, dict[str, Any]] = {}
    for check_id in ["system_echo", "developer_mode", "spctl_status", "cc_compile", "spctl_assess", "hello_run"]:
        check = checks.get(check_id)
        if not isinstance(check, dict):
            continue
        summary[check_id] = {
            "returncode": check.get("returncode"),
            "timed_out": check.get("timed_out"),
            "elapsed_seconds": check.get("elapsed_seconds"),
            "stdout": str(check.get("stdout", "")).strip(),
            "stderr": str(check.get("stderr", "")).strip(),
        }
    return summary


def interesting_policy_lines(diagnostic: dict[str, Any], limit: int = 12) -> list[str]:
    policy_log = diagnostic.get("policy_log") if isinstance(diagnostic.get("policy_log"), dict) else {}
    lines = [line for line in policy_log.get("lines", []) if isinstance(line, str)]
    priority_patterns = [
        "Security policy would not allow process",
        "AMFI",
        "CMS blob",
        "Gatekeeper",
        "AppleSystemPolicy",
        "provenance",
    ]
    interesting: list[str] = []
    seen: set[str] = set()
    for pattern in priority_patterns:
        for line in lines:
            if pattern in line and line not in seen:
                interesting.append(line)
                seen.add(line)
    return (interesting or lines)[:limit]


def collect_blocked_docs(docs_payload: dict[str, Any]) -> list[dict[str, Any]]:
    blocked_docs: list[dict[str, Any]] = []
    for doc in docs_payload.get("docs", []):
        if not isinstance(doc, dict):
            continue
        blocked_items = []
        for item in doc.get("coverage", []):
            if not isinstance(item, dict):
                continue
            if BINARY_BLOCKER in string_list(item.get("blockers")):
                blocked_items.append(
                    {
                        "id": item.get("id", ""),
                        "status": item.get("status", ""),
                        "gap_count": len(string_list(item.get("gaps"))),
                    }
                )
        if blocked_items:
            blocked_docs.append(
                {
                    "doc_path": doc.get("doc_path", ""),
                    "status": doc.get("status", ""),
                    "blocked_items": blocked_items,
                }
            )
    return blocked_docs


def collect_progress_entries(progress_payload: dict[str, Any]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for section in ["current_findings", "next_recommended"]:
        for item in progress_payload.get(section, []):
            if not isinstance(item, dict):
                continue
            if item.get("id") == BINARY_BLOCKER or item.get("id") == "local_binary_launch_recovery":
                entries.append(
                    {
                        "section": section,
                        "id": item.get("id", ""),
                        "summary": item.get("summary", ""),
                        "report": item.get("report", ""),
                    }
                )
    return entries


def recovery_decision(diagnostic_decision: str) -> str:
    if diagnostic_decision == "local_binary_launch_ok":
        return "post_recovery_validation_required"
    if diagnostic_decision == "local_binary_launch_probe_failed":
        return "diagnostic_probe_failed"
    return "recovery_required"


def build_packet(
    diagnostic_path: Path,
    failure_case_path: Path,
    progress_path: Path,
    docs_coverage_path: Path | None,
    repo_root: Path,
) -> dict[str, Any]:
    diagnostic = load_json_object(diagnostic_path)
    failure_case = load_json_object(failure_case_path)
    progress = load_json_object(progress_path)
    docs_coverage = load_json_object(docs_coverage_path) if docs_coverage_path is not None else {}

    diagnostic_decision = str(diagnostic.get("decision", ""))
    signals = diagnostic.get("signals") if isinstance(diagnostic.get("signals"), dict) else {}
    checks = extract_check_summary(diagnostic)

    why_not_gameplay_failure = [
        "The compiled hello probe is independent of GameCore, Harness, Runtime, Gym, content, and replay logic.",
        "The probe compiles successfully but does not enter main before the timeout, so downstream binary timeouts are host execution-policy evidence first.",
        "Until the diagnostic returns local_binary_launch_ok, Rust/Bevy/Harness/Gym timeouts must remain blocker evidence rather than gameplay or policy-quality evidence.",
    ]
    if signals.get("security_policy_would_not_allow"):
        why_not_gameplay_failure.append("Policy logs include a Security policy denial for the newly compiled hello binary.")
    if signals.get("developer_mode_disabled"):
        why_not_gameplay_failure.append("Developer Mode is currently disabled in the captured session.")

    recovery_actions = [
        "Enable Developer Mode for the host/toolchain session, or rerun from a trusted developer host.",
        "If available, sign local test binaries with a trusted code-signing identity that produces a CMS signature.",
        "Rerun the diagnostic until its decision is exactly local_binary_launch_ok before interpreting game binaries.",
        "Only after local_binary_launch_ok should Harness, Runtime, Gym, Replay, and RC gates be revalidated.",
    ]

    blocked_docs = collect_blocked_docs(docs_coverage)
    progress_entries = collect_progress_entries(progress)

    return {
        "report_version": 1,
        "decision": recovery_decision(diagnostic_decision),
        "diagnostic_decision": diagnostic_decision,
        "diagnostic_path": relative_repo_path(repo_root, diagnostic_path),
        "failure_case_path": relative_repo_path(repo_root, failure_case_path),
        "progress_path": relative_repo_path(repo_root, progress_path),
        "docs_coverage_path": relative_repo_path(repo_root, docs_coverage_path) if docs_coverage_path else "",
        "signals": signal_rows(signals),
        "check_summary": checks,
        "policy_log_lines": interesting_policy_lines(diagnostic),
        "failure_case": {
            "case_id": failure_case.get("case_id", ""),
            "category": failure_case.get("category", ""),
            "content_id": failure_case.get("content_id", ""),
            "symptom": failure_case.get("symptom", ""),
            "root_cause": failure_case.get("root_cause", ""),
            "fix": failure_case.get("fix", ""),
            "validation": failure_case.get("validation", ""),
        },
        "why_not_gameplay_failure": why_not_gameplay_failure,
        "recovery_actions": recovery_actions,
        "post_recovery_commands": POST_RECOVERY_COMMANDS,
        "blocked_docs": blocked_docs,
        "blocked_doc_count": len(blocked_docs),
        "progress_entries": progress_entries,
        "limitations": [
            "This packet organizes recovery evidence only; it does not change host security policy.",
            "This packet is not gameplay evidence and cannot explain policy quality, balance, or player experience.",
            "It does not prove Rust, Bevy, GameCore, Harness, Runtime, Gym, Replay, performance, or release gates are working.",
            "It must not be cited as a passing RC, platform, privacy, legal, or manual playtest gate.",
            "The blocker remains active until a fresh diagnostic report records local_binary_launch_ok.",
        ],
    }


def write_markdown(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Local Binary Launch Recovery Packet",
        "",
        f"- Decision: `{packet['decision']}`",
        f"- Diagnostic decision: `{packet['diagnostic_decision']}`",
        f"- Diagnostic report: `{packet['diagnostic_path']}`",
        f"- Failure case: `{packet['failure_case_path']}`",
        f"- Progress ledger: `{packet['progress_path']}`",
        f"- Docs coverage ledger: `{packet['docs_coverage_path']}`",
        "",
        "## Current Signals",
        "",
        "| Signal | Value |",
        "|---|---|",
    ]
    for signal in packet["signals"]:
        lines.append(f"| {markdown_escape(signal['label'])} | `{signal['value']}` |")

    lines.extend(["", "## Key Checks", "", "| Check | Return code | Timed out | Elapsed seconds | Output |", "|---|---:|---|---:|---|"])
    for check_id, check in packet["check_summary"].items():
        output = check.get("stdout") or check.get("stderr") or ""
        if len(str(output)) > 180:
            output = str(output)[:177] + "..."
        lines.append(
            "| "
            + " | ".join(
                [
                    code(check_id),
                    code(check.get("returncode")),
                    code(check.get("timed_out")),
                    code(check.get("elapsed_seconds")),
                    code(output),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Policy Log Highlights", ""])
    if packet["policy_log_lines"]:
        lines.extend(f"- `{line}`" for line in packet["policy_log_lines"])
    else:
        lines.append("- None captured")

    failure = packet["failure_case"]
    lines.extend(
        [
            "",
            "## Failure Case",
            "",
            f"- Case id: `{failure['case_id']}`",
            f"- Category: `{failure['category']}`",
            f"- Content id: `{failure['content_id']}`",
            f"- Symptom: {markdown_escape(failure['symptom'])}",
            f"- Root cause: {markdown_escape(failure['root_cause'])}",
            f"- Fix: {markdown_escape(failure['fix'])}",
            f"- Validation: {markdown_escape(failure['validation'])}",
            "",
            "## Why This Is Not Gameplay Evidence",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in packet["why_not_gameplay_failure"])

    lines.extend(["", "## Recovery Actions", ""])
    lines.extend(f"- {item}" for item in packet["recovery_actions"])

    lines.extend(["", "## Ordered Post-Recovery Validation", ""])
    for index, command in enumerate(packet["post_recovery_commands"], start=1):
        lines.append(f"{index}. `{command}`")

    lines.extend(["", "## Blocked Docs", "", "| Doc | Status | Blocked items |", "|---|---|---:|"])
    for doc in packet["blocked_docs"]:
        lines.append(f"| `{doc['doc_path']}` | `{doc['status']}` | {len(doc['blocked_items'])} |")
    if not packet["blocked_docs"]:
        lines.append("| None |  | 0 |")

    lines.extend(["", "## Progress Entries", "", "| Section | Id | Report |", "|---|---|---|"])
    for entry in packet["progress_entries"]:
        lines.append(
            "| "
            + " | ".join([code(entry["section"]), code(entry["id"]), code(entry["report"])])
            + " |"
        )
    if not packet["progress_entries"]:
        lines.append("| None |  |  |")

    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in packet["limitations"])

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a local binary launch recovery handoff packet.")
    parser.add_argument("--diagnostic", type=Path, default=DEFAULT_DIAGNOSTIC, help="Diagnostic JSON report")
    parser.add_argument("--failure-case", type=Path, default=DEFAULT_FAILURE_CASE, help="Failure case JSON")
    parser.add_argument("--progress", type=Path, default=DEFAULT_PROGRESS, help="Progress ledger JSON")
    parser.add_argument(
        "--docs-coverage",
        type=Path,
        default=DEFAULT_DOCS_COVERAGE,
        help="Docs implementation coverage ledger JSON",
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--out", type=Path, required=True, help="Output Markdown packet")
    parser.add_argument("--json-out", type=Path, default=None, help="Optional output JSON packet")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    diagnostic = resolve_repo_path(repo_root, args.diagnostic)
    failure_case = resolve_repo_path(repo_root, args.failure_case)
    progress = resolve_repo_path(repo_root, args.progress)
    docs_coverage = resolve_repo_path(repo_root, args.docs_coverage) if args.docs_coverage is not None else None

    packet = build_packet(diagnostic, failure_case, progress, docs_coverage, repo_root)
    write_markdown(packet, args.out)
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
