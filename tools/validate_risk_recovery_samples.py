#!/usr/bin/env python3
"""Validate late risk-recovery supervision samples.

These samples are emitted by the diagnostic late_recovery_filter adapter. They
may be used as repair training inputs, but they are never policy acceptance
evidence.
"""

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

FORBIDDEN_ROLE_TOKENS = {
    "acceptance",
    "accepted",
    "candidate",
    "release",
    "playtest",
    "rl_test_bot_candidate",
}

ALLOWED_RISK_REASONS = {
    "wallward_edge",
    "idle_under_late_pressure",
    "toward_hazard",
    "toward_boss",
    "toward_enemy_pressure",
}


def as_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def clamp_float(value: Any, minimum: float = 0.0, maximum: float = 1.0) -> float:
    number = as_number(value)
    if number is None or not math.isfinite(number):
        return minimum
    return min(max(float(number), minimum), maximum)


def vector_from_payload(value: Any) -> tuple[float, float]:
    if not isinstance(value, (list, tuple)) or len(value) < 2:
        return (0.0, 0.0)
    x = as_number(value[0])
    y = as_number(value[1])
    if x is None or y is None:
        return (0.0, 0.0)
    return (float(x), float(y))


def action_vector_alignment(action_index: int, vector: tuple[float, float]) -> float:
    movement = GYM_ACTION_MOVEMENTS.get(int(action_index), (0.0, 0.0))
    vx, vy = vector
    mx, my = movement
    movement_len = math.hypot(mx, my)
    vector_len = math.hypot(vx, vy)
    if movement_len <= 0.0 or vector_len <= 1e-6:
        return 0.0
    return (mx * vx + my * vy) / (movement_len * vector_len)


def action_moves_toward_vector(
    action_index: int,
    vector: tuple[float, float],
    threshold: float,
) -> bool:
    return action_vector_alignment(action_index, vector) > float(threshold)


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


def load_samples(paths: Iterable[Path]) -> list[dict[str, Any]]:
    samples = []
    for path in paths:
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                text = line.strip()
                if not text:
                    continue
                payload = json.loads(text)
                if not isinstance(payload, dict):
                    raise ValueError(f"{path}:{line_number} must contain a JSON object")
                payload["_source_path"] = str(path)
                payload["_source_line"] = line_number
                samples.append(payload)
    return samples


def add_error(errors: list[str], sample: dict[str, Any], message: str) -> None:
    source = sample.get("_source_path", "?")
    line = sample.get("_source_line", "?")
    seed = sample.get("seed", "?")
    map_id = sample.get("map_id", "?")
    errors.append(f"{source}:{line} seed {seed} map {map_id}: {message}")


def add_warning(warnings: list[str], sample: dict[str, Any], message: str) -> None:
    source = sample.get("_source_path", "?")
    line = sample.get("_source_line", "?")
    seed = sample.get("seed", "?")
    map_id = sample.get("map_id", "?")
    warnings.append(f"{source}:{line} seed {seed} map {map_id}: {message}")


def thresholds_from_decision(decision: dict[str, Any]) -> dict[str, float]:
    thresholds = decision.get("thresholds")
    if not isinstance(thresholds, dict):
        thresholds = {}
    return {
        "hazard": clamp_float(thresholds.get("hazard"), 0.0, 1.0),
        "boss": clamp_float(thresholds.get("boss"), 0.0, 1.0),
        "enemy": clamp_float(thresholds.get("enemy"), 0.0, 1.0),
        "low_health": clamp_float(thresholds.get("low_health"), 0.0, 1.0),
        "toward_dot": clamp_float(thresholds.get("toward_dot"), -1.0, 1.0),
    }


def pressure_context_from_decision(decision: dict[str, Any]) -> dict[str, Any]:
    pressure = decision.get("pressure_context")
    return pressure if isinstance(pressure, dict) else {}


def pressure_metric(pressure: dict[str, Any], key: str) -> float:
    return clamp_float(pressure.get(key), 0.0, 1.0)


