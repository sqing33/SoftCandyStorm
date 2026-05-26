#!/usr/bin/env python3
"""Validate headless Harness performance budget evidence.

This is a machine-checkable release-support gate for docs/11. It inspects
`game_harness matrix` metrics instead of launching Bevy, so it can prove only
headless/entity-budget properties: finite numeric metrics, bounded run length,
terminal outcomes, and observed enemy counts below the prototype ceiling.
It does not replace Runtime FPS, memory, or human readability review.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


DEFAULT_MAX_ENEMY_COUNT = 140
DEFAULT_WARNING_ENEMY_COUNT = 105
DEFAULT_DURATION_TOLERANCE_SECONDS = 1.0


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def is_finite_number(value: Any) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(float(value))


def finite_number(value: Any, label: str, errors: list[str]) -> float:
    if not is_finite_number(value):
        errors.append(f"{label}: must be a finite number")
        return 0.0
    return float(value)


def finite_int(value: Any, label: str, errors: list[str]) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        errors.append(f"{label}: must be an integer")
        return 0
    return value


def nonempty_string(value: Any, label: str, errors: list[str]) -> str:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}: must be a non-empty string")
        return ""
    return value


def validate_run(
    run: Any,
    *,
    bot_label: str,
    index: int,
    duration_target: float,
    duration_tolerance_seconds: float,
    max_enemy_count: int,
    warning_enemy_count: int,
    errors: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    if not isinstance(run, dict):
        errors.append(f"{bot_label}.runs[{index}]: must be an object")
        return {
            "seed": None,
            "terminal": None,
            "duration_seconds": 0.0,
            "level": 0,
            "kills": 0,
            "damage_taken": 0.0,
            "max_enemy_count": 0,
            "status": "invalid",
        }

    prefix = f"{bot_label}.runs[{index}]"
    seed = finite_int(run.get("seed"), f"{prefix}.seed", errors)
    terminal = nonempty_string(run.get("terminal"), f"{prefix}.terminal", errors)
    duration_seconds = finite_number(run.get("duration_seconds"), f"{prefix}.duration_seconds", errors)
    level = finite_int(run.get("level"), f"{prefix}.level", errors)
    kills = finite_int(run.get("kills"), f"{prefix}.kills", errors)
    damage_taken = finite_number(run.get("damage_taken"), f"{prefix}.damage_taken", errors)
    observed_enemy_count = finite_int(run.get("max_enemy_count"), f"{prefix}.max_enemy_count", errors)

    if terminal not in {"victory", "defeat"}:
        errors.append(f"{prefix}.terminal: expected victory or defeat, got `{terminal}`")
    if duration_seconds < 0:
        errors.append(f"{prefix}.duration_seconds: must be non-negative")
    if duration_seconds > duration_target + duration_tolerance_seconds:
        errors.append(
            f"{prefix}.duration_seconds: {duration_seconds:.3f} exceeds target "
            f"{duration_target:.3f} + tolerance {duration_tolerance_seconds:.3f}"
        )
    if level < 0:
        errors.append(f"{prefix}.level: must be non-negative")
    if kills < 0:
        errors.append(f"{prefix}.kills: must be non-negative")
    if damage_taken < 0:
        errors.append(f"{prefix}.damage_taken: must be non-negative")
    if observed_enemy_count < 0:
        errors.append(f"{prefix}.max_enemy_count: must be non-negative")
    if observed_enemy_count > max_enemy_count:
        errors.append(
            f"{prefix}.max_enemy_count: {observed_enemy_count} exceeds headless ceiling {max_enemy_count}"
        )
    elif observed_enemy_count > warning_enemy_count:
        warnings.append(
            f"{prefix}.max_enemy_count: {observed_enemy_count} is near prototype ceiling {max_enemy_count}"
        )

    return {
        "seed": seed,
        "terminal": terminal,
        "duration_seconds": duration_seconds,
        "level": level,
        "kills": kills,
        "damage_taken": damage_taken,
        "max_enemy_count": observed_enemy_count,
        "status": "ok",
    }


def validate_bot(
    bot: Any,
    *,
    index: int,
    max_enemy_count: int,
    warning_enemy_count: int,
    duration_tolerance_seconds: float,
    errors: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    if not isinstance(bot, dict):
        errors.append(f"bots[{index}]: must be an object")
        return {
            "bot": f"bots[{index}]",
            "map_id": "",
            "seed_start": 0,
            "seeds": 0,
            "seconds": 0.0,
            "tick_rate": 0,
            "victories": 0,
            "win_rate": 0.0,
            "average_duration_seconds": 0.0,
            "average_level": 0.0,
            "average_kills": 0.0,
            "max_enemy_count": 0,
            "runs": [],
            "status": "invalid",
        }

    bot_name = nonempty_string(bot.get("bot"), f"bots[{index}].bot", errors)
    bot_label = f"bot `{bot_name or index}`"
    map_id = nonempty_string(bot.get("map_id"), f"{bot_label}.map_id", errors)
    seed_start = finite_int(bot.get("seed_start"), f"{bot_label}.seed_start", errors)
    seeds = finite_int(bot.get("seeds"), f"{bot_label}.seeds", errors)
    seconds = finite_number(bot.get("seconds"), f"{bot_label}.seconds", errors)
    tick_rate = finite_int(bot.get("tick_rate"), f"{bot_label}.tick_rate", errors)
    victories = finite_int(bot.get("victories"), f"{bot_label}.victories", errors)
    win_rate = finite_number(bot.get("win_rate"), f"{bot_label}.win_rate", errors)
    average_duration = finite_number(
        bot.get("average_duration_seconds"), f"{bot_label}.average_duration_seconds", errors
    )
    average_level = finite_number(bot.get("average_level"), f"{bot_label}.average_level", errors)
    average_kills = finite_number(bot.get("average_kills"), f"{bot_label}.average_kills", errors)
    bot_max_enemy_count = finite_int(bot.get("max_enemy_count"), f"{bot_label}.max_enemy_count", errors)

    if seeds <= 0:
        errors.append(f"{bot_label}.seeds: must be positive")
    if seconds <= 0:
        errors.append(f"{bot_label}.seconds: must be positive")
    if tick_rate <= 0:
        errors.append(f"{bot_label}.tick_rate: must be positive")
    if victories < 0 or victories > max(seeds, 0):
        errors.append(f"{bot_label}.victories: must be between 0 and seeds")
    if not (0.0 <= win_rate <= 1.0):
        errors.append(f"{bot_label}.win_rate: must be between 0 and 1")
    if average_duration < 0:
        errors.append(f"{bot_label}.average_duration_seconds: must be non-negative")
    if average_level < 0:
        errors.append(f"{bot_label}.average_level: must be non-negative")
    if average_kills < 0:
        errors.append(f"{bot_label}.average_kills: must be non-negative")
    if bot_max_enemy_count > max_enemy_count:
        errors.append(
            f"{bot_label}.max_enemy_count: {bot_max_enemy_count} exceeds headless ceiling {max_enemy_count}"
        )
    elif bot_max_enemy_count > warning_enemy_count:
        warnings.append(
            f"{bot_label}.max_enemy_count: {bot_max_enemy_count} is near prototype ceiling {max_enemy_count}"
        )

    runs_payload = bot.get("runs")
    if not isinstance(runs_payload, list):
        errors.append(f"{bot_label}.runs: must be a list")
        runs_payload = []
    if seeds > 0 and len(runs_payload) != seeds:
        errors.append(f"{bot_label}.runs: expected {seeds} run(s), got {len(runs_payload)}")

    runs = [
        validate_run(
            run,
            bot_label=bot_label,
            index=run_index,
            duration_target=seconds,
            duration_tolerance_seconds=duration_tolerance_seconds,
            max_enemy_count=max_enemy_count,
            warning_enemy_count=warning_enemy_count,
            errors=errors,
            warnings=warnings,
        )
        for run_index, run in enumerate(runs_payload)
    ]

    observed_run_max = max((run["max_enemy_count"] for run in runs), default=0)
    if observed_run_max != bot_max_enemy_count:
        errors.append(
            f"{bot_label}.max_enemy_count: summary {bot_max_enemy_count} does not match run max {observed_run_max}"
        )

    expected_win_rate = (victories / seeds) if seeds > 0 else 0.0
    if abs(win_rate - expected_win_rate) > 0.001:
        errors.append(
            f"{bot_label}.win_rate: summary {win_rate:.3f} does not match victories/seeds {expected_win_rate:.3f}"
        )

    return {
        "bot": bot_name,
        "map_id": map_id,
        "seed_start": seed_start,
        "seeds": seeds,
        "seconds": seconds,
        "tick_rate": tick_rate,
        "victories": victories,
        "win_rate": win_rate,
        "average_duration_seconds": average_duration,
        "average_level": average_level,
        "average_kills": average_kills,
        "max_enemy_count": bot_max_enemy_count,
        "runs": runs,
        "status": "ok",
    }


def build_report(
    metrics_path: Path,
    *,
    max_enemy_count: int = DEFAULT_MAX_ENEMY_COUNT,
    warning_enemy_count: int = DEFAULT_WARNING_ENEMY_COUNT,
    duration_tolerance_seconds: float = DEFAULT_DURATION_TOLERANCE_SECONDS,
) -> dict[str, Any]:
    payload = load_json_object(metrics_path)
    errors: list[str] = []
    warnings: list[str] = []

    kind = payload.get("kind")
    if kind != "bot_matrix":
        errors.append(f"`kind` must be `bot_matrix`, got `{kind}`")

    bots_payload = payload.get("bots")
    if not isinstance(bots_payload, list):
        errors.append("`bots` must be a list")
        bots_payload = []
    if not bots_payload:
        errors.append("`bots` must contain at least one bot result")

    if max_enemy_count <= 0:
        errors.append("max_enemy_count threshold must be positive")
    if warning_enemy_count <= 0:
        errors.append("warning_enemy_count threshold must be positive")
    if warning_enemy_count > max_enemy_count:
        errors.append("warning_enemy_count threshold must not exceed max_enemy_count")
    if duration_tolerance_seconds < 0:
        errors.append("duration_tolerance_seconds must be non-negative")

    bots = [
        validate_bot(
            bot,
            index=index,
            max_enemy_count=max_enemy_count,
            warning_enemy_count=warning_enemy_count,
            duration_tolerance_seconds=duration_tolerance_seconds,
            errors=errors,
            warnings=warnings,
        )
        for index, bot in enumerate(bots_payload)
    ]

    total_runs = sum(len(bot.get("runs", [])) for bot in bots)
    observed_max_enemy_count = max((bot.get("max_enemy_count", 0) for bot in bots), default=0)
    bot_count = len(bots)
    decision = "harness_performance_budget_valid" if not errors else "harness_performance_budget_invalid"

    return {
        "report_version": 1,
        "source": str(metrics_path),
        "decision": decision,
        "thresholds": {
            "max_enemy_count": max_enemy_count,
            "warning_enemy_count": warning_enemy_count,
            "duration_tolerance_seconds": duration_tolerance_seconds,
        },
        "summary": {
            "kind": kind,
            "bot_count": bot_count,
            "run_count": total_runs,
            "observed_max_enemy_count": observed_max_enemy_count,
        },
        "bots": bots,
        "errors": errors,
        "warnings": warnings,
        "limitations": [
            "This validates headless Harness metrics only; it does not measure Runtime FPS, GPU cost, memory growth, or frame pacing.",
            "A valid result supports entity-budget and no-deadlock evidence, but does not make a Release Candidate ready.",
            "Manual playtest, content acceptance, asset acceptance, and privacy gates remain separate release requirements.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    summary = report["summary"]
    thresholds = report["thresholds"]
    lines = [
        "# Harness Performance Budget Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Decision: `{report['decision']}`",
        f"- Bots: `{summary['bot_count']}`",
        f"- Runs: `{summary['run_count']}`",
        f"- Observed max enemies: `{summary['observed_max_enemy_count']}`",
        f"- Max enemy ceiling: `{thresholds['max_enemy_count']}`",
        f"- Warning enemy ceiling: `{thresholds['warning_enemy_count']}`",
        "",
        "## Bot Summary",
        "",
        "| Bot | Map | Seeds | Seconds | Win Rate | Max Enemies |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for bot in report["bots"]:
        lines.append(
            f"| `{bot['bot']}` | `{bot['map_id']}` | {bot['seeds']} | "
            f"{bot['seconds']:.0f} | {bot['win_rate'] * 100:.1f}% | {bot['max_enemy_count']} |"
        )

    lines.extend(["", "## Errors", ""])
    if report["errors"]:
        lines.extend(f"- {error}" for error in report["errors"])
    else:
        lines.append("- None")

    lines.extend(["", "## Warnings", ""])
    if report["warnings"]:
        lines.extend(f"- {warning}" for warning in report["warnings"])
    else:
        lines.append("- None")

    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm headless performance budget metrics.")
    parser.add_argument("metrics", type=Path, help="Harness matrix metrics.json")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON validation report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown validation summary")
    parser.add_argument("--max-enemy-count", type=int, default=DEFAULT_MAX_ENEMY_COUNT)
    parser.add_argument("--warning-enemy-count", type=int, default=DEFAULT_WARNING_ENEMY_COUNT)
    parser.add_argument("--duration-tolerance-seconds", type=float, default=DEFAULT_DURATION_TOLERANCE_SECONDS)
    args = parser.parse_args()

    report = build_report(
        args.metrics,
        max_enemy_count=args.max_enemy_count,
        warning_enemy_count=args.warning_enemy_count,
        duration_tolerance_seconds=args.duration_tolerance_seconds,
    )
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))

    return 0 if report["decision"] == "harness_performance_budget_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
