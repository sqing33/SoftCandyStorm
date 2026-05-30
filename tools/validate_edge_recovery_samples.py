#!/usr/bin/env python3
"""Validate edge-recovery supervision samples.

These samples are produced by diagnostic edge-recovery adapters. They are
allowed as repair training inputs, but they are never policy acceptance
evidence.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


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

ALLOWED_TARGET_SOURCES = {
    "edge_recovery_branch",
    "edge_recovery_filter",
    "route_recovery_trace_hotspot",
}


def as_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


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


def load_samples(path: Path) -> list[dict[str, Any]]:
    samples = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            payload = json.loads(text)
            if not isinstance(payload, dict):
                raise ValueError(f"{path}:{line_number} must contain a JSON object")
            payload["_source_line"] = line_number
            samples.append(payload)
    return samples


def add_error(errors: list[str], sample: dict[str, Any], message: str) -> None:
    line = sample.get("_source_line", "?")
    seed = sample.get("seed", "?")
    map_id = sample.get("map_id", "?")
    errors.append(f"line {line} seed {seed} map {map_id}: {message}")


def validate_sample(sample: dict[str, Any], errors: list[str], warnings: list[str]) -> None:
    if sample.get("record_type") != "edge_recovery_supervision_sample":
        add_error(errors, sample, "record_type must be edge_recovery_supervision_sample")
    role = str(sample.get("sample_role", ""))
    if role != "repair_training_input":
        add_error(errors, sample, "sample_role must be repair_training_input")
    lowered_role = role.lower()
    if any(token in lowered_role for token in FORBIDDEN_ROLE_TOKENS):
        add_error(errors, sample, f"sample_role is too strong: {role}")
    target_source = sample.get("target_source")
    if target_source not in ALLOWED_TARGET_SOURCES:
        add_error(
            errors,
            sample,
            "target_source must be one of "
            + ", ".join(sorted(ALLOWED_TARGET_SOURCES)),
        )

    observation = sample.get("observation")
    observation_len = sample.get("observation_len")
    if not isinstance(observation, list) or not observation:
        add_error(errors, sample, "observation must be a non-empty list")
    elif observation_len != len(observation):
        add_error(errors, sample, "observation_len does not match observation")
    elif not all(as_number(value) is not None for value in observation):
        add_error(errors, sample, "observation must contain only numbers")

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
    edge_distance = as_number(decision.get("edge_distance"))
    if edge_distance is None or edge_distance < 0.0:
        add_error(errors, sample, "adapter_decision.edge_distance must be non-negative")
        return
    if decision.get("mode") not in ALLOWED_TARGET_SOURCES:
        add_error(
            errors,
            sample,
            "adapter_decision.mode must be one of "
            + ", ".join(sorted(ALLOWED_TARGET_SOURCES)),
        )
    if target_source in ALLOWED_TARGET_SOURCES and decision.get("mode") != target_source:
        add_error(errors, sample, "adapter_decision.mode must match target_source")
    if decision.get("original_action") != original_action:
        add_error(errors, sample, "adapter_decision original_action mismatch")
    if decision.get("target_action") != target_action:
        add_error(errors, sample, "adapter_decision target_action mismatch")

    diagnostics = sample.get("diagnostics")
    if not isinstance(diagnostics, dict):
        add_error(errors, sample, "diagnostics must be an object")
        return
    if not isinstance(diagnostics.get("boundary"), dict):
        add_error(errors, sample, "diagnostics.boundary is required")
        return
    if original_action in GYM_ACTION_MOVEMENTS and not action_pushes_into_edge(
        int(original_action),
        diagnostics,
        edge_distance,
    ):
        add_error(errors, sample, "original_action does not push into the recorded edge")
    if target_action in GYM_ACTION_MOVEMENTS and action_pushes_into_edge(
        int(target_action),
        diagnostics,
        edge_distance,
    ):
        add_error(errors, sample, "target_action still pushes into the recorded edge")

    limitations = sample.get("limitations")
    if not isinstance(limitations, list) or not limitations:
        warnings.append(f"line {sample.get('_source_line', '?')}: missing limitations")
    elif not any("not RL policy acceptance evidence" in str(item) for item in limitations):
        warnings.append(f"line {sample.get('_source_line', '?')}: limitations should reject acceptance evidence use")


def summarize_distribution(samples: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for sample in samples:
        value = str(sample.get(key))
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: item[0]))


def build_report(samples_path: Path) -> dict[str, Any]:
    samples = load_samples(samples_path)
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
        "source": str(samples_path),
        "decision": (
            "edge_recovery_samples_valid"
            if samples and not errors
            else "edge_recovery_samples_invalid"
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
        "errors": errors,
        "warnings": warnings,
        "limitations": [
            "This validator checks sample structure and edge-action consistency only.",
            "A valid result means samples may be used for repair training inputs, not RL policy acceptance.",
            "Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Edge Recovery Sample Validation",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Source: `{report['source']}`",
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("samples")
    parser.add_argument("--report", default=None)
    parser.add_argument("--markdown", default=None)
    args = parser.parse_args()

    report = build_report(Path(args.samples))
    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    if args.markdown:
        write_markdown(report, Path(args.markdown))
    if not args.report:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    raise SystemExit(0 if report["decision"] == "edge_recovery_samples_valid" else 1)


if __name__ == "__main__":
    main()
