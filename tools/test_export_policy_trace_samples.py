#!/usr/bin/env python3
"""Tests for policy trace sample export."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from export_policy_trace_samples import build_report


def write_trace(
    path: Path,
    *,
    seed: int = 63400,
    map_id: str = "soda-creek",
    terminal_kind: str = "victory",
    action: int = 7,
    time_seconds: float = 32.0,
    edge_risk: float = 1.0,
    enemy_pressure_risk: float = 0.2,
    include_observation: bool = True,
) -> None:
    step = {
        "step": 960,
        "tick": 960,
        "time_seconds": time_seconds,
        "action": action,
        "health": 90.0,
        "level": 2,
        "kills": 10,
        "action_score": {
            "kind": "probability",
            "top_actions": [{"action": str(action), "score": 0.7}],
        },
        "diagnostics": {
            "boundary": {
                "left_distance": 2400.0,
                "right_distance": 0.0,
                "bottom_distance": 300.0,
                "top_distance": 1500.0,
                "min_distance": 0.0,
                "edge_risk": edge_risk,
            },
            "enemy_pressure_risk": enemy_pressure_risk,
        },
    }
    if include_observation:
        step["observation_version"] = 2
        step["observation"] = [0.5, 0.75, 0.25]
    payload = {
        "record_type": "policy_episode_trace",
        "episode": {
            "seed": seed,
            "map_id": map_id,
            "terminal_kind": terminal_kind,
            "terminal_reason": "duration_reached",
        },
        "steps": [step],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


class PolicyTraceSampleExportTests(unittest.TestCase):
    def test_exports_victory_action_sample(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            trace = root / "soda-creek_seed63400_trace.json"
            out = root / "samples.jsonl"
            write_trace(trace)

            report = build_report(
                [root],
                out=out,
                terminal_filter="victory",
                map_ids={"soda-creek"},
                seeds={63400},
                min_seconds=31.0,
                max_seconds=33.0,
                actions={7, 3},
                min_boundary_edge_risk=0.75,
            )
            rows = [json.loads(line) for line in out.read_text().splitlines()]

        self.assertEqual(report["decision"], "policy_trace_samples_exported")
        self.assertEqual(report["sample_count"], 1)
        self.assertEqual(rows[0]["record_type"], "metadata")
        self.assertEqual(rows[1]["record_type"], "sample")
        self.assertEqual(rows[1]["action"], 7)
        self.assertEqual(rows[1]["sample_role"], "retention_anchor_input")
        self.assertEqual(rows[1]["observation_len"], 3)

    def test_filters_terminal_and_action(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = root / "samples.jsonl"
            write_trace(root / "defeat_trace.json", terminal_kind="defeat", action=7)
            write_trace(root / "wrong_action_trace.json", seed=63401, action=5)

            report = build_report(
                [root],
                out=out,
                terminal_filter="victory",
                actions={7},
                allow_empty=True,
            )

        self.assertEqual(report["decision"], "policy_trace_samples_unavailable")
        self.assertEqual(report["sample_count"], 0)
        self.assertEqual(report["dropped_counts"]["terminal_filtered_trace"], 1)
        self.assertEqual(report["dropped_counts"]["action_not_selected"], 1)

    def test_missing_observation_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            trace = root / "trace.json"
            out = root / "samples.jsonl"
            write_trace(trace, include_observation=False)

            report = build_report([trace], out=out, allow_empty=True)

        self.assertEqual(report["decision"], "policy_trace_samples_unavailable")
        self.assertEqual(report["dropped_counts"]["missing_observation"], 1)


if __name__ == "__main__":
    unittest.main()
