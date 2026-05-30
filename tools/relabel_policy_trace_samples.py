#!/usr/bin/env python3
"""Relabel exported policy trace samples with counterfactual target actions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ACTION_COUNT = 9


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            payload = json.loads(text)
            if not isinstance(payload, dict):
                raise ValueError(f"{path}:{line_number}: record must be an object")
            records.append(payload)
    return records


def parse_actions(value: str) -> list[int]:
    actions: list[int] = []
    for item in value.split(","):
        text = item.strip()
        if not text:
            continue
        action = int(text)
        if action < 0 or action >= ACTION_COUNT:
            raise argparse.ArgumentTypeError(f"action must be in 0..{ACTION_COUNT - 1}")
        actions.append(action)
    if not actions:
        raise argparse.ArgumentTypeError("--target-actions must include at least one action")
    return actions


def count_distribution(values: list[int]) -> dict[str, dict[str, float | int]]:
    counts: dict[int, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    total = max(1, len(values))
    return {
        str(action): {
            "count": counts.get(action, 0),
            "ratio": round(counts.get(action, 0) / total, 4),
        }
        for action in range(ACTION_COUNT)
        if counts.get(action, 0) > 0
    }


def relabel_records(
    records: list[dict[str, Any]],
    *,
    target_actions: list[int],
    sample_role: str,
    sample_source: str,
    target_source: str,
    reason: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    output: list[dict[str, Any]] = []
    original_actions: list[int] = []
    relabeled_actions: list[int] = []
    sample_index = 0
    unchanged_count = 0

    for record in records:
        record_type = record.get("record_type")
        item = dict(record)
        if record_type == "metadata":
            item["sample_role"] = sample_role
            item["sample_source"] = sample_source
            item["target_source"] = target_source
            item["counterfactual_targets"] = {
                "target_actions": target_actions,
                "assignment": "cycle",
                "reason": reason,
            }
            output.append(item)
            continue
        if record_type != "sample":
            raise ValueError(f"unsupported record_type `{record_type}`")
        original = item.get("action")
        if not isinstance(original, int) or original < 0 or original >= ACTION_COUNT:
            raise ValueError("sample action must be an integer in 0..8")
        target = target_actions[sample_index % len(target_actions)]
        item["original_action"] = original
        item["action"] = target
        item["sample_role"] = sample_role
        item["sample_source"] = sample_source
        item["target_source"] = target_source
        item["counterfactual_label"] = {
            "original_action": original,
            "target_action": target,
            "assignment": "cycle",
            "reason": reason,
        }
        original_actions.append(original)
        relabeled_actions.append(target)
        if original == target:
            unchanged_count += 1
        output.append(item)
        sample_index += 1

    report = {
        "decision": "policy_trace_samples_relabeled" if sample_index else "policy_trace_samples_empty",
        "sample_count": sample_index,
        "target_actions": target_actions,
        "assignment": "cycle",
        "sample_role": sample_role,
        "sample_source": sample_source,
        "target_source": target_source,
        "unchanged_count": unchanged_count,
        "original_action_distribution": count_distribution(original_actions),
        "relabeled_action_distribution": count_distribution(relabeled_actions),
        "limitations": [
            "Counterfactual labels are design hypotheses, not observed successful actions.",
            "A dataset produced by this tool must pass dry-run checks, anchor validation, target-seed preflight, fixed-window comparison, and no-regression review before use as policy evidence.",
        ],
    }
    return output, report


def write_jsonl(records: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Policy Trace Sample Relabel",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Samples: `{report['sample_count']}`",
        f"- Target actions: `{','.join(str(item) for item in report['target_actions'])}`",
        f"- Unchanged: `{report['unchanged_count']}`",
        "",
        "## Original Actions",
        "",
        "| Action | Count | Ratio |",
        "|---|---:|---:|",
    ]
    for action, payload in report["original_action_distribution"].items():
        lines.append(f"| `{action}` | `{payload['count']}` | `{payload['ratio']}` |")
    lines.extend(["", "## Relabeled Actions", "", "| Action | Count | Ratio |", "|---|---:|---:|"])
    for action, payload in report["relabeled_action_distribution"].items():
        lines.append(f"| `{action}` | `{payload['count']}` | `{payload['ratio']}` |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Relabel policy trace samples.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--target-actions", type=parse_actions, required=True)
    parser.add_argument("--sample-role", default="counterfactual_repair_input")
    parser.add_argument("--sample-source", default="policy_trace_counterfactual")
    parser.add_argument("--target-source", default="counterfactual_prefailure_relabel")
    parser.add_argument("--reason", default="replace observed failure action with hypothesized repair target")
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--markdown", type=Path, default=None)
    args = parser.parse_args()

    records = load_jsonl(args.input)
    output, report = relabel_records(
        records,
        target_actions=args.target_actions,
        sample_role=args.sample_role,
        sample_source=args.sample_source,
        target_source=args.target_source,
        reason=args.reason,
    )
    report["input"] = str(args.input)
    report["output"] = str(args.out)
    write_jsonl(output, args.out)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "policy_trace_samples_relabeled" else 1


if __name__ == "__main__":
    raise SystemExit(main())
