#!/usr/bin/env python3
"""Create trace and preflight tasks from RL failure-lane analysis."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


BUCKET_WINDOWS = {
    "opening_lt_60": (0.0, 60.0),
    "mid_60_to_180": (60.0, 180.0),
    "late_180_to_300": (180.0, 300.0),
    "post_300": (300.0, 360.0),
}

LANE_TASK_DEFAULTS = {
    "opening_repair": {
        "task_type": "opening_trace_preflight",
        "priority": 1,
        "trace_goal": "capture target opening defeat and parent/candidate divergence before more PPO",
        "preflight": "60s caramel window target preflight plus target seed trace comparison",
        "repair_shape": "opening boundary escape or early-route branch",
    },
    "mid_retention_repair": {
        "task_type": "mid_retention_trace_preflight",
        "priority": 2,
        "trace_goal": "capture 60-180s route retention and handoff debt",
        "preflight": "180s target seed retention preflight before full 300s matrices",
        "repair_shape": "mid-window route retention branch",
    },
    "late_terminal_survival_conversion": {
        "task_type": "late_terminal_trace_preflight",
        "priority": 1,
        "trace_goal": "capture late low-health, hazard, and terminal conversion failures",
        "preflight": "late terminal conversion probe plus 300s caramel no-regression gate",
        "repair_shape": "state-conditioned terminal conversion branch",
    },
    "post_300_review": {
        "task_type": "extended_run_trace_review",
        "priority": 3,
        "trace_goal": "capture extended-run duration and post-300 accounting",
        "preflight": "extended-run gate review before promotion",
        "repair_shape": "extended-run policy or gate adjustment",
    },
}


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def sorted_ints(values: Any) -> list[int]:
    if not isinstance(values, list):
        return []
    return sorted(as_int(value) for value in values)


def unique_sorted(values: list[str]) -> list[str]:
    return sorted(dict.fromkeys(values))


def lane_defaults(lane_id: str) -> dict[str, Any]:
    return LANE_TASK_DEFAULTS.get(
        lane_id,
        {
            "task_type": "mixed_failure_trace_review",
            "priority": 3,
            "trace_goal": "capture mixed failure lane before choosing a training objective",
            "preflight": "rerun target preflight after trace diagnostics",
            "repair_shape": "mixed repair branch",
        },
    )


def failures_for_lane(map_report: dict[str, Any], lane: dict[str, Any]) -> list[dict[str, Any]]:
    seeds = set(sorted_ints(lane.get("seeds")))
    buckets = set(str(item) for item in lane.get("time_buckets", []) if item)
    failures = map_report.get("failures", [])
    if not isinstance(failures, list):
        return []
    result = []
    for failure in failures:
        if not isinstance(failure, dict):
            continue
        seed = as_int(failure.get("seed"), -1)
        bucket = str(failure.get("time_bucket") or "")
        if seeds and seed not in seeds:
            continue
        if buckets and bucket not in buckets:
            continue
        result.append(failure)
    return result


def average(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 4)


def time_span(failures: list[dict[str, Any]]) -> dict[str, float | None]:
    values = [as_float(failure.get("time_seconds")) for failure in failures]
    if not values:
        return {"min": None, "max": None, "average": None}
    return {
        "min": round(min(values), 4),
        "max": round(max(values), 4),
        "average": average(values),
    }


def bucket_window(time_buckets: list[str]) -> tuple[float, float]:
    windows = [BUCKET_WINDOWS.get(bucket, BUCKET_WINDOWS["post_300"]) for bucket in time_buckets]
    if not windows:
        return BUCKET_WINDOWS["post_300"]
    return min(start for start, _ in windows), max(end for _, end in windows)


def trace_window(lane_id: str, time_buckets: list[str], span: dict[str, float | None]) -> dict[str, float]:
    bucket_start, bucket_end = bucket_window(time_buckets)
    min_time = span.get("min")
    max_time = span.get("max")
    if lane_id == "opening_repair":
        return {"start": 0.0, "end": 60.0}
    if lane_id == "late_terminal_survival_conversion":
        end = min(bucket_end, max(240.0, (max_time if max_time is not None else 240.0) + 15.0))
        return {"start": round(bucket_start, 4), "end": round(end, 4)}
    if lane_id == "mid_retention_repair":
        start = max(bucket_start, (min_time if min_time is not None else bucket_start) - 20.0)
        end = min(bucket_end, (max_time if max_time is not None else bucket_end) + 20.0)
        return {"start": round(start, 4), "end": round(end, 4)}
    start = max(bucket_start, (min_time if min_time is not None else bucket_start) - 30.0)
    end = max(bucket_end, (max_time if max_time is not None else bucket_end) + 30.0)
    return {"start": round(start, 4), "end": round(end, 4)}


def dispatch_window(lane_id: str, span: dict[str, float | None]) -> dict[str, float] | None:
    if lane_id != "late_terminal_survival_conversion":
        return None
    min_time = span.get("min")
    max_time = span.get("max")
    start = max(180.0, (min_time if min_time is not None else 210.0) - 5.0)
    end = min(300.0, max(240.0, (max_time if max_time is not None else 240.0) + 15.0))
    return {"start": round(start, 4), "end": round(end, 4)}


def contiguous_eval_range(seeds: list[int]) -> dict[str, Any]:
    if not seeds:
        return {
            "seed_start": None,
            "eval_episodes": 0,
            "contiguous": True,
            "extra_scan_seeds": [],
        }
    start = min(seeds)
    end = max(seeds)
    full_range = list(range(start, end + 1))
    return {
        "seed_start": start,
        "eval_episodes": len(full_range),
        "contiguous": len(full_range) == len(seeds),
        "extra_scan_seeds": [seed for seed in full_range if seed not in seeds],
    }


def dominant_action_counts(failures: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for failure in failures:
        action = (failure.get("dominant_action") or {}).get("action")
        if action is None:
            continue
        key = str(action)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def build_task(
    *,
    failure_analysis: Path,
    trace_root: Path,
    model_path: str | None,
    seconds: float,
    map_id: str,
    lane_id: str,
    lane: dict[str, Any],
    failures: list[dict[str, Any]],
) -> dict[str, Any]:
    seeds = sorted_ints(lane.get("seeds"))
    buckets = [str(item) for item in lane.get("time_buckets", []) if item]
    span = time_span(failures)
    defaults = lane_defaults(lane_id)
    eval_range = contiguous_eval_range(seeds)
    task_trace_dir = trace_root / lane_id / map_id
    task = {
        "lane_id": lane_id,
        "map_id": map_id,
        "task_type": defaults["task_type"],
        "priority": defaults["priority"],
        "failure_count": int(lane.get("count", len(failures)) or len(failures)),
        "ratio": as_float(lane.get("ratio")),
        "seeds": seeds,
        "time_buckets": buckets,
        "failure_time_seconds": span,
        "dominant_action_counts": dominant_action_counts(failures),
        "trace_window_seconds": trace_window(lane_id, buckets, span),
        "dispatch_window_seconds": dispatch_window(lane_id, span),
        "trace_dir": str(task_trace_dir),
        "evaluation_range": eval_range,
        "trace_goal": defaults["trace_goal"],
        "required_preflight": defaults["preflight"],
        "repair_shape": defaults["repair_shape"],
        "suggested_train_sb3_args": suggested_trace_args(
            model_path=model_path,
            map_id=map_id,
            seconds=seconds,
            trace_dir=task_trace_dir,
            eval_range=eval_range,
        ),
        "source_failure_analysis": str(failure_analysis),
    }
    return {key: value for key, value in task.items() if value is not None}


def suggested_trace_args(
    *,
    model_path: str | None,
    map_id: str,
    seconds: float,
    trace_dir: Path,
    eval_range: dict[str, Any],
) -> list[str]:
    args = [
        "--algorithm",
        "ppo",
        "--compare-rule-bots",
        "--map-id",
        map_id,
        "--eval-seconds",
        f"{seconds:g}",
        "--trace-dir",
        str(trace_dir),
        "--trace-failed-only",
        "--trace-sample-stride",
        "15",
        "--trace-include-observation",
    ]
    if model_path:
        args.extend(["--model", model_path])
    if eval_range.get("seed_start") is not None:
        args.extend(["--seed-start", str(eval_range["seed_start"])])
    if eval_range.get("eval_episodes"):
        args.extend(["--eval-episodes", str(eval_range["eval_episodes"])])
    return args


def map_lane_tasks(
    *,
    failure_analysis: Path,
    trace_root: Path,
    model_path: str | None,
    seconds: float,
    map_report: dict[str, Any],
) -> list[dict[str, Any]]:
    map_id = str(map_report.get("map_id") or "unknown")
    lanes = map_report.get("failure_lanes")
    if not isinstance(lanes, dict):
        return []
    tasks = []
    for lane_id, lane in lanes.items():
        if not isinstance(lane, dict):
            continue
        failures = failures_for_lane(map_report, lane)
        tasks.append(
            build_task(
                failure_analysis=failure_analysis,
                trace_root=trace_root,
                model_path=model_path,
                seconds=seconds,
                map_id=map_id,
                lane_id=str(lane_id),
                lane=lane,
                failures=failures,
            )
        )
    return sorted(tasks, key=lambda item: (item["priority"], item["map_id"], item["lane_id"]))


def build_report(failure_analysis: Path, trace_root: Path) -> dict[str, Any]:
    errors: list[str] = []
    try:
        payload = load_json_object(failure_analysis)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return invalid_report(failure_analysis, trace_root, [str(exc)])

    map_reports = payload.get("maps")
    if not isinstance(map_reports, list):
        return invalid_report(failure_analysis, trace_root, ["failure analysis missing maps list"])

    model_path = payload.get("model_path")
    seconds = as_float(payload.get("seconds"), 300.0)
    tasks: list[dict[str, Any]] = []
    for map_report in map_reports:
        if isinstance(map_report, dict):
            tasks.extend(
                map_lane_tasks(
                    failure_analysis=failure_analysis,
                    trace_root=trace_root,
                    model_path=str(model_path) if model_path else None,
                    seconds=seconds,
                    map_report=map_report,
                )
            )
    if not tasks:
        errors.append("failure analysis contains no map-level failure_lanes")

    lane_ids = unique_sorted([str(task["lane_id"]) for task in tasks])
    decision = "rl_failure_lane_trace_plan_invalid" if errors else "rl_failure_lane_trace_plan_ready"
    return {
        "report_version": 1,
        "decision": decision,
        "source": str(failure_analysis),
        "source_model_path": str(model_path) if model_path else None,
        "trace_root": str(trace_root),
        "lane_count": len(lane_ids),
        "task_count": len(tasks),
        "lane_ids": lane_ids,
        "tasks": tasks,
        "errors": errors,
        "limitations": [
            "This report creates trace and preflight tasks only; it does not run simulation or train a policy.",
            "Non-contiguous lane seeds may require scanning extra seeds because train_sb3 comparison uses seed_start plus eval_episodes.",
            "A trace plan is repair routing evidence, not RL acceptance or candidate promotion evidence.",
        ],
    }


def invalid_report(failure_analysis: Path, trace_root: Path, errors: list[str]) -> dict[str, Any]:
    return {
        "report_version": 1,
        "decision": "rl_failure_lane_trace_plan_invalid",
        "source": str(failure_analysis),
        "trace_root": str(trace_root),
        "lane_count": 0,
        "task_count": 0,
        "lane_ids": [],
        "tasks": [],
        "errors": errors,
        "limitations": [
            "Invalid trace plans cannot be used to route RL repair work.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# RL Failure Lane Trace Plan",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Source: `{report['source']}`",
        f"- Lanes: `{report['lane_count']}`",
        f"- Tasks: `{report['task_count']}`",
        "",
        "## Tasks",
        "",
        "| Lane | Map | Type | Priority | Seeds | Trace Window | Eval Range | Extra Scan Seeds | Required Preflight |",
        "|---|---|---|---:|---|---|---|---|---|",
    ]
    for task in report["tasks"]:
        trace_window = task["trace_window_seconds"]
        eval_range = task["evaluation_range"]
        seed_text = ", ".join(str(seed) for seed in task["seeds"]) or "n/a"
        extra_text = ", ".join(str(seed) for seed in eval_range.get("extra_scan_seeds", [])) or "none"
        lines.append(
            "| `{lane}` | `{map_id}` | `{task_type}` | {priority} | {seeds} | {start}-{end}s | seed `{seed_start}` x `{episodes}` | {extra} | {preflight} |".format(
                lane=task["lane_id"],
                map_id=task["map_id"],
                task_type=task["task_type"],
                priority=task["priority"],
                seeds=seed_text,
                start=trace_window["start"],
                end=trace_window["end"],
                seed_start=eval_range.get("seed_start"),
                episodes=eval_range.get("eval_episodes"),
                extra=extra_text,
                preflight=task["required_preflight"],
            )
        )

    lines.extend(["", "## Details", ""])
    for task in report["tasks"]:
        lines.extend(
            [
                f"### `{task['lane_id']}` / `{task['map_id']}`",
                f"- Trace dir: `{task['trace_dir']}`",
                f"- Trace goal: {task['trace_goal']}",
                f"- Repair shape: {task['repair_shape']}",
                f"- Failure time seconds: `{json.dumps(task['failure_time_seconds'], sort_keys=True)}`",
                f"- Dominant actions: `{json.dumps(task['dominant_action_counts'], sort_keys=True)}`",
                f"- Suggested args: `{' '.join(task['suggested_train_sb3_args'])}`",
                "",
            ]
        )

    if report.get("errors"):
        lines.extend(["## Errors", ""])
        lines.extend(f"- {item}" for item in report["errors"])
        lines.append("")

    lines.extend(["## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create RL failure-lane trace/preflight tasks.")
    parser.add_argument("--failure-analysis", type=Path, required=True)
    parser.add_argument("--trace-root", type=Path, required=True)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--markdown", type=Path, default=None)
    args = parser.parse_args()

    report = build_report(args.failure_analysis, args.trace_root)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "rl_failure_lane_trace_plan_ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
