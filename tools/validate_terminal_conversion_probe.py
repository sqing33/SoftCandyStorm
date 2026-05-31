#!/usr/bin/env python3
"""Validate terminal-conversion branch probe evidence.

This gate is deliberately narrower than RL acceptance. It answers one question:
did a terminal-conversion branch both run in the target online window and improve
the target map without violating the supplied no-regression evidence?
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


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


def summary_map_entries(report: dict[str, Any]) -> list[dict[str, Any]]:
    summary = report.get("summary")
    if isinstance(summary, dict) and isinstance(summary.get("maps"), list):
        return [item for item in summary["maps"] if isinstance(item, dict)]
    return []


def policy_map_entries(report: dict[str, Any]) -> list[dict[str, Any]]:
    maps = report.get("maps")
    if isinstance(maps, list):
        return [item for item in maps if isinstance(item, dict)]
    policy = report.get("policy")
    if isinstance(policy, dict):
        return [
            {
                "map_id": report.get("map_id") or policy.get("map_id"),
                "policy": policy,
                "policy_adapter": policy.get("policy_adapter") or report.get("policy_adapter"),
            }
        ]
    return []


def summary_for_map(report: dict[str, Any], map_id: str) -> dict[str, Any] | None:
    for item in summary_map_entries(report):
        if item.get("map_id") == map_id:
            return item
    for item in policy_map_entries(report):
        if item.get("map_id") != map_id:
            continue
        policy = item.get("policy")
        if isinstance(policy, dict) and isinstance(policy.get("summary"), dict):
            summary = dict(policy["summary"])
            summary.setdefault("map_id", map_id)
            return summary
    return None


def adapter_for_map(report: dict[str, Any], map_id: str) -> dict[str, Any] | None:
    for item in policy_map_entries(report):
        if item.get("map_id") != map_id:
            continue
        adapter = item.get("policy_adapter")
        if isinstance(adapter, dict):
            return adapter
        policy = item.get("policy")
        if isinstance(policy, dict) and isinstance(policy.get("policy_adapter"), dict):
            return policy["policy_adapter"]
    adapter = report.get("policy_adapter")
    return adapter if isinstance(adapter, dict) else None


def iter_adapters(adapter: dict[str, Any]) -> list[dict[str, Any]]:
    found = [adapter]
    for key in (
        "wrapped_policy_adapter",
        "base_policy_adapter",
        "branch_policy_adapter",
        "terminal_policy_adapter",
    ):
        child = adapter.get(key)
        if isinstance(child, dict):
            found.extend(iter_adapters(child))
    return found


def usage_entry_count(entry: dict[str, Any], primary_key: str, fallback_key: str) -> int:
    value = entry.get(primary_key)
    if isinstance(value, int):
        return value
    value = entry.get(fallback_key)
    if isinstance(value, int):
        return value
    return 0


def usage_entry_ratio(entry: dict[str, Any], primary_key: str, fallback_key: str) -> float:
    ratio_key = primary_key.replace("_decisions", "_ratio")
    value = as_number(entry.get(ratio_key))
    if value is not None:
        return value
    total = as_number(entry.get("total_decisions"))
    count = float(usage_entry_count(entry, primary_key, fallback_key))
    if total and total > 0:
        return count / total
    return 0.0


def terminal_usage(report: dict[str, Any], map_id: str, time_bucket: str | None) -> dict[str, Any]:
    adapter = adapter_for_map(report, map_id)
    if adapter is None:
        return {
            "found": False,
            "map_total_decisions": 0,
            "map_terminal_decisions": 0,
            "map_terminal_ratio": 0.0,
            "bucket": time_bucket,
            "bucket_total_decisions": 0,
            "bucket_terminal_decisions": 0,
            "bucket_terminal_ratio": 0.0,
        }

    usage_reports: list[dict[str, Any]] = []
    for candidate in iter_adapters(adapter):
        if candidate.get("mode") != "terminal_conversion_branch":
            continue
        usage = candidate.get("usage")
        if not isinstance(usage, dict):
            continue
        by_map = usage.get("by_map")
        map_usage = by_map.get(map_id) if isinstance(by_map, dict) else None
        if not isinstance(map_usage, dict):
            map_usage = usage
        by_time_bucket = usage.get("by_time_bucket")
        bucket_usage = (
            by_time_bucket.get(time_bucket)
            if time_bucket and isinstance(by_time_bucket, dict)
            else None
        )
        if not isinstance(bucket_usage, dict):
            bucket_usage = {}
        usage_reports.append(
            {
                "found": True,
                "mode": candidate.get("mode"),
                "target_maps": candidate.get("target_maps"),
                "map_total_decisions": int(map_usage.get("total_decisions", 0) or 0),
                "map_terminal_decisions": usage_entry_count(
                    map_usage,
                    "terminal_decisions",
                    "branch_decisions",
                ),
                "map_terminal_ratio": round(
                    usage_entry_ratio(map_usage, "terminal_decisions", "branch_decisions"),
                    6,
                ),
                "bucket": time_bucket,
                "bucket_total_decisions": int(bucket_usage.get("total_decisions", 0) or 0),
                "bucket_terminal_decisions": usage_entry_count(
                    bucket_usage,
                    "terminal_decisions",
                    "branch_decisions",
                ),
                "bucket_terminal_ratio": round(
                    usage_entry_ratio(bucket_usage, "terminal_decisions", "branch_decisions"),
                    6,
                ),
            }
        )

    if not usage_reports:
        return {
            "found": False,
            "map_total_decisions": 0,
            "map_terminal_decisions": 0,
            "map_terminal_ratio": 0.0,
            "bucket": time_bucket,
            "bucket_total_decisions": 0,
            "bucket_terminal_decisions": 0,
            "bucket_terminal_ratio": 0.0,
        }
    return max(
        usage_reports,
        key=lambda item: (item["bucket_terminal_decisions"], item["map_terminal_decisions"]),
    )


def metric(summary: dict[str, Any] | None, keys: tuple[str, ...]) -> float | None:
    if not isinstance(summary, dict):
        return None
    for key in keys:
        value = as_number(summary.get(key))
        if value is not None:
            return value
    return None


def validate_window_regression(path: Path | None, blockers: list[str], errors: list[str]) -> dict[str, Any] | None:
    if path is None:
        return None
    try:
        payload = load_json_object(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"window_regression: unable to load {path}: {exc}")
        return None
    decision = payload.get("decision") or payload.get("gate_decision")
    report_blockers = payload.get("blockers")
    blocker_count = len(report_blockers) if isinstance(report_blockers, list) else 0
    if decision != "policy_window_regression_passed":
        blockers.append(f"window_regression: expected policy_window_regression_passed, got {decision}")
    return {
        "path": str(path),
        "decision": decision,
        "blocker_count": blocker_count,
    }


def build_report(
    baseline_windows: dict[str, Path],
    candidate_windows: dict[str, Path],
    target_map: str,
    target_window: str,
    terminal_time_bucket: str | None,
    min_target_win_rate: float | None,
    min_win_rate_delta: float,
    min_survival_delta: float,
    min_terminal_decisions: int,
    min_terminal_ratio: float,
    min_bucket_terminal_decisions: int | None,
    min_bucket_terminal_ratio: float | None,
    window_regression: Path | None,
) -> dict[str, Any]:
    errors: list[str] = []
    blockers: list[str] = []
    warnings: list[str] = []

    baseline_report = None
    candidate_report = None
    try:
        baseline_report = load_json_object(baseline_windows[target_window])
    except KeyError:
        errors.append(f"target_window `{target_window}` missing from baseline windows")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"baseline {target_window}: unable to load report: {exc}")
    try:
        candidate_report = load_json_object(candidate_windows[target_window])
    except KeyError:
        errors.append(f"target_window `{target_window}` missing from candidate windows")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"candidate {target_window}: unable to load report: {exc}")

    baseline_summary = summary_for_map(baseline_report or {}, target_map)
    candidate_summary = summary_for_map(candidate_report or {}, target_map)
    if baseline_report is not None and baseline_summary is None:
        errors.append(f"baseline {target_window}: target map `{target_map}` missing")
    if candidate_report is not None and candidate_summary is None:
        errors.append(f"candidate {target_window}: target map `{target_map}` missing")

    baseline_win_rate = metric(baseline_summary, ("policy_win_rate", "win_rate"))
    candidate_win_rate = metric(candidate_summary, ("policy_win_rate", "win_rate"))
    baseline_survival = metric(
        baseline_summary,
        ("policy_average_survival_seconds", "average_survival_seconds"),
    )
    candidate_survival = metric(
        candidate_summary,
        ("policy_average_survival_seconds", "average_survival_seconds"),
    )
    win_rate_delta = (
        None
        if baseline_win_rate is None or candidate_win_rate is None
        else round(candidate_win_rate - baseline_win_rate, 6)
    )
    survival_delta = (
        None
        if baseline_survival is None or candidate_survival is None
        else round(candidate_survival - baseline_survival, 6)
    )
    if candidate_win_rate is None:
        errors.append("candidate target win rate missing")
    elif min_target_win_rate is not None and candidate_win_rate < min_target_win_rate:
        blockers.append(
            f"{target_window}/{target_map}: win_rate {candidate_win_rate:.4f} "
            f"below required {min_target_win_rate:.4f}"
        )
    if win_rate_delta is None:
        errors.append("target win-rate delta unavailable")
    elif win_rate_delta < min_win_rate_delta:
        blockers.append(
            f"{target_window}/{target_map}: win_rate delta {win_rate_delta:.4f} "
            f"below required {min_win_rate_delta:.4f}"
        )
    if survival_delta is None:
        errors.append("target survival delta unavailable")
    elif survival_delta < min_survival_delta:
        blockers.append(
            f"{target_window}/{target_map}: survival delta {survival_delta:.4f}s "
            f"below required {min_survival_delta:.4f}s"
        )

    usage = terminal_usage(candidate_report or {}, target_map, terminal_time_bucket)
    if not usage.get("found"):
        blockers.append(f"{target_window}/{target_map}: terminal_conversion_branch usage not found")
    if usage["map_terminal_decisions"] < min_terminal_decisions:
        blockers.append(
            f"{target_window}/{target_map}: terminal decisions {usage['map_terminal_decisions']} "
            f"below required {min_terminal_decisions}"
        )
    if usage["map_terminal_ratio"] < min_terminal_ratio:
        blockers.append(
            f"{target_window}/{target_map}: terminal ratio {usage['map_terminal_ratio']:.4f} "
            f"below required {min_terminal_ratio:.4f}"
        )
    if min_bucket_terminal_decisions is not None and (
        usage["bucket_terminal_decisions"] < min_bucket_terminal_decisions
    ):
        blockers.append(
            f"{target_window}/{target_map}/{terminal_time_bucket}: terminal decisions "
            f"{usage['bucket_terminal_decisions']} below required {min_bucket_terminal_decisions}"
        )
    if min_bucket_terminal_ratio is not None and usage["bucket_terminal_ratio"] < min_bucket_terminal_ratio:
        blockers.append(
            f"{target_window}/{target_map}/{terminal_time_bucket}: terminal ratio "
            f"{usage['bucket_terminal_ratio']:.4f} below required {min_bucket_terminal_ratio:.4f}"
        )
    if usage.get("found") and candidate_win_rate == 0 and usage["map_terminal_decisions"] > 0:
        warnings.append(
            f"{target_window}/{target_map}: terminal branch was used but produced no victories"
        )

    window_regression_report = validate_window_regression(window_regression, blockers, errors)

    decision = (
        "terminal_conversion_probe_invalid"
        if errors
        else "terminal_conversion_probe_failed"
        if blockers
        else "terminal_conversion_probe_passed_for_limited_followup"
    )
    return {
        "report_version": 1,
        "decision": decision,
        "gate_decision": decision,
        "target": {
            "map_id": target_map,
            "window": target_window,
            "terminal_time_bucket": terminal_time_bucket,
        },
        "criteria": {
            "min_target_win_rate": min_target_win_rate,
            "min_win_rate_delta": min_win_rate_delta,
            "min_survival_delta": min_survival_delta,
            "min_terminal_decisions": min_terminal_decisions,
            "min_terminal_ratio": min_terminal_ratio,
            "min_bucket_terminal_decisions": min_bucket_terminal_decisions,
            "min_bucket_terminal_ratio": min_bucket_terminal_ratio,
        },
        "baseline_windows": {key: str(value) for key, value in sorted(baseline_windows.items())},
        "candidate_windows": {key: str(value) for key, value in sorted(candidate_windows.items())},
        "window_regression": window_regression_report,
        "target_metrics": {
            "baseline_win_rate": baseline_win_rate,
            "candidate_win_rate": candidate_win_rate,
            "win_rate_delta": win_rate_delta,
            "baseline_average_survival_seconds": baseline_survival,
            "candidate_average_survival_seconds": candidate_survival,
            "survival_delta_seconds": survival_delta,
        },
        "terminal_usage": usage,
        "errors": errors,
        "blockers": blockers,
        "warnings": warnings,
        "limitations": [
            "This gate validates terminal-conversion repair evidence only.",
            "Passing allows limited follow-up consideration, not RL acceptance or release promotion.",
            "It depends on supplied comparison and no-regression reports; it does not replay episodes by itself.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    metrics = report["target_metrics"]
    usage = report["terminal_usage"]
    lines = [
        "# Terminal Conversion Probe Gate",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Target: `{report['target']['map_id']}` / `{report['target']['window']}`",
        f"- Errors: `{len(report['errors'])}`",
        f"- Blockers: `{len(report['blockers'])}`",
        f"- Warnings: `{len(report['warnings'])}`",
        "",
        "## Target Metrics",
        "",
        "| Metric | Baseline | Candidate | Delta |",
        "|---|---:|---:|---:|",
        "| Win rate | {baseline} | {candidate} | {delta} |".format(
            baseline=metrics.get("baseline_win_rate"),
            candidate=metrics.get("candidate_win_rate"),
            delta=metrics.get("win_rate_delta"),
        ),
        "| Average survival seconds | {baseline} | {candidate} | {delta} |".format(
            baseline=metrics.get("baseline_average_survival_seconds"),
            candidate=metrics.get("candidate_average_survival_seconds"),
            delta=metrics.get("survival_delta_seconds"),
        ),
        "",
        "## Terminal Usage",
        "",
        f"- Found terminal branch: `{usage.get('found')}`",
        f"- Map terminal decisions: `{usage.get('map_terminal_decisions')}` / `{usage.get('map_total_decisions')}` (`{usage.get('map_terminal_ratio')}`)",
        f"- Bucket: `{usage.get('bucket')}`",
        f"- Bucket terminal decisions: `{usage.get('bucket_terminal_decisions')}` / `{usage.get('bucket_total_decisions')}` (`{usage.get('bucket_terminal_ratio')}`)",
        "",
        "## Blockers",
        "",
    ]
    if report["blockers"]:
        lines.extend(f"- {item}" for item in report["blockers"])
    else:
        lines.append("- None")
    lines.extend(["", "## Errors", ""])
    if report["errors"]:
        lines.extend(f"- {item}" for item in report["errors"])
    else:
        lines.append("- None")
    lines.extend(["", "## Warnings", ""])
    if report["warnings"]:
        lines.extend(f"- {item}" for item in report["warnings"])
    else:
        lines.append("- None")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate terminal conversion probe evidence.")
    parser.add_argument("--baseline-window", action="append", type=parse_window_arg, required=True)
    parser.add_argument("--candidate-window", action="append", type=parse_window_arg, required=True)
    parser.add_argument("--target-map", required=True)
    parser.add_argument("--target-window", default="300s")
    parser.add_argument("--terminal-time-bucket", default="late_180_to_300")
    parser.add_argument("--min-target-win-rate", type=float, default=None)
    parser.add_argument("--min-win-rate-delta", type=float, default=0.0)
    parser.add_argument("--min-survival-delta", type=float, default=0.0)
    parser.add_argument("--min-terminal-decisions", type=int, default=1)
    parser.add_argument("--min-terminal-ratio", type=float, default=0.0)
    parser.add_argument("--min-bucket-terminal-decisions", type=int, default=None)
    parser.add_argument("--min-bucket-terminal-ratio", type=float, default=None)
    parser.add_argument("--window-regression", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--markdown", type=Path, default=None)
    parser.add_argument("--allow-fail", action="store_true")
    args = parser.parse_args()

    if args.min_target_win_rate is not None and not (0.0 <= args.min_target_win_rate <= 1.0):
        parser.error("--min-target-win-rate must be between 0 and 1")
    if not (0.0 <= args.min_terminal_ratio <= 1.0):
        parser.error("--min-terminal-ratio must be between 0 and 1")
    if args.min_bucket_terminal_ratio is not None and not (0.0 <= args.min_bucket_terminal_ratio <= 1.0):
        parser.error("--min-bucket-terminal-ratio must be between 0 and 1")
    if args.min_terminal_decisions < 0:
        parser.error("--min-terminal-decisions must be non-negative")
    if args.min_bucket_terminal_decisions is not None and args.min_bucket_terminal_decisions < 0:
        parser.error("--min-bucket-terminal-decisions must be non-negative")

    try:
        baseline_windows = window_map(args.baseline_window)
        candidate_windows = window_map(args.candidate_window)
    except ValueError as exc:
        parser.error(str(exc))

    report = build_report(
        baseline_windows=baseline_windows,
        candidate_windows=candidate_windows,
        target_map=args.target_map,
        target_window=args.target_window,
        terminal_time_bucket=args.terminal_time_bucket,
        min_target_win_rate=args.min_target_win_rate,
        min_win_rate_delta=args.min_win_rate_delta,
        min_survival_delta=args.min_survival_delta,
        min_terminal_decisions=args.min_terminal_decisions,
        min_terminal_ratio=args.min_terminal_ratio,
        min_bucket_terminal_decisions=args.min_bucket_terminal_decisions,
        min_bucket_terminal_ratio=args.min_bucket_terminal_ratio,
        window_regression=args.window_regression,
    )
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    if report["decision"] == "terminal_conversion_probe_passed_for_limited_followup":
        return 0
    return 0 if args.allow_fail else 1


if __name__ == "__main__":
    raise SystemExit(main())
