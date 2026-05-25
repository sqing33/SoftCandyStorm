#!/usr/bin/env python3
"""Regression tests for release candidate evidence validation.

Run with:
    python3 tools/test_validate_release_candidate_evidence.py
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
VALIDATOR = SCRIPT_DIR / "validate_release_candidate_evidence.py"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_release_candidate_evidence import REQUIRED_GATES, build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str = "evidence\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_manifest(root: Path, *, blocked_gate: str | None = None, synthetic_gate: str | None = None) -> Path:
    evidence_path = root / "evidence" / "gate.md"
    write_text(evidence_path)
    gates = []
    for gate_id in REQUIRED_GATES:
        status = "blocked" if gate_id == blocked_gate else "pass"
        gates.append(
            {
                "id": gate_id,
                "status": status,
                "summary": f"{gate_id} evidence",
                "evidence_paths": [str(evidence_path.relative_to(root))],
                "synthetic": gate_id == synthetic_gate,
            }
        )
    manifest = root / "release" / "candidate.json"
    write_json(
        manifest,
        {
            "candidate_id": "fixture-rc",
            "generated_at": "2026-05-26",
            "release_stage": "fixture",
            "summary": "Fixture release candidate.",
            "gates": gates,
        },
    )
    return manifest


class ReleaseCandidateEvidenceValidatorTests(unittest.TestCase):
    def test_all_required_gates_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = make_manifest(root)

            report = build_report(manifest, root)

            self.assertEqual(report["decision"], "release_candidate_ready")
            self.assertEqual(report["missing_gates"], [])
            self.assertEqual(report["blockers"], [])

    def test_blocked_gate_prevents_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = make_manifest(root, blocked_gate="compile")

            report = build_report(manifest, root)

            self.assertEqual(report["decision"], "release_candidate_not_ready")
            self.assertTrue(any("compile" in blocker for blocker in report["blockers"]))

    def test_synthetic_pass_is_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = make_manifest(root, synthetic_gate="manual_playtest")

            report = build_report(manifest, root)

            self.assertEqual(report["decision"], "release_candidate_not_ready")
            self.assertTrue(any("synthetic" in error for error in report["errors"]))

    def test_missing_gate_is_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = make_manifest(root)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["gates"] = [gate for gate in payload["gates"] if gate["id"] != "replay_regression"]
            write_json(manifest, payload)

            report = build_report(manifest, root)

            self.assertEqual(report["decision"], "release_candidate_not_ready")
            self.assertIn("replay_regression", report["missing_gates"])

    def test_cli_writes_not_ready_report_with_allow_flag(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = make_manifest(root, blocked_gate="compile")
            report_path = root / "report.json"
            markdown_path = root / "summary.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(manifest),
                    "--repo-root",
                    str(root),
                    "--report",
                    str(report_path),
                    "--markdown",
                    str(markdown_path),
                    "--allow-not-ready",
                ],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                json.loads(report_path.read_text(encoding="utf-8"))["decision"],
                "release_candidate_not_ready",
            )
            self.assertIn("Release Candidate Evidence Validation", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