def computed_risk_reasons(
    action_index: int,
    *,
    diagnostics: dict[str, Any],
    decision: dict[str, Any],
    time_seconds: float,
) -> list[str]:
    min_seconds = as_number(decision.get("min_seconds"))
    if min_seconds is not None and time_seconds < min_seconds:
        return []

    thresholds = thresholds_from_decision(decision)
    edge_distance = as_number(decision.get("edge_distance")) or 0.0
    pressure = pressure_context_from_decision(decision)
    hazard_pressure = pressure_metric(pressure, "hazard_pressure_risk")
    boss_pressure = pressure_metric(pressure, "boss_pressure_risk")
    enemy_pressure = pressure_metric(pressure, "enemy_pressure_risk")
    low_health = pressure_metric(pressure, "low_health_risk")
    combined_pressure = max(
        pressure_metric(pressure, "combined_pressure"),
        hazard_pressure,
        boss_pressure,
        enemy_pressure,
    )

    reasons: list[str] = []
    if action_pushes_into_edge(action_index, diagnostics, edge_distance):
        reasons.append("wallward_edge")
    if (
        int(action_index) == 0
        and combined_pressure > 0.0
        and (
            low_health >= thresholds["low_health"]
            or hazard_pressure >= thresholds["hazard"]
            or boss_pressure >= thresholds["boss"]
            or enemy_pressure >= thresholds["enemy"]
        )
    ):
        reasons.append("idle_under_late_pressure")
    if hazard_pressure >= thresholds["hazard"] and action_moves_toward_vector(
        action_index,
        vector_from_payload(pressure.get("hazard_vector")),
        thresholds["toward_dot"],
    ):
        reasons.append("toward_hazard")
    if boss_pressure >= thresholds["boss"] and action_moves_toward_vector(
        action_index,
        vector_from_payload(pressure.get("boss_vector")),
        thresholds["toward_dot"],
    ):
        reasons.append("toward_boss")
    if enemy_pressure >= thresholds["enemy"] and action_moves_toward_vector(
        action_index,
        vector_from_payload(pressure.get("enemy_vector")),
        thresholds["toward_dot"],
    ):
        reasons.append("toward_enemy_pressure")
    return reasons


def action_risk_score(
    action_index: int,
    *,
    diagnostics: dict[str, Any],
    decision: dict[str, Any],
) -> float:
    thresholds = thresholds_from_decision(decision)
    edge_distance = as_number(decision.get("edge_distance")) or 0.0
    pressure = pressure_context_from_decision(decision)
    hazard_pressure = pressure_metric(pressure, "hazard_pressure_risk")
    boss_pressure = pressure_metric(pressure, "boss_pressure_risk")
    enemy_pressure = pressure_metric(pressure, "enemy_pressure_risk")
    low_health = pressure_metric(pressure, "low_health_risk")
    combined_pressure = max(
        pressure_metric(pressure, "combined_pressure"),
        hazard_pressure,
        boss_pressure,
        enemy_pressure,
    )

    score = 0.0
    if action_pushes_into_edge(action_index, diagnostics, edge_distance):
        score += 1.0
    score += hazard_pressure * max(
        0.0,
        action_vector_alignment(action_index, vector_from_payload(pressure.get("hazard_vector"))),
    )
    score += boss_pressure * max(
        0.0,
        action_vector_alignment(action_index, vector_from_payload(pressure.get("boss_vector"))),
    )
    score += enemy_pressure * max(
        0.0,
        action_vector_alignment(action_index, vector_from_payload(pressure.get("enemy_vector"))),
    )
    if int(action_index) == 0 and combined_pressure > 0.0:
        score += 0.25 * combined_pressure
    return round(score * (1.0 + low_health), 6)


def validate_role(sample: dict[str, Any], errors: list[str]) -> None:
    if sample.get("record_type") != "risk_recovery_supervision_sample":
        add_error(errors, sample, "record_type must be risk_recovery_supervision_sample")
    role = str(sample.get("sample_role", ""))
    if role != "repair_training_input":
        add_error(errors, sample, "sample_role must be repair_training_input")
    lowered_role = role.lower()
    if any(token in lowered_role for token in FORBIDDEN_ROLE_TOKENS):
        add_error(errors, sample, f"sample_role is too strong: {role}")
    if sample.get("target_source") != "late_recovery_filter":
        add_error(errors, sample, "target_source must be late_recovery_filter")


def validate_observation(sample: dict[str, Any], errors: list[str]) -> None:
    observation = sample.get("observation")
    observation_len = sample.get("observation_len")
    if not isinstance(observation, list) or not observation:
        add_error(errors, sample, "observation must be a non-empty list")
    elif observation_len != len(observation):
        add_error(errors, sample, "observation_len does not match observation")
    elif not all(as_number(value) is not None for value in observation):
        add_error(errors, sample, "observation must contain only numbers")


