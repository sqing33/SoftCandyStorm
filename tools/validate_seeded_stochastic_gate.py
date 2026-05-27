#!/usr/bin/env python3
"""Validate seeded stochastic RL watch evidence.

This validator is intentionally not an RL policy acceptance gate. It checks
whether a seeded stochastic comparison pair is strong enough to keep exploring
the repair direction while preserving the deterministic acceptance boundary.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_CRITERIA = {
    "required_map_preset": "high-pressure",
    "min_map_count": 3,
    "min_short_seconds": 60.0,
    "min_long_seconds": 180.0,
    "min_short_seeds": 10,
    "min_long_seeds": 3,
    "min_policy_win_rate": 1.0,
    "min_normalized_action_entropy": 0.75,
    "max_dominant_action_ratio": 0.7,
}

FORBIDDEN_DECISION_TOKENS = {
    "acceptance",
    "accepted",
    "candidate",
    "release",
    "playtest",
    "balance_gate_pass",
    "rl_test_bot_candidate",
}


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


def map_entries(report: dict[str, Any]) -> list[dict[str, Any]]:
    summary = report.get("summary")
    if not isinstance(summary, dict):
        return []
    maps = summary.get("maps")
    if not isinstance(maps, list):
        return []
    return [item for item in maps if isinstance(item, dict)]


def dominant_action_ratio(map_entry: dict[str, Any]) -> float | None:
    dominant = map_entry.get("policy_dominant_action")
    if not isinstance(dominant, dict):
        return None
    return as_number(dominant.get("ratio"))


def has_repair_findings(report: dict[str, Any]) -> bool:
    findings = report.get("findings")
    if not isinstance(findings, list):
        return False
    return any(
        isinstance(item, dict) and item.get("severity") == "repair"
        for item in findings
    )


def report_summary(report: dict[str, Any]) -> dict[str, Any]:
    entries = map_entries(report)
    return {
        "action_selection": report.get("action_selection"),
        "action_random_seed": report.get("action_random_seed"),
        "map_preset": report.get("map_preset"),
        "seed_start": report.get("seed_start"),
        "seeds": report.get("seeds"),
        "seconds": report.get("seconds"),
        "gate_decision": report.get("gate_decision"),
        "minimum_policy_win_rate": (
            report.get("summary", {}).get("minimum_policy_win_rate")
            if isinstance(report.get("summary"), dict)
            else None
        ),
        "average_policy_win_rate": (
            report.get("summary", {}).get("average_policy_win_rate")
            if isinstance(report.get("summary"), dict)
            else None
        ),
        "maps": [
            {
                "map_id": item.get("map_id"),
                "policy_win_rate": item.get("policy_win_rate"),
                "policy_normalized_action_entropy": item.get(
                    "policy_normalized_action_entropy"
                ),
                "policy_dominant_action": item.get("policy_dominant_action"),
                "inner_gate_decision": item.get("inner_gate_decision"),
            }
            for item in entries
        ],
    }


def add_error(errors: list[str], label: str, message: str) -> None:
    errors.append(f"{label}: {message}")


def validate_report(
    label: str,
    report: dict[str, Any],
    *,
    min_seconds: float,
    min_seeds: int,
    criteria: dict[str, Any],
    errors: list[str],
    warnings: list[str],
) -> None:
    if report.get("action_selection") != "stochastic":
        add_error(errors, label, "action_selection must be stochastic")
    if as_number(report.get("action_random_seed")) is None:
        add_error(errors, label, "action_random_seed must be recorded")
    if report.get("map_preset") != criteria["required_map_preset"]:
        add_error(
            errors,
            label,
            f"map_preset must be {criteria['required_map_preset']}",
        )
    seconds = as_number(report.get("seconds"))
    if seconds is None or seconds < min_seconds:
        add_error(errors, label, f"seconds must be at least {min_seconds}")
    seeds = as_number(report.get("seeds"))
    if seeds is None or seeds < min_seeds:
        add_error(errors, label, f"seeds must be at least {min_seeds}")
    if has_repair_findings(report):
        add_error(errors, label, "repair findings are present")

    gate_decision = str(report.get("gate_decision", ""))
    lowered_gate = gate_decision.lower()
    if any(token in lowered_gate for token in FORBIDDEN_DECISION_TOKENS):
        add_error(errors, label, f"gate_decision is too strong: {gate_decision}")

    entries = map_entries(report)
    if len(entries) < int(criteria["min_map_count"]):
        add_error(errors, label, f"map_count must be at least {criteria['min_map_count']}")
    for item in entries:
        map_id = item.get("map_id", "unknown")
        prefix = f"{label}/{map_id}"
        win_rate = as_number(item.get("policy_win_rate"))
        if win_rate is None or win_rate < float(criteria["min_policy_win_rate"]):
            add_error(
                errors,
                prefix,
                f"policy_win_rate must be at least {criteria['min_policy_win_rate']}",
            )
        entropy = as_number(item.get("policy_normalized_action_entropy"))
        if entropy is None or entropy < float(criteria["min_normalized_action_entropy"]):
            add_error(
                errors,
                prefix,
                "policy_normalized_action_entropy below seeded stochastic watch threshold",
            )
        ratio = dominant_action_ratio(item)
        if ratio is None:
            warnings.append(f"{prefix}: missing policy_dominant_action ratio")
        elif ratio > float(criteria["max_dominant_action_ratio"]):
            add_error(errors, prefix, "dominant action ratio is too high")
        inner_gate = str(item.get("inner_gate_decision", ""))
        if "repair" in inner_gate:
            add_error(errors, prefix, f"inner gate is repair: {inner_gate}")


def build_report(
    short_report_path: Path,
    long_report_path: Path,
    *,
    criteria: dict[str, Any] | None = None,
) -> dict[str, Any]:
    criteria = dict(DEFAULT_CRITERIA if criteria is None else criteria)
    errors: list[str] = []
    warnings: list[str] = []
    short_report = load_json_object(short_report_path)
    long_report = load_json_object(long_report_path)

    validate_report(
        "short_report",
        short_report,
        min_seconds=float(criteria["min_short_seconds"]),
        min_seeds=int(criteria["min_short_seeds"]),
        criteria=criteria,
        errors=errors,
        warnings=warnings,
    )
    validate_report(
        "long_report",
        long_report,
        min_seconds=float(criteria["min_long_seconds"]),
        min_seeds=int(criteria["min_long_seeds"]),
        criteria=criteria,
        errors=errors,
        warnings=warnings,
    )

    short_seed = short_report.get("action_random_seed")
    long_seed = long_report.get("action_random_seed")
    if short_seed != long_seed:
        errors.append(
            f"action_random_seed mismatch: short={short_seed!r}, long={long_seed!r}"
        )

    decision = (
        "seeded_stochastic_watch_ready"
        if not errors
        else "seeded_stochastic_watch_blocked"
    )
    return {
        "report_version": 1,
        "decision": decision,
        "short_report_path": str(short_report_path),
        "long_report_path": str(long_report_path),
        "criteria": criteria,
        "action_random_seed": short_seed if short_seed == long_seed else None,
        "short_report": report_summary(short_report),
        "long_report": report_summary(long_report),
        "errors": errors,
        "warnings": warnings,
        "limitations": [
            "This validator produces watch evidence only; it is not RL policy acceptance.",
            "Seeded stochastic success does not clear deterministic high-pressure gates.",
            "Stage progression still requires the project-defined deterministic or explicitly approved stochastic gate.",
        ],
    }


def markdown_summary(report: dict[str, Any]) -> str:
    status = "ready" if report["decision"] == "seeded_stochastic_watch_ready" else "blocked"
    lines = [
        "# Seeded Stochastic Watch Validation",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Status: `{status}`",
        f"- Action random seed: `{report.get('action_random_seed')}`",
        f"- Short report: `{report['short_report_path']}`",
        f"- Long report: `{report['long_report_path']}`",
        "",
        "## Map Summary",
        "",
        "| Report | Map | Win rate | Entropy | Dominant action |",
        "|---|---|---:|---:|---|",
    ]
    for label in ("short_report", "long_report"):
        for item in report[label]["maps"]:
            dominant = item.get("policy_dominant_action") or {}
            dominant_text = (
                f"{dominant.get('action')} @ {dominant.get('ratio')}"
                if isinstance(dominant, dict)
                else "n/a"
            )
            lines.append(
                "| "
                f"{label} | {item.get('map_id')} | {item.get('policy_win_rate')} | "
                f"{item.get('policy_normalized_action_entropy')} | {dominant_text} |"
            )
    if report["errors"]:
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {error}" for error in report["errors"])
    if report["warnings"]:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in report["warnings"])
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "- This is watch evidence only, not RL policy acceptance.",
            "- Deterministic gates and failure-case review still control stage progression.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate seeded stochastic RL watch evidence."
    )
    parser.add_argument("--short-report", required=True)
    parser.add_argument("--long-report", required=True)
    parser.add_argument("--report", default=None)
    parser.add_argument("--markdown", default=None)
    args = parser.parse_args()

    report = build_report(Path(args.short_report), Path(args.long_report))
    text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.report:
        target = Path(args.report)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    if args.markdown:
        target = Path(args.markdown)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(markdown_summary(report), encoding="utf-8")
    return 0 if report["decision"] == "seeded_stochastic_watch_ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
