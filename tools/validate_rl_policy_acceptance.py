#!/usr/bin/env python3
"""Validate RL policy acceptance evidence manifests.

This gate keeps RL/BC policies from being promoted on the strength of training
smoke alone. It checks that a candidate is backed by model artifacts, training
reports, local binary diagnostics, high-pressure 60/300 second comparisons, rule
Bot baselines, and unresolved failure-case review.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ALLOWED_POLICY_TYPES = {"dqn", "ppo", "behavior_clone", "scripted_adapter"}
ALLOWED_GATE_DECISIONS = {
    "blocked_by_local_binary_launch",
    "watch",
    "repair",
    "reject",
    "rl_test_bot_candidate",
}
FORBIDDEN_GATE_DECISIONS = {
    "release_ready",
    "balance_gate_pass",
    "playtest_proof",
    "fun_proven",
    "production_ready",
}

DEFAULT_CRITERIA = {
    "required_map_preset": "high-pressure",
    "min_map_count": 3,
    "min_short_seconds": 60.0,
    "min_long_seconds": 300.0,
    "min_normalized_action_entropy": 0.5,
    "max_dominant_action_ratio": 0.7,
    "min_short_policy_win_rate": 1.0,
    "min_long_policy_win_rate": 1.0,
    "must_match_best_rule_bot": True,
}


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]


def as_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def resolve_repo_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def is_inside_repo(repo_root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return False
    return True


def load_optional_json(repo_root: Path, label: str, path_value: str | None, errors: list[str]) -> dict[str, Any] | None:
    if not is_nonempty_string(path_value):
        return None
    resolved = resolve_repo_path(repo_root, str(path_value))
    if not is_inside_repo(repo_root, resolved):
        errors.append(f"{label}: path must stay inside repository: {path_value}")
        return None
    if not resolved.exists():
        errors.append(f"{label}: path does not exist: {path_value}")
        return None
    try:
        return load_json_object(resolved)
    except (json.JSONDecodeError, ValueError) as exc:
        errors.append(f"{label}: must be a JSON object: {exc}")
        return None


def validate_existing_path(
    repo_root: Path,
    label: str,
    path_value: Any,
    errors: list[str],
    *,
    required: bool,
) -> str | None:
    if not is_nonempty_string(path_value):
        if required:
            errors.append(f"{label}: path must be non-empty")
        return None
    path_text = str(path_value)
    resolved = resolve_repo_path(repo_root, path_text)
    if not is_inside_repo(repo_root, resolved):
        errors.append(f"{label}: path must stay inside repository: {path_text}")
    elif not resolved.exists():
        errors.append(f"{label}: path does not exist: {path_text}")
    return path_text


def merge_criteria(raw: Any) -> dict[str, Any]:
    criteria = dict(DEFAULT_CRITERIA)
    if isinstance(raw, dict):
        criteria.update(raw)
    return criteria


def add_candidate_issue(
    message: str,
    *,
    candidate_mode: bool,
    errors: list[str],
    blockers: list[str],
) -> None:
    if candidate_mode:
        errors.append(message)
    else:
        blockers.append(message)


def validate_training_report(
    manifest: dict[str, Any],
    training_report: dict[str, Any] | None,
    *,
    candidate_mode: bool,
    errors: list[str],
    warnings: list[str],
    blockers: list[str],
) -> dict[str, Any] | None:
    if training_report is None:
        add_candidate_issue(
            "training_report: missing or unreadable training report",
            candidate_mode=candidate_mode,
            errors=errors,
            blockers=blockers,
        )
        return None

    report = {
        "status": training_report.get("status"),
        "gate_decision": training_report.get("gate_decision"),
        "model_path": training_report.get("model_path"),
    }
    if training_report.get("status") not in {"trained", "evaluated", "compared"}:
        add_candidate_issue(
            f"training_report: status is `{training_report.get('status')}`",
            candidate_mode=candidate_mode,
            errors=errors,
            blockers=blockers,
        )
    if is_nonempty_string(training_report.get("model_path")) and training_report.get("model_path") != manifest.get(
        "model_path"
    ):
        errors.append(
            "training_report: model_path does not match manifest "
            f"({training_report.get('model_path')} != {manifest.get('model_path')})"
        )

    gate_decision = str(training_report.get("gate_decision", ""))
    if "smoke_only" in gate_decision or gate_decision in {"not_evaluated", "behavior_clone_smoke_only_not_policy_gate"}:
        add_candidate_issue(
            f"training_report: gate_decision `{gate_decision}` is not policy acceptance evidence",
            candidate_mode=candidate_mode,
            errors=errors,
            blockers=blockers,
        )
    elif not gate_decision:
        warnings.append("training_report: gate_decision is missing")
    return report


def map_summary_entries(report: dict[str, Any]) -> list[dict[str, Any]]:
    summary = report.get("summary")
    if isinstance(summary, dict) and isinstance(summary.get("maps"), list):
        return [item for item in summary["maps"] if isinstance(item, dict)]
    if isinstance(report.get("map_id"), str):
        policy = report.get("policy")
        policy_summary = policy.get("summary") if isinstance(policy, dict) else {}
        if isinstance(policy_summary, dict):
            return [
                {
                    "map_id": report["map_id"],
                    "policy_win_rate": policy_summary.get("win_rate"),
                    "policy_normalized_action_entropy": policy_summary.get("normalized_action_entropy"),
                    "policy_dominant_action": policy_summary.get("dominant_action"),
                }
            ]
    return []


def report_map_count(report: dict[str, Any]) -> int:
    summary = report.get("summary")
    if isinstance(summary, dict) and isinstance(summary.get("map_count"), int):
        return int(summary["map_count"])
    maps = report.get("maps")
    if isinstance(maps, list):
        return len(maps)
    return 1 if isinstance(report.get("map_id"), str) else 0


def report_minimum_win_rate(report: dict[str, Any]) -> float | None:
    summary = report.get("summary")
    if isinstance(summary, dict):
        value = as_number(summary.get("minimum_policy_win_rate"))
        if value is not None:
            return value
    entries = map_summary_entries(report)
    win_rates = [as_number(item.get("policy_win_rate")) for item in entries]
    concrete = [value for value in win_rates if value is not None]
    return min(concrete) if concrete else None


def validate_comparison_report(
    label: str,
    report: dict[str, Any] | None,
    criteria: dict[str, Any],
    *,
    required_seconds: float,
    min_policy_win_rate: float,
    candidate_mode: bool,
    errors: list[str],
    blockers: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "label": label,
        "present": report is not None,
        "status": None,
        "gate_decision": None,
        "action_selection": None,
        "seconds": None,
        "map_count": 0,
        "minimum_policy_win_rate": None,
    }
    if report is None:
        add_candidate_issue(
            f"{label}: missing comparison/evaluation report",
            candidate_mode=candidate_mode,
            errors=errors,
            blockers=blockers,
        )
        return result

    status = report.get("status")
    gate_decision = report.get("gate_decision")
    action_selection = report.get("action_selection")
    seconds = as_number(report.get("seconds"))
    map_count = report_map_count(report)
    min_win_rate = report_minimum_win_rate(report)
    result.update(
        {
            "status": status,
            "gate_decision": gate_decision,
            "action_selection": action_selection,
            "seconds": seconds,
            "map_count": map_count,
            "minimum_policy_win_rate": min_win_rate,
        }
    )

    if status not in {"compared", "evaluated"}:
        add_candidate_issue(
            f"{label}: status must be compared/evaluated, got `{status}`",
            candidate_mode=candidate_mode,
            errors=errors,
            blockers=blockers,
        )
    if seconds is None or seconds < required_seconds:
        add_candidate_issue(
            f"{label}: requires at least {required_seconds:g}s, got `{seconds}`",
            candidate_mode=candidate_mode,
            errors=errors,
            blockers=blockers,
        )
    if map_count < int(criteria["min_map_count"]):
        add_candidate_issue(
            f"{label}: requires at least {criteria['min_map_count']} maps, got {map_count}",
            candidate_mode=candidate_mode,
            errors=errors,
            blockers=blockers,
        )
    required_preset = criteria.get("required_map_preset")
    if is_nonempty_string(required_preset) and report.get("map_preset") != required_preset:
        add_candidate_issue(
            f"{label}: map_preset must be `{required_preset}`, got `{report.get('map_preset')}`",
            candidate_mode=candidate_mode,
            errors=errors,
            blockers=blockers,
        )
    if min_win_rate is None or min_win_rate < min_policy_win_rate:
        add_candidate_issue(
            f"{label}: minimum policy win rate must be >= {min_policy_win_rate:g}, got `{min_win_rate}`",
            candidate_mode=candidate_mode,
            errors=errors,
            blockers=blockers,
        )
    if isinstance(gate_decision, str) and ("repair" in gate_decision or "watch" in gate_decision):
        add_candidate_issue(
            f"{label}: report gate_decision `{gate_decision}` still indicates repair/watch",
            candidate_mode=candidate_mode,
            errors=errors,
            blockers=blockers,
        )
    if action_selection == "stochastic" or report.get("action_random_seed") is not None:
        add_candidate_issue(
            f"{label}: stochastic action selection is watch evidence only, not RL acceptance",
            candidate_mode=candidate_mode,
            errors=errors,
            blockers=blockers,
        )
    elif action_selection not in {None, "deterministic"}:
        add_candidate_issue(
            f"{label}: unsupported action_selection `{action_selection}`",
            candidate_mode=candidate_mode,
            errors=errors,
            blockers=blockers,
        )
    elif action_selection is None:
        warnings.append(f"{label}: action_selection is missing; deterministic evidence is assumed for legacy reports")
    findings = report.get("findings")
    if isinstance(findings, list) and findings:
        add_candidate_issue(
            f"{label}: report still contains {len(findings)} finding(s)",
            candidate_mode=candidate_mode,
            errors=errors,
            blockers=blockers,
        )

    min_entropy = float(criteria["min_normalized_action_entropy"])
    max_dominant = float(criteria["max_dominant_action_ratio"])
    must_match_best_rule_bot = bool(criteria.get("must_match_best_rule_bot", True))
    for item in map_summary_entries(report):
        map_id = item.get("map_id", "unknown-map")
        entropy = as_number(item.get("policy_normalized_action_entropy"))
        dominant = item.get("policy_dominant_action")
        dominant_ratio = as_number(dominant.get("ratio")) if isinstance(dominant, dict) else None
        policy_win_rate = as_number(item.get("policy_win_rate"))
        best_rule_bot_win_rate = as_number(item.get("best_rule_bot_win_rate"))
        if entropy is not None and entropy < min_entropy:
            add_candidate_issue(
                f"{label}.{map_id}: normalized action entropy {entropy:g} is below {min_entropy:g}",
                candidate_mode=candidate_mode,
                errors=errors,
                blockers=blockers,
            )
        if dominant_ratio is not None and dominant_ratio > max_dominant:
            add_candidate_issue(
                f"{label}.{map_id}: dominant action ratio {dominant_ratio:g} is above {max_dominant:g}",
                candidate_mode=candidate_mode,
                errors=errors,
                blockers=blockers,
            )
        if (
            must_match_best_rule_bot
            and policy_win_rate is not None
            and best_rule_bot_win_rate is not None
            and policy_win_rate + 1e-9 < best_rule_bot_win_rate
        ):
            add_candidate_issue(
                f"{label}.{map_id}: policy win rate {policy_win_rate:g} is below best rule Bot {best_rule_bot_win_rate:g}",
                candidate_mode=candidate_mode,
                errors=errors,
                blockers=blockers,
            )

    if not map_summary_entries(report):
        warnings.append(f"{label}: no per-map summary entries were available for action distribution checks")

    return result


def validate_local_binary_diagnostic(
    diagnostic: dict[str, Any] | None,
    manifest_gate_decision: str | None,
    *,
    candidate_mode: bool,
    errors: list[str],
    blockers: list[str],
    warnings: list[str],
) -> str | None:
    if diagnostic is None:
        add_candidate_issue(
            "local_binary_diagnostic: missing or unreadable diagnostic report",
            candidate_mode=candidate_mode,
            errors=errors,
            blockers=blockers,
        )
        return None

    decision = diagnostic.get("decision")
    if decision != "local_binary_launch_ok":
        add_candidate_issue(
            f"local_binary_diagnostic: decision is `{decision}`",
            candidate_mode=candidate_mode,
            errors=errors,
            blockers=blockers,
        )
    if manifest_gate_decision == "blocked_by_local_binary_launch" and decision == "local_binary_launch_ok":
        warnings.append("local_binary_diagnostic: manifest still says blocked even though diagnostic is ok")
    return str(decision) if decision is not None else None


def validate_failure_paths(
    repo_root: Path,
    manifest: dict[str, Any],
    *,
    candidate_mode: bool,
    errors: list[str],
    warnings: list[str],
) -> dict[str, int]:
    counts = {"failure_case_count": 0, "unresolved_failure_case_count": 0}
    for field in ("failure_case_paths", "unresolved_failure_case_paths"):
        raw_value = manifest.get(field)
        paths = string_list(raw_value)
        if raw_value is not None and not isinstance(raw_value, list):
            errors.append(f"{field}: must be a list")
            continue
        for index, path_text in enumerate(paths):
            validate_existing_path(repo_root, f"{field}[{index}]", path_text, errors, required=True)
    unresolved = string_list(manifest.get("unresolved_failure_case_paths"))
    counts["failure_case_count"] = len(string_list(manifest.get("failure_case_paths")))
    counts["unresolved_failure_case_count"] = len(unresolved)
    if candidate_mode and unresolved:
        errors.append("unresolved_failure_case_paths: rl_test_bot_candidate cannot have unresolved failure cases")
    if manifest.get("gate_decision") in {"watch", "repair"} and not unresolved:
        warnings.append("unresolved_failure_case_paths: watch/repair decisions should cite unresolved failure cases")
    return counts


def build_report(manifest_path: Path, repo_root: Path) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    manifest = load_json_object(manifest_path)
    errors: list[str] = []
    warnings: list[str] = []
    blockers: list[str] = []

    for field in ("generated_at", "policy_id", "policy_type", "policy_phase", "summary"):
        if not is_nonempty_string(manifest.get(field)):
            errors.append(f"`{field}` must be non-empty")

    policy_type = manifest.get("policy_type")
    if policy_type not in ALLOWED_POLICY_TYPES:
        errors.append(f"`policy_type` must be one of {', '.join(sorted(ALLOWED_POLICY_TYPES))}")

    gate_decision = manifest.get("gate_decision")
    if gate_decision in FORBIDDEN_GATE_DECISIONS:
        errors.append(f"`gate_decision` `{gate_decision}` is forbidden for RL policy acceptance")
    elif gate_decision not in ALLOWED_GATE_DECISIONS:
        errors.append(f"`gate_decision` must be one of {', '.join(sorted(ALLOWED_GATE_DECISIONS))}")
    candidate_mode = gate_decision == "rl_test_bot_candidate"

    criteria = merge_criteria(manifest.get("acceptance_criteria"))
    model_path = validate_existing_path(repo_root, "model_path", manifest.get("model_path"), errors, required=True)
    metadata_path = validate_existing_path(
        repo_root,
        "model_metadata_path",
        manifest.get("model_metadata_path"),
        errors,
        required=candidate_mode,
    )
    training_report_path = validate_existing_path(
        repo_root,
        "training_report_path",
        manifest.get("training_report_path"),
        errors,
        required=True,
    )
    short_eval_report_path = validate_existing_path(
        repo_root,
        "short_eval_report_path",
        manifest.get("short_eval_report_path"),
        errors,
        required=candidate_mode,
    )
    long_eval_report_path = validate_existing_path(
        repo_root,
        "long_eval_report_path",
        manifest.get("long_eval_report_path"),
        errors,
        required=candidate_mode,
    )
    rule_bot_comparison_report_path = validate_existing_path(
        repo_root,
        "rule_bot_comparison_report_path",
        manifest.get("rule_bot_comparison_report_path"),
        errors,
        required=candidate_mode,
    )
    local_binary_diagnostic_report_path = validate_existing_path(
        repo_root,
        "local_binary_diagnostic_report_path",
        manifest.get("local_binary_diagnostic_report_path"),
        errors,
        required=True,
    )

    if not candidate_mode and metadata_path is None:
        warnings.append("model_metadata_path: missing metadata is allowed only because this is not a candidate")

    failure_counts = validate_failure_paths(
        repo_root,
        manifest,
        candidate_mode=candidate_mode,
        errors=errors,
        warnings=warnings,
    )

    training_report = load_optional_json(repo_root, "training_report_path", training_report_path, errors)
    local_binary_diagnostic = load_optional_json(
        repo_root,
        "local_binary_diagnostic_report_path",
        local_binary_diagnostic_report_path,
        errors,
    )
    short_eval_report = load_optional_json(repo_root, "short_eval_report_path", short_eval_report_path, errors)
    long_eval_report = load_optional_json(repo_root, "long_eval_report_path", long_eval_report_path, errors)
    rule_bot_comparison_report = load_optional_json(
        repo_root,
        "rule_bot_comparison_report_path",
        rule_bot_comparison_report_path,
        errors,
    )

    training_summary = validate_training_report(
        manifest,
        training_report,
        candidate_mode=candidate_mode,
        errors=errors,
        warnings=warnings,
        blockers=blockers,
    )
    local_binary_decision = validate_local_binary_diagnostic(
        local_binary_diagnostic,
        gate_decision,
        candidate_mode=candidate_mode,
        errors=errors,
        blockers=blockers,
        warnings=warnings,
    )
    short_summary = validate_comparison_report(
        "short_eval_report",
        short_eval_report,
        criteria,
        required_seconds=float(criteria["min_short_seconds"]),
        min_policy_win_rate=float(criteria["min_short_policy_win_rate"]),
        candidate_mode=candidate_mode,
        errors=errors,
        blockers=blockers,
        warnings=warnings,
    )
    long_summary = validate_comparison_report(
        "long_eval_report",
        long_eval_report,
        criteria,
        required_seconds=float(criteria["min_long_seconds"]),
        min_policy_win_rate=float(criteria["min_long_policy_win_rate"]),
        candidate_mode=candidate_mode,
        errors=errors,
        blockers=blockers,
        warnings=warnings,
    )
    rule_bot_summary = validate_comparison_report(
        "rule_bot_comparison_report",
        rule_bot_comparison_report,
        criteria,
        required_seconds=float(criteria["min_long_seconds"]),
        min_policy_win_rate=float(criteria["min_long_policy_win_rate"]),
        candidate_mode=candidate_mode,
        errors=errors,
        blockers=blockers,
        warnings=warnings,
    )

    ready = candidate_mode and not errors and not blockers
    decision = "rl_policy_acceptance_ready" if ready else "rl_policy_acceptance_not_ready"
    return {
        "report_version": 1,
        "source": str(manifest_path),
        "repo_root": str(repo_root),
        "decision": decision,
        "gate_decision": gate_decision,
        "policy": {
            "policy_id": manifest.get("policy_id"),
            "policy_type": policy_type,
            "policy_phase": manifest.get("policy_phase"),
            "model_path": model_path,
            "model_metadata_path": metadata_path,
        },
        "criteria": criteria,
        "evidence": {
            "training_report_path": training_report_path,
            "short_eval_report_path": short_eval_report_path,
            "long_eval_report_path": long_eval_report_path,
            "rule_bot_comparison_report_path": rule_bot_comparison_report_path,
            "local_binary_diagnostic_report_path": local_binary_diagnostic_report_path,
            "local_binary_decision": local_binary_decision,
            **failure_counts,
        },
        "training_report": training_summary,
        "evaluation_reports": [short_summary, long_summary, rule_bot_summary],
        "errors": errors,
        "warnings": warnings,
        "blockers": blockers,
        "limitations": [
            "This validator checks evidence shape and recorded metrics only; it does not run Rust, Gym, Harness, or training.",
            "An rl_test_bot_candidate decision is still not a fun, balance, playtest, release, or accepted-content gate.",
            "When local_binary_launch_blocked is active, no RL/Gym comparison depending on game_harness can be promoted.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# RL Policy Acceptance Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Policy: `{report['policy']['policy_id']}`",
        f"- Policy type: `{report['policy']['policy_type']}`",
        f"- Gate decision: `{report['gate_decision']}`",
        f"- Decision: `{report['decision']}`",
        f"- Local binary: `{report['evidence']['local_binary_decision']}`",
        "",
        "## Evidence",
        "",
    ]
    for key, value in report["evidence"].items():
        lines.append(f"- {key}: `{value}`")

    lines.extend(["", "## Evaluation Reports", "", "| Report | Present | Seconds | Maps | Min win rate | Gate |", "|---|---|---:|---:|---:|---|"])
    for item in report["evaluation_reports"]:
        lines.append(
            f"| `{item['label']}` | {item['present']} | {item['seconds']} | "
            f"{item['map_count']} | {item['minimum_policy_win_rate']} | `{item['gate_decision']}` |"
        )

    lines.extend(["", "## Blockers", ""])
    if report["blockers"]:
        lines.extend(f"- {blocker}" for blocker in report["blockers"])
    else:
        lines.append("- None")

    lines.extend(["", "## Errors", ""])
    if report["errors"]:
        lines.extend(f"- {error}" for error in report["errors"])
    else:
        lines.append("- None")

    lines.extend(["", "## Warnings", ""])
    if report["warnings"]:
        lines.extend(f"- {warning}" for warning in report["warnings"])
    else:
        lines.append("- None")

    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm RL policy acceptance evidence.")
    parser.add_argument("manifest", type=Path, help="RL policy acceptance manifest JSON")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON validation report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown validation summary")
    parser.add_argument(
        "--allow-not-ready",
        action="store_true",
        help="Exit 0 after writing a not-ready report; useful while blockers are intentionally recorded",
    )
    args = parser.parse_args()

    report = build_report(args.manifest, args.repo_root)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))

    if report["decision"] == "rl_policy_acceptance_ready" or args.allow_not_ready:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
