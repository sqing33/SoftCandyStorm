#!/usr/bin/env python3
"""Filter bot trajectory JSONL into focused movement training samples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable


def as_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def input_paths(values: Iterable[Path]) -> list[Path]:
    paths: list[Path] = []
    for value in values:
        if value.is_dir():
            paths.extend(sorted(path for path in value.rglob("*.jsonl") if path.is_file()))
        elif value.is_file():
            paths.append(value)
        else:
            raise FileNotFoundError(value)
    return sorted(dict.fromkeys(paths))


def parse_csv_filter(values: list[str] | None) -> set[str] | None:
    if not values:
        return None
    result = {
        item.strip()
        for value in values
        for item in value.split(",")
        if item.strip()
    }
    return result or None


def parse_action_filter(value: str | None) -> set[int] | None:
    if value is None:
        return None
    result: set[int] = set()
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        result.add(int(item))
    return result or None


def episode_key(record: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(record.get("seed", "")),
        str(record.get("map_id", "")),
        str(record.get("bot", "")),
    )


def terminal_matches(terminal: str | None, mode: str) -> bool:
    terminal = str(terminal or "")
    if mode == "any":
        return True
    if mode == "victory":
        return terminal == "victory"
    if mode == "non_victory":
        return terminal != "victory"
    raise ValueError(f"unsupported terminal filter: {mode}")


def sample_matches(
    sample: dict[str, Any],
    *,
    min_seconds: float | None,
    max_seconds: float | None,
    min_health_ratio: float | None,
    max_health_ratio: float | None,
    actions: set[int] | None,
) -> tuple[bool, str | None]:
    time_seconds = as_number(sample.get("time_seconds"))
    if min_seconds is not None and (time_seconds is None or time_seconds < min_seconds):
        return False, "time_before_min"
    if max_seconds is not None and (time_seconds is None or time_seconds > max_seconds):
        return False, "time_after_max"

    health_ratio = as_number(sample.get("health_ratio"))
    if min_health_ratio is not None and (
        health_ratio is None or health_ratio < min_health_ratio
    ):
        return False, "health_below_min"
    if max_health_ratio is not None and (
        health_ratio is None or health_ratio > max_health_ratio
    ):
        return False, "health_above_max"

    if actions is not None:
        action = sample.get("action")
        if not isinstance(action, int) or action not in actions:
            return False, "action_not_selected"
    return True, None


def merged_metadata(
    metadata: list[dict[str, Any]],
    *,
    source_files: list[Path],
    terminal_filter: str,
    map_ids: set[str] | None,
    seeds: set[str] | None,
    bots: set[str] | None,
    min_seconds: float | None,
    max_seconds: float | None,
    min_health_ratio: float | None,
    max_health_ratio: float | None,
    actions: set[int] | None,
) -> dict[str, Any]:
    def unique_value(key: str) -> Any:
        values = {
            item.get(key)
            for item in metadata
            if item.get(key) is not None
        }
        if len(values) == 1:
            return next(iter(values))
        return None

    return {
        "record_type": "metadata",
        "dataset_version": "bot-trajectory-filter-v0",
        "source_files": [str(path) for path in source_files],
        "terminal_filter": terminal_filter,
        "map_ids": sorted(map_ids) if map_ids else None,
        "seeds": sorted(seeds) if seeds else None,
        "bots": sorted(bots) if bots else None,
        "min_seconds": min_seconds,
        "max_seconds": max_seconds,
        "min_health_ratio": min_health_ratio,
        "max_health_ratio": max_health_ratio,
        "actions": sorted(actions) if actions else None,
        "bot": unique_value("bot"),
        "map_id": unique_value("map_id"),
        "observation_version": unique_value("observation_version"),
        "observation_len": unique_value("observation_len"),
        "action_count": unique_value("action_count"),
        "sample_start_seconds": min_seconds,
        "sample_end_seconds": max_seconds,
        "content_hash": unique_value("content_hash"),
    }


def build_report(
    inputs: list[Path],
    *,
    out: Path,
    terminal_filter: str = "victory",
    map_ids: set[str] | None = None,
    seeds: set[str] | None = None,
    bots: set[str] | None = None,
    min_seconds: float | None = None,
    max_seconds: float | None = None,
    min_health_ratio: float | None = None,
    max_health_ratio: float | None = None,
    actions: set[int] | None = None,
    max_samples_per_episode: int | None = None,
    max_total_samples: int | None = None,
    allow_empty: bool = False,
) -> dict[str, Any]:
    paths = input_paths(inputs)
    metadata: list[dict[str, Any]] = []
    samples_by_episode: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    episodes: dict[tuple[str, str, str], dict[str, Any]] = {}
    load_errors: list[str] = []
    dropped_samples: dict[str, int] = {}
    source_sample_count = 0
    source_episode_count = 0
    source_summary_count = 0

    for path in paths:
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    load_errors.append(f"{path}:{line_number}: invalid JSON: {exc}")
                    continue
                if not isinstance(record, dict):
                    load_errors.append(f"{path}:{line_number}: record must be an object")
                    continue
                record_type = record.get("record_type")
                if record_type == "metadata":
                    metadata.append(record)
                    continue
                if record_type == "sample":
                    source_sample_count += 1
                    samples_by_episode.setdefault(episode_key(record), []).append(record)
                    continue
                if record_type == "episode":
                    source_episode_count += 1
                    episodes[episode_key(record)] = record
                    continue
                if record_type == "summary":
                    source_summary_count += 1
                    continue

    kept_samples: list[dict[str, Any]] = []
    kept_episodes: list[dict[str, Any]] = []
    dropped_episode_count = 0
    orphan_sample_count = 0
    for key, samples in sorted(samples_by_episode.items()):
        if max_total_samples is not None and len(kept_samples) >= max_total_samples:
            break
        episode = episodes.get(key)
        if episode is None:
            orphan_sample_count += len(samples)
            continue
        if map_ids is not None and str(episode.get("map_id")) not in map_ids:
            dropped_episode_count += 1
            continue
        if seeds is not None and str(episode.get("seed")) not in seeds:
            dropped_episode_count += 1
            continue
        if bots is not None and str(episode.get("bot")) not in bots:
            dropped_episode_count += 1
            continue
        if not terminal_matches(episode.get("terminal"), terminal_filter):
            dropped_episode_count += 1
            continue

        episode_samples: list[dict[str, Any]] = []
        for sample in samples:
            matches, reason = sample_matches(
                sample,
                min_seconds=min_seconds,
                max_seconds=max_seconds,
                min_health_ratio=min_health_ratio,
                max_health_ratio=max_health_ratio,
                actions=actions,
            )
            if not matches:
                dropped_samples[reason or "unknown"] = (
                    dropped_samples.get(reason or "unknown", 0) + 1
                )
                continue
            episode_samples.append(sample)
            if max_samples_per_episode is not None and len(episode_samples) >= max_samples_per_episode:
                break
        if episode_samples:
            if max_total_samples is not None:
                remaining = max_total_samples - len(kept_samples)
                episode_samples = episode_samples[:remaining]
            kept_episodes.append(
                {
                    **episode,
                    "filtered_sample_count": len(episode_samples),
                }
            )
            kept_samples.extend(episode_samples)

    errors = list(load_errors)
    if not kept_samples and not allow_empty:
        errors.append("no samples matched the requested filters")

    decision = (
        "bot_trajectory_samples_filter_invalid"
        if errors
        else "bot_trajectory_samples_filter_empty"
        if not kept_samples
        else "bot_trajectory_samples_filtered"
    )

    out.parent.mkdir(parents=True, exist_ok=True)
    if not errors:
        with out.open("w", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    merged_metadata(
                        metadata,
                        source_files=paths,
                        terminal_filter=terminal_filter,
                        map_ids=map_ids,
                        seeds=seeds,
                        bots=bots,
                        min_seconds=min_seconds,
                        max_seconds=max_seconds,
                        min_health_ratio=min_health_ratio,
                        max_health_ratio=max_health_ratio,
                        actions=actions,
                    ),
                    ensure_ascii=False,
                )
                + "\n"
            )
            for sample in kept_samples:
                handle.write(json.dumps(sample, ensure_ascii=False) + "\n")
            for episode in kept_episodes:
                handle.write(json.dumps(episode, ensure_ascii=False) + "\n")
            handle.write(
                json.dumps(
                    {
                        "record_type": "summary",
                        "sample_count": len(kept_samples),
                        "episode_count": len(kept_episodes),
                        "victory_count": sum(
                            1
                            for episode in kept_episodes
                            if episode.get("terminal") == "victory"
                        ),
                        "source_sample_count": source_sample_count,
                        "source_episode_count": source_episode_count,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

    map_counts: dict[str, int] = {}
    bot_counts: dict[str, int] = {}
    terminal_counts: dict[str, int] = {}
    for episode in kept_episodes:
        map_id = str(episode.get("map_id"))
        bot = str(episode.get("bot"))
        terminal = str(episode.get("terminal"))
        map_counts[map_id] = map_counts.get(map_id, 0) + 1
        bot_counts[bot] = bot_counts.get(bot, 0) + 1
        terminal_counts[terminal] = terminal_counts.get(terminal, 0) + 1

    return {
        "report_version": 1,
        "decision": decision,
        "output_file": str(out),
        "source_files": [str(path) for path in paths],
        "source_file_count": len(paths),
        "source_sample_count": source_sample_count,
        "source_episode_count": source_episode_count,
        "source_summary_count": source_summary_count,
        "kept_sample_count": len(kept_samples),
        "kept_episode_count": len(kept_episodes),
        "orphan_sample_count": orphan_sample_count,
        "dropped_episode_count": dropped_episode_count,
        "dropped_samples": dict(sorted(dropped_samples.items())),
        "map_counts": dict(sorted(map_counts.items())),
        "bot_counts": dict(sorted(bot_counts.items())),
        "terminal_counts": dict(sorted(terminal_counts.items())),
        "filters": {
            "terminal": terminal_filter,
            "map_ids": sorted(map_ids) if map_ids else None,
            "seeds": sorted(seeds) if seeds else None,
            "bots": sorted(bots) if bots else None,
            "min_seconds": min_seconds,
            "max_seconds": max_seconds,
            "min_health_ratio": min_health_ratio,
            "max_health_ratio": max_health_ratio,
            "actions": sorted(actions) if actions else None,
            "max_samples_per_episode": max_samples_per_episode,
            "max_total_samples": max_total_samples,
        },
        "errors": errors,
        "limitations": [
            "This filter only preserves existing bot trajectory movement samples.",
            "Victory-window samples are training input, not policy acceptance evidence.",
            "Filtered samples still require behavior-clone or SB3 training plus fixed-window high-pressure gates.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Bot Trajectory Sample Filter",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Output: `{report['output_file']}`",
        f"- Source files: `{report['source_file_count']}`",
        f"- Source samples: `{report['source_sample_count']}`",
        f"- Kept samples: `{report['kept_sample_count']}`",
        f"- Kept episodes: `{report['kept_episode_count']}`",
        "",
        "## Filters",
        "",
    ]
    for key, value in report["filters"].items():
        lines.append(f"- `{key}`: `{value}`")
    if report["map_counts"]:
        lines.extend(["", "## Maps", ""])
        lines.extend(f"- `{key}`: {value}" for key, value in report["map_counts"].items())
    if report["dropped_samples"]:
        lines.extend(["", "## Dropped Samples", ""])
        lines.extend(
            f"- `{key}`: {value}" for key, value in report["dropped_samples"].items()
        )
    if report["errors"]:
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {item}" for item in report["errors"])
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Filter bot trajectory movement samples.")
    parser.add_argument("inputs", type=Path, nargs="+")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--terminal", choices=["victory", "non_victory", "any"], default="victory")
    parser.add_argument("--map-id", action="append", default=None)
    parser.add_argument("--seed", action="append", default=None)
    parser.add_argument("--bot", action="append", default=None)
    parser.add_argument("--min-seconds", type=float, default=None)
    parser.add_argument("--max-seconds", type=float, default=None)
    parser.add_argument("--min-health-ratio", type=float, default=None)
    parser.add_argument("--max-health-ratio", type=float, default=None)
    parser.add_argument("--actions", default=None)
    parser.add_argument("--max-samples-per-episode", type=int, default=None)
    parser.add_argument("--max-total-samples", type=int, default=None)
    parser.add_argument("--allow-empty", action="store_true")
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--markdown", type=Path, default=None)
    args = parser.parse_args()

    if args.min_seconds is not None and args.min_seconds < 0.0:
        parser.error("--min-seconds must be non-negative")
    if args.max_seconds is not None and args.max_seconds <= 0.0:
        parser.error("--max-seconds must be greater than zero")
    if (
        args.min_seconds is not None
        and args.max_seconds is not None
        and args.max_seconds <= args.min_seconds
    ):
        parser.error("--max-seconds must be greater than --min-seconds")
    for name in ("min_health_ratio", "max_health_ratio"):
        value = getattr(args, name)
        if value is not None and not (0.0 <= value <= 1.0):
            parser.error(f"--{name.replace('_', '-')} must be between 0 and 1")
    if (
        args.min_health_ratio is not None
        and args.max_health_ratio is not None
        and args.max_health_ratio < args.min_health_ratio
    ):
        parser.error("--max-health-ratio must be greater than or equal to --min-health-ratio")
    if args.max_samples_per_episode is not None and args.max_samples_per_episode <= 0:
        parser.error("--max-samples-per-episode must be positive")
    if args.max_total_samples is not None and args.max_total_samples <= 0:
        parser.error("--max-total-samples must be positive")

    try:
        actions = parse_action_filter(args.actions)
    except ValueError:
        parser.error("--actions must be a comma-separated list of integers")

    report = build_report(
        args.inputs,
        out=args.out,
        terminal_filter=args.terminal,
        map_ids=parse_csv_filter(args.map_id),
        seeds=parse_csv_filter(args.seed),
        bots=parse_csv_filter(args.bot),
        min_seconds=args.min_seconds,
        max_seconds=args.max_seconds,
        min_health_ratio=args.min_health_ratio,
        max_health_ratio=args.max_health_ratio,
        actions=actions,
        max_samples_per_episode=args.max_samples_per_episode,
        max_total_samples=args.max_total_samples,
        allow_empty=args.allow_empty,
    )
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if not report["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
