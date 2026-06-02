#!/usr/bin/env python3
"""Launch optional human content-tour Runtime runs for v25.

These runs help a human try every v25 map and every playable character. They
are not part of the required 9-run manual acceptance matrix and must not be
used as acceptance evidence without a separately filled human review.
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from run_v25_manual_playtest import (
    CANDIDATE_ID,
    CONTENT_DIR,
    CONTENT_HASH,
    DEFAULT_CAPTURE_INTERVAL,
    DEFAULT_SECONDS,
    FORBIDDEN_MANUAL_FLAGS,
)


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
REPORT_PREFIX = "harness/telemetry/local/v25_content_tour"
SUMMARY_SCRIPT = Path("harness/playtest/summarize_v25_content_tour_reports.py")


@dataclass(frozen=True)
class ContentTourRun:
    run_id: str
    character_id: str
    map_id: str
    seed: int
    focus: str

    @property
    def report_path(self) -> Path:
        return Path(f"{REPORT_PREFIX}_{self.run_id}.json")


TOUR_RUNS: tuple[ContentTourRun, ...] = (
    ContentTourRun("frosting_jar_keeper", "jar-keeper", "frosting-grassland", 25201, "新手基准角色和糖霜草地开局"),
    ContentTourRun("soda_bubble_courier", "bubble-courier", "soda-creek", 25202, "速度角色和汽水溪谷泡泡压力"),
    ContentTourRun("cotton_pudding_crafter", "pudding-crafter", "cotton-cloud-pasture", 25203, "召唤角色和棉花云群体压力"),
    ContentTourRun("caramel_sour_plum_doctor", "sour-plum-doctor", "caramel-workshop", 25204, "控制角色和焦糖工坊路线干扰"),
    ContentTourRun("jelly_cream_knight", "cream-knight", "jelly-platform", 25205, "防御角色和果冻月台环形路线"),
    ContentTourRun("cracked_jar_keeper", "jar-keeper", "cracked-star-jar", 25206, "最终地图混合怪潮压力"),
)

RUN_BY_ID = {run.run_id: run for run in TOUR_RUNS}


def shell_quote(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def build_tour_command(
    run: ContentTourRun,
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
            "--character-id",
            run.character_id,
            "--map-id",
            run.map_id,
            "--seed",
            str(run.seed),
            "--seconds",
            str(seconds),
            "--player-skill",
            "tour",
            "--playtest-report",
            str(run.report_path),
            "--capture-interval",
            str(capture_interval),
        ]
    )
    return command


def validate_tour_command(command: list[str]) -> None:
    forbidden = sorted(flag for flag in FORBIDDEN_MANUAL_FLAGS if flag in command)
    if forbidden:
        raise ValueError(f"content tour command must not include automation flags: {', '.join(forbidden)}")


def build_summary_command() -> list[str]:
    executable = sys.executable or "python3"
    return [executable, str(SUMMARY_SCRIPT), "--allow-incomplete"]


def run_tour_and_maybe_summarize(
    command: list[str],
    *,
    repo_root: Path,
    summarize_after: bool = True,
) -> int:
    completed = subprocess.run(command, cwd=repo_root, check=False)
    runtime_returncode = completed.returncode
    if not summarize_after:
        return runtime_returncode

    summary_command = build_summary_command()
    print(f"Summary: {shell_quote(summary_command)}")
    summary_completed = subprocess.run(summary_command, cwd=repo_root, check=False)
    if runtime_returncode != 0:
        return runtime_returncode
    return summary_completed.returncode


def report_exists(repo_root: Path, run: ContentTourRun) -> bool:
    return (repo_root / run.report_path).exists()


def first_missing_run(repo_root: Path) -> ContentTourRun | None:
    for run in TOUR_RUNS:
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
    for run in TOUR_RUNS:
        status = ""
        if repo_root is not None:
            status = " | done" if report_exists(repo_root, run) else " | missing"
        lines.append(
            f"{run.run_id} | {run.character_id} | {run.map_id} | {run.seed} | {run.focus} | {run.report_path}{status}"
        )
    return "\n".join(lines)


def status_text(repo_root: Path) -> str:
    existing_count = sum(1 for run in TOUR_RUNS if report_exists(repo_root, run))
    next_run = first_missing_run(repo_root)
    lines = [
        f"Candidate: {CANDIDATE_ID}",
        f"Content hash: {CONTENT_HASH}",
        "Purpose: optional content tour, not acceptance evidence",
        f"Reports: {existing_count} / {len(TOUR_RUNS)}",
    ]
    if next_run is None:
        lines.append("Next tour run: none, all local content-tour reports exist")
    else:
        lines.append(f"Next tour run: {next_run.run_id}")
        lines.append(f"Character: {next_run.character_id}")
        lines.append(f"Map: {next_run.map_id}")
        lines.append(f"Focus: {next_run.focus}")
        lines.append(f"Report: {next_run.report_path}")
        lines.append("Launch: python3 harness/playtest/run_v25_content_tour.py --next")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch an optional v25 human content-tour Runtime run.")
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
    parser.add_argument(
        "--no-summary-after",
        action="store_true",
        help="Do not refresh the objective content-tour summary after Runtime exits",
    )
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
            print("All optional v25 content-tour reports already exist.")
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
    return run_tour_and_maybe_summarize(
        command,
        repo_root=repo_root,
        summarize_after=not args.no_summary_after,
    )


if __name__ == "__main__":
    raise SystemExit(main())
