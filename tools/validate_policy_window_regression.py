#!/usr/bin/env python3
"""Validate policy no-regression across fixed comparison windows.

This validator compares a candidate policy against a named baseline using the
same deterministic high-pressure windows. It is repair-gate evidence only: a
passing result means the candidate did not regress against the supplied
baseline, not that it is ready for RL acceptance.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


FORBIDDEN_DECISION_TOKENS = {
    "acceptance",
    "accepted",
    "balance_gate_pass",
    "candidate",
    "playtest",
    "production",
    "release",
    "rl_test_bot_candidate",
}


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def as_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def parse_window_arg(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("window report must use LABEL=PATH")
    label, path_text = value.split("=", 1)
    label = label.strip()
    path_text = path_text.strip()
    if not label:
        raise argparse.ArgumentTypeError("window label must be non-empty")
    if not path_text:
        raise argparse.ArgumentTypeError("window path must be non-empty")
    return label, Path(path_text)


def window_map(entries: list[tuple[str, Path]]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for label, path in entries:
        if label in result:
            raise ValueError(f"duplicate window label `{label}`")
        result[label] = path
    return result


def summary_maps(report: dict[str, Any]) -> list[dict[str, Any]]:
    summary = report.get("summary")
    if not isinstance(summary, dict):
        return []
    maps = summary.get("maps")
    if not isinstance(maps, list):
        return []
    return [item for item in maps if isinstance(item, dict)]


def map_by_id(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in summary_maps(report):
        map_id = item.get("map_id")
        if isinstance(map_id, str) and map_id:
            result[map_id] = item
    return result


def dominant_ratio(entry: dict[str, Any]) -> float | None:
    dominant = entry.get("policy_dominant_action")
    if not isinstance(dominant, dict):
        return None
    return as_number(dominant.get("ratio"))


def metric_delta(candidate: float | None, baseline: float | None) -> float | None:
    if candidate is None or baseline is None:
        return None
    return round(candidate - baseline, 6)


def collect_report_warnings(
    label: str,
    report_name: str,
    report: dict[str, Any],
    warnings: list[str],
) -> None:
    gate_decision = str(report.get("gate_decision", ""))
    lowered_gate = gate_decision.lower()
    if any(token in lowered_gate for token in FORBIDDEN_DECISION_TOKENS):
        warnings.append(f"{report_name}/{label}: gate_decision wording is too strong: {gate_decision}")
    if report.get("action_selection") == "stochastic":
        warnings.append(f"{report_name}/{label}: stochastic comparison is diagnostic only")


def compare_map_entry(
    *,
    window: str,
    map_id: str,
    baseline: dict[str, Any],
    candidate: dict[str, Any],
    min_win_rate_delta: float,
    max_survival_drop_seconds: float,
    max_dominant_ratio_increase: float | None,
) -> dict[str, Any]:
    baseline_win = as_number(baseline.get("policy_win_rate"))
    candidate_win = as_number(candidate.get("policy_win_rate"))
    baseline_survival = as_number(baseline.get("policy_average_survival_seconds"))
    candidate_survival = as_number(candidate.get("policy_average_survival_seconds"))
    baseline_dominant_ratio = dominant_ratio(baseline)
    candidate_dominant_ratio = dominant_ratio(candidate)
    blockers: list[str] = []

    win_delta = metric_delta(candidate_win, baseline_win)
    if win_delta is None:
        blockers.append("missing policy_win_rate")
    elif win_delta < min_win_rate_delta:
        blockers.append(
            f"win_rate_delta {win_delta} below required {round(min_win_rate_delta, 6)}"
        )

    survival_delta = metric_delta(candidate_survival, baseline_survival)
    if survival_delta is None:
        blockers.append("missing policy_average_survival_seconds")
    elif survival_delta < -max_survival_drop_seconds:
        blockers.append(
            "average_survival_seconds dropped "
            f"{round(abs(survival_delta), 6)}s beyond allowed {max_survival_drop_seconds}s"
        )

    dominant_delta = metric_delta(candidate_dominant_ratio, baseline_dominant_ratio)
    if max_dominant_ratio_increase is not None:
        if dominant_delta is None:
            blockers.append("missing policy_dominant_action ratio")
        elif dominant_delta > max_dominant_ratio_increase:
            blockers.append(
                "dominant_action_ratio increased "
                f"{dominant_delta} beyond allowed {max_dominant_ratio_increase}"
            )

    return {
        "window": window,
        "map_id": map_id,
        "baseline": {
            "policy_win_rate": baseline_win,
            "policy_average_survival_seconds": baseline_survival,
            "policy_dominant_action": baseline.get("policy_dominant_action"),
        },
        "candidate": {
            "policy_win_rate": candidate_win,
            "policy_average_survival_seconds": candidate_survival,
            "policy_dominant_action": candidate.get("policy_dominant_action"),
        },
        "deltas": {
            "policy_win_rate": win_delta,
            "policy_average_survival_seconds": survival_delta,
            "policy_dominant_action_ratio": dominant_delta,
        },
        "status": "pass" if not blockers else "regression",
        "blockers": blockers,
    }


def build_report(
    baseline_windows: dict[str, Path],
    candidate_windows: dict[str, Path],
    *,
    min_win_rate_delta: float = 0.0,
    max_survival_drop_seconds: float = 0.0,
    max_dominant_ratio_increase: float | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    blockers: list[str] = []
    window_reports: list[dict[str, Any]] = []

    missing_candidate = sorted(set(baseline_windows) - set(candidate_windows))
    missing_baseline = sorted(set(candidate_windows) - set(baseline_windows))
    for label in missing_candidate:
        errors.append(f"candidate window `{label}` is missing")
    for label in missing_baseline:
        errors.append(f"baseline window `{label}` is missing")

    for label in sorted(set(baseline_windows) & set(candidate_windows)):
        baseline_path = baseline_windows[label]
        candidate_path = candidate_windows[label]
        try:
            baseline_report = load_json_object(baseline_path)
            candidate_report = load_json_object(candidate_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{label}: unable to load report pair: {exc}")
            continue

        collect_report_warnings(label, "baseline", baseline_report, warnings)
        collect_report_warnings(label, "candidate", candidate_report, warnings)

        baseline_maps = map_by_id(baseline_report)
        candidate_maps = map_by_id(candidate_report)
        if not baseline_maps:
            errors.append(f"{label}: baseline summary maps are missing")
        if not candidate_maps:
            errors.append(f"{label}: candidate summary maps are missing")
        for map_id in sorted(set(baseline_maps) - set(candidate_maps)):
            errors.append(f"{label}/{map_id}: candidate map is missing")
        for map_id in sorted(set(candidate_maps) - set(baseline_maps)):
            warnings.append(f"{label}/{map_id}: candidate map is not present in baseline")

        map_results = [
            compare_map_entry(
                window=label,
                map_id=map_id,
                baseline=baseline_maps[map_id],
                candidate=candidate_maps[map_id],
                min_win_rate_delta=min_win_rate_delta,
                max_survival_drop_seconds=max_survival_drop_seconds,
                max_dominant_ratio_increase=max_dominant_ratio_increase,
            )
            for map_id in sorted(set(baseline_maps) & set(candidate_maps))
        ]
        for item in map_results:
            for blocker in item["blockers"]:
                blockers.append(f"{label}/{item['map_id']}: {blocker}")

        window_reports.append(
            {
                "label": label,
                "baseline_path": str(baseline_path),
                "candidate_path": str(candidate_path),
                "baseline_seconds": baseline_report.get("seconds"),
                "candidate_seconds": candidate_report.get("seconds"),
                "baseline_gate_decision": baseline_report.get("gate_decision"),
                "candidate_gate_decision": candidate_report.get("gate_decision"),
                "map_results": map_results,
            }
        )

    decision = (
        "policy_window_regression_invalid"
        if errors
        else "policy_window_regression_failed"
        if blockers
        else "policy_window_regression_passed"
    )
    return {
        "report_version": 1,
        "decision": decision,
        "gate_decision": decision,
        "baseline_window_count": len(baseline_windows),
        "candidate_window_count": len(candidate_windows),
        "criteria": {
            "min_win_rate_delta": min_win_rate_delta,
            "max_survival_drop_seconds": max_survival_drop_seconds,
            "max_dominant_ratio_increase": max_dominant_ratio_increase,
        },
        "errors": errors,
        "warnings": warnings,
        "blockers": blockers,
        "windows": window_reports,
        "limitations": [
            "This validator checks no-regression against supplied comparison reports only.",
            "A passing no-regression result is repair evidence, not RL policy acceptance.",
            "Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Policy Window Regression",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Baseline windows: `{report['baseline_window_count']}`",
        f"- Candidate windows: `{report['candidate_window_count']}`",
        f"- Blockers: `{len(report['blockers'])}`",
        "",
        "## Window Results",
        "",
        "| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |",
        "|---|---|---:|---:|---:|---|",
    ]
    for window in report["windows"]:
        for item in window["map_results"]:
            deltas = item["deltas"]
            lines.append(
                "| `{window}` | `{map_id}` | `{win}` | `{survival}` | `{dominant}` | `{status}` |".format(
                    window=window["label"],
                    map_id=item["map_id"],
                    win=deltas.get("policy_win_rate"),
                    survival=deltas.get("policy_average_survival_seconds"),
                    dominant=deltas.get("policy_dominant_action_ratio"),
                    status=item["status"],
                )
            )
    if report["errors"]:
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {item}" for item in report["errors"])
    if report["blockers"]:
        lines.extend(["", "## Blockers", ""])
        lines.extend(f"- {item}" for item in report["blockers"])
    if report["warnings"]:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {item}" for item in report["warnings"])
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate fixed-window policy no-regression.")
    parser.add_argument("--baseline-window", action="append", type=parse_window_arg, required=True)
    parser.add_argument("--candidate-window", action="append", type=parse_window_arg, required=True)
    parser.add_argument("--min-win-rate-delta", type=float, default=0.0)
    parser.add_argument("--max-survival-drop-seconds", type=float, default=0.0)
    parser.add_argument("--max-dominant-ratio-increase", type=float, default=None)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--markdown", type=Path, default=None)
    parser.add_argument("--allow-regression", action="store_true")
    args = parser.parse_args()

    if args.max_survival_drop_seconds < 0.0:
        parser.error("--max-survival-drop-seconds must be non-negative")
    if args.max_dominant_ratio_increase is not None and args.max_dominant_ratio_increase < 0.0:
        parser.error("--max-dominant-ratio-increase must be non-negative")

    try:
        baseline_windows = window_map(args.baseline_window)
        candidate_windows = window_map(args.candidate_window)
    except ValueError as exc:
        parser.error(str(exc))

    report = build_report(
        baseline_windows,
        candidate_windows,
        min_win_rate_delta=args.min_win_rate_delta,
        max_survival_drop_seconds=args.max_survival_drop_seconds,
        max_dominant_ratio_increase=args.max_dominant_ratio_increase,
    )
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    if report["decision"] == "policy_window_regression_passed":
        return 0
    return 0 if args.allow_regression else 1


if __name__ == "__main__":
    raise SystemExit(main())
