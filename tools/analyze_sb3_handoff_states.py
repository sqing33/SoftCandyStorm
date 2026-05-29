#!/usr/bin/env python3
"""Compare SB3 base/late policies on traced handoff observations."""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from python.train.compare_sb3_to_behavior_clone_anchor import (  # noqa: E402
    argmax,
    entropy_nats,
    kl_divergence,
    probability_distribution,
)
from python.train.train_sb3 import (  # noqa: E402
    dependency_status,
    policy_action_scores,
    require_dependencies,
    stable_baselines_model_classes,
)


PRESSURE_FIELDS = [
    "enemy_pressure_risk",
    "hazard_pressure_risk",
    "boss_pressure_risk",
    "low_health_risk",
    "safety_risk_score",
]
PRESSURE_HIGH_THRESHOLD = 0.5


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def trace_paths(inputs: list[Path]) -> list[Path]:
    paths: list[Path] = []
    for item in inputs:
        if item.is_dir():
            paths.extend(sorted(item.rglob("*_trace.json")))
        elif item.is_file():
            paths.append(item)
        else:
            raise ValueError(f"trace input does not exist: {item}")
    return sorted(dict.fromkeys(paths))


def as_float(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        if math.isfinite(float(value)):
            return float(value)
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def maybe_call(policy: Any, method_name: str, *args: Any) -> None:
    method = getattr(policy, method_name, None)
    if callable(method):
        method(*args)


def set_policy_context(policy: Any, sample: dict[str, Any]) -> None:
    maybe_call(
        policy,
        "set_step_context",
        {
            "time_seconds": sample.get("time_seconds", 0.0),
            "map_id": sample.get("map_id"),
            "seed": sample.get("seed"),
            "diagnostics": sample.get("diagnostics", {}),
        },
    )


def window_label(time_seconds: float, split_seconds: float) -> str:
    if time_seconds < split_seconds:
        return "pre_split"
    return "post_split"


def load_trace_samples(
    inputs: list[Path],
    *,
    map_id: str | None = None,
    start_seconds: float | None = None,
    end_seconds: float | None = None,
) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    for path in trace_paths(inputs):
        payload = load_json_object(path)
        episode = payload.get("episode") if isinstance(payload.get("episode"), dict) else {}
        trace_map_id = str(episode.get("map_id") or payload.get("map_id") or "unknown")
        if map_id is not None and trace_map_id != map_id:
            continue
        for step in payload.get("steps", []):
            if not isinstance(step, dict):
                continue
            if "observation" not in step:
                continue
            time_seconds = as_float(step.get("time_seconds"))
            if time_seconds is None:
                continue
            if start_seconds is not None and time_seconds < start_seconds:
                continue
            if end_seconds is not None and time_seconds > end_seconds:
                continue
            samples.append(
                {
                    "trace_path": str(path),
                    "seed": episode.get("seed"),
                    "map_id": trace_map_id,
                    "episode_outcome": episode.get("terminal_kind"),
                    "episode_time_seconds": episode.get("time_seconds"),
                    "step": step.get("step"),
                    "time_seconds": time_seconds,
                    "health": as_float(step.get("health")),
                    "action": step.get("action"),
                    "observation": step["observation"],
                    "diagnostics": step.get("diagnostics", {}),
                }
            )
    return samples


def empty_bucket(action_count: int) -> dict[str, Any]:
    return {
        "sample_count": 0,
        "base_to_late_kl_total": 0.0,
        "late_to_base_kl_total": 0.0,
        "max_base_to_late_kl": 0.0,
        "argmax_agreement_count": 0,
        "base_entropy_total": 0.0,
        "late_entropy_total": 0.0,
        "base_top_counts": Counter({str(action): 0 for action in range(action_count)}),
        "late_top_counts": Counter({str(action): 0 for action in range(action_count)}),
        "trace_action_counts": Counter({str(action): 0 for action in range(action_count)}),
        "trace_matches_base_count": 0,
        "trace_matches_late_count": 0,
        "health_total": 0.0,
        "health_count": 0,
        "health_min": None,
        "boundary_min_total": 0.0,
        "boundary_min_count": 0,
        "boundary_min_min": None,
        "pressure_totals": {field: 0.0 for field in PRESSURE_FIELDS},
        "pressure_counts": {field: 0 for field in PRESSURE_FIELDS},
        "pressure_high_counts": {field: 0 for field in PRESSURE_FIELDS},
    }


def ratio_distribution(counter: Counter[str], sample_count: int) -> dict[str, dict[str, float | int]]:
    return {
        key: {
            "count": int(value),
            "ratio": round(int(value) / max(1, sample_count), 4),
        }
        for key, value in sorted(counter.items(), key=lambda item: int(item[0]))
    }


def record_numeric_summary(
    bucket: dict[str, Any],
    total_key: str,
    count_key: str,
    min_key: str,
    value: float | None,
) -> None:
    if value is None:
        return
    bucket[total_key] += value
    bucket[count_key] += 1
    current_min = bucket[min_key]
    bucket[min_key] = value if current_min is None else min(current_min, value)


def diagnostics_value(diagnostics: Any, field: str) -> float | None:
    if not isinstance(diagnostics, dict):
        return None
    return as_float(diagnostics.get(field))


def boundary_min_distance(diagnostics: Any) -> float | None:
    if not isinstance(diagnostics, dict):
        return None
    boundary = diagnostics.get("boundary")
    if not isinstance(boundary, dict):
        return None
    return as_float(boundary.get("min_distance"))


def record_bucket(
    bucket: dict[str, Any],
    sample: dict[str, Any],
    base_probabilities: list[float],
    late_probabilities: list[float],
) -> dict[str, Any]:
    base_top = argmax(base_probabilities)
    late_top = argmax(late_probabilities)
    base_to_late_kl = kl_divergence(base_probabilities, late_probabilities)
    late_to_base_kl = kl_divergence(late_probabilities, base_probabilities)

    bucket["sample_count"] += 1
    bucket["base_to_late_kl_total"] += base_to_late_kl
    bucket["late_to_base_kl_total"] += late_to_base_kl
    bucket["max_base_to_late_kl"] = max(bucket["max_base_to_late_kl"], base_to_late_kl)
    if base_top == late_top:
        bucket["argmax_agreement_count"] += 1
    bucket["base_entropy_total"] += entropy_nats(base_probabilities)
    bucket["late_entropy_total"] += entropy_nats(late_probabilities)
    bucket["base_top_counts"][str(base_top)] += 1
    bucket["late_top_counts"][str(late_top)] += 1

    trace_action = sample.get("action")
    if trace_action is not None:
        trace_key = str(int(trace_action))
        bucket["trace_action_counts"][trace_key] += 1
        if int(trace_action) == base_top:
            bucket["trace_matches_base_count"] += 1
        if int(trace_action) == late_top:
            bucket["trace_matches_late_count"] += 1

    record_numeric_summary(
        bucket,
        "health_total",
        "health_count",
        "health_min",
        sample.get("health"),
    )
    record_numeric_summary(
        bucket,
        "boundary_min_total",
        "boundary_min_count",
        "boundary_min_min",
        boundary_min_distance(sample.get("diagnostics")),
    )
    for field in PRESSURE_FIELDS:
        value = diagnostics_value(sample.get("diagnostics"), field)
        if value is None:
            continue
        bucket["pressure_totals"][field] += value
        bucket["pressure_counts"][field] += 1
        if value >= PRESSURE_HIGH_THRESHOLD:
            bucket["pressure_high_counts"][field] += 1

    return {
        "base_top": base_top,
        "late_top": late_top,
        "base_to_late_kl": base_to_late_kl,
        "late_to_base_kl": late_to_base_kl,
        "base_top_probability": base_probabilities[base_top],
        "late_top_probability": late_probabilities[late_top],
    }


def finalize_bucket(bucket: dict[str, Any]) -> dict[str, Any]:
    sample_count = int(bucket["sample_count"])
    if sample_count == 0:
        return {
            "sample_count": 0,
            "mean_base_to_late_kl": None,
            "mean_late_to_base_kl": None,
            "max_base_to_late_kl": None,
            "argmax_agreement": None,
        }
    health_count = max(1, int(bucket["health_count"]))
    boundary_count = max(1, int(bucket["boundary_min_count"]))
    pressure = {}
    for field in PRESSURE_FIELDS:
        count = int(bucket["pressure_counts"][field])
        pressure[field] = {
            "mean": (
                round(bucket["pressure_totals"][field] / count, 4)
                if count > 0
                else None
            ),
            "high_ratio": (
                round(bucket["pressure_high_counts"][field] / count, 4)
                if count > 0
                else None
            ),
        }
    return {
        "sample_count": sample_count,
        "mean_base_to_late_kl": round(bucket["base_to_late_kl_total"] / sample_count, 6),
        "mean_late_to_base_kl": round(bucket["late_to_base_kl_total"] / sample_count, 6),
        "max_base_to_late_kl": round(bucket["max_base_to_late_kl"], 6),
        "argmax_agreement": round(bucket["argmax_agreement_count"] / sample_count, 4),
        "base_entropy_nats": round(bucket["base_entropy_total"] / sample_count, 6),
        "late_entropy_nats": round(bucket["late_entropy_total"] / sample_count, 6),
        "base_top_action_distribution": ratio_distribution(
            bucket["base_top_counts"], sample_count
        ),
        "late_top_action_distribution": ratio_distribution(
            bucket["late_top_counts"], sample_count
        ),
        "trace_action_distribution": ratio_distribution(
            bucket["trace_action_counts"], sample_count
        ),
        "trace_matches_base_argmax": round(
            bucket["trace_matches_base_count"] / sample_count, 4
        ),
        "trace_matches_late_argmax": round(
            bucket["trace_matches_late_count"] / sample_count, 4
        ),
        "health_mean": round(bucket["health_total"] / health_count, 4)
        if bucket["health_count"]
        else None,
        "health_min": round(bucket["health_min"], 4)
        if bucket["health_min"] is not None
        else None,
        "boundary_min_distance_mean": round(
            bucket["boundary_min_total"] / boundary_count, 4
        )
        if bucket["boundary_min_count"]
        else None,
        "boundary_min_distance_min": round(bucket["boundary_min_min"], 4)
        if bucket["boundary_min_min"] is not None
        else None,
        "pressure": pressure,
    }


def compact_example(
    sample: dict[str, Any],
    score_row: dict[str, Any],
) -> dict[str, Any]:
    diagnostics = sample.get("diagnostics") if isinstance(sample.get("diagnostics"), dict) else {}
    return {
        "trace_path": sample.get("trace_path"),
        "seed": sample.get("seed"),
        "map_id": sample.get("map_id"),
        "episode_outcome": sample.get("episode_outcome"),
        "step": sample.get("step"),
        "time_seconds": round(float(sample.get("time_seconds", 0.0)), 4),
        "health": sample.get("health"),
        "trace_action": sample.get("action"),
        "base_top": score_row["base_top"],
        "late_top": score_row["late_top"],
        "base_top_probability": round(score_row["base_top_probability"], 6),
        "late_top_probability": round(score_row["late_top_probability"], 6),
        "base_to_late_kl": round(score_row["base_to_late_kl"], 6),
        "boundary_min_distance": boundary_min_distance(diagnostics),
        "enemy_pressure_risk": diagnostics_value(diagnostics, "enemy_pressure_risk"),
        "hazard_pressure_risk": diagnostics_value(diagnostics, "hazard_pressure_risk"),
        "boss_pressure_risk": diagnostics_value(diagnostics, "boss_pressure_risk"),
        "low_health_risk": diagnostics_value(diagnostics, "low_health_risk"),
    }


def build_findings(report: dict[str, Any]) -> list[dict[str, Any]]:
    findings = []
    if report["sample_count"] == 0:
        findings.append(
            {
                "id": "no_handoff_samples",
                "severity": "repair",
                "summary": "No trace observations matched the requested handoff window.",
            }
        )
        return findings

    overall = report["overall"]
    agreement = overall.get("argmax_agreement")
    if agreement is not None and agreement < 0.5:
        findings.append(
            {
                "id": "low_base_late_argmax_agreement",
                "severity": "watch",
                "summary": "Base and late policies disagree on most traced handoff observations.",
            }
        )
    for label in ("pre_split", "post_split"):
        if report["by_window"].get(label, {}).get("sample_count", 0) == 0:
            findings.append(
                {
                    "id": f"missing_{label}_samples",
                    "severity": "watch",
                    "summary": f"The diagnostic has no {label} observations in the selected trace window.",
                }
            )
    return findings


def compare_handoff_samples(
    samples: list[dict[str, Any]],
    base_policy: Any,
    late_policy: Any,
    *,
    action_count: int,
    split_seconds: float,
    sample_stride: int = 1,
    limit_samples: int | None = None,
    top_examples: int = 12,
) -> dict[str, Any]:
    if action_count <= 0:
        raise ValueError("action_count must be greater than 0")
    if sample_stride <= 0:
        raise ValueError("sample_stride must be greater than 0")
    if limit_samples is not None and limit_samples <= 0:
        raise ValueError("limit_samples must be greater than 0")

    selected_samples = [
        sample for index, sample in enumerate(samples) if index % sample_stride == 0
    ]
    if limit_samples is not None:
        selected_samples = selected_samples[:limit_samples]

    overall = empty_bucket(action_count)
    by_window: dict[str, dict[str, Any]] = {}
    by_episode_outcome: dict[str, dict[str, Any]] = {}
    examples: list[dict[str, Any]] = []
    active_episode = None

    for sample in selected_samples:
        episode_key = (sample.get("trace_path"), sample.get("seed"), sample.get("map_id"))
        if episode_key != active_episode:
            for policy in (base_policy, late_policy):
                maybe_call(policy, "reset")
                maybe_call(policy, "set_map_id", sample.get("map_id"))
            active_episode = episode_key

        for policy in (base_policy, late_policy):
            set_policy_context(policy, sample)

        base_probabilities = probability_distribution(
            policy_action_scores(base_policy, sample["observation"]),
            action_count,
        )
        late_probabilities = probability_distribution(
            policy_action_scores(late_policy, sample["observation"]),
            action_count,
        )

        score_row = record_bucket(overall, sample, base_probabilities, late_probabilities)
        label = window_label(float(sample["time_seconds"]), split_seconds)
        by_window.setdefault(label, empty_bucket(action_count))
        record_bucket(by_window[label], sample, base_probabilities, late_probabilities)
        outcome = str(sample.get("episode_outcome") or "unknown")
        by_episode_outcome.setdefault(outcome, empty_bucket(action_count))
        record_bucket(
            by_episode_outcome[outcome],
            sample,
            base_probabilities,
            late_probabilities,
        )
        examples.append(compact_example(sample, score_row))

    report = {
        "sample_count": len(selected_samples),
        "split_seconds": split_seconds,
        "sample_stride": sample_stride,
        "limit_samples": limit_samples,
        "overall": finalize_bucket(overall),
        "by_window": {
            key: finalize_bucket(value)
            for key, value in sorted(by_window.items())
        },
        "by_episode_outcome": {
            key: finalize_bucket(value)
            for key, value in sorted(by_episode_outcome.items())
        },
        "top_kl_examples": sorted(
            examples,
            key=lambda item: item["base_to_late_kl"],
            reverse=True,
        )[:top_examples],
        "limitations": [
            "This compares policy scores on sampled trace observations only.",
            "Trace observations are produced by Gym evaluation and are not full Replay snapshots.",
            "This diagnostic does not train, repair, or approve a policy candidate.",
        ],
    }
    report["findings"] = build_findings(report)
    return report


def build_report(
    trace_inputs: list[Path],
    base_policy: Any,
    late_policy: Any,
    *,
    base_model_path: str,
    late_model_path: str,
    action_count: int,
    split_seconds: float,
    window_before_seconds: float,
    window_after_seconds: float,
    map_id: str | None = None,
    sample_stride: int = 1,
    limit_samples: int | None = None,
    top_examples: int = 12,
) -> dict[str, Any]:
    start_seconds = split_seconds - window_before_seconds
    end_seconds = split_seconds + window_after_seconds
    samples = load_trace_samples(
        trace_inputs,
        map_id=map_id,
        start_seconds=start_seconds,
        end_seconds=end_seconds,
    )
    comparison = compare_handoff_samples(
        samples,
        base_policy,
        late_policy,
        action_count=action_count,
        split_seconds=split_seconds,
        sample_stride=sample_stride,
        limit_samples=limit_samples,
        top_examples=top_examples,
    )
    return {
        "report_version": 1,
        "decision": "sb3_handoff_state_distribution_recorded",
        "base_model_path": base_model_path,
        "late_model_path": late_model_path,
        "trace_inputs": [str(path) for path in trace_inputs],
        "trace_count": len(trace_paths(trace_inputs)),
        "map_id_filter": map_id,
        "action_count": action_count,
        "window": {
            "split_seconds": split_seconds,
            "start_seconds": start_seconds,
            "end_seconds": end_seconds,
            "window_before_seconds": window_before_seconds,
            "window_after_seconds": window_after_seconds,
        },
        **comparison,
    }


def distribution_top_text(distribution: dict[str, Any]) -> str:
    if not distribution:
        return "n/a"
    action, value = max(
        distribution.items(),
        key=lambda item: float(item[1].get("ratio", 0.0)),
    )
    return f"`{action}` / {float(value.get('ratio', 0.0)):.2%}"


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# SB3 Handoff State Distribution",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Base model: `{report['base_model_path']}`",
        f"- Late model: `{report['late_model_path']}`",
        f"- Trace count: `{report['trace_count']}`",
        f"- Samples: `{report['sample_count']}`",
        f"- Window: `{report['window']['start_seconds']}` to `{report['window']['end_seconds']}` seconds",
        "",
        "## Overall",
        "",
        f"- Mean base-to-late KL: `{report['overall'].get('mean_base_to_late_kl')}`",
        f"- Argmax agreement: `{report['overall'].get('argmax_agreement')}`",
        f"- Base top action: {distribution_top_text(report['overall'].get('base_top_action_distribution', {}))}",
        f"- Late top action: {distribution_top_text(report['overall'].get('late_top_action_distribution', {}))}",
        "",
        "## Window Summary",
        "",
        "| Window | Samples | Mean KL | Argmax Agreement | Base Top | Late Top | Health Mean | Boundary Min Mean |",
        "| --- | ---: | ---: | ---: | --- | --- | ---: | ---: |",
    ]
    for label, item in report["by_window"].items():
        lines.append(
            "| {label} | {samples} | {kl} | {agree} | {base} | {late} | {health} | {boundary} |".format(
                label=f"`{label}`",
                samples=item.get("sample_count"),
                kl=item.get("mean_base_to_late_kl"),
                agree=item.get("argmax_agreement"),
                base=distribution_top_text(item.get("base_top_action_distribution", {})),
                late=distribution_top_text(item.get("late_top_action_distribution", {})),
                health=item.get("health_mean"),
                boundary=item.get("boundary_min_distance_mean"),
            )
        )
    lines.extend(["", "## Findings", ""])
    if report["findings"]:
        for finding in report["findings"]:
            lines.append(
                f"- `{finding['severity']}` `{finding['id']}`: {finding['summary']}"
            )
    else:
        lines.append("- No automatic finding thresholds were triggered.")
    lines.extend(["", "## Top KL Examples", ""])
    for example in report["top_kl_examples"]:
        lines.append(
            "- seed `{seed}` time `{time}` trace `{trace}` base `{base}` late `{late}` KL `{kl}` health `{health}`".format(
                seed=example.get("seed"),
                time=example.get("time_seconds"),
                trace=example.get("trace_action"),
                base=example.get("base_top"),
                late=example.get("late_top"),
                kl=example.get("base_to_late_kl"),
                health=example.get("health"),
            )
        )
    lines.extend(["", "## Limitations", ""])
    for limitation in report["limitations"]:
        lines.append(f"- {limitation}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_json_report(report: dict[str, Any], path: Path | None) -> None:
    if path is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare SB3 base and late policies on sampled handoff trace states."
    )
    parser.add_argument("traces", type=Path, nargs="+", help="Trace JSON files or directories.")
    parser.add_argument("--base-model", required=True)
    parser.add_argument("--late-model", required=True)
    parser.add_argument("--algorithm", choices=["dqn", "ppo"], default="ppo")
    parser.add_argument("--action-count", type=int, default=9)
    parser.add_argument("--split-seconds", type=float, required=True)
    parser.add_argument("--window-before-seconds", type=float, default=60.0)
    parser.add_argument("--window-after-seconds", type=float, default=60.0)
    parser.add_argument("--map-id", default=None)
    parser.add_argument("--sample-stride", type=int, default=1)
    parser.add_argument("--limit-samples", type=int, default=None)
    parser.add_argument("--top-examples", type=int, default=12)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--markdown", type=Path, default=None)
    parser.add_argument("--check-deps", action="store_true")
    args = parser.parse_args()

    if args.check_deps:
        write_json_report({"status": "ok", "dependencies": dependency_status()}, args.report)
        return
    if args.split_seconds <= 0.0:
        parser.error("--split-seconds must be greater than 0")
    if args.window_before_seconds < 0.0 or args.window_after_seconds < 0.0:
        parser.error("handoff windows must be non-negative")

    require_dependencies()
    model_class = stable_baselines_model_classes()[args.algorithm]
    base_policy = model_class.load(args.base_model)
    late_policy = model_class.load(args.late_model)
    report = build_report(
        args.traces,
        base_policy,
        late_policy,
        base_model_path=args.base_model,
        late_model_path=args.late_model,
        action_count=args.action_count,
        split_seconds=args.split_seconds,
        window_before_seconds=args.window_before_seconds,
        window_after_seconds=args.window_after_seconds,
        map_id=args.map_id,
        sample_stride=args.sample_stride,
        limit_samples=args.limit_samples,
        top_examples=args.top_examples,
    )
    write_json_report(report, args.report)
    if args.markdown is not None:
        write_markdown(report, args.markdown)


if __name__ == "__main__":
    main()
