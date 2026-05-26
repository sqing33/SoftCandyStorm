#!/usr/bin/env python3
"""Regression tests for release package manifest validation.

Run with:
    python3 tools/test_validate_release_package_manifest.py
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
VALIDATOR = SCRIPT_DIR / "validate_release_package_manifest.py"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_release_package_manifest import (  # noqa: E402
    REQUIRED_READY_CHECKS,
    REQUIRED_READY_ITEM_KINDS,
    build_report,
)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str = "evidence\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sha256_fixture(index: int) -> str:
    return f"{index:064x}"


def make_ready_manifest(root: Path) -> Path:
    candidate_evidence = root / "harness/release/current_local_rc_evidence.json"
    write_json(candidate_evidence, {"candidate_id": "fixture-rc"})
    package_items = []
    for index, kind in enumerate(sorted(REQUIRED_READY_ITEM_KINDS), start=1):
        path = root / "dist" / f"{kind}.txt"
        write_text(path, kind)
        package_items.append(
            {
                "id": kind,
                "kind": kind,
                "path": str(path.relative_to(root)),
                "sha256": sha256_fixture(index),
                "synthetic": False,
            }
        )
    checks = []
    for check_id in sorted(REQUIRED_READY_CHECKS):
        path = root / "evidence" / f"{check_id}.md"
        write_text(path, check_id)
        checks.append(
            {
                "id": check_id,
                "status": "pass",
                "summary": f"{check_id} passed.",
                "evidence_paths": [str(path.relative_to(root))],
                "synthetic": False,
            }
        )
    manifest = root / "harness/release/package.json"
    write_json(
        manifest,
        {
            "manifest_version": 1,
            "package_id": "fixture-package",
            "candidate_id": "fixture-rc",
            "created_at": "2026-05-26",
            "release_stage": "fixture",
            "package_status": "ready",
            "summary": "Fixture package manifest.",
            "candidate_evidence": str(candidate_evidence.relative_to(root)),
            "package_items": package_items,
            "checks": checks,
            "blockers": [],
            "next_actions": [],
        },
    )
    return manifest


def make_blocked_manifest(root: Path) -> Path:
    candidate_evidence = root / "harness/release/current_local_rc_evidence.json"
    failure_case = root / "harness/failed_cases/fail_local_binary.json"
    write_json(candidate_evidence, {"candidate_id": "fixture-rc"})
    write_json(failure_case, {"case_id": "fail_local_binary"})
    manifest = root / "harness/release/package.json"
    write_json(
        manifest,
        {
            "manifest_version": 1,
            "package_id": "fixture-package",
            "candidate_id": "fixture-rc",
            "created_at": "2026-05-26",
            "release_stage": "fixture",
            "package_status": "blocked",
            "summary": "Fixture package is blocked before archive creation.",
            "candidate_evidence": str(candidate_evidence.relative_to(root)),
            "package_items": [],
            "checks": [
                {
                    "id": "package_created",
                    "status": "blocked",
                    "summary": "Local binary launch is blocked, so no package can be created.",
                    "evidence_paths": [str(failure_case.relative_to(root))],
                    "synthetic": False,
                }
            ],
            "blockers": ["local binary launch blocked"],
            "next_actions": ["restore binary launch, then create release archive"],
        },
    )
    return manifest


class ReleasePackageManifestValidatorTests(unittest.TestCase):
    def test_ready_manifest_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = make_ready_manifest(root)

            report = build_report(manifest, root)

            self.assertEqual(report["decision"], "release_package_ready")
            self.assertEqual(report["errors"], [])
            self.assertEqual(report["blockers"], [])

    def test_blocked_manifest_is_honest_not_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = make_blocked_manifest(root)

            report = build_report(manifest, root)

            self.assertEqual(report["decision"], "release_package_not_ready")
            self.assertEqual(report["errors"], [])
            self.assertTrue(any("package_status" in blocker for blocker in report["blockers"]))

    def test_ready_manifest_missing_item_is_not_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = make_ready_manifest(root)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["package_items"] = [
                item for item in payload["package_items"] if item["kind"] != "release_archive"
            ]
            write_json(manifest, payload)

            report = build_report(manifest, root)

            self.assertEqual(report["decision"], "release_package_not_ready")
            self.assertIn("release_archive", report["missing_ready_item_kinds"])

    def test_missing_item_path_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = make_ready_manifest(root)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["package_items"][0]["path"] = "missing/artifact.zip"
            write_json(manifest, payload)

            report = build_report(manifest, root)

            self.assertEqual(report["decision"], "release_package_manifest_invalid")
            self.assertTrue(any("does not exist" in error for error in report["errors"]))

    def test_ready_manifest_bad_sha256_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = make_ready_manifest(root)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["package_items"][0]["sha256"] = "not-a-digest"
            write_json(manifest, payload)

            report = build_report(manifest, root)

            self.assertEqual(report["decision"], "release_package_manifest_invalid")
            self.assertTrue(any("64-character hexadecimal" in error for error in report["errors"]))

    def test_synthetic_pass_check_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = make_ready_manifest(root)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["checks"][0]["synthetic"] = True
            write_json(manifest, payload)

            report = build_report(manifest, root)

            self.assertEqual(report["decision"], "release_package_manifest_invalid")
            self.assertTrue(any("synthetic evidence" in error for error in report["errors"]))

    def test_cli_allow_not_ready_writes_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = make_blocked_manifest(root)
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
                "release_package_not_ready",
            )
            self.assertIn("Release Package Manifest Validation", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
