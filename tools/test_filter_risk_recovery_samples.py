#!/usr/bin/env python3
"""Regression tests for clean risk recovery sample filtering."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from filter_risk_recovery_samples import build_filter_report  # noqa: E402
from test_validate_risk_recovery_samples import sample_payload, write_jsonl  # noqa: E402


class RiskRecoverySampleFilterTests(unittest.TestCase):
    def test_keeps_clean_valid_sample(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "samples.jsonl"
            out = root / "clean.jsonl"
            write_jsonl(source, [sample_payload()])

            report = build_filter_report([source], out=out)
            rows = [json.loads(line) for line in out.read_text().splitlines()]

        self.assertEqual(report["decision"], "risk_recovery_clean_samples_exported")
        self.assertEqual(report["kept_sample_count"], 1)
        self.assertEqual(report["drop_count"], 0)
        self.assertEqual(rows[0]["record_type"], "risk_recovery_supervision_sample")
        self.assertNotIn("_source_line", rows[0])

    def test_drops_target_with_risk_reasons_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "samples.jsonl"
            out = root / "clean.jsonl"
            payload = sample_payload(target_action=2)
            payload["adapter_decision"]["target_action"] = 2
            payload["adapter_decision"]["target_risk_reasons"] = ["wallward_edge"]
            write_jsonl(source, [payload])

            report = build_filter_report([source], out=out)
            clean_text = out.read_text()

        self.assertEqual(report["decision"], "risk_recovery_clean_samples_unavailable")
        self.assertEqual(report["drop_reasons"]["target_risk_reasons"], 1)
        self.assertEqual(clean_text, "")

    def test_allow_target_risk_keeps_residual_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "samples.jsonl"
            out = root / "clean.jsonl"
            payload = sample_payload(target_action=2)
            payload["adapter_decision"]["target_action"] = 2
            payload["adapter_decision"]["target_risk_reasons"] = ["wallward_edge"]
            write_jsonl(source, [payload])

            report = build_filter_report([source], out=out, allow_target_risk=True)

        self.assertEqual(report["decision"], "risk_recovery_clean_samples_exported")
        self.assertEqual(report["kept_sample_count"], 1)

    def test_drops_worse_target_risk_score(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "samples.jsonl"
            out = root / "clean.jsonl"
            payload = sample_payload(original_action=3, target_action=4)
            payload["adapter_decision"]["original_action"] = 3
            payload["adapter_decision"]["target_action"] = 4
            payload["adapter_decision"]["risk_reasons"] = ["toward_enemy_pressure"]
            payload["adapter_decision"]["target_risk_reasons"] = ["toward_enemy_pressure"]
            payload["adapter_decision"]["pressure_context"]["enemy_pressure_risk"] = 0.7
            payload["adapter_decision"]["pressure_context"]["combined_pressure"] = 0.7
            payload["adapter_decision"]["pressure_context"]["enemy_vector"] = [1.0, -1.0]
            payload["diagnostics"]["boundary"]["top_distance"] = 1900.0
            write_jsonl(source, [payload])

            report = build_filter_report([source], out=out, allow_target_risk=True)

        self.assertEqual(report["decision"], "risk_recovery_clean_samples_unavailable")
        self.assertEqual(report["drop_reasons"]["worse_target_risk_score"], 1)

    def test_can_filter_clean_samples_by_map_and_time_window(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "samples.jsonl"
            out = root / "clean.jsonl"
            keep = sample_payload(map_id="cracked-star-jar", time_seconds=210.0)
            wrong_map = sample_payload(map_id="soda-creek", time_seconds=210.0)
            wrong_time = sample_payload(map_id="cracked-star-jar", time_seconds=310.0)
            write_jsonl(source, [keep, wrong_map, wrong_time])

            report = build_filter_report(
                [source],
                out=out,
                map_filter={"cracked-star-jar"},
                min_seconds=180.0,
                max_seconds=300.0,
            )
            rows = [json.loads(line) for line in out.read_text().splitlines()]

        self.assertEqual(report["decision"], "risk_recovery_clean_samples_exported")
        self.assertEqual(report["kept_sample_count"], 1)
        self.assertEqual(report["drop_reasons"]["map_filter"], 1)
        self.assertEqual(report["drop_reasons"]["time_window"], 1)
        self.assertEqual(report["filter"]["map_filter"], ["cracked-star-jar"])
        self.assertEqual(report["filter"]["min_seconds"], 180.0)
        self.assertEqual(report["filter"]["max_seconds"], 300.0)
        self.assertEqual(rows[0]["map_id"], "cracked-star-jar")


if __name__ == "__main__":
    unittest.main()
