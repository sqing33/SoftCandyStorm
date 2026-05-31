#!/usr/bin/env python3
"""Validate evaluation-only policy adapter usage scope.

This gate checks that diagnostic adapters such as edge_recovery_branch stayed
within their intended online scope. It is not RL acceptance evidence; it only
audits provenance and branch usage in already generated comparison reports.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


FORBIDDEN_DECISION_TOKENS = {
    "acceptance",
    "accepted",
    "candidate",
    "playtest",
    "production",
    "release",
    "rl_test_bot_candidate",
}

ADAPTER_CHILD_KEYS = (
    "wrapped_policy_adapter",
    "base_policy_adapter",
    "branch_policy_adapter",
    "terminal_policy_adapter",
)


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


def parse_labeled_path(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("comparison must use LABEL=PATH")
    label, path_text = value.split("=", 1)
    label = label.strip()
    path_text = path_text.strip()
    if not label:
        raise argparse.ArgumentTypeError("comparison label must be non-empty")
    if not path_text:
        raise argparse.ArgumentTypeError("comparison path must be non-empty")
    return label, Path(path_text)


def string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item]


def decision_uses_forbidden_token(value: Any) -> bool:
    lowered = str(value or "").lower()
    return any(token in lowered for token in FORBIDDEN_DECISION_TOKENS)


def collect_gate_wording_errors(label: str, report: dict[str, Any], errors: list[str]) -> None:
    for field in ("decision", "gate_decision"):
        if decision_uses_forbidden_token(report.get(field)):
            errors.append(f"{label}: {field} overclaims adapter evidence: {report.get(field)}")


def adapter_from_policy_map(item: dict[str, Any]) -> dict[str, Any] | None:
    adapter = item.get("policy_adapter")
    if isinstance(adapter, dict):
        return adapter
    policy = item.get("policy")
    if isinstance(policy, dict):
        adapter = policy.get("policy_adapter")
        if isinstance(adapter, dict):
            return adapter
    return None


def iter_adapters(adapter: dict[str, Any]) -> list[dict[str, Any]]:
    found = [adapter]
    for key in ADAPTER_CHILD_KEYS:
        child = adapter.get(key)
        if isinstance(child, dict):
            found.extend(iter_adapters(child))
    return found


def adapter_decision_count(adapter: dict[str, Any], count_key: str) -> int:
    usage = adapter.get("usage")
    if not isinstance(usage, dict):
        return 0
    return usage_count(usage, count_key)


def select_adapter(
    adapter: dict[str, Any],
    expected_mode: str,
    count_key: str,
) -> dict[str, Any] | None:
    matches = [
        candidate
        for candidate in iter_adapters(adapter)
        if candidate.get("mode") == expected_mode
    ]
    if not matches:
        return None
    return max(matches, key=lambda candidate: adapter_decision_count(candidate, count_key))


def policy_map_entries(report: dict[str, Any]) -> list[dict[str, Any]]:
    maps = report.get("maps")
    if isinstance(maps, list):
        return [item for item in maps if isinstance(item, dict)]
    policy = report.get("policy")
    if isinstance(policy, dict):
        return [
            {
                "map_id": report.get("map_id") or policy.get("map_id"),
                "policy": policy,
                "policy_adapter": policy.get("policy_adapter") or report.get("policy_adapter"),
            }
        ]
    return []


def adapter_count_keys(mode: str, count_key: str | None, ratio_key: str | None) -> tuple[str, str]:
    if count_key and ratio_key:
        return count_key, ratio_key
    if mode == "terminal_conversion_branch":
        return count_key or "terminal_decisions", ratio_key or "terminal_ratio"
    return count_key or "branch_decisions", ratio_key or "branch_ratio"


def usage_count(entry: dict[str, Any], count_key: str) -> int:
    value = entry.get(count_key)
    if isinstance(value, int):
        return value
    return 0


def usage_ratio(entry: dict[str, Any], count_key: str, ratio_key: str) -> float:
    value = as_number(entry.get(ratio_key))
    if value is not None:
        return value
    total = as_number(entry.get("total_decisions"))
    count = usage_count(entry, count_key)
    if total and total > 0:
        return count / total
    return 0.0


def extract_usage(adapter: dict[str, Any], count_key: str, ratio_key: str) -> dict[str, Any]:
    usage = adapter.get("usage")
    if not isinstance(usage, dict):
        return {
            "total_decisions": 0,
            "branch_decisions": 0,
            "branch_ratio": 0.0,
            "by_map": {},
            "by_time_bucket": {},
        }
    by_map = usage.get("by_map") if isinstance(usage.get("by_map"), dict) else {}
    by_time_bucket = (
        usage.get("by_time_bucket") if isinstance(usage.get("by_time_bucket"), dict) else {}
    )
    return {
        "total_decisions": usage.get("total_decisions", 0),
        "branch_decisions": usage_count(usage, count_key),
        "branch_ratio": usage_ratio(usage, count_key, ratio_key),
        "by_map": {
            key: {
                "total_decisions": value.get("total_decisions", 0) if isinstance(value, dict) else 0,
                "branch_decisions": usage_count(value, count_key) if isinstance(value, dict) else 0,
                "branch_ratio": usage_ratio(value, count_key, ratio_key) if isinstance(value, dict) else 0.0,
            }
            for key, value in by_map.items()
        },
        "by_time_bucket": {
            key: {
                "total_decisions": value.get("total_decisions", 0) if isinstance(value, dict) else 0,
                "branch_decisions": usage_count(value, count_key) if isinstance(value, dict) else 0,
                "branch_ratio": usage_ratio(value, count_key, ratio_key) if isinstance(value, dict) else 0.0,
            }
            for key, value in by_time_bucket.items()
        },
    }


def summarize_comparison(
    *,
    label: str,
    path: Path,
    report: dict[str, Any],
    expected_mode: str,
    allowed_branch_maps: set[str],
    allowed_branch_time_buckets: set[str],
    count_key: str,
    ratio_key: str,
    errors: list[str],
    blockers: list[str],
) -> dict[str, Any]:
    collect_gate_wording_errors(label, report, errors)
    root_adapter = report.get("policy_adapter")
    if not isinstance(root_adapter, dict):
        errors.append(f"{label}: top-level policy_adapter is missing")
        root_adapter = {}

    adapter = select_adapter(root_adapter, expected_mode, count_key)
    if adapter is None:
        errors.append(
            f"{label}: adapter mode `{root_adapter.get('mode')}` does not include expected `{expected_mode}`"
        )
        adapter = {}

    mode = adapter.get("mode")
    target_maps = string_list(adapter.get("target_maps"))
    unexpected_targets = sorted(set(target_maps) - allowed_branch_maps)
    if unexpected_targets:
        blockers.append(f"{label}: adapter target_maps include disallowed maps {unexpected_targets}")

    usage = extract_usage(adapter, count_key, ratio_key)
    for map_id, entry in usage["by_map"].items():
        if map_id not in allowed_branch_maps and entry["branch_decisions"] > 0:
            blockers.append(
                f"{label}: branch used on disallowed map `{map_id}` "
                f"({entry['branch_decisions']} decisions)"
            )
    for bucket, entry in usage["by_time_bucket"].items():
        if bucket not in allowed_branch_time_buckets and entry["branch_decisions"] > 0:
            blockers.append(
                f"{label}: branch used in disallowed time bucket `{bucket}` "
                f"({entry['branch_decisions']} decisions)"
            )

    map_summaries: list[dict[str, Any]] = []
    for item in policy_map_entries(report):
        map_id = item.get("map_id")
        if not isinstance(map_id, str) or not map_id:
            continue
        map_root_adapter = adapter_from_policy_map(item)
        if map_root_adapter is None:
            errors.append(f"{label}/{map_id}: policy_adapter is missing")
            continue
        map_adapter = select_adapter(map_root_adapter, expected_mode, count_key)
        if map_adapter is None:
            errors.append(
                f"{label}/{map_id}: adapter mode `{map_root_adapter.get('mode')}` "
                f"does not include expected `{expected_mode}`"
            )
            map_adapter = {}
        map_mode = map_adapter.get("mode")
        map_usage = extract_usage(map_adapter, count_key, ratio_key)
        map_decisions = map_usage["branch_decisions"]
        if map_id not in allowed_branch_maps and map_decisions > 0:
            blockers.append(
                f"{label}/{map_id}: branch used on disallowed map "
                f"({map_decisions} decisions)"
            )
        for bucket, entry in map_usage["by_time_bucket"].items():
            if bucket not in allowed_branch_time_buckets and entry["branch_decisions"] > 0:
                blockers.append(
                    f"{label}/{map_id}: branch used in disallowed time bucket `{bucket}` "
                    f"({entry['branch_decisions']} decisions)"
                )
        map_summaries.append(
            {
                "map_id": map_id,
                "mode": map_mode,
                "total_decisions": map_usage["total_decisions"],
                "branch_decisions": map_decisions,
                "branch_ratio": map_usage["branch_ratio"],
                "by_time_bucket": map_usage["by_time_bucket"],
            }
        )

    return {
        "label": label,
        "path": str(path),
        "loaded": True,
        "mode": mode,
        "target_maps": target_maps,
        "usage": usage,
        "maps": map_summaries,
    }


def build_report(
    comparisons: list[tuple[str, Path]],
    *,
    expected_mode: str,
    allowed_branch_maps: list[str],
    allowed_branch_time_buckets: list[str],
    min_total_branch_decisions: int | None = None,
    max_total_branch_ratio: float | None = None,
    count_key: str | None = None,
    ratio_key: str | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    blockers: list[str] = []
    if not comparisons:
        errors.append("at least one comparison report is required")
    allowed_maps = set(allowed_branch_maps)
    allowed_buckets = set(allowed_branch_time_buckets)
    if not expected_mode:
        errors.append("expected_mode must be non-empty")
    if not allowed_maps:
        errors.append("at least one allowed branch map is required")
    if not allowed_buckets:
        errors.append("at least one allowed branch time bucket is required")
    resolved_count_key, resolved_ratio_key = adapter_count_keys(expected_mode, count_key, ratio_key)

    report_summaries: list[dict[str, Any]] = []
    total_branch_decisions = 0
    total_decisions = 0
    seen_labels: set[str] = set()
    for label, path in comparisons:
        if label in seen_labels:
            errors.append(f"duplicate comparison label `{label}`")
            continue
        seen_labels.add(label)
        try:
            report = load_json_object(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{label}: unable to load {path}: {exc}")
            report_summaries.append({"label": label, "path": str(path), "loaded": False})
            continue
        summary = summarize_comparison(
            label=label,
            path=path,
            report=report,
            expected_mode=expected_mode,
            allowed_branch_maps=allowed_maps,
            allowed_branch_time_buckets=allowed_buckets,
            count_key=resolved_count_key,
            ratio_key=resolved_ratio_key,
            errors=errors,
            blockers=blockers,
        )
        usage = summary["usage"]
        usage_branch_decisions = int(usage.get("branch_decisions") or 0)
        usage_total_decisions = int(usage.get("total_decisions") or 0)
        map_branch_decisions = sum(
            int(item.get("branch_decisions") or 0)
            for item in summary.get("maps", [])
            if isinstance(item, dict)
        )
        map_total_decisions = sum(
            int(item.get("total_decisions") or 0)
            for item in summary.get("maps", [])
            if isinstance(item, dict)
        )
        if map_branch_decisions > usage_branch_decisions:
            effective_branch_decisions = map_branch_decisions
            effective_total_decisions = map_total_decisions
        else:
            effective_branch_decisions = usage_branch_decisions
            effective_total_decisions = usage_total_decisions
        summary["effective_total_decisions"] = effective_total_decisions
        summary["effective_branch_decisions"] = effective_branch_decisions
        summary["effective_branch_ratio"] = (
            round(effective_branch_decisions / effective_total_decisions, 6)
            if effective_total_decisions
            else 0.0
        )
        total_branch_decisions += effective_branch_decisions
        total_decisions += effective_total_decisions
        report_summaries.append(summary)

    total_branch_ratio = round(total_branch_decisions / total_decisions, 6) if total_decisions else 0.0
    if min_total_branch_decisions is not None and total_branch_decisions < min_total_branch_decisions:
        blockers.append(
            f"total branch decisions {total_branch_decisions} below required {min_total_branch_decisions}"
        )
    if max_total_branch_ratio is not None and total_branch_ratio > max_total_branch_ratio:
        blockers.append(
            f"total branch ratio {total_branch_ratio:.6f} above allowed {max_total_branch_ratio:.6f}"
        )

    decision = (
        "policy_adapter_scope_invalid"
        if errors
        else "policy_adapter_scope_failed"
        if blockers
        else "policy_adapter_scope_passed"
    )
    return {
        "report_version": 1,
        "decision": decision,
        "expected_mode": expected_mode,
        "allowed_branch_maps": sorted(allowed_maps),
        "allowed_branch_time_buckets": sorted(allowed_buckets),
        "count_key": resolved_count_key,
        "ratio_key": resolved_ratio_key,
        "comparison_count": len(comparisons),
        "total_decisions": total_decisions,
        "total_branch_decisions": total_branch_decisions,
        "total_branch_ratio": total_branch_ratio,
        "comparisons": report_summaries,
        "errors": errors,
        "blockers": blockers,
        "limitations": [
            "This gate validates evaluation-only policy adapter scope and provenance only.",
            "Passing does not make the policy an RL test Bot, content candidate, playtest candidate, or release candidate.",
            "A policy still requires fixed-window no-regression, target preflights, failure-case review, and RL acceptance gates.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Policy Adapter Scope Validation",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Expected mode: `{report['expected_mode']}`",
        f"- Comparisons: `{report['comparison_count']}`",
        f"- Total branch decisions: `{report['total_branch_decisions']}`",
        f"- Total branch ratio: `{report['total_branch_ratio']}`",
        "",
        "## Comparisons",
        "",
        "| Label | Mode | Branch decisions | Branch ratio |",
        "|---|---|---:|---:|",
    ]
    for item in report["comparisons"]:
        lines.append(
            "| `{label}` | `{mode}` | {decisions} | {ratio} |".format(
                label=item.get("label"),
                mode=item.get("mode"),
                decisions=item.get("effective_branch_decisions", 0),
                ratio=item.get("effective_branch_ratio", 0.0),
            )
        )
    lines.extend(["", "## Blockers", ""])
    lines.extend(f"- {item}" for item in report["blockers"]) if report["blockers"] else lines.append("- None")
    lines.extend(["", "## Errors", ""])
    lines.extend(f"- {item}" for item in report["errors"]) if report["errors"] else lines.append("- None")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate policy adapter scope in comparison reports.")
    parser.add_argument("--comparison", action="append", type=parse_labeled_path, required=True)
    parser.add_argument("--expected-mode", required=True)
    parser.add_argument("--allowed-branch-map", action="append", default=[])
    parser.add_argument("--allowed-branch-time-bucket", action="append", default=[])
    parser.add_argument("--min-total-branch-decisions", type=int, default=None)
    parser.add_argument("--max-total-branch-ratio", type=float, default=None)
    parser.add_argument("--count-key", default=None)
    parser.add_argument("--ratio-key", default=None)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--markdown", type=Path, default=None)
    parser.add_argument("--allow-fail", action="store_true")
    args = parser.parse_args()

    report = build_report(
        args.comparison,
        expected_mode=args.expected_mode,
        allowed_branch_maps=args.allowed_branch_map,
        allowed_branch_time_buckets=args.allowed_branch_time_bucket,
        min_total_branch_decisions=args.min_total_branch_decisions,
        max_total_branch_ratio=args.max_total_branch_ratio,
        count_key=args.count_key,
        ratio_key=args.ratio_key,
    )
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if report["decision"] != "policy_adapter_scope_passed" and not args.allow_fail:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
