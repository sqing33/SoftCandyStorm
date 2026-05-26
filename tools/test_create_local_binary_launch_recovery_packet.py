#!/usr/bin/env python3
"""Regression tests for local binary launch recovery packet generation.

Run with:
    python3 tools/test_create_local_binary_launch_recovery_packet.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
PACKET = SCRIPT_DIR / "create_local_binary_launch_recovery_packet.py"

sys.path.insert(0, str(SCRIPT_DIR))

from create_local_binary_launch_recovery_packet import build_packet  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def make_fixture(root: Path) -> dict[str, Path]:
    diagnostic = root / "harness/reports/diagnostic/local_binary_launch_diagnostic.json"
    failure_case = root / "harness/failed_cases/fail_20260526_024_local_binary_launch_blocked.json"
    progress = root / "harness/progress.json"
    docs_coverage = root / "harness/docs_implementation_coverage.json"

    write_json(
        diagnostic,
        {
            "decision": "local_binary_launch_blocked",
            "signals": {
                "system_binary_runs": True,
                "hello_compiled": True,
                "hello_runs": False,
                "hello_timed_out": True,
                "developer_mode_disabled": True,
                "spctl_rejected": True,
                "provenance_xattr_present": True,
                "security_policy_would_not_allow": True,
            },
            "checks": {
                "system_echo": {"returncode": 0, "timed_out": False, "elapsed_seconds": 0.01, "stdout": "ok\n"},
                "developer_mode": {
                    "returncode": 0,
                    "timed_out": False,
                    "elapsed_seconds": 0.01,
                    "stdout": "Developer mode is currently disabled.\n",
                },
                "spctl_assess": {
                    "returncode": 3,
                    "timed_out": False,
                    "elapsed_seconds": 0.1,
                    "stderr": "hello: rejected\n",
                },
                "hello_run": {
                    "returncode": None,
                    "timed_out": True,
                    "elapsed_seconds": 5.0,
                    "stdout": "",
                    "stderr": "",
                },
            },
            "policy_log": {
                "lines": [
                    "AppleSystemPolicy ASP: Security policy would not allow process: 123, softcandy_hello"
                ]
            },
        },
    )
    write_json(
        failure_case,
        {
            "case_id": "fail_20260526_024",
            "category": "tooling",
            "content_id": "local_macho_binary_launch",
            "symptom": "local binaries time out before main",
            "root_cause": "host execution policy blocks new Mach-O binaries",
            "fix": "restore host binary launch policy before rerunning game tools",
            "validation": "diagnostic must return local_binary_launch_ok before reruns",
        },
    )
    write_json(
        progress,
        {
            "updated_at": "2026-05-26",
            "phase": "fixture",
            "completed": [],
            "current_findings": [
                {
                    "id": "local_binary_launch_blocked",
                    "summary": "blocked",
                    "report": "harness/reports/diagnostic/summary.md",
                }
            ],
            "next_recommended": [
                {"id": "local_binary_launch_recovery", "summary": "recover host policy"}
            ],
        },
    )
    write_json(
        docs_coverage,
        {
            "docs": [
                {
                    "doc_path": "docs/07_Harness工程计划.md",
                    "status": "partial",
                    "coverage": [
                        {
                            "id": "harness-gates",
                            "status": "blocked",
                            "gaps": ["rerun harness"],
                            "blockers": ["local_binary_launch_blocked"],
                        }
                    ],
                },
                {
                    "doc_path": "docs/09_AI_Bot训练计划.md",
                    "status": "partial",
                    "coverage": [
                        {
                            "id": "rl-eval",
                            "status": "blocked",
                            "gaps": ["rerun gym"],
                            "blockers": ["local_binary_launch_blocked"],
                        }
                    ],
                },
            ]
        },
    )
    return {
        "diagnostic": diagnostic,
        "failure_case": failure_case,
        "progress": progress,
        "docs_coverage": docs_coverage,
    }


class LocalBinaryLaunchRecoveryPacketTests(unittest.TestCase):
    def test_build_packet_summarizes_recovery_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = make_fixture(root)

            packet = build_packet(
                paths["diagnostic"],
                paths["failure_case"],
                paths["progress"],
                paths["docs_coverage"],
                root,
            )

            self.assertEqual(packet["decision"], "recovery_required")
            self.assertEqual(packet["diagnostic_decision"], "local_binary_launch_blocked")
            self.assertEqual(packet["failure_case"]["case_id"], "fail_20260526_024")
            self.assertEqual(packet["blocked_doc_count"], 2)
            self.assertTrue(any("diagnose_local_binary_launch.py" in command for command in packet["post_recovery_commands"]))
            self.assertTrue(any("local_binary_launch_ok" in action for action in packet["recovery_actions"]))
            self.assertTrue(any("not gameplay" in item.lower() for item in packet["limitations"]))

    def test_cli_writes_markdown_and_json_packet(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = make_fixture(root)
            out = root / "summary.md"
            json_out = root / "packet.json"

            result = subprocess.run(
                [
                    sys.executable,
                    str(PACKET),
                    "--diagnostic",
                    str(paths["diagnostic"]),
                    "--failure-case",
                    str(paths["failure_case"]),
                    "--progress",
                    str(paths["progress"]),
                    "--docs-coverage",
                    str(paths["docs_coverage"]),
                    "--repo-root",
                    str(root),
                    "--out",
                    str(out),
                    "--json-out",
                    str(json_out),
                ],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            markdown = out.read_text(encoding="utf-8")
            self.assertIn("Local Binary Launch Recovery Packet", markdown)
            self.assertIn("recovery_required", markdown)
            self.assertIn("Ordered Post-Recovery Validation", markdown)
            self.assertEqual(json.loads(json_out.read_text(encoding="utf-8"))["decision"], "recovery_required")


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
