#!/usr/bin/env python3
"""Export a clean subset of late risk-recovery supervision samples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

from validate_risk_recovery_samples import (
    action_risk_score,
    as_number,
    build_report as build_validation_report,
    computed_risk_reasons,
    load_samples,
    summarize_distribution,
    summarize_reasons,
    validate_sample,
)


INTERNAL_KEYS = {"_source_path", "_source_line"}


def strip_internal_keys(sample: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in sample.items() if key not in INTERNAL_KEYS}


def normalize_paths(paths: Path | Iterable[Path]) -> list[Path]:
    if isinstance(paths, Path):
        return [paths]
    return [Path(path) for path in paths]


def parse_csv_filter(value: str | None) -> set[str] | None:
    if value is None:
        return None
    items = {item.strip() for item in value.split(",") if item.strip()}
    if not items:
        raise ValueError("filter must include at least one value")
    return items


def sample_risk_metrics(sample: dict[str, Any]) -> dict[str, Any]:
    decision = sample.get("adapter_decision") if isinstance(sample.get("adapter_decision"), dict) else {}
    diagnostics = sample.get("diagnostics") if isinstance(sample.get("diagnostics"), dict) else {}
    time_seconds = as_number(sample.get("time_seconds")) or 0.0
    original_action = int(sample.get("original_action", 0))
    target_action = int(sample.get("target_action", 0))
    original_score = action_risk_score(
        original_action,
        diagnostics=diagnostics,
        decision=decision,
    )
    target_score = action_risk_score(
        target_action,
        diagnostics=diagnostics,
        decision=decision,
    )
    target_risk_reasons = computed_risk_reasons(
        target_action,
        diagnostics=diagnostics,
        decision=decision,
        time_seconds=float(time_seconds),
    )
    return {
        "original_risk_score": original_score,
        "target_risk_score": target_score,
        "target_risk_delta": round(target_score - original_score, 6),
        "target_risk_reasons": target_risk_reasons,
    }


def write_samples(path: Path, samples: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for sample in samples:
            handle.write(json.dumps(strip_internal_keys(sample), ensure_ascii=False, sort_keys=True) + "\n")


def build_filter_report(
    paths: Path | Iterable[Path],
    *,
    out: Path,
    allow_target_risk: bool = False,
    allow_worse_target_risk: bool = False,
    target_risk_tolerance: float = 1e-6,
    max_target_risk_score: float | None = None,
    map_filter: set[str] | None = None,
    min_seconds: float | None = None,
    max_seconds: float | None = None,
) -> dict[str, Any]:
    sample_paths = normalize_paths(paths)
    samples = load_samples(sample_paths)
    kept: list[dict[str, Any]] = []
    invalid_count = 0
    target_risk_count = 0
    worse_target_risk_count = 0
    max_target_risk_count = 0
    map_filtered_count = 0
    time_filtered_count = 0
    warning_count = 0
    drop_examples: list[dict[str, Any]] = []

    for sample in samples:
        errors: list[str] = []
        warnings: list[str] = []
        validate_sample(sample, errors, warnings)
        warning_count += len(warnings)
        if errors:
            invalid_count += 1
            if len(drop_examples) < 10:
                drop_examples.append(
                    {
                        "reason": "invalid_sample",
                        "source": sample.get("_source_path"),
                        "line": sample.get("_source_line"),
                        "errors": errors[:3],
                    }
                )
            continue

        if map_filter is not None and str(sample.get("map_id")) not in map_filter:
            map_filtered_count += 1
            if len(drop_examples) < 10:
                drop_examples.append(
                    {
                        "reason": "map_filter",
                        "source": sample.get("_source_path"),
                        "line": sample.get("_source_line"),
                        "map_id": sample.get("map_id"),
                    }
                )
            continue

        time_seconds = as_number(sample.get("time_seconds")) or 0.0
        if min_seconds is not None and time_seconds < min_seconds:
            time_filtered_count += 1
            if len(drop_examples) < 10:
                drop_examples.append(
                    {
                        "reason": "time_window",
                        "source": sample.get("_source_path"),
                        "line": sample.get("_source_line"),
                        "time_seconds": time_seconds,
                    }
                )
            continue
        if max_seconds is not None and time_seconds >= max_seconds:
            time_filtered_count += 1
            if len(drop_examples) < 10:
                drop_examples.append(
                    {
                        "reason": "time_window",
                        "source": sample.get("_source_path"),
                        "line": sample.get("_source_line"),
                        "time_seconds": time_seconds,
                    }
                )
            continue

        metrics = sample_risk_metrics(sample)
        target_reasons = metrics["target_risk_reasons"]
        if target_reasons and not allow_target_risk:
            target_risk_count += 1
            if len(drop_examples) < 10:
                drop_examples.append(
                    {
                        "reason": "target_risk_reasons",
                        "source": sample.get("_source_path"),
                        "line": sample.get("_source_line"),
                        "target_risk_reasons": target_reasons,
                    }
                )
            continue

        if (
            metrics["target_risk_delta"] > target_risk_tolerance
            and not allow_worse_target_risk
        ):
            worse_target_risk_count += 1
            if len(drop_examples) < 10:
                drop_examples.append(
                    {
                        "reason": "worse_target_risk_score",
                        "source": sample.get("_source_path"),
                        "line": sample.get("_source_line"),
                        "target_risk_delta": metrics["target_risk_delta"],
                    }
                )
            continue

        if (
            max_target_risk_score is not None
            and metrics["target_risk_score"] > max_target_risk_score
        ):
            max_target_risk_count += 1
            if len(drop_examples) < 10:
                drop_examples.append(
                    {
                        "reason": "above_max_target_risk_score",
                        "source": sample.get("_source_path"),
                        "line": sample.get("_source_line"),
                        "target_risk_score": metrics["target_risk_score"],
                    }
                )
            continue

        kept.append(sample)

    write_samples(out, kept)
    validation_report = build_validation_report(out) if kept else None
    drop_count = len(samples) - len(kept)
    return {
        "report_version": 1,
        "decision": (
            "risk_recovery_clean_samples_exported"
            if kept
            else "risk_recovery_clean_samples_unavailable"
        ),
        "sources": [str(path) for path in sample_paths],
        "out": str(out),
        "input_sample_count": len(samples),
        "kept_sample_count": len(kept),
        "drop_count": drop_count,
        "drop_reasons": {
            "invalid_sample": invalid_count,
            "target_risk_reasons": target_risk_count,
            "worse_target_risk_score": worse_target_risk_count,
            "above_max_target_risk_score": max_target_risk_count,
            "map_filter": map_filtered_count,
            "time_window": time_filtered_count,
        },
        "source_warning_count": warning_count,
        "filter": {
            "allow_target_risk": allow_target_risk,
            "allow_worse_target_risk": allow_worse_target_risk,
            "target_risk_tolerance": target_risk_tolerance,
            "max_target_risk_score": max_target_risk_score,
            "map_filter": sorted(map_filter) if map_filter is not None else None,
            "min_seconds": min_seconds,
            "max_seconds": max_seconds,
        },
        "kept_original_action_distribution": summarize_distribution(kept, "original_action"),
        "kept_target_action_distribution": summarize_distribution(kept, "target_action"),
        "kept_risk_reason_distribution": summarize_reasons(kept, "risk_reasons"),
        "validation_decision": validation_report.get("decision") if validation_report else None,
        "drop_examples": drop_examples,
        "limitations": [
            "Clean risk-recovery subsets are still adapter-derived repair training inputs.",
            "Filtering removes obvious target-risk rows; it does not prove policy quality.",
            "Any policy trained with this output still needs deterministic high-pressure gates and failure-case review.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Clean Risk Recovery Samples",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Input samples: `{report['input_sample_count']}`",
        f"- Kept samples: `{report['kept_sample_count']}`",
        f"- Dropped samples: `{report['drop_count']}`",
        f"- Output: `{report['out']}`",
        f"- Validation decision: `{report['validation_decision']}`",
        "",
        "## Drop Reasons",
    ]
    for reason, count in report["drop_reasons"].items():
        lines.append(f"- `{reason}`: {count}")
    lines.extend(["", "## Kept Target Actions"])
    for action, count in report["kept_target_action_distribution"].items():
        lines.append(f"- `{action}`: {count}")
    lines.extend(["", "## Kept Risk Reasons"])
    for reason, count in report["kept_risk_reason_distribution"].items():
        lines.append(f"- `{reason}`: {count}")
    lines.extend(["", "## Drop Examples"])
    if report["drop_examples"]:
        for example in report["drop_examples"]:
            lines.append(f"- `{json.dumps(example, ensure_ascii=False, sort_keys=True)}`")
    else:
        lines.append("- None")
    lines.extend(["", "## Limitations"])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Export clean late risk-recovery supervision samples.")
    parser.add_argument("samples", type=Path, nargs="+", help="Risk recovery JSONL sample paths.")
    parser.add_argument("--out", type=Path, required=True, help="Output clean JSONL sample path.")
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--markdown", type=Path, default=None)
    parser.add_argument(
        "--allow-target-risk",
        action="store_true",
        help="Keep rows whose target action still has adapter target_risk_reasons.",
    )
    parser.add_argument(
        "--allow-worse-target-risk",
        action="store_true",
        help="Keep rows whose target risk score is higher than the original action's score.",
    )
    parser.add_argument(
        "--target-risk-tolerance",
        type=float,
        default=1e-6,
        help="Tolerance when comparing target risk score against original risk score.",
    )
    parser.add_argument(
        "--max-target-risk-score",
        type=float,
        default=None,
        help="Optional maximum continuous target risk score to keep.",
    )
    parser.add_argument(
        "--map-id",
        default=None,
        help="Optional comma-separated map ids to keep after clean-risk filtering.",
    )
    parser.add_argument(
        "--min-seconds",
        type=float,
        default=None,
        help="Optional inclusive lower time bound to keep.",
    )
    parser.add_argument(
        "--max-seconds",
        type=float,
        default=None,
        help="Optional exclusive upper time bound to keep.",
    )
    args = parser.parse_args()
    if args.target_risk_tolerance < 0.0:
        parser.error("--target-risk-tolerance must be non-negative")
    if args.max_target_risk_score is not None and args.max_target_risk_score < 0.0:
        parser.error("--max-target-risk-score must be non-negative")
    try:
        map_filter = parse_csv_filter(args.map_id)
    except ValueError as exc:
        parser.error(f"--map-id {exc}")
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

    report = build_filter_report(
        args.samples,
        out=args.out,
        allow_target_risk=args.allow_target_risk,
        allow_worse_target_risk=args.allow_worse_target_risk,
        target_risk_tolerance=args.target_risk_tolerance,
        max_target_risk_score=args.max_target_risk_score,
        map_filter=map_filter,
        min_seconds=args.min_seconds,
        max_seconds=args.max_seconds,
    )
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    if args.markdown:
        write_markdown(report, args.markdown)
    if not args.report:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "risk_recovery_clean_samples_exported" else 1


if __name__ == "__main__":
    raise SystemExit(main())