def validate_adapter_decision(
    sample: dict[str, Any],
    errors: list[str],
    warnings: list[str],
) -> None:
    original_action = sample.get("original_action")
    target_action = sample.get("target_action")
    if original_action not in GYM_ACTION_MOVEMENTS:
        add_error(errors, sample, "original_action must be in 0..8")
    if target_action not in GYM_ACTION_MOVEMENTS:
        add_error(errors, sample, "target_action must be in 0..8")
    if original_action == target_action:
        add_error(errors, sample, "target_action must differ from original_action")

    decision = sample.get("adapter_decision")
    if not isinstance(decision, dict):
        add_error(errors, sample, "adapter_decision must be an object")
        return
    if decision.get("mode") != "late_recovery_filter":
        add_error(errors, sample, "adapter_decision.mode must be late_recovery_filter")
    if decision.get("original_action") != original_action:
        add_error(errors, sample, "adapter_decision original_action mismatch")
    if decision.get("target_action") != target_action:
        add_error(errors, sample, "adapter_decision target_action mismatch")
    edge_distance = as_number(decision.get("edge_distance"))
    if edge_distance is None or edge_distance < 0.0:
        add_error(errors, sample, "adapter_decision.edge_distance must be non-negative")
    min_seconds = as_number(decision.get("min_seconds"))
    if min_seconds is None or min_seconds < 0.0:
        add_error(errors, sample, "adapter_decision.min_seconds must be non-negative")
    time_seconds = as_number(sample.get("time_seconds"))
    if time_seconds is None:
        add_error(errors, sample, "time_seconds must be numeric")
    elif min_seconds is not None and time_seconds < min_seconds:
        add_error(errors, sample, "sample time is before adapter_decision.min_seconds")

    thresholds = decision.get("thresholds")
    if not isinstance(thresholds, dict):
        add_error(errors, sample, "adapter_decision.thresholds must be an object")
    else:
        for key in ("hazard", "boss", "enemy", "low_health", "toward_dot"):
            if as_number(thresholds.get(key)) is None:
                add_error(errors, sample, f"adapter_decision.thresholds.{key} must be numeric")

    pressure = decision.get("pressure_context")
    if not isinstance(pressure, dict):
        add_error(errors, sample, "adapter_decision.pressure_context must be an object")
    else:
        for key in (
            "hazard_pressure_risk",
            "boss_pressure_risk",
            "enemy_pressure_risk",
            "low_health_risk",
            "combined_pressure",
        ):
            if as_number(pressure.get(key)) is None:
                add_error(errors, sample, f"adapter_decision.pressure_context.{key} must be numeric")

    diagnostics = sample.get("diagnostics")
    if not isinstance(diagnostics, dict):
        add_error(errors, sample, "diagnostics must be an object")
        return
    if not isinstance(diagnostics.get("boundary"), dict):
        add_error(errors, sample, "diagnostics.boundary is required")
        return

    if original_action not in GYM_ACTION_MOVEMENTS or target_action not in GYM_ACTION_MOVEMENTS:
        return
    if time_seconds is None:
        return

    recorded_original = decision.get("risk_reasons")
    if not isinstance(recorded_original, list) or not recorded_original:
        add_error(errors, sample, "adapter_decision.risk_reasons must be a non-empty list")
        recorded_original = []
    invalid_reasons = sorted(set(recorded_original) - ALLOWED_RISK_REASONS)
    if invalid_reasons:
        add_error(errors, sample, f"unsupported risk_reasons: {invalid_reasons}")

    recorded_target = decision.get("target_risk_reasons")
    if not isinstance(recorded_target, list):
        add_error(errors, sample, "adapter_decision.target_risk_reasons must be a list")
        recorded_target = []
    invalid_target_reasons = sorted(set(recorded_target) - ALLOWED_RISK_REASONS)
    if invalid_target_reasons:
        add_error(errors, sample, f"unsupported target_risk_reasons: {invalid_target_reasons}")

    computed_original = computed_risk_reasons(
        int(original_action),
        diagnostics=diagnostics,
        decision=decision,
        time_seconds=float(time_seconds),
    )
    computed_target = computed_risk_reasons(
        int(target_action),
        diagnostics=diagnostics,
        decision=decision,
        time_seconds=float(time_seconds),
    )
    if set(recorded_original) != set(computed_original):
        add_error(
            errors,
            sample,
            f"risk_reasons mismatch: recorded={sorted(recorded_original)} computed={computed_original}",
        )
    if set(recorded_target) != set(computed_target):
        add_error(
            errors,
            sample,
            f"target_risk_reasons mismatch: recorded={sorted(recorded_target)} computed={computed_target}",
        )

    original_score = action_risk_score(int(original_action), diagnostics=diagnostics, decision=decision)
    target_score = action_risk_score(int(target_action), diagnostics=diagnostics, decision=decision)
    if target_score > original_score + 1e-6:
        add_warning(
            warnings,
            sample,
            f"target risk score {target_score} is worse than original {original_score}",
        )


