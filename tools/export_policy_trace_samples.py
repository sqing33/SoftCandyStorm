#!/usr/bin/env python3
"""Export selected policy trace steps as behavior-clone samples.

This is intended for retention anchors and other supervised repair inputs that
come from already-evaluated policy traces. It writes regular `sample` records so
existing behavior-clone dry-runs and training can consume the result.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable


DEFAULT_MOVEMENT_ACTION_COUNT = 9


def as_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


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


def parse_csv_filter(values: list[str] | None) -> set[str] | None:
    if not values:
        return None
    result = {
        item.strip()
        for value in values
        for item in value.split(",")
        if item.strip()
    }
    return result or None


def parse_int_filter(value: str | None) -> set[int] | None:
    if value is None:
        return None
    result: set[int] = set()
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        result.add(int(item))
    return result or None


def terminal_matches(terminal_kind: str | None, mode: str) -> bool:
    terminal_kind = str(terminal_kind or "")
    if mode == "any":
        return True
    if mode == "victory":
        return terminal_kind == "victory"
    if mode == "defeat":
        return terminal_kind == "defeat"
    if mode == "non_defeat":
        return terminal_kind != "defeat"
    raise ValueError(f"unsupported terminal filter: {mode}")


def observation_values(step: dict[str, Any]) -> list[float] | None:
    observation = step.get("observation")
    if not isinstance(observation, list) or not observation:
        return None
    values: list[float] = []
    for value in observation:
        number = as_number(value)
        if number is None:
            return None
        values.append(number)
    return values


def health_ratio(step: dict[str, Any]) -> float:
    observation = step.get("observation")
    if isinstance(observation, list) and len(observation) >= 2:
        value = as_number(observation[1])
        if value is not None:
            return value
    health = as_number(step.get("health"))
    if health is not None:
        return max(0.0, min(1.0, health / 120.0))
    return 1.0


def pressure_value(step: dict[str, Any], key: str) -> float | None:
    diagnostics = step.get("diagnostics")
    if not isinstance(diagnostics, dict):
        return None
    if key == "boundary_edge_risk":
        boundary = diagnostics.get("boundary")
        if not isinstance(boundary, dict):
            return None
        return as_number(boundary.get("edge_risk"))
    return as_number(diagnostics.get(key))


def step_matches(
    step: dict[str, Any],
    *,
    min_seconds: float | None,
    max_seconds: float | None,
    actions: set[int] | None,
    min_boundary_edge_risk: float | None,
    min_enemy_pressure_risk: float | None,
    max_enemy_pressure_risk: float | None,
) -> tuple[bool, str | None]:
    time_seconds = as_number(step.get("time_seconds"))
    if min_seconds is not None and (time_seconds is None or time_seconds < min_seconds):
        return False, "time_before_min"
    if max_seconds is not None and (time_seconds is None or time_seconds > max_seconds):
        return False, "time_after_max"
    action = step.get("action")
    if actions is not None and (not isinstance(action, int) or action not in actions):
        return False, "action_not_selected"
    boundary_edge_risk = pressure_value(step, "boundary_edge_risk")
    if min_boundary_edge_risk is not None and (
        boundary_edge_risk is None or boundary_edge_risk < min_boundary_edge_risk
    ):
        return False, "boundary_edge_below_min"
    enemy_pressure_risk = pressure_value(step, "enemy_pressure_risk")
    if min_enemy_pressure_risk is not None and (
        enemy_pressure_risk is None or enemy_pressure_risk < min_enemy_pressure_risk
    ):
        return False, "enemy_pressure_below_min"
    if max_enemy_pressure_risk is not None and (
        enemy_pressure_risk is None or enemy_pressure_risk > max_enemy_pressure_risk
    ):
        return False, "enemy_pressure_above_max"
    return True, None


def infer_metadata(
    *,
    source_files: list[Path],
    terminal_filter: str,
    map_ids: set[str] | None,
    seeds: set[int] | None,
    min_seconds: float | None,
    max_seconds: float | None,
    actions: set[int] | None,
    sample_role: str,
    sample_source: str,
    observation_len: int | None,
) -> dict[str, Any]:
    return {
        "record_type": "metadata",
        "dataset_version": "policy-trace-sample-export-v0",
        "source_files": [str(path) for path in source_files],
        "terminal_filter": terminal_filter,
        "map_ids": sorted(map_ids) if map_ids else None,
        "seeds": sorted(seeds) if seeds else None,
        "min_seconds": min_seconds,
        "max_seconds": max_seconds,
        "actions": sorted(actions) if actions else None,
        "sample_role": sample_role,
        "sample_source": sample_source,
        "bot": sample_source,
        "map_id": next(iter(sorted(map_ids))) if map_ids and len(map_ids) == 1 else None,
        "observation_version": 2,
        "observation_len": observation_len,
        "action_count": DEFAULT_MOVEMENT_ACTION_COUNT,
        "sample_start_seconds": min_seconds,
        "sample_end_seconds": max_seconds,
        "content_hash": None,
    }


def build_sample(
    *,
    path: Path,
    episode: dict[str, Any],
    step: dict[str, Any],
    observation: list[float],
    sample_role: str,
    sample_source: str,
) -> dict[str, Any]:
    return {
        "record_type": "sample",
        "sample_role": sample_role,
        "sample_source": sample_source,
        "action": int(step["action"]),
        "observation": observation,
        "observation_version": int(step.get("observation_version", 2) or 2),
        "observation_len": len(observation),
        "seed": int(episode.get("seed", 0)),
        "map_id": episode.get("map_id"),
        "bot": sample_source,
        "tick": int(step.get("tick", step.get("step", 0)) or 0),
        "step": int(step.get("step", 0) or 0),
        "time_seconds": float(step.get("time_seconds", 0.0) or 0.0),
        "health_ratio": round(health_ratio(step), 6),
        "level": int(step.get("level", 0) or 0),
        "kills": int(step.get("kills", 0) or 0),
        "terminal_kind": episode.get("terminal_kind"),
        "target_source": "policy_trace_action_retention",
        "action_scores": step.get("action_score"),
        "diagnostics": step.get("diagnostics"),
        "trace_source": {
            "path": str(path),
            "sampled_trace_only": True,
        },
        "limitations": [
            "This sample is derived from sampled policy trace diagnostics.",
            "It may be used for supervised retention or repair anchors only.",
            "It is not RL policy acceptance evidence and does not replace deterministic high-pressure gates.",
        ],
    }


def build_report(
    inputs: list[Path],
    *,
    out: Path,
    terminal_filter: str = "victory",
    map_ids: set[str] | None = None,
    seeds: set[int] | None = None,
    min_seconds: float | None = None,
    max_seconds: float | None = None,
    actions: set[int] | None = None,
    min_boundary_edge_risk: float | None = None,
    min_enemy_pressure_risk: float | None = None,
    max_enemy_pressure_risk: float | None = None,
    max_samples_per_trace: int | None = None,
    max_total_samples: int | None = None,
    sample_role: str = "retention_anchor_input",
    sample_source: str = "policy_trace_retention",
    allow_empty: bool = False,
) -> dict[str, Any]:
    paths = trace_paths(inputs)
    samples: list[dict[str, Any]] = []
    trace_summaries: list[dict[str, Any]] = []
    dropped_counts: dict[str, int] = {}
    load_errors: list[str] = []
    source_step_count = 0
    source_trace_count = 0
    observation_len: int | None = None

    for path in paths:
        try:
            trace = load_json_object(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            load_errors.append(f"{path}: {exc}")
            continue
        episode = trace.get("episode")
        steps = trace.get("steps")
        if not isinstance(episode, dict) or not isinstance(steps, list):
            load_errors.append(f"{path}: invalid policy trace shape")
            continue
        source_trace_count += 1
        source_step_count += len(steps)
        map_id = str(episode.get("map_id", ""))
        seed = int(episode.get("seed", 0) or 0)
        terminal_kind = episode.get("terminal_kind")
        trace_kept = 0
        if map_ids is not None and map_id not in map_ids:
            dropped_counts["map_filtered_trace"] = dropped_counts.get("map_filtered_trace", 0) + 1
            continue
        if seeds is not None and seed not in seeds:
            dropped_counts["seed_filtered_trace"] = dropped_counts.get("seed_filtered_trace", 0) + 1
            continue
        if not terminal_matches(str(terminal_kind or ""), terminal_filter):
            dropped_counts["terminal_filtered_trace"] = (
                dropped_counts.get("terminal_filtered_trace", 0) + 1
            )
            continue
        for step in steps:
            if max_total_samples is not None and len(samples) >= max_total_samples:
                dropped_counts["max_total_samples"] = dropped_counts.get("max_total_samples", 0) + 1
                break
            if max_samples_per_trace is not None and trace_kept >= max_samples_per_trace:
                dropped_counts["max_samples_per_trace"] = (
                    dropped_counts.get("max_samples_per_trace", 0) + 1
                )
                break
            if not isinstance(step, dict):
                dropped_counts["invalid_step"] = dropped_counts.get("invalid_step", 0) + 1
                continue
            matched, reason = step_matches(
                step,
                min_seconds=min_seconds,
                max_seconds=max_seconds,
                actions=actions,
                min_boundary_edge_risk=min_boundary_edge_risk,
                min_enemy_pressure_risk=min_enemy_pressure_risk,
                max_enemy_pressure_risk=max_enemy_pressure_risk,
            )
            if not matched:
                dropped_counts[reason or "filtered_step"] = (
                    dropped_counts.get(reason or "filtered_step", 0) + 1
                )
                continue
            observation = observation_values(step)
            if observation is None:
                dropped_counts["missing_observation"] = (
                    dropped_counts.get("missing_observation", 0) + 1
                )
                continue
            if observation_len is None:
                observation_len = len(observation)
            elif len(observation) != observation_len:
                dropped_counts["mixed_observation_len"] = (
                    dropped_counts.get("mixed_observation_len", 0) + 1
                )
                continue
            samples.append(
                build_sample(
                    path=path,
                    episode=episode,
                    step=step,
                    observation=observation,
                    sample_role=sample_role,
                    sample_source=sample_source,
                )
            )
            trace_kept += 1
        trace_summaries.append(
            {
                "path": str(path),
                "map_id": map_id,
                "seed": seed,
                "terminal_kind": terminal_kind,
                "kept_samples": trace_kept,
            }
        )

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        if samples:
            metadata = infer_metadata(
                source_files=paths,
                terminal_filter=terminal_filter,
                map_ids=map_ids,
                seeds=seeds,
                min_seconds=min_seconds,
                max_seconds=max_seconds,
                actions=actions,
                sample_role=sample_role,
                sample_source=sample_source,
                observation_len=observation_len,
            )
            handle.write(json.dumps(metadata, ensure_ascii=False, sort_keys=True) + "\n")
            for sample in samples:
                handle.write(json.dumps(sample, ensure_ascii=False, sort_keys=True) + "\n")

    action_counts: dict[str, int] = {}
    map_counts: dict[str, int] = {}
    for sample in samples:
        action_key = str(sample["action"])
        action_counts[action_key] = action_counts.get(action_key, 0) + 1
        map_key = str(sample.get("map_id"))
        map_counts[map_key] = map_counts.get(map_key, 0) + 1

    decision = "policy_trace_samples_exported" if samples else "policy_trace_samples_unavailable"
    if load_errors:
        decision = "policy_trace_samples_invalid"
    if not samples and not allow_empty and not load_errors:
        load_errors.append("no samples matched filters; pass --allow-empty to record an empty export")
        decision = "policy_trace_samples_invalid"

    return {
        "decision": decision,
        "source_trace_count": source_trace_count,
        "source_step_count": source_step_count,
        "sample_count": len(samples),
        "samples_path": str(out),
        "terminal_filter": terminal_filter,
        "map_ids": sorted(map_ids) if map_ids else None,
        "seeds": sorted(seeds) if seeds else None,
        "min_seconds": min_seconds,
        "max_seconds": max_seconds,
        "actions": sorted(actions) if actions else None,
        "min_boundary_edge_risk": min_boundary_edge_risk,
        "min_enemy_pressure_risk": min_enemy_pressure_risk,
        "max_enemy_pressure_risk": max_enemy_pressure_risk,
        "sample_role": sample_role,
        "sample_source": sample_source,
        "observation_len": observation_len,
        "action_distribution": {
            action: {
                "count": count,
                "ratio": round(count / max(1, len(samples)), 4),
            }
            for action, count in sorted(action_counts.items(), key=lambda item: int(item[0]))
        },
        "map_distribution": {
            map_id: {
                "count": count,
                "ratio": round(count / max(1, len(samples)), 4),
            }
            for map_id, count in sorted(map_counts.items())
        },
        "trace_summaries": trace_summaries,
        "dropped_counts": dropped_counts,
        "errors": load_errors,
        "limitations": [
            "Exported samples come from sampled policy traces, not full replays.",
            "The output is supervised retention or repair input only, not policy acceptance evidence.",
            "Any model trained from these samples must still pass target-seed preflight, fixed-window high-pressure comparison, no-regression, and failure-case review.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Policy Trace Samples Export",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Samples: `{report['sample_count']}`",
        f"- Output: `{report['samples_path']}`",
        "",
        "## Action Distribution",
        "",
        "| Action | Count | Ratio |",
        "|---|---:|---:|",
    ]
    for action, payload in report["action_distribution"].items():
        lines.append(f"| `{action}` | `{payload['count']}` | `{payload['ratio']}` |")
    lines.extend(["", "## Trace Summaries", "", "| Trace | Seed | Kept |", "|---|---:|---:|"])
    for item in report["trace_summaries"]:
        lines.append(
            f"| `{item['path']}` | `{item['seed']}` | `{item['kept_samples']}` |"
        )
    if report["dropped_counts"]:
        lines.extend(["", "## Dropped Counts", ""])
        lines.extend(f"- `{key}`: `{value}`" for key, value in sorted(report["dropped_counts"].items()))
    if report["errors"]:
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {item}" for item in report["errors"])
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Export selected policy trace steps as samples.")
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--terminal-filter", choices=["any", "victory", "defeat", "non_defeat"], default="victory")
    parser.add_argument("--map-id", dest="map_ids", action="append")
    parser.add_argument("--seed", dest="seeds", type=int, action="append")
    parser.add_argument("--min-seconds", type=float, default=None)
    parser.add_argument("--max-seconds", type=float, default=None)
    parser.add_argument("--actions", type=parse_int_filter, default=None)
    parser.add_argument("--min-boundary-edge-risk", type=float, default=None)
    parser.add_argument("--min-enemy-pressure-risk", type=float, default=None)
    parser.add_argument("--max-enemy-pressure-risk", type=float, default=None)
    parser.add_argument("--max-samples-per-trace", type=int, default=None)
    parser.add_argument("--max-total-samples", type=int, default=None)
    parser.add_argument("--sample-role", default="retention_anchor_input")
    parser.add_argument("--sample-source", default="policy_trace_retention")
    parser.add_argument("--allow-empty", action="store_true")
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--markdown", type=Path, default=None)
    args = parser.parse_args()

    if args.min_seconds is not None and args.max_seconds is not None and args.min_seconds > args.max_seconds:
        parser.error("--min-seconds must be <= --max-seconds")
    if args.max_samples_per_trace is not None and args.max_samples_per_trace <= 0:
        parser.error("--max-samples-per-trace must be positive")
    if args.max_total_samples is not None and args.max_total_samples <= 0:
        parser.error("--max-total-samples must be positive")
    map_ids = parse_csv_filter(args.map_ids)
    seeds = set(args.seeds) if args.seeds else None

    report = build_report(
        args.inputs,
        out=args.out,
        terminal_filter=args.terminal_filter,
        map_ids=map_ids,
        seeds=seeds,
        min_seconds=args.min_seconds,
        max_seconds=args.max_seconds,
        actions=args.actions,
        min_boundary_edge_risk=args.min_boundary_edge_risk,
        min_enemy_pressure_risk=args.min_enemy_pressure_risk,
        max_enemy_pressure_risk=args.max_enemy_pressure_risk,
        max_samples_per_trace=args.max_samples_per_trace,
        max_total_samples=args.max_total_samples,
        sample_role=args.sample_role,
        sample_source=args.sample_source,
        allow_empty=args.allow_empty,
    )
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "policy_trace_samples_exported" or args.allow_empty else 1


if __name__ == "__main__":
    raise SystemExit(main())
