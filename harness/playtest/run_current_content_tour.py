#!/usr/bin/env python3
"""Launch optional human content-tour Runtime runs for the current candidate."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from current_candidate import (
    CANDIDATE_ID,
    CANDIDATE_LABEL,
    CONTENT_HASH,
    CONTENT_TOUR_RUNS,
    DEFAULT_CAPTURE_INTERVAL,
    DEFAULT_SECONDS,
    ContentTourRun,
    build_runtime_command,
    shell_quote,
    validate_human_runtime_command,
)


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
RUN_BY_ID = {run.run_id: run for run in CONTENT_TOUR_RUNS}


def build_tour_command(
    run: ContentTourRun,
    *,
    seconds: int = DEFAULT_SECONDS,
    capture_interval: int = DEFAULT_CAPTURE_INTERVAL,
    release: bool = False,
) -> list[str]:
    return build_runtime_command(
        character_id=run.character_id,
        map_id=run.map_id,
        seed=run.seed,
        player_skill="tour",
        report_path=run.report_path,
        seconds=seconds,
        capture_interval=capture_interval,
        release=release,
    )


def validate_tour_command(command: list[str]) -> None:
    validate_human_runtime_command(command, label="content tour")


def report_exists(repo_root: Path, run: ContentTourRun) -> bool:
    return (repo_root / run.report_path).exists()


def first_missing_run(repo_root: Path) -> ContentTourRun | None:
    for run in CONTENT_TOUR_RUNS:
        if not report_exists(repo_root, run):
            return run
    return None


def list_runs(repo_root: Path | None = None) -> str:
    lines = [
        f"Candidate: {CANDIDATE_ID}",
        f"Content hash: {CONTENT_HASH}",
        "Purpose: optional content tour, not acceptance evidence",
        "",
    ]
    if repo_root is None:
        lines.extend(["Run id | Character | Map | Seed | Focus | Report", "---|---|---|---:|---|---"])
    else:
        lines.extend(["Run id | Character | Map | Seed | Focus | Report | Status", "---|---|---|---:|---|---|---"])
    for run in CONTENT_TOUR_RUNS:
        status = ""
        if repo_root is not None:
            status = " | done" if report_exists(repo_root, run) else " | missing"
        lines.append(
            f"{run.run_id} | {run.character_id} | {run.map_id} | {run.seed} | {run.focus} | {run.report_path}{status}"
        )
    return "\n".join(lines)


def status_text(repo_root: Path) -> str:
    existing_count = sum(1 for run in CONTENT_TOUR_RUNS if report_exists(repo_root, run))
    next_run = first_missing_run(repo_root)
    lines = [
        f"Candidate: {CANDIDATE_ID}",
        f"Content hash: {CONTENT_HASH}",
        "Purpose: optional content tour, not acceptance evidence",
        f"Reports: {existing_count} / {len(CONTENT_TOUR_RUNS)}",
    ]
    if next_run is None:
        lines.append("Next tour run: none, all local content-tour reports exist")
    else:
        lines.append(f"Next tour run: {next_run.run_id}")
        lines.append(f"Character: {next_run.character_id}")
        lines.append(f"Map: {next_run.map_id}")
        lines.append(f"Focus: {next_run.focus}")
        lines.append(f"Report: {next_run.report_path}")
        lines.append("Launch: python3 harness/playtest/run_current_content_tour.py --next")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=f"Launch an optional {CANDIDATE_LABEL} human content-tour Runtime run.")
    parser.add_argument(
        "run_id",
        nargs="?",
        choices=sorted(RUN_BY_ID),
        help="Required run id unless --list, --status, or --next is used",
    )
    parser.add_argument("--list", action="store_true", help="List optional content-tour runs")
    parser.add_argument("--status", action="store_true", help="Print local content-tour progress")
    parser.add_argument("--next", action="store_true", help="Launch the first tour run whose report is missing")
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
            print(f"All optional {CANDIDATE_LABEL} content-tour reports already exist.")
            return 0
    elif args.run_id is None:
        raise SystemExit("run_id is required unless --list, --status, or --next is used")
    else:
        run = RUN_BY_ID[args.run_id]
    if args.seconds <= 0:
        raise SystemExit("--seconds must be positive")
    if args.capture_interval <= 0:
        raise SystemExit("--capture-interval must be positive")

    command = build_tour_command(
        run,
        seconds=args.seconds,
        capture_interval=args.capture_interval,
        release=args.release,
    )
    validate_tour_command(command)
    (repo_root / run.report_path).parent.mkdir(parents=True, exist_ok=True)
    print(shell_quote(command))
    if args.dry_run:
        return 0
    completed = subprocess.run(command, cwd=repo_root, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
