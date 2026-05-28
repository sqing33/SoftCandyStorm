#!/usr/bin/env python3
"""Preflight PPO anchor regularization inputs without running PPO training."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from python.train.train_sb3 import (  # noqa: E402
    ANCHOR_SAMPLE_WEIGHTING_MODES,
    load_config,
    parse_anchor_time_bucket_list,
    parse_anchor_time_bucket_weights,
    prepare_anchor_regularization,
)


def build_preflight_report(
    *,
    anchor_report: dict[str, Any],
    args: argparse.Namespace,
) -> dict[str, Any]:
    return {
        "report_version": 1,
        "decision": "anchor_regularization_input_valid",
        "gate_decision": "anchor_regularization_input_valid_not_policy_gate",
        "algorithm": args.algorithm,
        "config": args.config,
        "anchor_regularization": anchor_report,
        "limitations": [
            "This preflight validates offline anchor regularization inputs only.",
            "It does not train a PPO checkpoint.",
            "It is not high-pressure, no-regression, repair-probe, or RL acceptance evidence.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    anchor = report["anchor_regularization"]
    dataset = anchor["dataset"]
    sample_summary = dataset.get("sample_summary", {})
    source_distribution = sample_summary.get("sample_source_distribution", {})
    lines = [
        "# Anchor Regularization Input Preflight",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Gate decision: `{report['gate_decision']}`",
        f"- Algorithm: `{report['algorithm']}`",
        f"- Anchor model: `{anchor['anchor_model']}`",
        f"- Anchor opening model: `{anchor['anchor_opening_model']}`",
        f"- Dataset samples: `{dataset['sample_count']}`",
        f"- Observation len: `{dataset['observation_len']}`",
        f"- Action count: `{dataset['action_count']}`",
        f"- Anchor drift samples: `{dataset.get('anchor_drift_sample_records', 0)}`",
        f"- Time bucket filter: `{anchor['time_bucket_filter']['mode']}`",
        f"- Sample weighting: `{anchor['sample_weighting']['mode']}`",
        f"- Target argmax agreement with dataset actions: `{anchor['target']['anchor_argmax_agreement_with_dataset_actions']}`",
        "",
        "## Sample Sources",
        "",
        "| Source | Samples | Ratio |",
        "| --- | ---: | ---: |",
    ]
    for source, item in sorted(source_distribution.items()):
        lines.append(f"| `{source}` | `{item['count']}` | `{item['ratio']}` |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate PPO anchor regularization inputs without training."
    )
    parser.add_argument("--config", default="python/train/rl_training_config.json")
    parser.add_argument("--algorithm", choices=["ppo"], default="ppo")
    parser.add_argument("--anchor-model", required=True)
    parser.add_argument("--anchor-dataset", action="append", required=True)
    parser.add_argument("--anchor-opening-model", default=None)
    parser.add_argument("--anchor-opening-seconds", type=float, default=60.0)
    parser.add_argument("--anchor-regularization-weight", type=float, default=1.0)
    parser.add_argument("--anchor-regularization-interval", type=int, default=2048)
    parser.add_argument("--anchor-regularization-epochs", type=int, default=1)
    parser.add_argument("--anchor-regularization-batch-size", type=int, default=256)
    parser.add_argument("--anchor-regularization-learning-rate", type=float, default=None)
    parser.add_argument("--anchor-limit-samples", type=int, default=None)
    parser.add_argument(
        "--anchor-sample-weighting",
        choices=sorted(ANCHOR_SAMPLE_WEIGHTING_MODES),
        default="none",
    )
    parser.add_argument("--anchor-include-time-buckets", default=None)
    parser.add_argument("--anchor-time-bucket-weights", default=None)
    parser.add_argument("--anchor-validation-split", type=float, default=0.2)
    parser.add_argument("--anchor-seed", type=int, default=12345)
    parser.add_argument("--report", required=True)
    parser.add_argument("--markdown", default=None)
    args = parser.parse_args()

    anchor_include_time_buckets = parse_anchor_time_bucket_list(
        args.anchor_include_time_buckets
    )
    anchor_time_bucket_weights = parse_anchor_time_bucket_weights(
        args.anchor_time_bucket_weights
    )
    anchor_regularization = prepare_anchor_regularization(
        load_config(args.config),
        args.algorithm,
        anchor_model=Path(args.anchor_model),
        anchor_datasets=args.anchor_dataset,
        anchor_opening_model=(
            Path(args.anchor_opening_model) if args.anchor_opening_model else None
        ),
        anchor_opening_seconds=args.anchor_opening_seconds,
        anchor_regularization_weight=args.anchor_regularization_weight,
        anchor_regularization_interval=args.anchor_regularization_interval,
        anchor_regularization_epochs=args.anchor_regularization_epochs,
        anchor_regularization_batch_size=args.anchor_regularization_batch_size,
        anchor_regularization_learning_rate=args.anchor_regularization_learning_rate,
        anchor_limit_samples=args.anchor_limit_samples,
        anchor_sample_weighting=args.anchor_sample_weighting,
        anchor_include_time_buckets=anchor_include_time_buckets,
        anchor_time_bucket_weights=anchor_time_bucket_weights,
        anchor_validation_split=args.anchor_validation_split,
        anchor_seed=args.anchor_seed,
    )
    if anchor_regularization is None:
        parser.error("anchor regularization was not requested")
    report = build_preflight_report(
        anchor_report=anchor_regularization["report"],
        args=args,
    )
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    if args.markdown:
        write_markdown(report, Path(args.markdown))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
