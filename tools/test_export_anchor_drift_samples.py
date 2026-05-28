#!/usr/bin/env python3
"""Regression tests for anchor drift sample export helpers."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from export_anchor_drift_samples import (  # noqa: E402
    build_drift_row,
    filter_and_rank_rows,
    parse_time_bucket_filter,
    summarize_rows,
)


class AnchorDriftSamplesTests(unittest.TestCase):
    def test_build_drift_row_records_kl_and_disagreement(self) -> None:
        row = build_drift_row(
            index=7,
            observation=[0.1, 0.2],
            sample={
                "path": "fixture.jsonl",
                "map_id": "soda-creek",
                "seed": 63100,
                "time_seconds": 90.0,
                "action": 3,
            },
            anchor_probabilities=[0.1, 0.8, 0.1],
            candidate_probabilities=[0.1, 0.2, 0.7],
            include_observation=True,
            top_k=2,
        )

        self.assertEqual(row["time_bucket"], "mid_60_to_180")
        self.assertEqual(row["anchor_action"], 1)
        self.assertEqual(row["candidate_action"], 2)
        self.assertFalse(row["argmax_agree"])
        self.assertGreater(row["kl_divergence"], 0.0)
        self.assertEqual(row["observation"], [0.1, 0.2])
        self.assertEqual(len(row["anchor_top_actions"]), 2)

    def test_filter_and_rank_rows_keeps_requested_bucket_and_disagreement(self) -> None:
        rows = [
            {
                "sample_index": 1,
                "map_id": "soda-creek",
                "time_bucket": "mid_60_to_180",
                "time_seconds": 70.0,
                "kl_divergence": 0.2,
                "argmax_agree": False,
            },
            {
                "sample_index": 2,
                "map_id": "soda-creek",
                "time_bucket": "late_180_to_300",
                "time_seconds": 200.0,
                "kl_divergence": 0.9,
                "argmax_agree": False,
            },
            {
                "sample_index": 3,
                "map_id": "caramel-workshop",
                "time_bucket": "mid_60_to_180",
                "time_seconds": 80.0,
                "kl_divergence": 0.7,
                "argmax_agree": True,
            },
        ]

        result = filter_and_rank_rows(
            rows,
            map_filter={"soda-creek"},
            time_bucket_filter={"mid_60_to_180"},
            min_kl=0.1,
            only_disagreement=True,
            top=10,
        )

        self.assertEqual([row["sample_index"] for row in result], [1])

    def test_summarize_rows_counts_maps_and_buckets(self) -> None:
        rows = [
            {
                "map_id": "soda-creek",
                "time_bucket": "mid_60_to_180",
                "kl_divergence": 0.4,
                "argmax_agree": False,
                "anchor_action": 1,
                "candidate_action": 7,
            },
            {
                "map_id": "soda-creek",
                "time_bucket": "mid_60_to_180",
                "kl_divergence": 0.2,
                "argmax_agree": True,
                "anchor_action": 1,
                "candidate_action": 1,
            },
        ]

        summary = summarize_rows(rows)

        self.assertEqual(summary["sample_count"], 2)
        self.assertEqual(summary["argmax_disagreement_count"], 1)
        self.assertEqual(summary["by_map"]["soda-creek"]["sample_count"], 2)
        self.assertEqual(summary["by_time_bucket"]["mid_60_to_180"]["mean_kl"], 0.3)

    def test_parse_time_bucket_filter_rejects_unknown_label(self) -> None:
        with self.assertRaises(ValueError):
            parse_time_bucket_filter("mid_60_to_180,missing")


if __name__ == "__main__":
    unittest.main()
