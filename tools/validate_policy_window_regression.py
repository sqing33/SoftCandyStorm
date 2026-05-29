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


def policy_summary_by_map(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    if isinstance(report.get("map_id"), str):
        policy = report.get("policy")
        summary = policy.get("summary") if isinstance(policy, dict) else None
        if isinstance(summary, dict):
            result[report["map_id"]] = summary
    for item in report.get("maps", []):
        if not isinstance(item, dict):
            continue
        map_id = item.get("map_id")
        policy = item.get("policy")
        summary = policy.get("summary") if isinstance(policy, dict) else None
        if isinstance(map_id, str) and map_id and isinstance(summary, dict):
            result[map_id] = summary
    return result


def dominant_ratio(entry: dict[str, Any]) -> float | None:
    dominant = entry.get("policy_dominant_action")
    if not isinstance(dominant, dict):
        return None
    return as_number(dominant.get("ratio"))


def normalized_entropy(
    entry: dict[str, Any],
    policy_summary: dict[str, Any] | None,
) -> float | None:
    if isinstance(policy_summary, dict):
        value = as_number(policy_summary.get("normalized_action_entropy"))
        if value is not None:
            return value
    return as_number(entry.get("policy_normalized_action_entropy"))


def normalize_action_distribution(value: Any) -> dict[str, float] | None:
    if not isinstance(value, dict):
        return None
    result: dict[str, float] = {}
    for action, payload in value.items():
        if not isinstance(payload, dict):
            continue
        ratio = as_number(payload.get("ratio"))
        if ratio is not None:
            result[str(action)] = ratio
    return result


def action_sort_key(value: str) -> tuple[int, int | str]:
    try:
        return (0, int(value))
    except ValueError:
        return (1, value)


def metric_delta(candidate: float | None, baseline: float | None) -> float | None:
    if candidate is None or baseline is None:
        return None
    return round(candidate - baseline, 6)


def action_distribution_delta_report(
    *,
    baseline_summary: dict[str, Any] | None,
    candidate_summary: dict[str, Any] | None,
    baseline_entry: dict[str, Any],
    candidate_entry: dict[str, Any],
    max_action_ratio_increase: float | None,
    max_action_distribution_l1_delta: float | None,
    max_normalized_entropy_drop: float | None,
) -> tuple[dict[str, Any], list[str]]:
    enabled = any(
        value is not None
        for value in (
            max_action_ratio_increase,
            max_action_distribution_l1_delta,
            max_normalized_entropy_drop,
        )
    )
    if not enabled:
        return {"enabled": False}, []

    blockers: list[str] = []
    baseline_entropy = normalized_entropy(baseline_entry, baseline_summary)
    candidate_entropy = normalized_entropy(candidate_entry, candidate_summary)
    entropy_delta = metric_delta(candidate_entropy, baseline_entropy)

    baseline_distribution = normalize_action_distribution(
        baseline_summary.get("action_distribution")
        if isinstance(baseline_summary, dict)
        else None
    )
    candidate_distribution = normalize_action_distribution(
        candidate_summary.get("action_distribution")
        if isinstance(candidate_summary, dict)
        else None
    )

    action_ratio_deltas: dict[str, float] | None = None
    l1_delta: float | None = None
    max_increase: dict[str, Any] | None = None
    max_decrease: dict[str, Any] | None = None
    needs_distribution = (
        max_action_ratio_increase is not None
        or max_action_distribution_l1_delta is not None
    )
    if needs_distribution and (
        baseline_distribution is None or candidate_distribution is None
    ):
        blockers.append("missing policy action_distribution")
    elif baseline_distribution is not None and candidate_distribution is not None:
        action_ratio_deltas = {}
        actions = sorted(
            set(baseline_distribution) | set(candidate_distribution),
            key=action_sort_key,
        )
        abs_total = 0.0
        for action in actions:
            delta = metric_delta(
                candidate_distribution.get(action, 0.0),
                baseline_distribution.get(action, 0.0),
            )
            action_ratio_deltas[action] = delta
            abs_total += abs(delta)
        l1_delta = round(abs_total, 6)
        if action_ratio_deltas:
            increase_action, increase_delta = max(
                action_ratio_deltas.items(), key=lambda item: item[1]
            )
            decrease_action, decrease_delta = min(
                action_ratio_deltas.items(), key=lambda item: item[1]
            )
            max_increase = {
                "action": increase_action,
                "delta": increase_delta,
                "baseline_ratio": baseline_distribution.get(increase_action, 0.0),
                "candidate_ratio": candidate_distribution.get(increase_action, 0.0),
            }
            max_decrease = {
                "action": decrease_action,
                "delta": decrease_delta,
                "baseline_ratio": baseline_distribution.get(decrease_action, 0.0),
                "candidate_ratio": candidate_distribution.get(decrease_action, 0.0),
            }
            if (
                max_action_ratio_increase is not None
                and increase_delta > max_action_ratio_increase
            ):
                blockers.append(
                    f"action {increase_action} ratio increased {increase_delta} "
                    f"beyond allowed {max_action_ratio_increase}"
                )
        if (
            max_action_distribution_l1_delta is not None
            and l1_delta > max_action_distribution_l1_delta
        ):
            blockers.append(
                "action_distribution_l1_delta "
                f"{l1_delta} beyond allowed {max_action_distribution_l1_delta}"
            )

    if max_normalized_entropy_drop is not None:
        if entropy_delta is None:
            blockers.append("missing normalized action entropy")
        elif entropy_delta < -max_normalized_entropy_drop:
            blockers.append(
                "normalized_action_entropy dropped "
                f"{round(abs(entropy_delta), 6)} beyond allowed {max_normalized_entropy_drop}"
            )

    return {
        "enabled": True,
        "baseline_normalized_action_entropy": baseline_entropy,
        "candidate_normalized_action_entropy": candidate_entropy,
        "normalized_action_entropy_delta": entropy_delta,
        "action_ratio_deltas": action_ratio_deltas,
        "action_distribution_l1_delta": l1_delta,
        "max_action_ratio_increase": max_increase,
        "max_action_ratio_decrease": max_decrease,
    }, blockers


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


def collect_context_errors(
    label: str,
    baseline_report: dict[str, Any],
    candidate_report: dict[str, Any],
    errors: list[str],
) -> None:
    fields = [
        "seconds",
        "seed_start",
        "seeds",
        "map_preset",
        "action_selection",
        "reward_profile",
    ]
    for field in fields:
        baseline_value = baseline_report.get(field)
        candidate_value = candidate_report.get(field)
        if baseline_value is None and candidate_value is None:
            continue
        if baseline_value != candidate_value:
            errors.append(
                f"{label}: baseline {field} `{baseline_value}` does not match "
                f"candidate {field} `{candidate_value}`"
            )


def compare_map_entry(
    *,
    window: str,
    map_id: str,
    baseline: dict[str, Any],
    candidate: dict[str, Any],
    baseline_policy_summary: dict[str, Any] | None,
    candidate_policy_summary: dict[str, Any] | None,
    min_win_rate_delta: float,
    max_survival_drop_seconds: float,
    max_dominant_ratio_increase: float | None,
    max_action_ratio_increase: float | None,
    max_action_distribution_l1_delta: float | None,
    max_normalized_entropy_drop: float | None,
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

    action_delta, action_blockers = action_distribution_delta_report(
        baseline_summary=baseline_policy_summary,
        candidate_summary=candidate_policy_summary,
        baseline_entry=baseline,
        candidate_entry=candidate,
        max_action_ratio_increase=max_action_ratio_increase,
        max_action_distribution_l1_delta=max_action_distribution_l1_delta,
        max_normalized_entropy_drop=max_normalized_entropy_drop,
    )
    blockers.extend(action_blockers)

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
        "action_distribution_delta": action_delta,
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
    max_action_ratio_increase: float | None = None,
    max_action_distribution_l1_delta: float | None = None,
    max_normalized_entropy_drop: float | None = None,
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
        collect_context_errors(label, baseline_report, candidate_report, errors)

        baseline_maps = map_by_id(baseline_report)
        candidate_maps = map_by_id(candidate_report)
        baseline_policy_summaries = policy_summary_by_map(baseline_report)
        candidate_policy_summaries = policy_summary_by_map(candidate_report)
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
                baseline_policy_summary=baseline_policy_summaries.get(map_id),
                candidate_policy_summary=candidate_policy_summaries.get(map_id),
                min_win_rate_delta=min_win_rate_delta,
                max_survival_drop_seconds=max_survival_drop_seconds,
                max_dominant_ratio_increase=max_dominant_ratio_increase,
                max_action_ratio_increase=max_action_ratio_increase,
                max_action_distribution_l1_delta=max_action_distribution_l1_delta,
                max_normalized_entropy_drop=max_normalized_entropy_drop,
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
            "max_action_ratio_increase": max_action_ratio_increase,
            "max_action_distribution_l1_delta": max_action_distribution_l1_delta,
            "max_normalized_entropy_drop": max_normalized_entropy_drop,
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
        "| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Action L1 Δ | Max Action Ratio Δ | Entropy Δ | Status |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for window in report["windows"]:
        for item in window["map_results"]:
            deltas = item["deltas"]
            action_delta = item.get("action_distribution_delta", {})
            action_l1 = action_delta.get("action_distribution_l1_delta")
            max_action = action_delta.get("max_action_ratio_increase") or {}
            entropy_delta = action_delta.get("normalized_action_entropy_delta")
            lines.append(
                "| `{window}` | `{map_id}` | `{win}` | `{survival}` | `{dominant}` | `{action_l1}` | `{action}` | `{entropy}` | `{status}` |".format(
                    window=window["label"],
                    map_id=item["map_id"],
                    win=deltas.get("policy_win_rate"),
                    survival=deltas.get("policy_average_survival_seconds"),
                    dominant=deltas.get("policy_dominant_action_ratio"),
                    action_l1=action_l1,
                    action=max_action.get("delta"),
                    entropy=entropy_delta,
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
    parser.add_argument("--max-action-ratio-increase", type=float, default=None)
    parser.add_argument("--max-action-distribution-l1-delta", type=float, default=None)
    parser.add_argument("--max-normalized-entropy-drop", type=float, default=None)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--markdown", type=Path, default=None)
    parser.add_argument("--allow-regression", action="store_true")
    args = parser.parse_args()

    if args.max_survival_drop_seconds < 0.0:
        parser.error("--max-survival-drop-seconds must be non-negative")
    if args.max_dominant_ratio_increase is not None and args.max_dominant_ratio_increase < 0.0:
        parser.error("--max-dominant-ratio-increase must be non-negative")
    if args.max_action_ratio_increase is not None and args.max_action_ratio_increase < 0.0:
        parser.error("--max-action-ratio-increase must be non-negative")
    if (
        args.max_action_distribution_l1_delta is not None
        and args.max_action_distribution_l1_delta < 0.0
    ):
        parser.error("--max-action-distribution-l1-delta must be non-negative")
    if args.max_normalized_entropy_drop is not None and args.max_normalized_entropy_drop < 0.0:
        parser.error("--max-normalized-entropy-drop must be non-negative")

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
        max_action_ratio_increase=args.max_action_ratio_increase,
        max_action_distribution_l1_delta=args.max_action_distribution_l1_delta,
        max_normalized_entropy_drop=args.max_normalized_entropy_drop,
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
