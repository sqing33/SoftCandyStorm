#!/usr/bin/env python3
"""Run current Runtime capture and Gym bridge smoke evidence.

This smoke is intentionally technical evidence only. It proves that the Python
Gym wrapper can talk to the Rust `game_harness gym-bridge` process and that the
Bevy Runtime can produce a validated local demo-input capture on this machine.
It does not replace human playtest, broad hardware profiling, or release gates.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


REQUIRED_CHECKS = {
    "gym_bridge_smoke",
    "gym_observation_shape",
    "gym_action_space",
    "runtime_capture_command",
    "runtime_performance_capture",
    "runtime_privacy_defaults",
}


REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = REPO_ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from validate_runtime_performance_capture import build_report as build_runtime_capture_report  # noqa: E402


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(path)


def trim_stream(value: str, limit: int = 4000) -> str:
    if len(value) <= limit:
        return value
    return value[-limit:]


def run_command(repo_root: Path, argv: list[str], expected_returncode: int) -> dict[str, Any]:
    result = subprocess.run(
        argv,
        cwd=repo_root,
        check=False,
        text=True,
        capture_output=True,
    )
    return {
        "argv": argv,
        "expected_returncode": expected_returncode,
        "returncode": result.returncode,
        "stdout_tail": trim_stream(result.stdout),
        "stderr_tail": trim_stream(result.stderr),
    }


def add_check(checks: list[dict[str, Any]], check_id: str, passed: bool, summary: str) -> None:
    checks.append({"id": check_id, "status": "pass" if passed else "fail", "summary": summary})


def parse_gym_smoke_output(command: dict[str, Any]) -> dict[str, Any]:
    stdout = str(command.get("stdout_tail", "")).strip()
    if not stdout:
        return {}
    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    if not lines:
        return {}
    return json.loads(lines[-1])


def summarize_runtime_validation(report: dict[str, Any]) -> dict[str, Any]:
    summary = report.get("summary", {})
    frame_metrics = summary.get("frame_metrics", {}) if isinstance(summary, dict) else {}
    samples = summary.get("samples", {}) if isinstance(summary, dict) else {}
    final_metrics = summary.get("final_metrics", {}) if isinstance(summary, dict) else {}
    privacy = summary.get("privacy", {}) if isinstance(summary, dict) else {}
    return {
        "decision": report.get("decision"),
        "input_mode": summary.get("input_mode") if isinstance(summary, dict) else None,
        "simulation_speed": summary.get("simulation_speed") if isinstance(summary, dict) else None,
        "average_fps": frame_metrics.get("average_fps"),
        "worst_frame_fps": frame_metrics.get("worst_frame_fps"),
        "slow_frame_count_30fps": frame_metrics.get("slow_frame_count_30fps"),
        "frame_count": frame_metrics.get("frame_count"),
        "sample_count": samples.get("sample_count"),
        "max_visible_enemies": samples.get("max_visible_enemies"),
        "max_visible_projectiles": samples.get("max_visible_projectiles"),
        "terminal": final_metrics.get("terminal"),
        "duration_seconds": final_metrics.get("duration_seconds"),
        "target_duration_seconds": final_metrics.get("target_duration_seconds"),
        "local_capture_only": privacy.get("local_capture_only"),
        "upload_transport": privacy.get("upload_transport"),
    }


def finalize_report(report: dict[str, Any]) -> dict[str, Any]:
    errors = list(report.get("errors", []))
    commands = report.get("commands", [])
    if not isinstance(commands, list):
        errors.append("commands must be a list")
        commands = []
    for command in commands:
        if not isinstance(command, dict):
            errors.append("commands must contain objects")
            continue
        if command.get("returncode") != command.get("expected_returncode"):
            rendered = " ".join(str(part) for part in command.get("argv", []))
            errors.append(
                f"command returncode mismatch for {rendered}: "
                f"expected {command.get('expected_returncode')}, got {command.get('returncode')}"
            )

    check_statuses = {
        str(check.get("id")): check.get("status")
        for check in report.get("checks", [])
        if isinstance(check, dict) and isinstance(check.get("id"), str)
    }
    for check_id in sorted(REQUIRED_CHECKS):
        if check_statuses.get(check_id) != "pass":
            errors.append(f"{check_id}: required smoke check did not pass")

    failed_checks = [check_id for check_id, status in check_statuses.items() if status != "pass"]
    report["errors"] = errors
    report["decision"] = (
        "runtime_gym_current_smoke_valid"
        if not errors and not failed_checks
        else "runtime_gym_current_smoke_invalid"
    )
    return report


def build_smoke_report(
    repo_root: Path,
    runtime_capture: Path,
    runtime_validation_report: Path,
    *,
    seconds: float,
    seed: int,
    simulation_speed: float,
    capture_interval: float,
) -> dict[str, Any]:
    gym_command = run_command(
        repo_root,
        [sys.executable, "python/gym_env/smoke_test.py"],
        0,
    )
    gym_payload: dict[str, Any] = {}
    gym_errors: list[str] = []
    try:
        gym_payload = parse_gym_smoke_output(gym_command)
    except (json.JSONDecodeError, TypeError, ValueError) as error:
        gym_errors.append(f"gym smoke output is not valid JSON: {error}")

    runtime_command = run_command(
        repo_root,
        [
            "cargo",
            "run",
            "-p",
            "game_runtime",
            "--",
            "--content-dir",
            "content/base_demo",
            "--seed",
            str(seed),
            "--seconds",
            str(seconds),
            "--demo-input",
            "--simulation-speed",
            str(simulation_speed),
            "--playtest-report",
            str(runtime_capture),
            "--player-skill",
            "demo-bot",
            "--capture-interval",
            str(capture_interval),
            "--auto-exit-after-report",
        ],
        0,
    )

    runtime_validation: dict[str, Any] = {
        "decision": "runtime_performance_capture_not_run",
        "summary": {},
        "errors": [],
        "warnings": [],
    }
    if runtime_command["returncode"] == 0 and runtime_capture.exists():
        runtime_validation = build_runtime_capture_report(runtime_capture)
        write_json(runtime_validation_report, runtime_validation)

    runtime_summary = summarize_runtime_validation(runtime_validation)
    checks: list[dict[str, Any]] = []
    add_check(
        checks,
        "gym_bridge_smoke",
        gym_command["returncode"] == 0 and gym_payload.get("status") == "ok" and not gym_errors,
        "Python Gym wrapper completed the smoke episode through game_harness gym-bridge.",
    )
    add_check(
        checks,
        "gym_observation_shape",
        isinstance(gym_payload.get("observation_len"), int) and gym_payload.get("observation_len", 0) > 0,
        "Gym smoke reported a positive observation length.",
    )
    add_check(
        checks,
        "gym_action_space",
        gym_payload.get("action_count") == 9,
        "Gym smoke reported the expected 9-direction discrete action space.",
    )
    add_check(
        checks,
        "runtime_capture_command",
        runtime_command["returncode"] == 0 and runtime_capture.exists(),
        "game_runtime demo-input capture command completed and wrote the capture JSON.",
    )
    add_check(
        checks,
        "runtime_performance_capture",
        runtime_validation.get("decision") == "runtime_performance_capture_valid",
        "Runtime capture passed local performance, sample, terminal, and entity-count validation.",
    )
    add_check(
        checks,
        "runtime_privacy_defaults",
        runtime_summary.get("local_capture_only") is True and runtime_summary.get("upload_transport") == "not_implemented",
        "Runtime capture kept local-only privacy defaults with no upload transport enabled.",
    )

    return finalize_report(
        {
            "report_version": 1,
            "decision": "runtime_gym_current_smoke_pending",
            "repo_root": str(repo_root),
            "artifacts": {
                "runtime_capture": repo_relative(repo_root, runtime_capture),
                "runtime_validation_report": repo_relative(repo_root, runtime_validation_report),
            },
            "gym_smoke": gym_payload,
            "runtime_validation": runtime_summary,
            "commands": [gym_command, runtime_command],
            "checks": checks,
            "errors": gym_errors,
            "limitations": [
                "This smoke is one local technical run; it is not a human playtest.",
                "Runtime frame metrics come from Bevy frame deltas and do not replace GPU profiling or memory growth checks.",
                "The Gym bridge smoke is a short wrapper/shape check, not RL policy acceptance or high-pressure training evidence.",
                "Manual readability, fun, device input review, platform privacy review, and release gates remain separate blockers.",
            ],
        }
    )


def write_markdown(report: dict[str, Any], path: Path) -> None:
    gym = report.get("gym_smoke", {})
    runtime = report.get("runtime_validation", {})
    lines = [
        "# Runtime / Gym Current Smoke",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Runtime capture: `{report['artifacts']['runtime_capture']}`",
        f"- Runtime validation: `{report['artifacts']['runtime_validation_report']}`",
        f"- Gym status: `{gym.get('status')}`",
        f"- Gym steps: `{gym.get('steps')}`",
        f"- Gym observation length: `{gym.get('observation_len')}`",
        f"- Gym action count: `{gym.get('action_count')}`",
        f"- Runtime terminal: `{runtime.get('terminal')}`",
        f"- Runtime duration: `{runtime.get('duration_seconds')}` / `{runtime.get('target_duration_seconds')}` seconds",
        f"- Runtime average FPS: `{runtime.get('average_fps')}`",
        f"- Runtime worst frame FPS: `{runtime.get('worst_frame_fps')}`",
        f"- Runtime samples: `{runtime.get('sample_count')}`",
        f"- Runtime max enemies/projectiles: `{runtime.get('max_visible_enemies')}` / `{runtime.get('max_visible_projectiles')}`",
        f"- Runtime privacy: local_capture_only `{runtime.get('local_capture_only')}`, upload `{runtime.get('upload_transport')}`",
        "",
        "## Checks",
        "",
        "| Check | Status | Summary |",
        "|---|---|---|",
    ]
    for check in report["checks"]:
        lines.append(f"| `{check['id']}` | `{check['status']}` | {check['summary']} |")

    lines.extend(["", "## Commands", "", "| Command | Return | Expected |", "|---|---:|---:|"])
    for command in report["commands"]:
        rendered = " ".join(str(part) for part in command["argv"])
        lines.append(f"| `{rendered}` | {command['returncode']} | {command['expected_returncode']} |")

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
    parser = argparse.ArgumentParser(description="Run current Runtime capture and Gym bridge smoke evidence.")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument(
        "--runtime-capture",
        type=Path,
        required=True,
        help="Runtime --playtest-report JSON path",
    )
    parser.add_argument(
        "--runtime-validation-report",
        type=Path,
        default=None,
        help="Write Runtime capture validation JSON report",
    )
    parser.add_argument("--report", type=Path, required=True, help="Write combined JSON smoke report")
    parser.add_argument("--markdown", type=Path, required=True, help="Write combined Markdown summary")
    parser.add_argument("--seconds", type=float, default=120.0, help="Runtime demo target seconds")
    parser.add_argument("--seed", type=int, default=12345, help="Runtime demo seed")
    parser.add_argument("--simulation-speed", type=float, default=30.0, help="Runtime simulation speed")
    parser.add_argument("--capture-interval", type=float, default=5.0, help="Runtime capture interval seconds")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    runtime_capture = args.runtime_capture if args.runtime_capture.is_absolute() else repo_root / args.runtime_capture
    runtime_validation_report = (
        args.runtime_validation_report
        if args.runtime_validation_report is not None
        else args.report.parent / "runtime_performance_capture.json"
    )
    if not runtime_validation_report.is_absolute():
        runtime_validation_report = repo_root / runtime_validation_report
    report_path = args.report if args.report.is_absolute() else repo_root / args.report
    markdown_path = args.markdown if args.markdown.is_absolute() else repo_root / args.markdown

    # Avoid writing Python bytecode to user-level cache paths in sandboxed runs.
    os.environ.setdefault("PYTHONPYCACHEPREFIX", "/private/tmp/soft-candy-pycache")

    report = build_smoke_report(
        repo_root,
        runtime_capture,
        runtime_validation_report,
        seconds=args.seconds,
        seed=args.seed,
        simulation_speed=args.simulation_speed,
        capture_interval=args.capture_interval,
    )
    write_json(report_path, report)
    write_markdown(report, markdown_path)
    return 0 if report["decision"] == "runtime_gym_current_smoke_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
