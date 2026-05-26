#!/usr/bin/env python3
"""Diagnose whether this macOS session can launch newly built Mach-O binaries.

The long-running goal depends on Rust Harness and Runtime executables. This
probe keeps the local execution-policy blocker auditable without relying on a
particular crate: it compiles a tiny C program, tries to execute it with a short
timeout, and captures code-signing, Gatekeeper, Developer Mode, and policy-log
signals that explain the result.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any


HELLO_SOURCE = '#include <stdio.h>\nint main(){ puts("softcandy-local-binary-ok"); return 0; }\n'
POLICY_LOG_PREDICATE = (
    'process == "syspolicyd" OR process == "amfid" '
    'OR eventMessage CONTAINS[c] "Security policy" '
    'OR eventMessage CONTAINS[c] "CMS blob" '
    'OR eventMessage CONTAINS[c] "provenance" '
    'OR eventMessage CONTAINS[c] "Gatekeeper" '
    'OR eventMessage CONTAINS[c] "softcandy"'
)


def clean_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    cleaned: list[str] = []
    for char in value:
        codepoint = ord(char)
        if char in "\n\r\t" or codepoint >= 32:
            cleaned.append(char)
        else:
            cleaned.append(f"\\x{codepoint:02x}")
    return "".join(cleaned)


def run_command(cmd: list[str], timeout: float, cwd: Path | None = None) -> dict[str, Any]:
    started_at = time.monotonic()
    try:
        completed = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd is not None else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,
            timeout=timeout,
        )
        return {
            "command": cmd,
            "returncode": completed.returncode,
            "timed_out": False,
            "elapsed_seconds": round(time.monotonic() - started_at, 3),
            "stdout": clean_text(completed.stdout),
            "stderr": clean_text(completed.stderr),
        }
    except subprocess.TimeoutExpired as error:
        return {
            "command": cmd,
            "returncode": None,
            "timed_out": True,
            "elapsed_seconds": round(time.monotonic() - started_at, 3),
            "stdout": clean_text(error.stdout),
            "stderr": clean_text(error.stderr),
        }
    except OSError as error:
        return {
            "command": cmd,
            "returncode": None,
            "timed_out": False,
            "elapsed_seconds": round(time.monotonic() - started_at, 3),
            "stdout": "",
            "stderr": str(error),
        }


def run_policy_log_probe(binary: Path, timeout: float) -> dict[str, Any]:
    log_binary = Path("/usr/bin/log")
    if not log_binary.exists():
        return {"available": False, "lines": [], "error": "/usr/bin/log not found"}

    log_cmd = [
        str(log_binary),
        "stream",
        "--style",
        "compact",
        "--predicate",
        POLICY_LOG_PREDICATE,
    ]
    log_process = subprocess.Popen(log_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        time.sleep(0.75)
        run_result = run_command([str(binary)], timeout=timeout)
        time.sleep(0.5)
        log_process.terminate()
        try:
            output, _ = log_process.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            log_process.kill()
            output, _ = log_process.communicate(timeout=2)
    finally:
        if log_process.poll() is None:
            log_process.kill()

    lines = clean_text(output).splitlines()
    return {
        "available": True,
        "command": log_cmd,
        "trigger_run": run_result,
        "line_count": len(lines),
        "lines": lines[:120],
    }


def analyze_signals(report: dict[str, Any]) -> dict[str, bool]:
    serialized = json.dumps(report, ensure_ascii=False)
    return {
        "system_binary_runs": report["checks"]["system_echo"]["returncode"] == 0
        and not report["checks"]["system_echo"]["timed_out"],
        "hello_compiled": report["checks"]["cc_compile"]["returncode"] == 0,
        "hello_runs": report["checks"]["hello_run"]["returncode"] == 0
        and "softcandy-local-binary-ok" in report["checks"]["hello_run"]["stdout"],
        "hello_timed_out": bool(report["checks"]["hello_run"]["timed_out"]),
        "developer_mode_disabled": "disabled" in report["checks"]["developer_mode"]["stdout"].lower(),
        "spctl_rejected": "rejected" in report["checks"]["spctl_assess"]["stderr"].lower()
        or "rejected" in report["checks"]["spctl_assess"]["stdout"].lower(),
        "provenance_xattr_present": "com.apple.provenance" in report["checks"]["xattr"]["stdout"],
        "amfi_no_cms_blob": "has no CMS blob" in serialized,
        "security_policy_would_not_allow": "Security policy would not allow process" in serialized,
    }


def build_report(repo_root: Path, timeout: float) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="softcandy_binary_launch_") as tmp:
        tmp_dir = Path(tmp)
        source = tmp_dir / "hello.c"
        binary = tmp_dir / "softcandy_hello"
        source.write_text(HELLO_SOURCE, encoding="utf-8")

        cc = shutil.which("cc") or "/usr/bin/cc"
        checks: dict[str, Any] = {
            "system_echo": run_command(["/bin/echo", "system-binary-ok"], timeout=timeout),
            "developer_mode": run_command(["/usr/sbin/DevToolsSecurity", "-status"], timeout=timeout),
            "spctl_status": run_command(["/usr/sbin/spctl", "--status"], timeout=timeout),
            "cc_compile": run_command([cc, str(source), "-o", str(binary)], timeout=max(timeout, 20)),
        }

        if binary.exists():
            checks.update(
                {
                    "file": run_command(["/usr/bin/file", str(binary)], timeout=timeout),
                    "xattr": run_command(["/usr/bin/xattr", "-lr", str(binary)], timeout=timeout),
                    "codesign": run_command(
                        ["/usr/bin/codesign", "-dv", "--verbose=4", str(binary)],
                        timeout=timeout,
                    ),
                    "spctl_assess": run_command(
                        ["/usr/sbin/spctl", "-a", "-vvv", str(binary)],
                        timeout=timeout,
                    ),
                    "hello_run": run_command([str(binary)], timeout=timeout),
                }
            )
            policy_log = run_policy_log_probe(binary, timeout=timeout)
        else:
            missing = {
                "command": [str(binary)],
                "returncode": None,
                "timed_out": False,
                "elapsed_seconds": 0,
                "stdout": "",
                "stderr": "compiled binary was not created",
            }
            checks.update(
                {
                    "file": missing,
                    "xattr": missing,
                    "codesign": missing,
                    "spctl_assess": missing,
                    "hello_run": missing,
                }
            )
            policy_log = {"available": False, "lines": [], "error": "compiled binary was not created"}

        report: dict[str, Any] = {
            "report_version": 1,
            "repo_root": str(repo_root),
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "environment": {
                "platform": run_command(["/usr/bin/uname", "-a"], timeout=timeout),
                "macos": run_command(["/usr/bin/sw_vers"], timeout=timeout),
                "arch": run_command(["/usr/bin/arch"], timeout=timeout),
                "cwd": str(repo_root),
                "path": os.environ.get("PATH", ""),
            },
            "checks": checks,
            "policy_log": policy_log,
            "limitations": [
                "This diagnostic proves only the current local session's ability to launch a newly compiled Mach-O binary.",
                "It does not validate GameCore, Harness, Runtime, Gym, replay semantics, or gameplay balance.",
                "A blocked result should prevent interpreting Rust Harness, Runtime, or Gym timeouts as game logic failures.",
            ],
        }
        signals = analyze_signals(report)
        if signals["hello_runs"]:
            decision = "local_binary_launch_ok"
        elif checks["cc_compile"]["returncode"] != 0:
            decision = "local_binary_launch_probe_failed"
        else:
            decision = "local_binary_launch_blocked"
        report["decision"] = decision
        report["signals"] = signals
        report["next_actions"] = build_next_actions(decision, signals)
        return report


def build_next_actions(decision: str, signals: dict[str, bool]) -> list[str]:
    if decision == "local_binary_launch_ok":
        return [
            "Run target/debug/game_harness --help with the same timeout guard.",
            "If game_harness launches, rerun cargo test --workspace and the blocked Harness/Gym reports.",
        ]

    actions = [
        "Do not treat Harness, Runtime, or Gym timeouts as game logic failures until this diagnostic returns local_binary_launch_ok.",
        "Run the same diagnostic from a trusted developer host or after enabling Developer Mode for the tool that launches local binaries.",
        "If available, sign local test binaries with a trusted code-signing identity that produces a CMS signature, then rerun this diagnostic.",
    ]
    if signals.get("developer_mode_disabled"):
        actions.append("Developer Mode is disabled in this session; enabling it is likely required before local ad-hoc binaries can launch.")
    if signals.get("security_policy_would_not_allow") or signals.get("amfi_no_cms_blob"):
        actions.append("Policy logs show AppleSystemPolicy or AMFI blocking the compiled hello binary before main executes.")
    return actions


def write_markdown(report: dict[str, Any], path: Path) -> None:
    signals = report["signals"]
    checks = report["checks"]
    lines = [
        "# Local Binary Launch Diagnostic",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Repo root: `{report['repo_root']}`",
        f"- System binary runs: `{signals['system_binary_runs']}`",
        f"- Hello compiled: `{signals['hello_compiled']}`",
        f"- Hello runs: `{signals['hello_runs']}`",
        f"- Hello timed out: `{signals['hello_timed_out']}`",
        f"- Developer Mode disabled: `{signals['developer_mode_disabled']}`",
        f"- `spctl` rejected hello: `{signals['spctl_rejected']}`",
        f"- `com.apple.provenance` present: `{signals['provenance_xattr_present']}`",
        f"- AMFI no CMS blob signal: `{signals['amfi_no_cms_blob']}`",
        f"- Security policy denial signal: `{signals['security_policy_would_not_allow']}`",
        "",
        "## Key Command Output",
        "",
        f"- Developer Mode: `{checks['developer_mode']['stdout'].strip() or checks['developer_mode']['stderr'].strip()}`",
        f"- `spctl --status`: `{checks['spctl_status']['stdout'].strip() or checks['spctl_status']['stderr'].strip()}`",
        f"- Hello run elapsed: `{checks['hello_run']['elapsed_seconds']}` seconds",
        f"- Hello run stdout: `{checks['hello_run']['stdout'].strip()}`",
        f"- Hello run stderr: `{checks['hello_run']['stderr'].strip()}`",
        "",
        "## Policy Log Signals",
        "",
    ]
    policy_lines = report["policy_log"].get("lines", [])
    interesting_patterns = [
        "Security policy",
        "CMS blob",
        "AppleSystemPolicy",
        "AppleMobileFileIntegrity",
        "AMFI",
        "Unable to apply provenance",
    ]
    interesting_lines = [
        line
        for line in policy_lines
        if any(pattern in line for pattern in interesting_patterns)
    ]
    displayed_policy_lines = interesting_lines[:40] if interesting_lines else policy_lines[:40]
    if displayed_policy_lines:
        lines.extend(f"- `{line}`" for line in displayed_policy_lines)
    else:
        lines.append("- None captured")

    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {item}" for item in report["next_actions"])
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose local Mach-O binary launch policy.")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON diagnostic report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown diagnostic summary")
    parser.add_argument("--timeout", type=float, default=5.0, help="Per-command timeout in seconds")
    args = parser.parse_args()

    report = build_report(args.repo_root.resolve(), args.timeout)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "local_binary_launch_ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
