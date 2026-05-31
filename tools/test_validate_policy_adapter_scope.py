#!/usr/bin/env python3
"""Tests for evaluation-only policy adapter scope validation."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from validate_policy_adapter_scope import build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def usage_entry(total_decisions: int, branch_decisions: int) -> dict:
    ratio = round(branch_decisions / total_decisions, 4) if total_decisions else 0.0
    return {
        "total_decisions": total_decisions,
        "base_decisions": total_decisions - branch_decisions,
        "branch_decisions": branch_decisions,
        "branch_ratio": ratio,
    }


def adapter_payload(
    *,
    mode: str = "edge_recovery_branch",
    target_maps: list[str] | None = None,
    total_decisions: int = 1000,
    branch_decisions: int = 4,
    by_map: dict | None = None,
    by_time_bucket: dict | None = None,
) -> dict:
    target_maps = target_maps if target_maps is not None else ["soda-creek"]
    return {
        "mode": mode,
        "target_maps": target_maps,
        "usage": {
            **usage_entry(total_decisions, branch_decisions),
            "by_map": by_map if by_map is not None else {"soda-creek": usage_entry(total_decisions, branch_decisions)},
            "by_time_bucket": (
                by_time_bucket
                if by_time_bucket is not None
                else {"opening_lt_60": usage_entry(total_decisions, branch_decisions)}
            ),
        },
    }


def terminal_usage_entry(total_decisions: int, terminal_decisions: int) -> dict:
    ratio = round(terminal_decisions / total_decisions, 4) if total_decisions else 0.0
    return {
        "total_decisions": total_decisions,
        "base_decisions": total_decisions - terminal_decisions,
        "terminal_decisions": terminal_decisions,
        "terminal_ratio": ratio,
    }


def terminal_adapter_payload() -> dict:
    return {
        "mode": "terminal_conversion_branch",
        "target_maps": ["caramel-workshop"],
        "usage": {
            **terminal_usage_entry(1000, 80),
            "by_map": {
                "caramel-workshop": terminal_usage_entry(1000, 80),
            },
            "by_time_bucket": {
                "late_180_to_300": terminal_usage_entry(600, 80),
                "mid_60_to_180": terminal_usage_entry(400, 0),
            },
        },
    }


def comparison_payload(
    *,
    gate_decision: str = "multimap_comparison_recorded_needs_policy_repair",
    top_adapter: dict | None = None,
    maps: list[dict] | None = None,
) -> dict:
    if maps is None:
        maps = [
            {
                "map_id": "soda-creek",
                "policy_adapter": adapter_payload(
                    total_decisions=1000,
                    branch_decisions=4,
                    by_map={"soda-creek": usage_entry(1000, 4)},
                    by_time_bucket={"opening_lt_60": usage_entry(1000, 4)},
                ),
            },
            {
                "map_id": "caramel-workshop",
                "policy_adapter": adapter_payload(
                    total_decisions=900,
                    branch_decisions=0,
                    by_map={"caramel-workshop": usage_entry(900, 0)},
                    by_time_bucket={"opening_lt_60": usage_entry(900, 0)},
                ),
            },
        ]
    if top_adapter is None:
        top_adapter = adapter_payload(
            total_decisions=1900,
            branch_decisions=4,
            by_map={
                "soda-creek": usage_entry(1000, 4),
                "caramel-workshop": usage_entry(900, 0),
            },
            by_time_bucket={"opening_lt_60": usage_entry(1900, 4)},
        )
    return {
        "gate_decision": gate_decision,
        "policy_adapter": top_adapter,
        "maps": maps,
    }


def validate(path: Path, *, label: str = "60s") -> dict:
    return build_report(
        [(label, path)],
        expected_mode="edge_recovery_branch",
        allowed_branch_maps=["soda-creek"],
        allowed_branch_time_buckets=["opening_lt_60"],
        min_total_branch_decisions=1,
        max_total_branch_ratio=0.01,
    )


class PolicyAdapterScopeTests(unittest.TestCase):
    def test_allowed_map_and_time_bucket_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "comparison.json"
            write_json(path, comparison_payload())

            report = validate(path)

        self.assertEqual(report["decision"], "policy_adapter_scope_passed")
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["blockers"], [])
        self.assertEqual(report["total_branch_decisions"], 4)

    def test_terminal_conversion_branch_uses_terminal_count_keys(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "comparison.json"
            adapter = terminal_adapter_payload()
            write_json(
                path,
                {
                    "gate_decision": "multimap_comparison_recorded_needs_policy_repair",
                    "policy_adapter": adapter,
                    "maps": [
                        {
                            "map_id": "caramel-workshop",
                            "policy_adapter": adapter,
                        }
                    ],
                },
            )

            report = build_report(
                [("300s", path)],
                expected_mode="terminal_conversion_branch",
                allowed_branch_maps=["caramel-workshop"],
                allowed_branch_time_buckets=["late_180_to_300"],
                min_total_branch_decisions=1,
                max_total_branch_ratio=0.1,
            )

        self.assertEqual(report["decision"], "policy_adapter_scope_passed")
        self.assertEqual(report["count_key"], "terminal_decisions")
        self.assertEqual(report["ratio_key"], "terminal_ratio")
        self.assertEqual(report["total_branch_decisions"], 80)

    def test_disallowed_map_branch_usage_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "comparison.json"
            top_adapter = adapter_payload(
                total_decisions=1900,
                branch_decisions=5,
                by_map={
                    "soda-creek": usage_entry(1000, 4),
                    "caramel-workshop": usage_entry(900, 1),
                },
                by_time_bucket={"opening_lt_60": usage_entry(1900, 5)},
            )
            maps = [
                {
                    "map_id": "caramel-workshop",
                    "policy_adapter": adapter_payload(
                        total_decisions=900,
                        branch_decisions=1,
                        by_map={"caramel-workshop": usage_entry(900, 1)},
                        by_time_bucket={"opening_lt_60": usage_entry(900, 1)},
                    ),
                }
            ]
            write_json(path, comparison_payload(top_adapter=top_adapter, maps=maps))

            report = validate(path)

        self.assertEqual(report["decision"], "policy_adapter_scope_failed")
        self.assertTrue(any("disallowed map" in blocker for blocker in report["blockers"]))

    def test_disallowed_time_bucket_branch_usage_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "comparison.json"
            top_adapter = adapter_payload(
                total_decisions=1900,
                branch_decisions=5,
                by_map={"soda-creek": usage_entry(1900, 5)},
                by_time_bucket={
                    "opening_lt_60": usage_entry(1000, 4),
                    "mid_60_to_180": usage_entry(900, 1),
                },
            )
            write_json(path, comparison_payload(top_adapter=top_adapter))

            report = validate(path)

        self.assertEqual(report["decision"], "policy_adapter_scope_failed")
        self.assertTrue(any("disallowed time bucket" in blocker for blocker in report["blockers"]))

    def test_missing_top_level_adapter_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "comparison.json"
            payload = comparison_payload()
            payload.pop("policy_adapter")
            write_json(path, payload)

            report = validate(path)

        self.assertEqual(report["decision"], "policy_adapter_scope_invalid")
        self.assertTrue(any("top-level policy_adapter" in error for error in report["errors"]))

    def test_forbidden_gate_wording_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "comparison.json"
            write_json(path, comparison_payload(gate_decision="rl_test_bot_candidate_passed"))

            report = validate(path)

        self.assertEqual(report["decision"], "policy_adapter_scope_invalid")
        self.assertTrue(any("overclaims adapter evidence" in error for error in report["errors"]))

    def test_duplicate_comparison_label_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "comparison.json"
            write_json(path, comparison_payload())

            report = build_report(
                [("60s", path), ("60s", path)],
                expected_mode="edge_recovery_branch",
                allowed_branch_maps=["soda-creek"],
                allowed_branch_time_buckets=["opening_lt_60"],
            )

        self.assertEqual(report["decision"], "policy_adapter_scope_invalid")
        self.assertTrue(any("duplicate comparison label" in error for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()
