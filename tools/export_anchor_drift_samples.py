#!/usr/bin/env python3
"""Export high-drift samples between an SB3 policy and behavior-clone anchor."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from python.train.compare_sb3_to_behavior_clone_anchor import (  # noqa: E402
    argmax,
    kl_divergence,
    probability_distribution,
    set_policy_context,
    time_bucket_label,
)
from python.train.train_behavior_clone import (  # noqa: E402
    load_trajectory_dataset,
    summarize_dataset,
)
from python.train.train_sb3 import (  # noqa: E402
    dependency_status,
    load_behavior_clone_policy_with_optional_opening,
    policy_action_scores,
    require_dependencies,
    stable_baselines_model_classes,
)


TIME_BUCKET_CHOICES = {
    "all",
    "opening_lt_60",
    "mid_60_to_180",
    "late_180_to_300",
    "post_300",
}


def parse_csv_filter(value: str | None) -> set[str] | None:
    if value is None or value.strip() == "":
        return None
    result = {item.strip() for item in value.split(",") if item.strip()}
    return result or None


def parse_time_bucket_filter(value: str | None) -> set[str] | None:
    labels = parse_csv_filter(value)
    if labels is None or "all" in labels:
        return None
    unknown = sorted(labels - TIME_BUCKET_CHOICES)
    if unknown:
        raise ValueError(f"unknown time bucket(s): {', '.join(unknown)}")
    return labels


def top_actions(probabilities: list[float], top_k: int) -> list[dict[str, Any]]:
    ranked = sorted(
        enumerate(probabilities),
        key=lambda item: (-item[1], item[0]),
    )[:top_k]
    return [
        {"action": str(action), "probability": round(float(score), 6)}
        for action, score in ranked
    ]


def build_drift_row(
    *,
    index: int,
    observation: list[float],
    sample: dict[str, Any],
    anchor_probabilities: list[float],
    candidate_probabilities: list[float],
    include_observation: bool = False,
    top_k: int = 3,
) -> dict[str, Any]:
    anchor_action = int(argmax(anchor_probabilities))
    candidate_action = int(argmax(candidate_probabilities))
    kl_value = float(kl_divergence(anchor_probabilities, candidate_probabilities))
    row = {
        "record_type": "anchor_drift_sample",
        "schema_version": 1,
        "sample_role": "repair_diagnostics",
        "sample_index": int(index),
        "path": sample.get("path"),
        "map_id": sample.get("map_id") or "unknown",
        "seed": sample.get("seed"),
        "time_seconds": round(float(sample.get("time_seconds", 0.0)), 4),
        "time_bucket": time_bucket_label(sample.get("time_seconds", 0.0)),
        "dataset_action": int(sample.get("action", -1)),
        "anchor_action": anchor_action,
        "candidate_action": candidate_action,
        "argmax_agree": anchor_action == candidate_action,
        "kl_divergence": round(kl_value, 6),
        "anchor_action_probability": round(float(anchor_probabilities[anchor_action]), 6),
        "candidate_action_probability": round(float(candidate_probabilities[candidate_action]), 6),
        "anchor_probability_for_candidate_action": round(
            float(anchor_probabilities[candidate_action]), 6
        ),
        "candidate_probability_for_anchor_action": round(
            float(candidate_probabilities[anchor_action]), 6
        ),
        "anchor_top_actions": top_actions(anchor_probabilities, top_k),
        "candidate_top_actions": top_actions(candidate_probabilities, top_k),
        "limitations": [
            "This row is offline anchor-drift diagnostic evidence only.",
            "It is not RL policy acceptance evidence.",
            "Use deterministic high-pressure and no-regression gates before promoting any repair.",
        ],
    }
    if include_observation:
        row["observation"] = observation
    return row


def should_keep_row(
    row: dict[str, Any],
    *,
    map_filter: set[str] | None = None,
    time_bucket_filter: set[str] | None = None,
    min_kl: float = 0.0,
    only_disagreement: bool = False,
) -> bool:
    if map_filter is not None and row.get("map_id") not in map_filter:
        return False
    if time_bucket_filter is not None and row.get("time_bucket") not in time_bucket_filter:
        return False
    if float(row.get("kl_divergence", 0.0)) < min_kl:
        return False
    if only_disagreement and bool(row.get("argmax_agree")):
        return False
    return True


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_map: dict[str, dict[str, Any]] = {}
    by_time_bucket: dict[str, dict[str, Any]] = {}
    for row in rows:
        for table, key in ((by_map, row["map_id"]), (by_time_bucket, row["time_bucket"])):
            bucket = table.setdefault(
                key,
                {
                    "sample_count": 0,
                    "kl_total": 0.0,
                    "max_kl": 0.0,
                    "argmax_disagreement_count": 0,
                    "anchor_action_counts": {},
                    "candidate_action_counts": {},
                },
            )
            bucket["sample_count"] += 1
            bucket["kl_total"] += float(row["kl_divergence"])
            bucket["max_kl"] = max(bucket["max_kl"], float(row["kl_divergence"]))
            if not row["argmax_agree"]:
                bucket["argmax_disagreement_count"] += 1
            for field, target in (
                ("anchor_action", "anchor_action_counts"),
                ("candidate_action", "candidate_action_counts"),
            ):
                action = str(row[field])
                bucket[target][action] = bucket[target].get(action, 0) + 1

    def finalize(table: dict[str, dict[str, Any]]) -> dict[str, Any]:
        result = {}
        for key, value in sorted(table.items()):
            count = max(1, int(value["sample_count"]))
            result[key] = {
                "sample_count": int(value["sample_count"]),
                "mean_kl": round(float(value["kl_total"]) / count, 6),
                "max_kl": round(float(value["max_kl"]), 6),
                "argmax_disagreement_count": int(value["argmax_disagreement_count"]),
                "argmax_disagreement_ratio": round(
                    float(value["argmax_disagreement_count"]) / count,
                    4,
                ),
                "anchor_action_counts": dict(sorted(value["anchor_action_counts"].items())),
                "candidate_action_counts": dict(sorted(value["candidate_action_counts"].items())),
            }
        return result

    total = len(rows)
    return {
        "sample_count": total,
        "mean_kl": round(
            sum(float(row["kl_divergence"]) for row in rows) / max(1, total),
            6,
        ),
        "max_kl": round(
            max((float(row["kl_divergence"]) for row in rows), default=0.0),
            6,
        ),
        "argmax_disagreement_count": sum(1 for row in rows if not row["argmax_agree"]),
        "argmax_disagreement_ratio": round(
            sum(1 for row in rows if not row["argmax_agree"]) / max(1, total),
            4,
        ),
        "by_map": finalize(by_map),
        "by_time_bucket": finalize(by_time_bucket),
    }


def filter_and_rank_rows(
    rows: list[dict[str, Any]],
    *,
    map_filter: set[str] | None = None,
    time_bucket_filter: set[str] | None = None,
    min_kl: float = 0.0,
    only_disagreement: bool = False,
    top: int | None = None,
) -> list[dict[str, Any]]:
    filtered = [
        row
        for row in rows
        if should_keep_row(
            row,
            map_filter=map_filter,
            time_bucket_filter=time_bucket_filter,
            min_kl=min_kl,
            only_disagreement=only_disagreement,
        )
    ]
    filtered.sort(
        key=lambda row: (
            -float(row["kl_divergence"]),
            str(row.get("map_id") or ""),
            float(row.get("time_seconds") or 0.0),
            int(row.get("sample_index") or 0),
        )
    )
    if top is not None:
        return filtered[:top]
    return filtered


def collect_drift_rows(
    *,
    dataset: dict[str, Any],
    candidate_policy: Any,
    anchor_policy: Any,
    sample_stride: int = 1,
    limit_samples: int | None = None,
    include_observation: bool = False,
    top_k: int = 3,
) -> tuple[list[dict[str, Any]], int]:
    if sample_stride <= 0:
        raise ValueError("sample_stride must be greater than zero")
    if limit_samples is not None and limit_samples <= 0:
        raise ValueError("limit_samples must be greater than zero")

    action_count = int(dataset["action_count"])
    rows: list[dict[str, Any]] = []
    active_episode = None
    inspected = 0
    for index, (observation, sample) in enumerate(
        zip(dataset["observations"], dataset["sample_metadata"])
    ):
        if index % sample_stride != 0:
            continue
        if limit_samples is not None and inspected >= limit_samples:
            break
        episode_key = (sample.get("path"), sample.get("seed"), sample.get("map_id"))
        if episode_key != active_episode:
            for policy in (candidate_policy, anchor_policy):
                reset = getattr(policy, "reset", None)
                if callable(reset):
                    reset()
                set_map_id = getattr(policy, "set_map_id", None)
                if callable(set_map_id):
                    set_map_id(sample.get("map_id"))
            active_episode = episode_key
        for policy in (candidate_policy, anchor_policy):
            set_policy_context(policy, sample)
        anchor_probabilities = probability_distribution(
            policy_action_scores(anchor_policy, observation),
            action_count,
        )
        candidate_probabilities = probability_distribution(
            policy_action_scores(candidate_policy, observation),
            action_count,
        )
        rows.append(
            build_drift_row(
                index=index,
                observation=observation,
                sample=sample,
                anchor_probabilities=anchor_probabilities,
                candidate_probabilities=candidate_probabilities,
                include_observation=include_observation,
                top_k=top_k,
            )
        )
        inspected += 1
    return rows, inspected


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Anchor Drift Samples",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Inspected samples: `{report['inspected_sample_count']}`",
        f"- Matched samples: `{report['matched_sample_count']}`",
        f"- Exported samples: `{report['exported_sample_count']}`",
        f"- Time bucket filter: `{report['filters']['time_buckets']}`",
        f"- Map filter: `{report['filters']['maps']}`",
        f"- Minimum KL: `{report['filters']['min_kl']}`",
        f"- Only disagreement: `{report['filters']['only_disagreement']}`",
        f"- Include observation: `{report['filters']['include_observation']}`",
        "",
        "## Summary",
        "",
        "| Scope | Samples | Mean KL | Max KL | Disagreement |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    summary = report["export_summary"]
    lines.append(
        "| `overall` | `{sample_count}` | `{mean_kl}` | `{max_kl}` | `{ratio}` |".format(
            sample_count=summary["sample_count"],
            mean_kl=summary["mean_kl"],
            max_kl=summary["max_kl"],
            ratio=summary["argmax_disagreement_ratio"],
        )
    )
    lines.extend(["", "## By Map", "", "| Map | Samples | Mean KL | Max KL | Disagreement |", "| --- | ---: | ---: | ---: | ---: |"])
    for key, item in summary["by_map"].items():
        lines.append(
            f"| `{key}` | `{item['sample_count']}` | `{item['mean_kl']}` | `{item['max_kl']}` | `{item['argmax_disagreement_ratio']}` |"
        )
    lines.extend(["", "## By Time Bucket", "", "| Bucket | Samples | Mean KL | Max KL | Disagreement |", "| --- | ---: | ---: | ---: | ---: |"])
    for key, item in summary["by_time_bucket"].items():
        lines.append(
            f"| `{key}` | `{item['sample_count']}` | `{item['mean_kl']}` | `{item['max_kl']}` | `{item['argmax_disagreement_ratio']}` |"
        )
    if report["top_examples"]:
        lines.extend(["", "## Top Examples", "", "| Map | Seed | Time | KL | Anchor | Candidate |", "| --- | ---: | ---: | ---: | ---: | ---: |"])
        for row in report["top_examples"]:
            lines.append(
                "| `{map_id}` | `{seed}` | `{time}` | `{kl}` | `{anchor}` | `{candidate}` |".format(
                    map_id=row["map_id"],
                    seed=row.get("seed"),
                    time=row["time_seconds"],
                    kl=row["kl_divergence"],
                    anchor=row["anchor_action"],
                    candidate=row["candidate_action"],
                )
            )
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_report(
    *,
    dataset: dict[str, Any],
    all_row_count: int,
    inspected_sample_count: int,
    matched_rows: list[dict[str, Any]],
    exported_rows: list[dict[str, Any]],
    args: argparse.Namespace,
) -> dict[str, Any]:
    return {
        "report_version": 1,
        "decision": "anchor_drift_samples_recorded",
        "gate_decision": "anchor_drift_samples_recorded_not_policy_gate",
        "candidate_model": args.model,
        "anchor_model": args.anchor_model,
        "opening_model": args.opening_model,
        "opening_seconds": args.opening_seconds if args.opening_model else None,
        "dependency_status": dependency_status(),
        "dataset": summarize_dataset(dataset),
        "all_drift_row_count": all_row_count,
        "inspected_sample_count": inspected_sample_count,
        "matched_sample_count": len(matched_rows),
        "exported_sample_count": len(exported_rows),
        "output_path": args.out,
        "filters": {
            "maps": sorted(parse_csv_filter(args.map_id) or ["all"]),
            "time_buckets": sorted(parse_time_bucket_filter(args.time_bucket) or ["all"]),
            "min_kl": args.min_kl,
            "only_disagreement": bool(args.only_disagreement),
            "top": args.top,
            "sample_stride": args.sample_stride,
            "limit_samples": args.limit_samples,
            "include_observation": bool(args.include_observation),
        },
        "matched_summary": summarize_rows(matched_rows),
        "export_summary": summarize_rows(exported_rows),
        "top_examples": [
            {
                key: row.get(key)
                for key in (
                    "map_id",
                    "seed",
                    "time_seconds",
                    "time_bucket",
                    "kl_divergence",
                    "anchor_action",
                    "candidate_action",
                    "argmax_agree",
                )
            }
            for row in exported_rows[:10]
        ],
        "limitations": [
            "This report is offline anchor-drift diagnostic evidence only.",
            "Exported rows are not RL policy acceptance evidence.",
            "Any repair trained from these rows must rerun deterministic high-pressure, no-regression, and repair-probe gates.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export high-drift anchor/candidate samples.")
    parser.add_argument("--algorithm", choices=["dqn", "ppo"], default="ppo")
    parser.add_argument("--model", required=True)
    parser.add_argument("--anchor-model", required=True)
    parser.add_argument("--opening-model", default=None)
    parser.add_argument("--opening-seconds", type=float, default=60.0)
    parser.add_argument("--dataset", action="append", required=True)
    parser.add_argument("--map-id", default=None, help="Comma-separated map ids to keep.")
    parser.add_argument(
        "--time-bucket",
        default="all",
        help="Comma-separated time buckets to keep, or all.",
    )
    parser.add_argument("--min-kl", type=float, default=0.0)
    parser.add_argument("--only-disagreement", action="store_true")
    parser.add_argument("--top", type=int, default=200)
    parser.add_argument("--sample-stride", type=int, default=1)
    parser.add_argument("--limit-samples", type=int, default=None)
    parser.add_argument("--top-actions", type=int, default=3)
    parser.add_argument("--include-observation", action="store_true")
    parser.add_argument("--out", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--markdown", default=None)
    args = parser.parse_args()

    if args.opening_seconds <= 0.0:
        parser.error("--opening-seconds must be greater than zero")
    if args.min_kl < 0.0:
        parser.error("--min-kl must be non-negative")
    if args.top <= 0:
        parser.error("--top must be greater than zero")
    if args.sample_stride <= 0:
        parser.error("--sample-stride must be greater than zero")
    if args.limit_samples is not None and args.limit_samples <= 0:
        parser.error("--limit-samples must be greater than zero")
    if args.top_actions <= 0:
        parser.error("--top-actions must be greater than zero")
    try:
        time_bucket_filter = parse_time_bucket_filter(args.time_bucket)
    except ValueError as exc:
        parser.error(str(exc))
    map_filter = parse_csv_filter(args.map_id)

    require_dependencies()
    dataset = load_trajectory_dataset(args.dataset, limit=None)
    model_class = stable_baselines_model_classes()[args.algorithm]
    candidate_policy = model_class.load(args.model)
    anchor_policy = load_behavior_clone_policy_with_optional_opening(
        args.algorithm,
        Path(args.anchor_model),
        opening_model_path=Path(args.opening_model) if args.opening_model else None,
        opening_seconds=args.opening_seconds,
    )
    all_rows, inspected_sample_count = collect_drift_rows(
        dataset=dataset,
        candidate_policy=candidate_policy,
        anchor_policy=anchor_policy,
        sample_stride=args.sample_stride,
        limit_samples=args.limit_samples,
        include_observation=args.include_observation,
        top_k=args.top_actions,
    )
    matched_rows = filter_and_rank_rows(
        all_rows,
        map_filter=map_filter,
        time_bucket_filter=time_bucket_filter,
        min_kl=args.min_kl,
        only_disagreement=args.only_disagreement,
        top=None,
    )
    exported_rows = matched_rows[: args.top]
    write_jsonl(Path(args.out), exported_rows)
    report = build_report(
        dataset=dataset,
        all_row_count=len(all_rows),
        inspected_sample_count=inspected_sample_count,
        matched_rows=matched_rows,
        exported_rows=exported_rows,
        args=args,
    )
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown:
        write_markdown(report, Path(args.markdown))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
