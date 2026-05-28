#!/usr/bin/env python3
"""Regression tests for anchor regularization input preflight reporting."""

from __future__ import annotations

import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

from validate_anchor_regularization_input import (  # noqa: E402
    build_preflight_report,
    write_markdown,
)


class AnchorRegularizationInputPreflightTests(unittest.TestCase):
    def test_build_preflight_report_marks_not_policy_gate(self) -> None:
        report = build_preflight_report(
            anchor_report={
                "anchor_model": "fallback.pt",
                "anchor_opening_model": "opening.zip",
                "dataset": {
                    "sample_count": 2,
                    "observation_len": 145,
                    "action_count": 9,
                    "anchor_drift_sample_records": 2,
                    "sample_summary": {
                        "sample_source_distribution": {
                            "anchor_drift_diagnostic": {
                                "count": 2,
                                "ratio": 1.0,
                            }
                        }
                    },
                },
                "time_bucket_filter": {"mode": "include_time_buckets"},
                "sample_weighting": {"mode": "map_time_bucket_balance"},
                "target": {"anchor_argmax_agreement_with_dataset_actions": 1.0},
            },
            args=Namespace(
                algorithm="ppo",
                config="python/train/rl_training_config.json",
            ),
        )

        self.assertEqual(report["decision"], "anchor_regularization_input_valid")
        self.assertEqual(
            report["gate_decision"],
            "anchor_regularization_input_valid_not_policy_gate",
        )
        self.assertIn("does not train", " ".join(report["limitations"]))

    def test_write_markdown_includes_dataset_counts(self) -> None:
        report = build_preflight_report(
            anchor_report={
                "anchor_model": "fallback.pt",
                "anchor_opening_model": None,
                "dataset": {
                    "sample_count": 2,
                    "observation_len": 145,
                    "action_count": 9,
                    "anchor_drift_sample_records": 2,
                    "sample_summary": {
                        "sample_source_distribution": {
                            "anchor_drift_diagnostic": {
                                "count": 2,
                                "ratio": 1.0,
                            }
                        }
                    },
                },
                "time_bucket_filter": {"mode": "include_time_buckets"},
                "sample_weighting": {"mode": "none"},
                "target": {"anchor_argmax_agreement_with_dataset_actions": 1.0},
            },
            args=Namespace(
                algorithm="ppo",
                config="python/train/rl_training_config.json",
            ),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "report.md"
            write_markdown(report, path)
            text = path.read_text(encoding="utf-8")

        self.assertIn("Anchor drift samples: `2`", text)
        self.assertIn("anchor_drift_diagnostic", text)


if __name__ == "__main__":
    unittest.main()
