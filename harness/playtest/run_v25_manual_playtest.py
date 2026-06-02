#!/usr/bin/env python3
"""Launch manual Runtime playtest runs for demo buildcraft repair v25.

This helper intentionally launches human-playable Runtime sessions only. It
does not add demo input, simulation speed, auto-exit, or any acceptance logic.
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]

CANDIDATE_ID = "2026-06-02_demo_buildcraft_repair_v25_full_pack"
CONTENT_HASH = "fnv1a64:aab110776109609d"
CONTENT_DIR = Path("harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack")
DEFAULT_SECONDS = 600
DEFAULT_CAPTURE_INTERVAL = 2
REPORT_PREFIX = "harness/telemetry/local/v25_manual_playtest"


@dataclass(frozen=True)
class PlaytestRun:
    run_id: str
    skill: str
    seed: int
    intent: str

    @property
    def report_path(self) -> Path:
        return Path(f"{REPORT_PREFIX}_{self.run_id}.json")


RUNS: tuple[PlaytestRun, ...] = (
    PlaytestRun("new_001", "new", 25001, "不看说明直接开始"),
    PlaytestRun("new_002", "new", 25002, "尝试贪 XP"),
    PlaytestRun("new_003", "new", 25003, "保守绕圈"),
    PlaytestRun("skilled_001", "skilled", 25011, "主动拉怪收 XP"),
    PlaytestRun("skilled_002", "skilled", 25012, "主动挑战 Boss"),
    PlaytestRun("skilled_003", "skilled", 25013, "高压波次存活"),
    PlaytestRun("build_001", "build", 25021, "远程投射物优先"),
    PlaytestRun("build_002", "build", 25022, "防御 / 移速优先"),
    PlaytestRun("build_003", "build", 25023, "控制 / 范围优先"),
)

RUN_BY_ID = {run.run_id: run for run in RUNS}

FORBIDDEN_MANUAL_FLAGS = {
    "--demo-input",
    "--simulation-speed",
    "--auto-exit-after-report",
}


def build_runtime_command(
    run: PlaytestRun,
    *,
    seconds: int = DEFAULT_SECONDS,
    capture_interval: int = DEFAULT_CAPTURE_INTERVAL,
    release: bool = False,
) -> list[str]:
    command = ["cargo", "run"]
    if release:
        command.append("--release")
    command.extend(
        [
            "-p",
            "game_runtime",
            "--",
            "--content-dir",
            str(CONTENT_DIR),
            "--seed",
            str(run.seed),
            "--seconds",
            str(seconds),
            "--player-skill",
            run.skill,
            "--playtest-report",
            str(run.report_path),
            "--capture-interval",
            str(capture_interval),
        ]
    )
    return command


def shell_quote(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def validate_manual_command(command: list[str]) -> None:
    forbidden = sorted(flag for flag in FORBIDDEN_MANUAL_FLAGS if flag in command)
    if forbidden:
        raise ValueError(f"manual playtest command must not include automation flags: {', '.join(forbidden)}")


def list_runs() -> str:
    lines = [
        f"Candidate: {CANDIDATE_ID}",
        f"Content hash: {CONTENT_HASH}",
        "",
        "Run id | Skill | Seed | Intent | Report",
        "---|---|---:|---|---",
    ]
    for run in RUNS:
        lines.append(f"{run.run_id} | {run.skill} | {run.seed} | {run.intent} | {run.report_path}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch a v25 manual playtest Runtime run.")
    parser.add_argument("run_id", nargs="?", choices=sorted(RUN_BY_ID), help="Required run id unless --list is used")
    parser.add_argument("--list", action="store_true", help="List the 9 required manual runs")
    parser.add_argument("--dry-run", action="store_true", help="Print the command without launching Runtime")
    parser.add_argument("--release", action="store_true", help="Use cargo run --release")
    parser.add_argument("--seconds", type=int, default=DEFAULT_SECONDS, help="Target run duration in seconds")
    parser.add_argument(
        "--capture-interval",
        type=int,
        default=DEFAULT_CAPTURE_INTERVAL,
        help="Runtime playtest capture interval in seconds",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.list:
        print(list_runs())
        return 0
    if args.run_id is None:
        raise SystemExit("run_id is required unless --list is used")
    if args.seconds <= 0:
        raise SystemExit("--seconds must be positive")
    if args.capture_interval <= 0:
        raise SystemExit("--capture-interval must be positive")

    run = RUN_BY_ID[args.run_id]
    command = build_runtime_command(
        run,
        seconds=args.seconds,
        capture_interval=args.capture_interval,
        release=args.release,
    )
    validate_manual_command(command)
    run.report_path.parent.mkdir(parents=True, exist_ok=True)

    print(shell_quote(command))
    if args.dry_run:
        return 0
    completed = subprocess.run(command, cwd=REPO_ROOT, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
