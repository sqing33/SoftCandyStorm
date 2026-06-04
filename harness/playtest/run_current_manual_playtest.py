#!/usr/bin/env python3
"""Launch manual Runtime playtest runs for the current playable candidate."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from current_candidate import (
    CANDIDATE_ID,
    CANDIDATE_LABEL,
    CONTENT_HASH,
    DEFAULT_CAPTURE_INTERVAL,
    DEFAULT_SECONDS,
    MANUAL_PLAYTEST_RUNS,
    ManualPlaytestRun,
    build_runtime_command,
    shell_quote,
    validate_human_runtime_command,
)


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
RUN_BY_ID = {run.run_id: run for run in MANUAL_PLAYTEST_RUNS}


def build_manual_playtest_command(
    run: ManualPlaytestRun,
    *,
    seconds: int = DEFAULT_SECONDS,
    capture_interval: int = DEFAULT_CAPTURE_INTERVAL,
    release: bool = False,
) -> list[str]:
    return build_runtime_command(
        character_id=run.character_id,
        map_id=run.map_id,
        seed=run.seed,
        player_skill=run.skill,
        report_path=run.report_path,
        seconds=seconds,
        capture_interval=capture_interval,
        release=release,
    )


def validate_manual_playtest_command(command: list[str]) -> None:
    validate_human_runtime_command(command, label="manual playtest")


def report_exists(repo_root: Path, run: ManualPlaytestRun) -> bool:
    return (repo_root / run.report_path).exists()


def first_missing_run(repo_root: Path) -> ManualPlaytestRun | None:
    for run in MANUAL_PLAYTEST_RUNS:
        if not report_exists(repo_root, run):
            return run
    return None


def list_runs(repo_root: Path | None = None) -> str:
    lines = [
        f"Candidate: {CANDIDATE_ID}",
        f"Content hash: {CONTENT_HASH}",
        "Purpose: human manual playtest matrix, candidate-only, not acceptance by itself",
        "",
    ]
    if repo_root is None:
        lines.extend(["Run id | Skill | Character | Map | Seed | Intent | Report", "---|---|---|---|---:|---|---"])
    else:
        lines.extend(
            [
                "Run id | Skill | Character | Map | Seed | Intent | Report | Status",
                "---|---|---|---|---:|---|---|---",
            ]
        )
    for run in MANUAL_PLAYTEST_RUNS:
        status = ""
        if repo_root is not None:
            status = " | done" if report_exists(repo_root, run) else " | missing"
        lines.append(
            f"{run.run_id} | {run.skill} | {run.character_id} | {run.map_id} | "
            f"{run.seed} | {run.intent} | {run.report_path}{status}"
        )
    return "\n".join(lines)


def status_text(repo_root: Path) -> str:
    existing_count = sum(1 for run in MANUAL_PLAYTEST_RUNS if report_exists(repo_root, run))
    next_run = first_missing_run(repo_root)
    lines = [
        f"Candidate: {CANDIDATE_ID}",
        f"Content hash: {CONTENT_HASH}",
        f"Reports: {existing_count} / {len(MANUAL_PLAYTEST_RUNS)}",
    ]
    if next_run is None:
        lines.append("Next run: none, all local reports exist")
        lines.append("Next check: run check_current_manual_playtest_status.py and strict manual review validation")
    else:
        lines.append(f"Next run: {next_run.run_id} ({next_run.skill}, seed {next_run.seed})")
        lines.append(f"Character: {next_run.character_id}")
        lines.append(f"Map: {next_run.map_id}")
        lines.append(f"Intent: {next_run.intent}")
        lines.append(f"Report: {next_run.report_path}")
        lines.append("Launch: python3 harness/playtest/run_current_manual_playtest.py --next")
    return "\n".join(lines)


def run_manual_playtest(command: list[str], *, repo_root: Path) -> int:
    completed = subprocess.run(command, cwd=repo_root, check=False)
    return completed.returncode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=f"Launch a {CANDIDATE_LABEL} manual playtest Runtime run.")
    parser.add_argument(
        "run_id",
        nargs="?",
        choices=sorted(RUN_BY_ID),
        help="Required run id unless --list, --status, or --next is used",
    )
    parser.add_argument("--list", action="store_true", help="List the required manual playtest runs")
    parser.add_argument("--status", action="store_true", help="Print local report progress and the next missing run")
    parser.add_argument("--next", action="store_true", help="Launch the first run whose local report is missing")
    parser.add_argument("--dry-run", action="store_true", help="Print the command without launching Runtime")
    parser.add_argument("--release", action="store_true", help="Use cargo run --release")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT, help=argparse.SUPPRESS)
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
    repo_root = args.repo_root
    if args.list:
        print(list_runs(repo_root))
        return 0
    if args.status:
        print(status_text(repo_root))
        return 0
    if args.next and args.run_id is not None:
        raise SystemExit("run_id cannot be combined with --next")
    if args.next:
        run = first_missing_run(repo_root)
        if run is None:
            print(f"All {len(MANUAL_PLAYTEST_RUNS)} local {CANDIDATE_LABEL} manual playtest reports already exist.")
            print("Run check_current_manual_playtest_status.py before strict manual review validation.")
            return 0
    elif args.run_id is None:
        raise SystemExit("run_id is required unless --list, --status, or --next is used")
    else:
        run = RUN_BY_ID[args.run_id]

    if args.seconds <= 0:
        raise SystemExit("--seconds must be positive")
    if args.capture_interval <= 0:
        raise SystemExit("--capture-interval must be positive")

    command = build_manual_playtest_command(
        run,
        seconds=args.seconds,
        capture_interval=args.capture_interval,
        release=args.release,
    )
    validate_manual_playtest_command(command)
    (repo_root / run.report_path).parent.mkdir(parents=True, exist_ok=True)

    print(shell_quote(command))
    print(f"Candidate-only manual playtest for {CANDIDATE_LABEL}; this does not approve or promote content.")
    if args.dry_run:
        return 0
    return run_manual_playtest(command, repo_root=repo_root)


if __name__ == "__main__":
    raise SystemExit(main())
