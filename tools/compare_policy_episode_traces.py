#!/usr/bin/env python3
"""Compare sampled policy episode traces across labels and seeds."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


ACTION_COUNT = 9
HIGH_BOUNDARY_EDGE_RISK = 0.75
HIGH_ENEMY_PRESSURE_RISK = 0.6
LOW_HEALTH_RISK = 0.6


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def trace_paths(inputs: Iterable[Path]) -> list[Path]:
    paths: list[Path] = []
    for item in inputs:
        if item.is_dir():
            paths.extend(sorted(item.rglob("*_trace.json")))
        elif item.is_file():
            paths.append(item)
        else:
            raise FileNotFoundError(item)
    return sorted(dict.fromkeys(paths))


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


def ratio_map(counts: Counter[str], total: int) -> dict[str, dict[str, float | int]]:
    return {
        str(action): {
            "count": int(counts.get(str(action), 0)),
            "ratio": round(int(counts.get(str(action), 0)) / max(1, total), 4),
        }
        for action in range(ACTION_COUNT)
    }


def diagnostics(step: dict[str, Any]) -> dict[str, Any]:
    value = step.get("diagnostics")
    return value if isinstance(value, dict) else {}


def boundary(step: dict[str, Any]) -> dict[str, Any]:
    value = diagnostics(step).get("boundary")
    return value if isinstance(value, dict) else {}


def top_actions(step: dict[str, Any]) -> list[dict[str, Any]]:
    score = step.get("action_score")
    if not isinstance(score, dict):
        return []
    result: list[dict[str, Any]] = []
    for item in score.get("top_actions", []) or []:
        if not isinstance(item, dict):
            continue
        result.append(
            {
                "action": str(item.get("action")),
                "score": round(as_float(item.get("score")), 4),
            }
        )
    return result


def compact_step(step: dict[str, Any]) -> dict[str, Any]:
    diag = diagnostics(step)
    bound = boundary(step)
    nearest_enemy = diag.get("nearest_enemy")
    if not isinstance(nearest_enemy, dict):
        nearest_enemy = {}
    return {
        "step": as_int(step.get("step")),
        "time_seconds": round(as_float(step.get("time_seconds")), 4),
        "action": as_int(step.get("action")),
        "health": round(as_float(step.get("health")), 4),
        "route_recovery": round(
            as_float((step.get("reward_breakdown") or {}).get("route_recovery")),
            4,
        ),
        "boundary_min_distance": round(as_float(bound.get("min_distance")), 4),
        "boundary_edge_risk": round(as_float(bound.get("edge_risk")), 4),
        "enemy_pressure_risk": round(as_float(diag.get("enemy_pressure_risk")), 4),
        "low_health_risk": round(as_float(diag.get("low_health_risk")), 4),
        "nearest_enemy_hitbox_distance": round(
            as_float(nearest_enemy.get("hitbox_distance")),
            4,
        ),
        "top_actions": top_actions(step),
    }


def action_runs(steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    runs: list[dict[str, Any]] = []
    if not steps:
        return runs
    start = 0
    current_action = as_int(steps[0].get("action"))
    for index, step in enumerate(steps[1:], start=1):
        action = as_int(step.get("action"))
        if action == current_action:
            continue
        runs.append(build_run(steps, start, index - 1, current_action))
        start = index
        current_action = action
    runs.append(build_run(steps, start, len(steps) - 1, current_action))
    return runs


def build_run(
    steps: list[dict[str, Any]],
    start_index: int,
    end_index: int,
    action: int,
) -> dict[str, Any]:
    first = steps[start_index]
    last = steps[end_index]
    return {
        "action": str(action),
        "sample_count": end_index - start_index + 1,
        "start_time_seconds": round(as_float(first.get("time_seconds")), 4),
        "end_time_seconds": round(as_float(last.get("time_seconds")), 4),
        "start_step": as_int(first.get("step")),
        "end_step": as_int(last.get("step")),
    }


def first_matching_step(
    steps: list[dict[str, Any]],
    *,
    min_boundary_edge_risk: float | None = None,
    min_enemy_pressure_risk: float | None = None,
    min_low_health_risk: float | None = None,
) -> dict[str, Any] | None:
    for step in steps:
        diag = diagnostics(step)
        bound = boundary(step)
        if min_boundary_edge_risk is not None and as_float(bound.get("edge_risk")) < min_boundary_edge_risk:
            continue
        if min_enemy_pressure_risk is not None and as_float(diag.get("enemy_pressure_risk")) < min_enemy_pressure_risk:
            continue
        if min_low_health_risk is not None and as_float(diag.get("low_health_risk")) < min_low_health_risk:
            continue
        return compact_step(step)
    return None


def summarize_trace(path: Path, label: str) -> dict[str, Any]:
    payload = load_json_object(path)
    episode = payload.get("episode") if isinstance(payload.get("episode"), dict) else {}
    steps = [step for step in payload.get("steps", []) if isinstance(step, dict)]
    action_counts = Counter(str(as_int(step.get("action"))) for step in steps)
    top_action_counts = Counter(
        str((top_actions(step) or [{"action": "unknown"}])[0]["action"])
        for step in steps
    )
    longest_runs = sorted(
        action_runs(steps),
        key=lambda item: (item["sample_count"], item["end_time_seconds"]),
        reverse=True,
    )[:5]
    return {
        "label": label,
        "trace_path": str(path),
        "seed": episode.get("seed"),
        "map_id": episode.get("map_id"),
        "terminal_kind": episode.get("terminal_kind"),
        "terminal_reason": episode.get("terminal_reason"),
        "episode_time_seconds": round(as_float(episode.get("time_seconds")), 4),
        "sample_count": len(steps),
        "action_distribution": ratio_map(action_counts, len(steps)),
        "top_action_distribution": ratio_map(top_action_counts, len(steps)),
        "longest_action_runs": longest_runs,
        "first_boundary_enemy_pressure_step": first_matching_step(
            steps,
            min_boundary_edge_risk=HIGH_BOUNDARY_EDGE_RISK,
            min_enemy_pressure_risk=HIGH_ENEMY_PRESSURE_RISK,
        ),
        "first_low_health_step": first_matching_step(
            steps,
            min_low_health_risk=LOW_HEALTH_RISK,
        ),
        "final_step": compact_step(steps[-1]) if steps else None,
    }


def parse_trace_group(value: str) -> tuple[str, list[Path]]:
    if "=" not in value:
        raise ValueError("--trace-group must use label=path[,path...]")
    label, raw_paths = value.split("=", 1)
    label = label.strip()
    paths = [Path(item.strip()) for item in raw_paths.split(",") if item.strip()]
    if not label or not paths:
        raise ValueError("--trace-group must include a label and at least one path")
    return label, paths


def load_groups(values: list[str]) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for value in values:
        label, inputs = parse_trace_group(value)
        groups[label] = [summarize_trace(path, label) for path in trace_paths(inputs)]
    return groups


def index_by_seed(groups: dict[str, list[dict[str, Any]]]) -> dict[Any, dict[str, dict[str, Any]]]:
    result: dict[Any, dict[str, dict[str, Any]]] = {}
    for label, traces in groups.items():
        for trace in traces:
            result.setdefault(trace["seed"], {})[label] = trace
    return dict(sorted(result.items(), key=lambda item: str(item[0])))


def action_ratio(trace: dict[str, Any], action: str) -> float:
    return float(trace["action_distribution"].get(str(action), {}).get("ratio", 0.0))


def first_divergent_action(
    left_path: Path,
    right_path: Path,
) -> dict[str, Any] | None:
    left_steps = load_json_object(left_path).get("steps", [])
    right_steps = load_json_object(right_path).get("steps", [])
    for left, right in zip(left_steps, right_steps):
        if not isinstance(left, dict) or not isinstance(right, dict):
            continue
        if as_int(left.get("action")) != as_int(right.get("action")):
            return {
                "step": as_int(left.get("step")),
                "time_seconds": round(as_float(left.get("time_seconds")), 4),
                "left_action": str(as_int(left.get("action"))),
                "right_action": str(as_int(right.get("action"))),
            }
    if len(left_steps) != len(right_steps):
        return {
            "step": min(len(left_steps), len(right_steps)) + 1,
            "time_seconds": None,
            "left_action": "ended" if len(left_steps) < len(right_steps) else "continues",
            "right_action": "ended" if len(right_steps) < len(left_steps) else "continues",
        }
    return None


def matched_seed_comparison(seed_index: dict[Any, dict[str, dict[str, Any]]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for seed, traces in seed_index.items():
        labels = sorted(traces)
        row: dict[str, Any] = {"seed": seed, "labels": labels, "per_label": traces}
        if len(labels) >= 2:
            left = traces[labels[0]]
            right = traces[labels[1]]
            row["time_delta_seconds"] = round(
                right["episode_time_seconds"] - left["episode_time_seconds"],
                4,
            )
            row["same_terminal_kind"] = left["terminal_kind"] == right["terminal_kind"]
            row["action_ratio_delta"] = {
                str(action): round(
                    action_ratio(right, str(action)) - action_ratio(left, str(action)),
                    4,
                )
                for action in range(ACTION_COUNT)
            }
            row["first_divergent_action"] = first_divergent_action(
                Path(left["trace_path"]),
                Path(right["trace_path"]),
            )
        rows.append(row)
    return rows


def average_success_action_ratios(
    traces: list[dict[str, Any]],
    *,
    exclude_seed: int | None,
) -> dict[str, float]:
    success = [
        trace
        for trace in traces
        if trace.get("terminal_kind") == "victory" and trace.get("seed") != exclude_seed
    ]
    if not success:
        return {str(action): 0.0 for action in range(ACTION_COUNT)}
    return {
        str(action): round(
            sum(action_ratio(trace, str(action)) for trace in success) / len(success),
            4,
        )
        for action in range(ACTION_COUNT)
    }


def target_seed_analysis(
    groups: dict[str, list[dict[str, Any]]],
    target_seed: int | None,
) -> dict[str, Any] | None:
    if target_seed is None:
        return None
    result: dict[str, Any] = {}
    for label, traces in groups.items():
        target = next((trace for trace in traces if trace.get("seed") == target_seed), None)
        if target is None:
            continue
        success_average = average_success_action_ratios(traces, exclude_seed=target_seed)
        target_ratios = {
            str(action): action_ratio(target, str(action)) for action in range(ACTION_COUNT)
        }
        result[label] = {
            "target_trace": target,
            "success_action_ratio_average": success_average,
            "target_minus_success_action_ratio": {
                str(action): round(target_ratios[str(action)] - success_average[str(action)], 4)
                for action in range(ACTION_COUNT)
            },
            "missing_success_actions": [
                str(action)
                for action in range(ACTION_COUNT)
                if success_average[str(action)] >= 0.1 and target_ratios[str(action)] <= 0.01
            ],
            "excess_target_actions": [
                str(action)
                for action in range(ACTION_COUNT)
                if target_ratios[str(action)] >= 0.1 and success_average[str(action)] <= 0.01
            ],
        }
    return result


def build_report(trace_groups: list[str], target_seed: int | None) -> dict[str, Any]:
    groups = load_groups(trace_groups)
    seed_index = index_by_seed(groups)
    return {
        "report_version": 1,
        "decision": "policy_episode_trace_comparison_recorded",
        "trace_groups": sorted(groups),
        "target_seed": target_seed,
        "trace_count": sum(len(traces) for traces in groups.values()),
        "matched_seed_comparison": matched_seed_comparison(seed_index),
        "target_seed_analysis": target_seed_analysis(groups, target_seed),
        "limitations": [
            "This report compares sampled policy traces only; unsampled frames are not inspected.",
            "Observation vectors are carried for follow-up tooling, but this report summarizes diagnostics instead of interpreting every observation feature.",
            "Trace comparison is diagnostic evidence and does not prove a policy fix or acceptance.",
        ],
    }


def action_mix_text(distribution: dict[str, dict[str, float | int]]) -> str:
    items = [
        (action, float(payload.get("ratio", 0.0)))
        for action, payload in distribution.items()
        if float(payload.get("ratio", 0.0)) > 0
    ]
    items.sort(key=lambda item: item[1], reverse=True)
    return ", ".join(f"{action}:{ratio:.2%}" for action, ratio in items[:5]) or "none"


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Policy Episode Trace Comparison",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Trace groups: `{', '.join(report['trace_groups'])}`",
        f"- Target seed: `{report.get('target_seed')}`",
        f"- Trace count: `{report['trace_count']}`",
        "",
        "## Matched Seeds",
        "",
        "| Seed | Label | Result | Time | Actions | First High Pressure | First Low Health | Final Top Actions |",
        "|---:|---|---|---:|---|---|---|---|",
    ]
    for row in report["matched_seed_comparison"]:
        for label in row["labels"]:
            trace = row["per_label"][label]
            high = trace.get("first_boundary_enemy_pressure_step") or {}
            low = trace.get("first_low_health_step") or {}
            final = trace.get("final_step") or {}
            final_top = ", ".join(
                f"{item['action']}:{item['score']}" for item in final.get("top_actions", [])
            )
            lines.append(
                "| {seed} | `{label}` | `{result}` | {time} | {actions} | {high} | {low} | {final_top} |".format(
                    seed=row["seed"],
                    label=label,
                    result=trace.get("terminal_kind"),
                    time=trace.get("episode_time_seconds"),
                    actions=action_mix_text(trace["action_distribution"]),
                    high=f"{high.get('time_seconds')}s a{high.get('action')}" if high else "n/a",
                    low=f"{low.get('time_seconds')}s a{low.get('action')}" if low else "n/a",
                    final_top=final_top or "n/a",
                )
            )

    target = report.get("target_seed_analysis") or {}
    if target:
        lines.extend(["", "## Target Seed Vs Success Average", ""])
        lines.extend(
            [
                "| Label | Missing Success Actions | Excess Target Actions | Target-Success Delta |",
                "|---|---|---|---|",
            ]
        )
        for label, item in sorted(target.items()):
            delta = {
                action: value
                for action, value in item["target_minus_success_action_ratio"].items()
                if abs(value) >= 0.05
            }
            lines.append(
                "| `{}` | `{}` | `{}` | `{}` |".format(
                    label,
                    ",".join(item["missing_success_actions"]) or "none",
                    ",".join(item["excess_target_actions"]) or "none",
                    json.dumps(delta, sort_keys=True),
                )
            )

    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare sampled policy episode traces.")
    parser.add_argument(
        "--trace-group",
        action="append",
        required=True,
        help="Trace group in label=path[,path...] form. Repeat for multiple labels.",
    )
    parser.add_argument("--target-seed", type=int, default=None)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--markdown", type=Path, default=None)
    args = parser.parse_args()

    report = build_report(args.trace_group, args.target_seed)
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
