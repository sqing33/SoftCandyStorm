#!/usr/bin/env python3
"""Run game_runtime and validate local resource usage.

The probe executes a Runtime command, records child-process max RSS via
`resource.getrusage`, then validates the produced `--playtest-report` capture
with the existing Runtime performance validator. It is single-machine evidence
only and does not replace GPU profiling, broad hardware coverage, or manual
playtest review.
"""

from __future__ import annotations

import argparse
import json
import resource
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_runtime_performance_capture import build_report as build_performance_report  # noqa: E402


DEFAULT_MAX_RSS_MIB = 2048.0


def max_rss_bytes_from_usage(usage: resource.struct_rusage) -> int:
    value = int(usage.ru_maxrss)
    if sys.platform == "darwin":
        return value
    return value * 1024


def mib(value: int) -> float:
    return value / (1024.0 * 1024.0)


def command_display(command: list[str]) -> str:
    return " ".join(command)


def build_report(
    *,
    command: list[str],
    capture_path: Path,
    profile: str,
    max_rss_mib: float,
    cwd: Path,
) -> dict[str, Any]:
    started_at = time.time()
    previous_capture_mtime_ns = capture_path.stat().st_mtime_ns if capture_path.exists() else None
    before_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    completed = subprocess.run(command, cwd=cwd, check=False, text=True, capture_output=True)
    wall_seconds = time.time() - started_at
    after_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    max_rss_bytes = max_rss_bytes_from_usage(after_usage)
    before_rss_bytes = max_rss_bytes_from_usage(before_usage)

    errors: list[str] = []
    warnings: list[str] = []
    if completed.returncode != 0:
        errors.append(f"runtime command exited with code {completed.returncode}")
    if not capture_path.exists():
        errors.append(f"capture path does not exist: {capture_path}")
        capture_mtime_ns = None
    else:
        capture_mtime_ns = capture_path.stat().st_mtime_ns
        if previous_capture_mtime_ns is not None and capture_mtime_ns <= previous_capture_mtime_ns:
            errors.append("capture path was not refreshed by the runtime command")

    performance_report: dict[str, Any] | None = None
    if capture_path.exists():
        performance_report = build_performance_report(capture_path, profile=profile)
        if performance_report.get("decision") != "runtime_performance_capture_valid":
            errors.append("runtime performance capture validation did not pass")
    else:
        performance_report = None

    if max_rss_mib <= 0:
        errors.append("max_rss_mib threshold must be positive")
    if mib(max_rss_bytes) > max_rss_mib:
        errors.append(f"max_rss_mib: observed {mib(max_rss_bytes):.2f} exceeds {max_rss_mib:.2f}")
    if max_rss_bytes < before_rss_bytes:
        warnings.append("resource.ru_maxrss decreased unexpectedly between before/after samples")

    decision = "runtime_resource_probe_valid" if not errors else "runtime_resource_probe_invalid"
    stderr_tail = completed.stderr.strip().splitlines()[-20:]
    stdout_tail = completed.stdout.strip().splitlines()[-20:]
    return {
        "report_version": 1,
        "decision": decision,
        "command": command,
        "command_display": command_display(command),
        "cwd": str(cwd),
        "capture_path": str(capture_path),
        "capture_refreshed": capture_path.exists()
        and (previous_capture_mtime_ns is None or capture_mtime_ns > previous_capture_mtime_ns),
        "profile": profile,
        "returncode": completed.returncode,
        "wall_seconds": wall_seconds,
        "resource": {
            "max_rss_bytes": max_rss_bytes,
            "max_rss_mib": mib(max_rss_bytes),
            "max_rss_threshold_mib": max_rss_mib,
            "before_max_rss_bytes": before_rss_bytes,
        },
        "performance_decision": performance_report.get("decision") if performance_report else None,
        "performance_summary": performance_report.get("summary") if performance_report else None,
        "errors": errors,
        "warnings": warnings,
        "stdout_tail": stdout_tail,
        "stderr_tail": stderr_tail,
        "limitations": [
            "This probe measures one local child process via resource.getrusage only.",
            "ru_maxrss is a peak resident set approximation and is not a heap profile or GPU memory measurement.",
            "The probe does not replace Steam Deck, broad hardware, GPU profiling, leak analysis, or human readability review.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    performance = report.get("performance_summary") or {}
    frame = performance.get("frame_metrics") if isinstance(performance, dict) else {}
    final = performance.get("final_metrics") if isinstance(performance, dict) else {}
    samples = performance.get("samples") if isinstance(performance, dict) else {}
    lines = [
        "# Runtime Resource Probe",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Command: `{report['command_display']}`",
        f"- Capture: `{report['capture_path']}`",
        f"- Profile: `{report['profile']}`",
        f"- Return code: `{report['returncode']}`",
        f"- Wall seconds: `{report['wall_seconds']:.2f}`",
        f"- Max RSS: `{report['resource']['max_rss_mib']:.2f}` MiB / `{report['resource']['max_rss_threshold_mib']:.2f}` MiB",
        f"- Performance decision: `{report['performance_decision']}`",
    ]
    if isinstance(frame, dict):
        lines.extend(
            [
                f"- Average FPS: `{float(frame.get('average_fps', 0.0)):.2f}`",
                f"- 30 FPS slow frame ratio: `{float(frame.get('slow_frame_ratio_30fps', 0.0)):.4f}`",
            ]
        )
    if isinstance(samples, dict):
        lines.append(f"- Samples: `{samples.get('sample_count', 0)}`")
    if isinstance(final, dict):
        lines.append(f"- Terminal: `{final.get('terminal', '-')}`")

    lines.extend(["", "## Errors", ""])
    if report["errors"]:
        lines.extend(f"- {item}" for item in report["errors"])
    else:
        lines.append("- None")

    lines.extend(["", "## Warnings", ""])
    if report["warnings"]:
        lines.extend(f"- {item}" for item in report["warnings"])
    else:
        lines.append("- None")

    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    if report["stderr_tail"]:
        lines.extend(["", "## Stderr Tail", ""])
        lines.extend(f"- `{line}`" for line in report["stderr_tail"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Runtime and capture resource probe evidence.")
    parser.add_argument("--binary", type=Path, default=Path("target/debug/game_runtime"))
    parser.add_argument("--capture", type=Path, required=True, help="Runtime --playtest-report path")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root / command cwd")
    parser.add_argument("--profile", choices=["smoke", "release-local"], default="smoke")
    parser.add_argument("--max-rss-mib", type=float, default=DEFAULT_MAX_RSS_MIB)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("runtime_args", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    runtime_args = args.runtime_args
    if runtime_args and runtime_args[0] == "--":
        runtime_args = runtime_args[1:]
    command = [str(args.binary)] + runtime_args
    report = build_report(
        command=command,
        capture_path=args.capture,
        profile=args.profile,
        max_rss_mib=args.max_rss_mib,
        cwd=args.repo_root,
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(report, args.markdown)
    return 0 if report["decision"] == "runtime_resource_probe_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
