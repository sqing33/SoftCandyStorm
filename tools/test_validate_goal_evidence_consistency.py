#!/usr/bin/env python3
"""Regression tests for Goal evidence consistency validation.

Run with:
    python3 tools/test_validate_goal_evidence_consistency.py
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
VALIDATOR = SCRIPT_DIR / "validate_goal_evidence_consistency.py"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_goal_evidence_consistency import (  # noqa: E402
    BINARY_DEPENDENT_RELEASE_GATES,
    BINARY_FAILURE_CASE,
    build_report,
)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str = "evidence\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_fixture(root: Path) -> dict[str, Path]:
    write_text(root / BINARY_FAILURE_CASE, "{}\n")
    write_text(root / "harness" / "playtest" / "runtime_manual_review_pack.md")
    write_text(root / "harness" / "reports" / "asset_provenance" / "summary.md")

    docs_path = root / "harness" / "docs_implementation_coverage.json"
    write_json(
        docs_path,
        {
            "updated_at": "2026-05-26",
            "scope": "fixture",
            "summary": "fixture",
            "docs": [
                {
                    "doc_id": "00",
                    "doc_path": "docs/00_index.md",
                    "status": "complete",
                    "summary": "complete",
                    "coverage": [
                        {
                            "id": "docs-index",
                            "requirement": "fixture",
                            "status": "complete",
                            "evidence": [BINARY_FAILURE_CASE],
                            "gaps": [],
                        }
                    ],
                },
                {
                    "doc_id": "02",
                    "doc_path": "docs/02_核心玩法规格.md",
                    "status": "partial",
                    "summary": "blocked by local binary launch",
                    "coverage": [
                        {
                            "id": "core-loop",
                            "requirement": "fixture",
                            "status": "blocked",
                            "evidence": [BINARY_FAILURE_CASE],
                            "gaps": ["needs runtime verification"],
                            "blockers": ["local_binary_launch_blocked"],
                        }
                    ],
                },
                {
                    "doc_id": "11",
                    "doc_path": "docs/11_测试指标与上线门禁.md",
                    "status": "partial",
                    "summary": "manual playtest pending",
                    "coverage": [
                        {
                            "id": "release-gates",
                            "requirement": "fixture",
                            "status": "blocked",
                            "evidence": ["harness/playtest/runtime_manual_review_pack.md"],
                            "gaps": ["needs human playtest"],
                            "blockers": ["manual_playtest_still_pending"],
                        }
                    ],
                },
            ],
        },
    )

    roadmap_path = root / "harness" / "roadmap_audit" / "roadmap_phase_audit.json"
    write_json(
        roadmap_path,
        {
            "report_version": 1,
            "updated_at": "2026-05-26",
            "scope": "fixture",
            "summary": "fixture",
            "phases": [
                {
                    "phase": 0,
                    "title": "docs",
                    "status": "complete",
                    "goal": "fixture",
                    "acceptance": ["fixture"],
                    "evidence": [BINARY_FAILURE_CASE],
                    "gaps": [],
                    "blockers": [],
                    "next_actions": [],
                },
                {
                    "phase": 1,
                    "title": "core",
                    "status": "blocked",
                    "goal": "fixture",
                    "acceptance": ["fixture"],
                    "evidence": [BINARY_FAILURE_CASE],
                    "gaps": ["needs binary"],
                    "blockers": ["local_binary_launch_blocked"],
                    "next_actions": ["recover binary launch"],
                },
                {
                    "phase": 2,
                    "title": "runtime",
                    "status": "blocked",
                    "goal": "fixture",
                    "acceptance": ["fixture"],
                    "evidence": ["harness/playtest/runtime_manual_review_pack.md"],
                    "gaps": ["needs playtest"],
                    "blockers": ["local_binary_launch_blocked", "manual_playtest_still_pending"],
                    "next_actions": ["run human playtest"],
                },
            ],
        },
    )

    progress_path = root / "harness" / "progress.json"
    write_json(
        progress_path,
        {
            "updated_at": "2026-05-26",
            "phase": "fixture",
            "completed": [],
            "current_findings": [
                {
                    "id": "local_binary_launch_blocked",
                    "summary": "fixture",
                    "report": BINARY_FAILURE_CASE,
                },
                {
                    "id": "manual_playtest_still_pending",
                    "summary": "fixture",
                    "report": "harness/playtest/runtime_manual_review_pack.md",
                },
            ],
            "next_recommended": [],
        },
    )

    rc_path = root / "harness" / "release" / "current_local_rc_evidence.json"
    gates = [
        {
            "id": gate_id,
            "status": "blocked",
            "summary": "blocked by local binary launch",
            "evidence_paths": [BINARY_FAILURE_CASE],
            "synthetic": False,
        }
        for gate_id in BINARY_DEPENDENT_RELEASE_GATES
    ]
    gates.extend(
        [
            {
                "id": "manual_playtest",
                "status": "waiting",
                "summary": "needs human playtest",
                "evidence_paths": ["harness/playtest/runtime_manual_review_pack.md"],
                "synthetic": False,
            },
            {
                "id": "asset_manual_review",
                "status": "waiting",
                "summary": "needs human asset review",
                "evidence_paths": [],
                "synthetic": False,
            },
            {
                "id": "story_codex_review",
                "status": "waiting",
                "summary": "needs human story review",
                "evidence_paths": [],
                "synthetic": False,
            },
            {
                "id": "telemetry_privacy",
                "status": "waiting",
                "summary": "needs privacy review",
                "evidence_paths": [],
                "synthetic": False,
            },
            {
                "id": "asset_provenance",
                "status": "pass",
                "summary": "candidate provenance only",
                "evidence_paths": ["harness/reports/asset_provenance/summary.md"],
                "synthetic": False,
            },
        ]
    )
    write_json(
        rc_path,
        {
            "candidate_id": "fixture",
            "generated_at": "2026-05-26",
            "release_stage": "prototype-local",
            "summary": "fixture",
            "gates": gates,
        },
    )

    package_path = root / "harness" / "release" / "current_local_package_manifest.json"
    write_json(
        package_path,
        {
            "package_id": "fixture",
            "candidate_id": "fixture",
            "release_stage": "prototype-local",
            "package_status": "blocked",
            "summary": "fixture",
            "blockers": ["local_binary_launch_blocked", "release_candidate_not_ready"],
            "checks": [],
            "package_items": [],
        },
    )

    return {
        "docs": docs_path,
        "roadmap": roadmap_path,
        "progress": progress_path,
        "rc": rc_path,
        "package": package_path,
    }


class GoalEvidenceConsistencyTests(unittest.TestCase):
    def test_consistent_not_ready_ledgers_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = make_fixture(root)

            report = build_report(
                paths["docs"],
                paths["roadmap"],
                paths["progress"],
                paths["rc"],
                paths["package"],
                root,
            )

            self.assertEqual(report["decision"], "goal_evidence_consistent")
            self.assertEqual(report["errors"], [])

    def test_missing_progress_binary_blocker_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = make_fixture(root)
            payload = json.loads(paths["progress"].read_text(encoding="utf-8"))
            payload["current_findings"] = [
                item for item in payload["current_findings"] if item["id"] != "local_binary_launch_blocked"
            ]
            write_json(paths["progress"], payload)

            report = build_report(
                paths["docs"],
                paths["roadmap"],
                paths["progress"],
                paths["rc"],
                paths["package"],
                root,
            )

            self.assertEqual(report["decision"], "goal_evidence_inconsistent")
            self.assertTrue(any("progress.current_findings" in error for error in report["errors"]))

    def test_binary_gate_pass_while_blocked_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = make_fixture(root)
            payload = json.loads(paths["rc"].read_text(encoding="utf-8"))
            payload["gates"][0]["status"] = "pass"
            write_json(paths["rc"], payload)

            report = build_report(
                paths["docs"],
                paths["roadmap"],
                paths["progress"],
                paths["rc"],
                paths["package"],
                root,
            )

            self.assertEqual(report["decision"], "goal_evidence_inconsistent")
            self.assertTrue(any("must remain `blocked`" in error for error in report["errors"]))

    def test_ready_package_while_rc_not_ready_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = make_fixture(root)
            payload = json.loads(paths["package"].read_text(encoding="utf-8"))
            payload["package_status"] = "ready"
            payload["blockers"] = []
            write_json(paths["package"], payload)

            report = build_report(
                paths["docs"],
                paths["roadmap"],
                paths["progress"],
                paths["rc"],
                paths["package"],
                root,
            )

            self.assertEqual(report["decision"], "goal_evidence_inconsistent")
            self.assertTrue(any("package cannot be ready" in error for error in report["errors"]))

    def test_cli_writes_report_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = make_fixture(root)
            report_path = root / "report.json"
            markdown_path = root / "summary.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--docs-coverage",
                    str(paths["docs"]),
                    "--roadmap-audit",
                    str(paths["roadmap"]),
                    "--progress",
                    str(paths["progress"]),
                    "--release-candidate",
                    str(paths["rc"]),
                    "--release-package",
                    str(paths["package"]),
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
            self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["decision"], "goal_evidence_consistent")
            self.assertIn("Goal Evidence Consistency", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