def validate_limitations(sample: dict[str, Any], warnings: list[str]) -> None:
    limitations = sample.get("limitations")
    if not isinstance(limitations, list) or not limitations:
        add_warning(warnings, sample, "missing limitations")
    elif not any("not RL policy acceptance evidence" in str(item) for item in limitations):
        add_warning(warnings, sample, "limitations should reject acceptance evidence use")


def validate_sample(
    sample: dict[str, Any],
    errors: list[str],
    warnings: list[str],
) -> None:
    validate_role(sample, errors)
    validate_observation(sample, errors)
    validate_adapter_decision(sample, errors, warnings)
    validate_limitations(sample, warnings)


def normalize_paths(paths: Path | Iterable[Path]) -> list[Path]:
    if isinstance(paths, Path):
        return [paths]
    return [Path(path) for path in paths]


def summarize_distribution(samples: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for sample in samples:
        value = str(sample.get(key))
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: item[0]))


def summarize_reasons(samples: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for sample in samples:
        decision = sample.get("adapter_decision")
        values = decision.get(key) if isinstance(decision, dict) else None
        if not isinstance(values, list):
            counts["<missing>"] = counts.get("<missing>", 0) + 1
            continue
        if not values:
            counts["<none>"] = counts.get("<none>", 0) + 1
            continue
        for value in values:
            text = str(value)
            counts[text] = counts.get(text, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def build_report(paths: Path | Iterable[Path]) -> dict[str, Any]:
    sample_paths = normalize_paths(paths)
    samples = load_samples(sample_paths)
    errors: list[str] = []
    warnings: list[str] = []
    for sample in samples:
        validate_sample(sample, errors, warnings)

    map_ids = sorted({str(sample.get("map_id")) for sample in samples})
    seeds = sorted({sample.get("seed") for sample in samples if sample.get("seed") is not None})
    times = [as_number(sample.get("time_seconds")) for sample in samples]
    times = [time for time in times if time is not None]
    return {
        "report_version": 1,
        "sources": [str(path) for path in sample_paths],
        "decision": (
            "risk_recovery_samples_valid"
            if samples and not errors
            else "risk_recovery_samples_invalid"
        ),
        "sample_count": len(samples),
        "map_ids": map_ids,
        "seeds": seeds,
        "time_range_seconds": {
            "min": round(min(times), 4) if times else None,
            "max": round(max(times), 4) if times else None,
        },
        "original_action_distribution": summarize_distribution(samples, "original_action"),
        "target_action_distribution": summarize_distribution(samples, "target_action"),
        "risk_reason_distribution": summarize_reasons(samples, "risk_reasons"),
        "target_risk_reason_distribution": summarize_reasons(samples, "target_risk_reasons"),
        "errors": errors,
        "warnings": warnings,
        "limitations": [
            "This validator checks sample structure and late-risk reason consistency only.",
            "A valid result means samples may be used for repair training inputs, not RL policy acceptance.",
            "Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Risk Recovery Sample Validation",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Sources: `{len(report['sources'])}`",
        f"- Samples: `{report['sample_count']}`",
        f"- Maps: `{', '.join(report['map_ids'])}`",
        f"- Seeds: `{', '.join(str(seed) for seed in report['seeds'])}`",
        f"- Time range: `{report['time_range_seconds']['min']}` to `{report['time_range_seconds']['max']}` seconds",
        "",
        "## Original Actions",
    ]
    for action, count in report["original_action_distribution"].items():
        lines.append(f"- `{action}`: {count}")
    lines.extend(["", "## Target Actions"])
    for action, count in report["target_action_distribution"].items():
        lines.append(f"- `{action}`: {count}")
    lines.extend(["", "## Risk Reasons"])
    for reason, count in report["risk_reason_distribution"].items():
        lines.append(f"- `{reason}`: {count}")
    lines.extend(["", "## Target Risk Reasons"])
    for reason, count in report["target_risk_reason_distribution"].items():
        lines.append(f"- `{reason}`: {count}")
    lines.extend(["", "## Notes"])
    lines.extend(f"- {item}" for item in report["limitations"])
    if report["errors"]:
        lines.extend(["", "## Errors"])
        lines.extend(f"- {error}" for error in report["errors"])
    if report["warnings"]:
        lines.extend(["", "## Warnings"])
        lines.extend(f"- {warning}" for warning in report["warnings"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate late risk-recovery supervision samples.")
    parser.add_argument("samples", type=Path, nargs="+", help="Risk recovery JSONL sample paths.")
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--markdown", type=Path, default=None)
    args = parser.parse_args()

    report = build_report(args.samples)
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
    return 0 if report["decision"] == "risk_recovery_samples_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
