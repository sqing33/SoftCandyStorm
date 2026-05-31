#!/usr/bin/env python3
"""Validate absolute map/window targets for RL repair preflights.

This is an early-stop helper for policy repair work. It checks one map inside
an existing comparison/evaluation report against explicit short-window targets
such as "caramel-workshop must keep at least 2/3 wins at 60 seconds". It is not
RL acceptance evidence and does not replace fixed-window regression checks.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from validate_policy_window_regression import (
    as_number,
    dominant_action_from_policy_summary,
    load_json_object,
    map_by_id,
    policy_summary_by_map,
)


def threshold_enabled(*values: float | None) -> bool:
    return any(value is not None for value in values)


def number_or_none(value: Any) -> float | None:
    return as_number(value)


def dominant_ratio(entry: dict[str, Any], summary: dict[str, Any] | None) -> float | None:
    dominant = entry.get("policy_dominant_action")
    if isinstance(dominant, dict):
        ratio = number_or_none(dominant.get("ratio"))
        if ratio is not None:
            return ratio
    if isinstance(summary, dict):
        summary_dominant = dominant_action_from_policy_summary(summary)
        if isinstance(summary_dominant, dict):
            return number_or_none(summary_dominant.get("ratio"))
    return None


def collect_context_errors(
    report: dict[str, Any],
    *,
    expected_seconds: float | None,
    expected_seed_start: int | None,
    expected_seeds: int | None,
    expected_map_preset: str | None,
    expected_action_selection: str | None,
    errors: list[str],
) -> None:
    expected_pairs: list[tuple[str, Any]] = [
        ("seconds", expected_seconds),
        ("seed_start", expected_seed_start),
        ("seeds", expected_seeds),
        ("map_preset", expected_map_preset),
        ("action_selection", expected_action_selection),
    ]
    for field, expected in expected_pairs:
        if expected is None:
            continue
        actual = report.get(field)
        if isinstance(expected, float):
            actual_number = number_or_none(actual)
            if actual_number is None or abs(actual_number - expected) > 1e-6:
                errors.append(f"context {field} `{actual}` does not match expected `{expected}`")
        elif actual != expected:
            errors.append(f"context {field} `{actual}` does not match expected `{expected}`")


def build_report(
    comparison: Path,
    *,
    label: str,
    map_id: str,
    min_win_rate: float | None = None,
    min_average_survival_seconds: float | None = None,
    min_normalized_action_entropy: float | None = None,
    max_dominant_action_ratio: float | None = None,
    expected_seconds: float | None = None,
    expected_seed_start: int | None = None,
    expected_seeds: int | None = None,
    expected_map_preset: str | None = None,
    expected_action_selection: str | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    blockers: list[str] = []
    if not label.strip():
        errors.append("label must be non-empty")
    if not map_id.strip():
        errors.append("map_id must be non-empty")
    if not threshold_enabled(
        min_win_rate,
        min_average_survival_seconds,
        min_normalized_action_entropy,
        max_dominant_action_ratio,
    ):
        errors.append("at least one threshold must be provided")

    try:
        source_report = load_json_object(comparison)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {
            "report_version": 1,
            "decision": "policy_window_target_preflight_invalid",
            "comparison": str(comparison),
            "label": label,
            "map_id": map_id,
            "target_count": 0,
            "target_result": None,
            "errors": [f"unable to load comparison report: {exc}"],
            "blockers": [],
            "limitations": limitations(),
        }

    collect_context_errors(
        source_report,
        expected_seconds=expected_seconds,
        expected_seed_start=expected_seed_start,
        expected_seeds=expected_seeds,
        expected_map_preset=expected_map_preset,
        expected_action_selection=expected_action_selection,
        errors=errors,
    )

    entries = map_by_id(source_report)
    summaries = policy_summary_by_map(source_report)
    entry = entries.get(map_id)
    summary = summaries.get(map_id)
    if entry is None:
        errors.append(f"map `{map_id}` missing from comparison report")
        entry = {}

    win_rate = number_or_none(entry.get("policy_win_rate"))
    if win_rate is None and isinstance(summary, dict):
        win_rate = number_or_none(summary.get("win_rate"))
    average_survival = number_or_none(entry.get("policy_average_survival_seconds"))
    if average_survival is None and isinstance(summary, dict):
        average_survival = number_or_none(summary.get("average_survival_seconds"))
    normalized_entropy = number_or_none(entry.get("policy_normalized_action_entropy"))
    if normalized_entropy is None and isinstance(summary, dict):
        normalized_entropy = number_or_none(summary.get("normalized_action_entropy"))
    dominant = dominant_ratio(entry, summary)
    episode_count = summary.get("episodes") if isinstance(summary, dict) else None

    prefix = f"{label}/{map_id}"
    if min_win_rate is not None:
        if win_rate is None:
            blockers.append(f"{prefix}: missing win_rate")
        elif win_rate < min_win_rate:
            blockers.append(f"{prefix}: win_rate {win_rate:.4f} below required {min_win_rate:.4f}")
    if min_average_survival_seconds is not None:
        if average_survival is None:
            blockers.append(f"{prefix}: missing average_survival_seconds")
        elif average_survival < min_average_survival_seconds:
            blockers.append(
                f"{prefix}: average_survival_seconds {average_survival:.4f} "
                f"below required {min_average_survival_seconds:.4f}"
            )
    if min_normalized_action_entropy is not None:
        if normalized_entropy is None:
            blockers.append(f"{prefix}: missing normalized_action_entropy")
        elif normalized_entropy < min_normalized_action_entropy:
            blockers.append(
                f"{prefix}: normalized_action_entropy {normalized_entropy:.4f} "
                f"below required {min_normalized_action_entropy:.4f}"
            )
    if max_dominant_action_ratio is not None:
        if dominant is None:
            blockers.append(f"{prefix}: missing dominant_action ratio")
        elif dominant > max_dominant_action_ratio:
            blockers.append(
                f"{prefix}: dominant_action_ratio {dominant:.4f} "
                f"above allowed {max_dominant_action_ratio:.4f}"
            )

    decision = (
        "policy_window_target_preflight_invalid"
        if errors
        else "policy_window_target_preflight_failed"
        if blockers
        else "policy_window_target_preflight_passed"
    )
    return {
        "report_version": 1,
        "decision": decision,
        "comparison": str(comparison),
        "label": label,
        "map_id": map_id,
        "context": {
            "seconds": source_report.get("seconds"),
            "seed_start": source_report.get("seed_start"),
            "seeds": source_report.get("seeds"),
            "map_preset": source_report.get("map_preset"),
            "action_selection": source_report.get("action_selection"),
        },
        "thresholds": {
            "min_win_rate": min_win_rate,
            "min_average_survival_seconds": min_average_survival_seconds,
            "min_normalized_action_entropy": min_normalized_action_entropy,
            "max_dominant_action_ratio": max_dominant_action_ratio,
        },
        "target_count": 1 if entry else 0,
        "target_result": {
            "map_id": map_id,
            "episodes": episode_count,
            "win_rate": win_rate,
            "average_survival_seconds": average_survival,
            "normalized_action_entropy": normalized_entropy,
            "dominant_action_ratio": dominant,
        },
        "errors": errors,
        "blockers": blockers,
        "limitations": limitations(),
    }


def limitations() -> list[str]:
    return [
        "This preflight validates one aggregate map/window target in an existing policy report.",
        "Passing does not make a policy an RL test Bot, content candidate, playtest candidate, or release candidate.",
        "Any follow-up still requires fixed-window no-regression, target seed checks when relevant, failure-case review, and RL acceptance gates.",
    ]


def write_markdown(report: dict[str, Any], path: Path) -> None:
    result = report.get("target_result") or {}
    lines = [
        "# Policy Window Target Preflight",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Comparison: `{report['comparison']}`",
        f"- Target: `{report['label']}` / `{report['map_id']}`",
        "",
        "## Result",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Win rate | `{result.get('win_rate')}` |",
        f"| Average survival seconds | `{result.get('average_survival_seconds')}` |",
        f"| Normalized action entropy | `{result.get('normalized_action_entropy')}` |",
        f"| Dominant action ratio | `{result.get('dominant_action_ratio')}` |",
        "",
        "## Blockers",
        "",
    ]
    lines.extend(f"- {item}" for item in report["blockers"]) if report["blockers"] else lines.append("- None")
    lines.extend(["", "## Errors", ""])
    lines.extend(f"- {item}" for item in report["errors"]) if report["errors"] else lines.append("- None")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate one policy map/window target preflight.")
    parser.add_argument("comparison", type=Path)
    parser.add_argument("--label", default="window-target")
    parser.add_argument("--map-id", required=True)
    parser.add_argument("--min-win-rate", type=float, default=None)
    parser.add_argument("--min-average-survival-seconds", type=float, default=None)
    parser.add_argument("--min-normalized-action-entropy", type=float, default=None)
    parser.add_argument("--max-dominant-action-ratio", type=float, default=None)
    parser.add_argument("--expected-seconds", type=float, default=None)
    parser.add_argument("--expected-seed-start", type=int, default=None)
    parser.add_argument("--expected-seeds", type=int, default=None)
    parser.add_argument("--expected-map-preset", default=None)
    parser.add_argument("--expected-action-selection", default=None)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--markdown", type=Path, default=None)
    parser.add_argument("--allow-fail", action="store_true")
    args = parser.parse_args()

    report = build_report(
        args.comparison,
        label=args.label,
        map_id=args.map_id,
        min_win_rate=args.min_win_rate,
        min_average_survival_seconds=args.min_average_survival_seconds,
        min_normalized_action_entropy=args.min_normalized_action_entropy,
        max_dominant_action_ratio=args.max_dominant_action_ratio,
        expected_seconds=args.expected_seconds,
        expected_seed_start=args.expected_seed_start,
        expected_seeds=args.expected_seeds,
        expected_map_preset=args.expected_map_preset,
        expected_action_selection=args.expected_action_selection,
    )
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if report["decision"] != "policy_window_target_preflight_passed" and not args.allow_fail:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
