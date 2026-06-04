#!/usr/bin/env python3
"""Launch an easy human-playable Runtime session for the current candidate."""

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
    QUICK_PLAY_PRESETS,
    QuickPlayPreset,
    build_runtime_command,
    shell_quote,
    validate_human_runtime_command,
)


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
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
    return build_runtime_command(
        character_id=preset.character_id,
        map_id=preset.map_id,
        seed=preset.seed,
        player_skill="quickplay",
        report_path=preset.report_path if report else None,
        seconds=seconds,
        capture_interval=capture_interval,
        release=release,
    )


def validate_quick_play_command(command: list[str]) -> None:
    validate_human_runtime_command(command, label="quick play")


def run_quick_play(command: list[str], *, repo_root: Path) -> int:
    completed = subprocess.run(command, cwd=repo_root, check=False)
    return completed.returncode


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
    parser = argparse.ArgumentParser(description=f"Launch a {CANDIDATE_LABEL} candidate Runtime quick-play session.")
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
    print(f"Candidate-only quick play for {CANDIDATE_LABEL}; this does not approve or promote content.")
    if args.dry_run:
        return 0
    return run_quick_play(command, repo_root=args.repo_root)


if __name__ == "__main__":
    raise SystemExit(main())
