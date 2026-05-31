#!/usr/bin/env python3
"""Validate target map/seed episodes before expensive RL repair probes continue.

This validator reads an existing policy comparison report and checks one or
more target episodes, such as `soda-creek:63402`, for online behavior. It is a
repair preflight only: passing means the selected target episodes satisfy the
configured checks in the supplied report, not that the policy is accepted.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


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


def parse_target(value: str) -> tuple[str, int]:
    if ":" not in value:
        raise argparse.ArgumentTypeError("target must use MAP_ID:SEED")
    map_id, seed_text = value.split(":", 1)
    map_id = map_id.strip()
    seed_text = seed_text.strip()
    if not map_id:
        raise argparse.ArgumentTypeError("target map id must be non-empty")
    try:
        seed = int(seed_text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("target seed must be an integer") from exc
    return map_id, seed


def parse_action_ratio(value: str) -> tuple[str, float]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("action ratio must use ACTION=RATIO")
    action, ratio_text = value.split("=", 1)
    action = action.strip()
    ratio_text = ratio_text.strip()
    if not action:
        raise argparse.ArgumentTypeError("action must be non-empty")
    try:
        ratio = float(ratio_text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("ratio must be numeric") from exc
    if ratio < 0.0 or ratio > 1.0:
        raise argparse.ArgumentTypeError("ratio must be between 0 and 1")
    return action, ratio


def collect_policy_episodes(report: dict[str, Any]) -> list[dict[str, Any]]:
    episodes: list[dict[str, Any]] = []

    def add_from_policy(policy: Any, fallback_map_id: Any) -> None:
        if not isinstance(policy, dict):
            return
        policy_episodes = policy.get("episodes")
        if not isinstance(policy_episodes, list):
            return
        for episode in policy_episodes:
            if not isinstance(episode, dict):
                continue
            item = dict(episode)
            if not isinstance(item.get("map_id"), str) and isinstance(fallback_map_id, str):
                item["map_id"] = fallback_map_id
            episodes.append(item)

    add_from_policy(report, report.get("map_id"))
    add_from_policy(report.get("policy"), report.get("map_id"))
    for map_entry in report.get("maps", []):
        if not isinstance(map_entry, dict):
            continue
        add_from_policy(map_entry.get("policy"), map_entry.get("map_id"))
    return episodes


def action_ratio(episode: dict[str, Any], action: str) -> float | None:
    counts = episode.get("action_counts")
    if not isinstance(counts, dict):
        return None
    numeric_counts: dict[str, float] = {}
    for key, value in counts.items():
        number = as_number(value)
        if number is not None:
            numeric_counts[str(key)] = number
    total = sum(numeric_counts.values())
    if total <= 0.0:
        return 0.0
    return round(numeric_counts.get(action, 0.0) / total, 6)


def target_key(map_id: str, seed: int) -> str:
    return f"{map_id}:{seed}"


def build_report(
    comparison_path: Path,
    targets: list[tuple[str, int]],
    *,
    min_survival_seconds: float | None = None,
    require_window_survival: bool = False,
    require_non_defeat: bool = False,
    min_action_ratios: list[tuple[str, float]] | None = None,
    max_action_ratios: list[tuple[str, float]] | None = None,
    survival_tolerance_seconds: float = 0.05,
) -> dict[str, Any]:
    errors: list[str] = []
    blockers: list[str] = []
    warnings: list[str] = []
    min_action_ratios = min_action_ratios or []
    max_action_ratios = max_action_ratios or []

    try:
        comparison = load_json_object(comparison_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {
            "decision": "policy_target_seed_preflight_invalid",
            "comparison": str(comparison_path),
            "errors": [f"unable to load comparison report: {exc}"],
            "blockers": [],
            "warnings": [],
            "target_results": [],
            "limitations": limitations(),
        }

    seconds = as_number(comparison.get("seconds"))
    if require_window_survival and seconds is None:
        errors.append("comparison report missing numeric seconds for --require-window-survival")
    if survival_tolerance_seconds < 0.0:
        errors.append("survival_tolerance_seconds must be non-negative")

    episodes = collect_policy_episodes(comparison)
    episode_index: dict[tuple[str, int], dict[str, Any]] = {}
    for episode in episodes:
        map_id = episode.get("map_id")
        seed_number = episode.get("seed")
        if isinstance(map_id, str) and isinstance(seed_number, int):
            episode_index[(map_id, seed_number)] = episode

    target_results: list[dict[str, Any]] = []
    for map_id, seed in targets:
        key = target_key(map_id, seed)
        episode = episode_index.get((map_id, seed))
        if episode is None:
            blockers.append(f"{key}: target episode missing")
            target_results.append({"map_id": map_id, "seed": seed, "found": False})
            continue

        time_seconds = as_number(episode.get("time_seconds"))
        terminal_kind = episode.get("terminal_kind")
        terminal_reason = episode.get("terminal_reason")
        action_ratios: dict[str, float | None] = {}
        for action, _ratio in [*min_action_ratios, *max_action_ratios]:
            action_ratios[action] = action_ratio(episode, action)

        result = {
            "map_id": map_id,
            "seed": seed,
            "found": True,
            "time_seconds": time_seconds,
            "terminal_kind": terminal_kind,
            "terminal_reason": terminal_reason,
            "terminated": episode.get("terminated"),
            "truncated": episode.get("truncated"),
            "action_ratios": action_ratios,
        }
        target_results.append(result)

        if min_survival_seconds is not None:
            if time_seconds is None:
                blockers.append(f"{key}: missing time_seconds")
            elif time_seconds + survival_tolerance_seconds < min_survival_seconds:
                blockers.append(
                    f"{key}: time_seconds {time_seconds:.4f} below required "
                    f"{min_survival_seconds:.4f}"
                )
        if require_window_survival and seconds is not None:
            if time_seconds is None:
                blockers.append(f"{key}: missing time_seconds for window survival")
            elif time_seconds + survival_tolerance_seconds < seconds:
                blockers.append(
                    f"{key}: time_seconds {time_seconds:.4f} did not reach "
                    f"window {seconds:.4f}"
                )
            if terminal_kind != "victory":
                blockers.append(f"{key}: terminal_kind `{terminal_kind}` is not `victory`")
        if require_non_defeat and terminal_kind == "defeat" and not require_window_survival:
            blockers.append(f"{key}: terminal_kind is `defeat`")

        for action, minimum in min_action_ratios:
            ratio = action_ratios.get(action)
            if ratio is None:
                blockers.append(f"{key}: missing action_counts for action {action}")
            elif ratio < minimum:
                blockers.append(
                    f"{key}: action {action} ratio {ratio:.6f} below required {minimum:.6f}"
                )
        for action, maximum in max_action_ratios:
            ratio = action_ratios.get(action)
            if ratio is None:
                blockers.append(f"{key}: missing action_counts for action {action}")
            elif ratio > maximum:
                blockers.append(
                    f"{key}: action {action} ratio {ratio:.6f} above allowed {maximum:.6f}"
                )

    decision = "policy_target_seed_preflight_passed"
    if errors:
        decision = "policy_target_seed_preflight_invalid"
    elif blockers:
        decision = "policy_target_seed_preflight_failed"

    return {
        "decision": decision,
        "comparison": str(comparison_path),
        "seconds": seconds,
        "gate_decision": comparison.get("gate_decision"),
        "action_selection": comparison.get("action_selection"),
        "reward_profile": comparison.get("reward_profile"),
        "target_count": len(targets),
        "target_results": target_results,
        "checks": {
            "min_survival_seconds": min_survival_seconds,
            "require_window_survival": require_window_survival,
            "require_non_defeat": require_non_defeat,
            "min_action_ratios": dict(min_action_ratios),
            "max_action_ratios": dict(max_action_ratios),
            "survival_tolerance_seconds": survival_tolerance_seconds,
        },
        "errors": errors,
        "blockers": blockers,
        "warnings": warnings,
        "limitations": limitations(),
    }


def limitations() -> list[str]:
    return [
        "This preflight only validates target episodes already present in a comparison report.",
        "A passing preflight does not replace fixed-window high-pressure comparison, no-regression validation, failure-case review, or RL acceptance.",
        "Target action ratios are diagnostic checks; they should not be used alone as proof of good play.",
    ]


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Policy Target Seed Preflight",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Comparison: `{report['comparison']}`",
        f"- Targets: `{report['target_count']}`",
        "",
        "## Target Results",
        "",
        "| Map | Seed | Found | Time | Terminal | Action Ratios |",
        "|---|---:|---|---:|---|---|",
    ]
    for result in report["target_results"]:
        ratios = result.get("action_ratios") or {}
        ratio_text = ", ".join(
            f"{action}={ratio}" for action, ratio in sorted(ratios.items())
        )
        time_seconds = result.get("time_seconds")
        time_text = "None" if time_seconds is None else f"{time_seconds:.4f}"
        lines.append(
            "| `{map_id}` | `{seed}` | `{found}` | `{time}` | `{terminal}` | `{ratios}` |".format(
                map_id=result.get("map_id"),
                seed=result.get("seed"),
                found=result.get("found"),
                time=time_text,
                terminal=result.get("terminal_kind"),
                ratios=ratio_text,
            )
        )
    if report["errors"]:
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {item}" for item in report["errors"])
    if report["blockers"]:
        lines.extend(["", "## Blockers", ""])
        lines.extend(f"- {item}" for item in report["blockers"])
    if report["warnings"]:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {item}" for item in report["warnings"])
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate target map/seed episodes.")
    parser.add_argument("--comparison", type=Path, required=True)
    parser.add_argument("--target", action="append", type=parse_target, required=True)
    parser.add_argument("--min-survival-seconds", type=float, default=None)
    parser.add_argument("--require-window-survival", action="store_true")
    parser.add_argument("--require-non-defeat", action="store_true")
    parser.add_argument("--min-action-ratio", action="append", type=parse_action_ratio, default=[])
    parser.add_argument("--max-action-ratio", action="append", type=parse_action_ratio, default=[])
    parser.add_argument("--survival-tolerance-seconds", type=float, default=0.05)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--markdown", type=Path, default=None)
    parser.add_argument("--allow-failure", action="store_true")
    args = parser.parse_args()

    if args.min_survival_seconds is not None and args.min_survival_seconds < 0.0:
        parser.error("--min-survival-seconds must be non-negative")
    if args.survival_tolerance_seconds < 0.0:
        parser.error("--survival-tolerance-seconds must be non-negative")

    report = build_report(
        args.comparison,
        args.target,
        min_survival_seconds=args.min_survival_seconds,
        require_window_survival=args.require_window_survival,
        require_non_defeat=args.require_non_defeat,
        min_action_ratios=args.min_action_ratio,
        max_action_ratios=args.max_action_ratio,
        survival_tolerance_seconds=args.survival_tolerance_seconds,
    )
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    if report["decision"] == "policy_target_seed_preflight_passed":
        return 0
    return 0 if args.allow_failure else 1


if __name__ == "__main__":
    raise SystemExit(main())
