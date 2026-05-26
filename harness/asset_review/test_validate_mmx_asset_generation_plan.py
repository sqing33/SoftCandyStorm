#!/usr/bin/env python3
"""Regression tests for mmx asset generation plan validation.

Run with:
    python3 harness/asset_review/test_validate_mmx_asset_generation_plan.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
VALIDATOR = SCRIPT_DIR / "validate_mmx_asset_generation_plan.py"
TEMPLATE = SCRIPT_DIR / "mmx_asset_generation_plan_template.json"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_mmx_asset_generation_plan import build_report, load_json_object  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def fixture_plan(root: Path) -> Path:
    plan_path = root / "harness" / "asset_review" / "plan.json"
    payload = load_json_object(TEMPLATE)
    write_json(plan_path, payload)
    return plan_path


class MmxAssetGenerationPlanValidatorTests(unittest.TestCase):
    def test_template_is_valid_pre_generation_plan(self) -> None:
        report = build_report(TEMPLATE, REPO_ROOT)

        self.assertEqual(report["decision"], "mmx_asset_generation_plan_valid")
        self.assertEqual(report["asset_count"], 3)
        self.assertEqual(report["errors"], [])

    def test_rejects_target_outside_generated_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            plan = fixture_plan(root)
            payload = load_json_object(plan)
            payload["target_batch_path"] = "assets/runtime"
            write_json(plan, payload)

            report = build_report(plan, root)

            self.assertEqual(report["decision"], "mmx_asset_generation_plan_invalid")
            self.assertTrue(any("asset/generated_candidates" in error for error in report["errors"]))

    def test_rejects_missing_agent_flags(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            plan = fixture_plan(root)
            payload = load_json_object(plan)
            command = payload["planned_assets"][0]["command"]
            payload["planned_assets"][0]["command"] = [
                token for token in command if token not in {"--non-interactive", "--quiet", "--output", "json"}
            ]
            write_json(plan, payload)

            report = build_report(plan, root)

            self.assertEqual(report["decision"], "mmx_asset_generation_plan_invalid")
            self.assertTrue(any("missing agent flags" in error for error in report["errors"]))
            self.assertTrue(any("--output json" in error or "`--output json`" in error for error in report["errors"]))

    def test_rejects_runtime_integration_claim(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            plan = fixture_plan(root)
            payload = load_json_object(plan)
            payload["project_rules"]["runtime_integrated"] = True
            write_json(plan, payload)

            report = build_report(plan, root)

            self.assertEqual(report["decision"], "mmx_asset_generation_plan_invalid")
            self.assertTrue(any("runtime_integrated" in error for error in report["errors"]))

    def test_rejects_command_output_outside_target_batch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            plan = fixture_plan(root)
            payload = load_json_object(plan)
            command = payload["planned_assets"][1]["command"]
            out_index = command.index("--out") + 1
            command[out_index] = "asset/generated_candidates/other_batch/audio/voice.mp3"
            write_json(plan, payload)

            report = build_report(plan, root)

            self.assertEqual(report["decision"], "mmx_asset_generation_plan_invalid")
            self.assertTrue(any("inside target_batch_path" in error for error in report["errors"]))

    def test_cli_writes_report_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            plan = fixture_plan(root)
            report_path = root / "report.json"
            markdown_path = root / "summary.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(plan),
                    "--repo-root",
                    str(root),
                    "--report",
                    str(report_path),
                    "--markdown",
                    str(markdown_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["decision"], "mmx_asset_generation_plan_valid")
            self.assertIn("mmx Asset Generation Plan Validation", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
