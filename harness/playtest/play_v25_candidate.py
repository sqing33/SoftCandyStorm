#!/usr/bin/env python3
"""Launch an easy human-playable Runtime session for the v25 candidate."""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from run_v25_content_tour import shell_quote
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
REPORT_PREFIX = "harness/telemetry/local/v25_quick_play"
SUMMARY_SCRIPT = Path("harness/playtest/summarize_v25_quick_play_reports.py")


@dataclass(frozen=True)
class QuickPlayPreset:
    preset_id: str
    title: str
    character_id: str
    map_id: str
    seed: int
    focus: str

    @property
    def report_path(self) -> Path:
        return Path(f"{REPORT_PREFIX}_{self.preset_id}.json")


QUICK_PLAY_PRESETS: tuple[QuickPlayPreset, ...] = (
    QuickPlayPreset("default", "默认新手局", "jar-keeper", "frosting-grassland", 25301, "糖罐守护员和糖霜草地基准体验"),
    QuickPlayPreset("speed", "速度拾取局", "bubble-courier", "soda-creek", 25302, "泡泡邮差和汽水溪谷移动压力"),
    QuickPlayPreset("summon", "召唤经营局", "pudding-crafter", "cotton-cloud-pasture", 25303, "布丁工匠和棉花云群体压力"),
    QuickPlayPreset("control", "控场路线局", "sour-plum-doctor", "caramel-workshop", 25304, "酸梅博士和焦糖工坊路线干扰"),
    QuickPlayPreset("defense", "防御近身局", "cream-knight", "jelly-platform", 25305, "奶油骑士和果冻月台环形路线"),
    QuickPlayPreset("final", "终局压力局", "jar-keeper", "cracked-star-jar", 25306, "裂星糖罐混合怪潮压力"),
)
PRESET_BY_ID = {preset.preset_id: preset for preset in QUICK_PLAY_PRESETS}
DEFAULT_PRESET_ID = "default"


def build_quick_play_command(
    preset: QuickPlayPreset,
    *,
    seconds: int = DEFAULT_SECONDS,
    capture_interval: int = DEFAULT_CAPTURE_INTERVAL,
    release: bool = False,
    report: bool = True,
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
            preset.character_id,
            "--map-id",
            preset.map_id,
            "--seed",
            str(preset.seed),
            "--seconds",
            str(seconds),
            "--player-skill",
            "quickplay",
        ]
    )
    if report:
        command.extend(
            [
                "--playtest-report",
                str(preset.report_path),
                "--capture-interval",
                str(capture_interval),
            ]
        )
    return command


def validate_quick_play_command(command: list[str]) -> None:
    forbidden = sorted(flag for flag in FORBIDDEN_MANUAL_FLAGS if flag in command)
    if forbidden:
        raise ValueError(f"quick play command must not include automation flags: {', '.join(forbidden)}")


def build_summary_command() -> list[str]:
    executable = sys.executable or "python3"
    return [executable, str(SUMMARY_SCRIPT), "--allow-incomplete"]


def run_quick_play_and_maybe_summarize(
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


def list_presets() -> str:
    lines = [
        f"Candidate: {CANDIDATE_ID}",
        f"Content hash: {CONTENT_HASH}",
        "Purpose: easy local quick play, candidate-only, not acceptance evidence",
        "",
        "Preset | Title | Character | Map | Seed | Focus | Report",
        "---|---|---|---|---:|---|---",
    ]
    for preset in QUICK_PLAY_PRESETS:
        lines.append(
            f"{preset.preset_id} | {preset.title} | {preset.character_id} | {preset.map_id} | "
            f"{preset.seed} | {preset.focus} | {preset.report_path}"
        )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch an easy v25 candidate Runtime quick-play session.")
    parser.add_argument(
        "preset_id",
        nargs="?",
        choices=sorted(PRESET_BY_ID),
        default=DEFAULT_PRESET_ID,
        help="Quick-play preset id; default launches the beginner baseline",
    )
    parser.add_argument("--list", action="store_true", help="List quick-play presets")
    parser.add_argument("--dry-run", action="store_true", help="Print the command without launching Runtime")
    parser.add_argument("--release", action="store_true", help="Use cargo run --release")
    parser.add_argument("--no-report", action="store_true", help="Do not write a local quick-play Runtime report")
    parser.add_argument(
        "--no-summary-after",
        action="store_true",
        help="Do not refresh the objective quick-play summary after Runtime exits",
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
    if args.list:
        print(list_presets())
        return 0
    if args.seconds <= 0:
        raise SystemExit("--seconds must be positive")
    if args.capture_interval <= 0:
        raise SystemExit("--capture-interval must be positive")

    preset = PRESET_BY_ID[args.preset_id]
    command = build_quick_play_command(
        preset,
        seconds=args.seconds,
        capture_interval=args.capture_interval,
        release=args.release,
        report=not args.no_report,
    )
    validate_quick_play_command(command)
    if not args.no_report:
        (args.repo_root / preset.report_path).parent.mkdir(parents=True, exist_ok=True)
    print(shell_quote(command))
    print("Candidate-only quick play; this does not approve or promote v25 content.")
    if args.dry_run:
        return 0
    return run_quick_play_and_maybe_summarize(
        command,
        repo_root=args.repo_root,
        summarize_after=not args.no_summary_after,
    )


if __name__ == "__main__":
    raise SystemExit(main())
