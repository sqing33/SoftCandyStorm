#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from python.train.train_behavior_clone import (
    dependency_status,
    diagnose_behavior_clone_policy_path,
    load_trajectory_dataset,
)


def write_json(path, payload):
    if path is None:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_markdown(path, report):
    if path is None:
        return
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    overall = report["overall"]
    dominant = overall.get("dominant_predicted_action") or {}
    lines = [
        "# Behavior Clone Offline Policy Diagnostic",
        "",
        f"- Gate decision: `{report['gate_decision']}`",
        f"- Model: `{report['model_path']}`",
        f"- Samples: `{overall['sample_count']}`",
        f"- Accuracy: `{overall['accuracy']}`",
        f"- Dominant predicted action: `{dominant.get('action')}` ratio `{dominant.get('ratio')}`",
        f"- Normalized predicted action entropy: `{overall['normalized_predicted_action_entropy']}`",
        f"- Normalized mean policy entropy: `{overall['normalized_mean_policy_entropy']}`",
        "",
        "## Phase Summary",
        "",
        "| Phase | Samples | Accuracy | Dominant Action | Dominant Ratio | Predicted Entropy |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for phase, phase_report in report["by_phase"].items():
        phase_dominant = phase_report.get("dominant_predicted_action") or {}
        lines.append(
            "| `{}` | {} | {} | `{}` | {} | {} |".format(
                phase,
                phase_report["sample_count"],
                phase_report["accuracy"],
                phase_dominant.get("action"),
                phase_dominant.get("ratio"),
                phase_report["normalized_predicted_action_entropy"],
            )
        )
    lines.extend(["", "## Findings", ""])
    if report["findings"]:
        for finding in report["findings"]:
            lines.append(f"- `{finding['id']}` ({finding['scope']}): {finding['summary']}")
    else:
        lines.append("- No repair finding from offline action-distribution diagnostics.")
    lines.extend(["", "## Limitations", ""])
    for limitation in report["limitations"]:
        lines.append(f"- {limitation}")
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Diagnose behavior clone predictions against an offline trajectory dataset."
    )
    parser.add_argument("--model", required=True, help="Behavior clone .pt checkpoint or staged checkpoint.")
    parser.add_argument(
        "--dataset",
        action="append",
        required=True,
        help="JSONL file or directory with JSONL files. Repeat to combine datasets.",
    )
    parser.add_argument("--limit-samples", type=int, default=None)
    parser.add_argument("--dominant-action-threshold", type=float, default=0.85)
    parser.add_argument("--low-entropy-threshold", type=float, default=0.1)
    parser.add_argument("--report", default=None, help="Write JSON report.")
    parser.add_argument("--markdown", default=None, help="Write Markdown summary.")
    args = parser.parse_args()

    if args.limit_samples is not None and args.limit_samples <= 0:
        parser.error("--limit-samples must be greater than zero")
    if not (0.0 < args.dominant_action_threshold <= 1.0):
        parser.error("--dominant-action-threshold must be in (0, 1]")
    if not (0.0 <= args.low_entropy_threshold <= 1.0):
        parser.error("--low-entropy-threshold must be in [0, 1]")

    dataset = load_trajectory_dataset(args.dataset, limit=args.limit_samples)
    report = diagnose_behavior_clone_policy_path(
        args.model,
        dataset,
        dominant_action_threshold=args.dominant_action_threshold,
        low_entropy_threshold=args.low_entropy_threshold,
    )
    report["dependency_status"] = dependency_status()
    write_json(args.report, report)
    write_markdown(args.markdown, report)


if __name__ == "__main__":
    main()
