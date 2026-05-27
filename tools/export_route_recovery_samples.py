#!/usr/bin/env python3
"""Export edge-recovery repair samples from route_recovery trace hotspots."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Iterable


GYM_ACTION_MOVEMENTS = {
    0: (0.0, 0.0),
    1: (0.0, 1.0),
    2: (math.sqrt(0.5), math.sqrt(0.5)),
    3: (1.0, 0.0),
    4: (math.sqrt(0.5), -math.sqrt(0.5)),
    5: (0.0, -1.0),
    6: (-math.sqrt(0.5), -math.sqrt(0.5)),
    7: (-1.0, 0.0),
    8: (-math.sqrt(0.5), math.sqrt(0.5)),
}

SOURCE_NAME = "route_recovery_trace_hotspot"


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


def action_pushes_into_edge(action_index: int, diagnostics: dict[str, Any], edge_distance: float) -> bool:
    movement = GYM_ACTION_MOVEMENTS.get(int(action_index), (0.0, 0.0))
    boundary = (diagnostics or {}).get("boundary") or {}
    left = as_number(boundary.get("left_distance"))
    right = as_number(boundary.get("right_distance"))
    bottom = as_number(boundary.get("bottom_distance"))
    top = as_number(boundary.get("top_distance"))
    dx, dy = movement
    return (
        (left is not None and left <= edge_distance and dx < 0.0)
        or (right is not None and right <= edge_distance and dx > 0.0)
        or (bottom is not None and bottom <= edge_distance and dy < 0.0)
        or (top is not None and top <= edge_distance and dy > 0.0)
    )


def inward_vector(diagnostics: dict[str, Any], edge_distance: float) -> tuple[float, float]:
    boundary = (diagnostics or {}).get("boundary") or {}
    dx = 0.0
    dy = 0.0
    left = as_number(boundary.get("left_distance"))
    right = as_number(boundary.get("right_distance"))
    bottom = as_number(boundary.get("bottom_distance"))
    top = as_number(boundary.get("top_distance"))
    if left is not None and left <= edge_distance:
        dx += 1.0
    if right is not None and right <= edge_distance:
        dx -= 1.0
    if bottom is not None and bottom <= edge_distance:
        dy += 1.0
    if top is not None and top <= edge_distance:
        dy -= 1.0
    return dx, dy


def pressure_tags(diagnostics: dict[str, Any]) -> list[str]:
    boundary = diagnostics.get("boundary", {}) if isinstance(diagnostics, dict) else {}
    tags: list[str] = []
    if float(boundary.get("edge_risk", 0.0) or 0.0) >= 0.75:
        tags.append("boundary_edge")
    if float(diagnostics.get("enemy_pressure_risk", 0.0) or 0.0) >= 0.6:
        tags.append("enemy_pressure")
    if float(diagnostics.get("hazard_pressure_risk", 0.0) or 0.0) >= 0.4:
        tags.append("hazard_pressure")
    if float(diagnostics.get("boss_pressure_risk", 0.0) or 0.0) >= 0.25:
        tags.append("boss_pressure")
    if float(diagnostics.get("low_health_risk", 0.0) or 0.0) >= 0.6:
        tags.append("low_health")
    if not tags:
        tags.append("no_major_pressure")
    return tags


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


def apply_phase_duration_conditioning(
    observation: list[float],
    *,
    time_seconds: float,
    phase_duration_seconds: float | None,
) -> list[float]:
    if phase_duration_seconds is None:
        return observation
    conditioned = list(observation)
    if conditioned:
        conditioned[0] = max(0.0, min(1.0, float(time_seconds) / phase_duration_seconds))
    return conditioned


def score_entries(action_score: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(action_score, dict):
        return []
    entries: list[dict[str, Any]] = []
    scores = action_score.get("scores")
    if isinstance(scores, list) and scores:
        for index, value in enumerate(scores):
            score = as_number(value)
            if score is None:
                continue
            entries.append({"action": index, "score": score, "rank": index + 1})
        entries.sort(key=lambda item: item["score"], reverse=True)
        for rank, item in enumerate(entries, start=1):
            item["rank"] = rank
        return entries

    seen = set()
    for rank, item in enumerate(action_score.get("top_actions", []) or [], start=1):
        if not isinstance(item, dict):
            continue
        try:
            action = int(item.get("action"))
        except (TypeError, ValueError):
            continue
        score = as_number(item.get("score"))
        if score is None or action in seen:
            continue
        seen.add(action)
        entries.append({"action": action, "score": score, "rank": rank})
    return entries


def geometry_target_action(
    original_action: int,
    diagnostics: dict[str, Any],
    edge_distance: float,
) -> tuple[int | None, dict[str, Any]]:
    inward_dx, inward_dy = inward_vector(diagnostics, edge_distance)
    if inward_dx == 0.0 and inward_dy == 0.0:
        return None, {"target_selection": "unavailable_no_edge_vector"}

    best_action = None
    best_dot = -float("inf")
    for action, (dx, dy) in GYM_ACTION_MOVEMENTS.items():
        if action == original_action:
            continue
        if action_pushes_into_edge(action, diagnostics, edge_distance):
            continue
        dot = dx * inward_dx + dy * inward_dy
        if dot > best_dot:
            best_action = action
            best_dot = dot

    if best_action is None:
        return None, {"target_selection": "unavailable_no_non_wallward_action"}
    if best_dot <= 0.0 and best_action != 0:
        return 0, {
            "target_selection": "neutral_non_wallward_fallback",
            "inward_vector": [round(inward_dx, 6), round(inward_dy, 6)],
            "geometry_dot": round(best_dot, 6),
        }
    return best_action, {
        "target_selection": "geometry_inward_non_wallward_action",
        "inward_vector": [round(inward_dx, 6), round(inward_dy, 6)],
        "geometry_dot": round(best_dot, 6),
    }


def choose_target_action(
    original_action: int,
    diagnostics: dict[str, Any],
    action_score: dict[str, Any],
    edge_distance: float,
) -> tuple[int | None, dict[str, Any]]:
    entries = score_entries(action_score)
    original_score = None
    for item in entries:
        if item["action"] == original_action:
            original_score = item["score"]
            break
    for item in entries:
        action = int(item["action"])
        if action == original_action:
            continue
        if action_pushes_into_edge(action, diagnostics, edge_distance):
            continue
        decision = {
            "target_selection": "highest_scored_non_wallward_action",
            "score_kind": action_score.get("kind"),
            "target_rank": item["rank"],
            "target_action_score": round(float(item["score"]), 6),
        }
        if original_score is not None:
            decision["original_action_score"] = round(float(original_score), 6)
            decision["score_margin"] = round(float(item["score"] - original_score), 6)
        return action, decision

    return geometry_target_action(original_action, diagnostics, edge_distance)


def compact_action_score(action_score: Any) -> dict[str, Any]:
    if not isinstance(action_score, dict):
        return {"kind": "unavailable", "reason": "missing action_score"}
    result: dict[str, Any] = {"kind": action_score.get("kind", "unknown")}
    if isinstance(action_score.get("scores"), list):
        result["scores"] = [
            round(float(value), 6)
            for value in action_score["scores"]
            if as_number(value) is not None
        ]
    if isinstance(action_score.get("top_actions"), list):
        result["top_actions"] = action_score["top_actions"]
    if "chosen_action_score" in action_score:
        result["chosen_action_score"] = action_score.get("chosen_action_score")
    return result


def health_ratio_from_observation(observation: list[float]) -> float | None:
    if len(observation) < 2:
        return None
    return max(0.0, min(1.0, float(observation[1])))


def build_sample(
    *,
    trace_path: Path,
    episode: dict[str, Any],
    step: dict[str, Any],
    observation: list[float],
    target_action: int,
    decision: dict[str, Any],
    edge_distance: float,
    route_recovery: float,
) -> dict[str, Any]:
    original_action = int(step.get("action", 0))
    diagnostics = step.get("diagnostics") if isinstance(step.get("diagnostics"), dict) else {}
    action_score = step.get("action_score") if isinstance(step.get("action_score"), dict) else {}
    tags = pressure_tags(diagnostics)
    health_ratio = health_ratio_from_observation(observation)
    adapter_decision = {
        "mode": SOURCE_NAME,
        "edge_distance": edge_distance,
        "original_action": original_action,
        "target_action": target_action,
        "route_recovery": round(route_recovery, 6),
        "pressure_tags": tags,
        **decision,
    }
    return {
        "record_type": "edge_recovery_supervision_sample",
        "schema_version": 1,
        "sample_role": "repair_training_input",
        "target_source": SOURCE_NAME,
        "seed": episode.get("seed"),
        "map_id": episode.get("map_id"),
        "step": int(step.get("step", 0)),
        "tick": step.get("tick"),
        "time_seconds": round(float(step.get("time_seconds", 0.0)), 4),
        "health": step.get("health"),
        "health_ratio": round(health_ratio, 6) if health_ratio is not None else None,
        "level": step.get("level"),
        "kills": step.get("kills"),
        "observation_version": step.get("observation_version"),
        "observation_len": len(observation),
        "observation": observation,
        "original_action": original_action,
        "target_action": int(target_action),
        "target_label": adapter_decision["target_selection"],
        "adapter_decision": adapter_decision,
        "action_scores": compact_action_score(action_score),
        "diagnostics": diagnostics,
        "trace_source": {
            "path": str(trace_path),
            "sampled_trace_only": True,
        },
        "limitations": [
            "This sample is derived from sampled route_recovery trace diagnostics.",
            "It may be used for repair training or behavior constraints only.",
            "It is not RL policy acceptance evidence and does not replace deterministic high-pressure gates.",
        ],
    }


def count_map(values: Iterable[Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def write_samples(path: Path, samples: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for sample in samples:
            handle.write(json.dumps(sample, ensure_ascii=False, sort_keys=True) + "\n")


def build_report(
    inputs: Iterable[Path],
    *,
    samples_out: Path,
    edge_distance: float,
    route_recovery_threshold: float,
    min_boundary_edge_risk: float,
    min_seconds: float | None = None,
    max_seconds: float | None = None,
    phase_duration_seconds: float | None = None,
    original_actions: set[int] | None = None,
    max_samples: int | None = None,
) -> dict[str, Any]:
    paths = trace_paths(inputs)
    samples: list[dict[str, Any]] = []
    inspected_step_count = 0
    negative_route_count = 0
    boundary_hotspot_count = 0
    missing_observation_count = 0
    original_not_edge_count = 0
    original_action_filtered_count = 0
    no_target_count = 0
    outside_time_window_count = 0

    for path in paths:
        payload = load_json_object(path)
        episode = payload.get("episode", {})
        if not isinstance(episode, dict):
            episode = {}
        steps = payload.get("steps")
        if not isinstance(steps, list):
            raise ValueError(f"{path} must contain a `steps` list")
        for step in steps:
            if not isinstance(step, dict):
                continue
            inspected_step_count += 1
            time_seconds = float(step.get("time_seconds", 0.0))
            if min_seconds is not None and time_seconds < min_seconds:
                outside_time_window_count += 1
                continue
            if max_seconds is not None and time_seconds >= max_seconds:
                outside_time_window_count += 1
                continue
            route_recovery = as_number((step.get("reward_breakdown") or {}).get("route_recovery"))
            if route_recovery is None or route_recovery >= route_recovery_threshold:
                continue
            negative_route_count += 1

            diagnostics = step.get("diagnostics") if isinstance(step.get("diagnostics"), dict) else {}
            boundary = diagnostics.get("boundary", {}) if isinstance(diagnostics, dict) else {}
            edge_risk = as_number(boundary.get("edge_risk")) or 0.0
            if edge_risk < min_boundary_edge_risk:
                continue
            boundary_hotspot_count += 1

            observation = observation_values(step)
            if observation is None:
                missing_observation_count += 1
                continue
            observation = apply_phase_duration_conditioning(
                observation,
                time_seconds=time_seconds,
                phase_duration_seconds=phase_duration_seconds,
            )

            original_action = int(step.get("action", 0))
            if original_actions is not None and original_action not in original_actions:
                original_action_filtered_count += 1
                continue
            if not action_pushes_into_edge(original_action, diagnostics, edge_distance):
                original_not_edge_count += 1
                continue

            target_action, decision = choose_target_action(
                original_action,
                diagnostics,
                step.get("action_score") if isinstance(step.get("action_score"), dict) else {},
                edge_distance,
            )
            if target_action is None:
                no_target_count += 1
                continue
            if action_pushes_into_edge(target_action, diagnostics, edge_distance):
                no_target_count += 1
                continue

            samples.append(
                build_sample(
                    trace_path=path,
                    episode=episode,
                    step=step,
                    observation=observation,
                    target_action=target_action,
                    decision=decision,
                    edge_distance=edge_distance,
                    route_recovery=route_recovery,
                )
            )
            if max_samples is not None and len(samples) >= max_samples:
                break
        if max_samples is not None and len(samples) >= max_samples:
            break

    write_samples(samples_out, samples)
    return {
        "report_version": 1,
        "decision": (
            "route_recovery_samples_exported"
            if samples
            else "route_recovery_samples_unavailable"
        ),
        "source_trace_count": len(paths),
        "inspected_step_count": inspected_step_count,
        "negative_route_recovery_count": negative_route_count,
        "boundary_hotspot_count": boundary_hotspot_count,
        "outside_time_window_count": outside_time_window_count,
        "missing_observation_count": missing_observation_count,
        "original_not_edge_count": original_not_edge_count,
        "original_action_filtered_count": original_action_filtered_count,
        "no_target_count": no_target_count,
        "sample_count": len(samples),
        "samples_path": str(samples_out),
        "edge_distance": edge_distance,
        "route_recovery_threshold": route_recovery_threshold,
        "min_boundary_edge_risk": min_boundary_edge_risk,
        "min_seconds": min_seconds,
        "max_seconds": max_seconds,
        "phase_duration_seconds": phase_duration_seconds,
        "original_actions": sorted(original_actions) if original_actions is not None else None,
        "map_distribution": count_map(sample.get("map_id") for sample in samples),
        "original_action_distribution": count_map(sample.get("original_action") for sample in samples),
        "target_action_distribution": count_map(sample.get("target_action") for sample in samples),
        "target_label_distribution": count_map(sample.get("target_label") for sample in samples),
        "limitations": [
            "Samples are extracted only from sampled trace rows that include observation vectors.",
            "The export targets boundary-pinned negative route_recovery hotspots, not all unsafe movement.",
            "A successful export is repair training material, not RL policy acceptance.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Route Recovery Supervision Samples",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Source traces: `{report['source_trace_count']}`",
        f"- Inspected trace rows: `{report['inspected_step_count']}`",
        f"- Negative route_recovery rows: `{report['negative_route_recovery_count']}`",
        f"- Boundary hotspot rows: `{report['boundary_hotspot_count']}`",
        f"- Outside time window rows: `{report['outside_time_window_count']}`",
        f"- Original action filtered rows: `{report['original_action_filtered_count']}`",
        f"- Missing observation rows: `{report['missing_observation_count']}`",
        f"- Exported samples: `{report['sample_count']}`",
        f"- Samples: `{report['samples_path']}`",
        "",
        "## Distributions",
        "",
        f"- Maps: `{json.dumps(report['map_distribution'], sort_keys=True, ensure_ascii=False)}`",
        f"- Original actions: `{json.dumps(report['original_action_distribution'], sort_keys=True)}`",
        f"- Target actions: `{json.dumps(report['target_action_distribution'], sort_keys=True)}`",
        f"- Target labels: `{json.dumps(report['target_label_distribution'], sort_keys=True)}`",
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export edge-recovery repair samples from route_recovery trace hotspots."
    )
    parser.add_argument("traces", type=Path, nargs="+", help="Trace JSON files or directories.")
    parser.add_argument("--out", type=Path, required=True, help="Output JSONL sample path.")
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--markdown", type=Path, default=None)
    parser.add_argument("--edge-distance", type=float, default=32.0)
    parser.add_argument("--route-recovery-threshold", type=float, default=0.0)
    parser.add_argument("--min-boundary-edge-risk", type=float, default=0.75)
    parser.add_argument("--min-seconds", type=float, default=None)
    parser.add_argument("--max-seconds", type=float, default=None)
    parser.add_argument(
        "--phase-duration-seconds",
        type=float,
        default=None,
        help="Rewrite observation progress using time_seconds / this horizon before writing samples.",
    )
    parser.add_argument(
        "--original-actions",
        default=None,
        help="Comma-separated original policy actions to export, for example `3` or `1,3,6`.",
    )
    parser.add_argument("--max-samples", type=int, default=None)
    args = parser.parse_args()
    if args.min_seconds is not None and args.min_seconds < 0.0:
        parser.error("--min-seconds must be greater than or equal to zero")
    if args.max_seconds is not None and args.max_seconds <= 0.0:
        parser.error("--max-seconds must be greater than zero")
    if (
        args.min_seconds is not None
        and args.max_seconds is not None
        and args.max_seconds <= args.min_seconds
    ):
        parser.error("--max-seconds must be greater than --min-seconds")
    if args.phase_duration_seconds is not None and args.phase_duration_seconds <= 0.0:
        parser.error("--phase-duration-seconds must be greater than zero")
    original_actions = None
    if args.original_actions:
        try:
            original_actions = {
                int(item.strip())
                for item in args.original_actions.split(",")
                if item.strip()
            }
        except ValueError:
            parser.error("--original-actions must be a comma-separated list of integers")
        if not original_actions:
            parser.error("--original-actions must include at least one action")
        invalid_actions = sorted(action for action in original_actions if action not in GYM_ACTION_MOVEMENTS)
        if invalid_actions:
            parser.error(f"--original-actions contains unsupported actions: {invalid_actions}")

    report = build_report(
        args.traces,
        samples_out=args.out,
        edge_distance=args.edge_distance,
        route_recovery_threshold=args.route_recovery_threshold,
        min_boundary_edge_risk=args.min_boundary_edge_risk,
        min_seconds=args.min_seconds,
        max_seconds=args.max_seconds,
        phase_duration_seconds=args.phase_duration_seconds,
        original_actions=original_actions,
        max_samples=args.max_samples,
    )
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
