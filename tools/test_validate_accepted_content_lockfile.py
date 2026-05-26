#!/usr/bin/env python3
"""Regression tests for accepted content lockfile validation.

Run with:
    python3 tools/test_validate_accepted_content_lockfile.py
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
VALIDATOR = SCRIPT_DIR / "validate_accepted_content_lockfile.py"

sys.path.insert(0, str(SCRIPT_DIR))

from validate_accepted_content_lockfile import REQUIRED_RUN_IDS, build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str = "fixture\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def manual_review(candidate_id: str, content_hash: str, *, low_rating: bool = False) -> dict:
    runs = []
    for index, run_id in enumerate(sorted(REQUIRED_RUN_IDS)):
        rating = 2 if low_rating and index == 0 else 4
        runs.append(
            {
                "run_id": run_id,
                "gate_decision": "playtest_pass",
                "manual_review": {
                    "fun_rating": rating,
                    "clarity_rating": 4,
                    "difficulty_rating": 4,
                    "projectile_readability": 4,
                    "hit_feedback": 4,
                    "xp_pickup_rhythm": 4,
                    "boss_spawn_clarity": 4,
                    "death_reason_clarity": 4,
                    "notes": f"Concrete observation for {run_id}.",
                    "tags": ["fixture"],
                    "next_actions": ["Keep this run in the acceptance evidence set."],
                },
            }
        )
    return {
        "template_version": 1,
        "candidate_id": candidate_id,
        "content_hash": content_hash,
        "reviewer": "human-reviewer-fixture",
        "reviewed_at": "2026-05-26",
        "summary": "Fixture manual playtest review with nine completed runs.",
        "acceptance_decision": "accept_candidate",
        "runs": runs,
    }


def make_lock_tree(root: Path, *, low_rating: bool = False, blocked: bool = False) -> Path:
    candidate_id = "base-demo-smoke"
    content_hash = "fnv1a64:0123456789abcdef"
    accepted_dir = root / "harness/accepted_content"
    candidate_dir = accepted_dir / candidate_id
    write_text(candidate_dir / "characters/jar-keeper.json", "{}\n")
    review_file = root / "harness/playtest_reviews/base-demo-smoke.json"
    write_json(review_file, manual_review(candidate_id, content_hash, low_rating=low_rating))
    gate_file = candidate_dir / "acceptance_gate.json"
    write_json(
        gate_file,
        {
            "candidate_id": candidate_id,
            "decision": "accept_candidate",
            "category": "human_playtest_passed",
            "content_hash": content_hash,
            "manual_review_file": str(review_file.relative_to(root)),
            "completed_run_count": 9,
            "average_rating": 4.0 if not low_rating else 3.75,
        },
    )
    lock_file = accepted_dir / "accepted_content.lock.json"
    entry = {
        "id": candidate_id,
        "source": str(candidate_dir.relative_to(root)),
        "runtime_content_dir": str(candidate_dir.relative_to(root)),
        "content_hash": content_hash,
        "object_count": 14,
        "acceptance_gate": str(gate_file.relative_to(root)),
        "manual_review_file": str(review_file.relative_to(root)),
        "completed_run_count": 9,
        "average_rating": 4.0 if not low_rating else 3.75,
        "status": "blocked" if blocked else "locked",
        "errors": ["fixture blocked entry"] if blocked else [],
    }
    write_json(
        lock_file,
        {
            "lock_version": 1,
            "status": "blocked" if blocked else "locked",
            "accepted_dir": str(accepted_dir.relative_to(root)),
            "lock_file": str(lock_file.relative_to(root)),
            "runtime_content_root": str(accepted_dir.relative_to(root)),
            "candidate_count": 1,
            "locked_count": 0 if blocked else 1,
            "blocked_count": 1 if blocked else 0,
            "entries": [entry],
            "errors": ["accepted candidate `base-demo-smoke` cannot be version-locked"] if blocked else [],
        },
    )
    return lock_file


class AcceptedContentLockfileValidatorTests(unittest.TestCase):
    def test_valid_lockfile_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            lock_file = make_lock_tree(root)

            report = build_report(lock_file, root)

            self.assertEqual(report["decision"], "accepted_content_lockfile_valid")
            self.assertEqual(report["errors"], [])
            self.assertEqual(report["locked_count"], 1)

    def test_low_manual_rating_invalidates_lockfile(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            lock_file = make_lock_tree(root, low_rating=True)

            report = build_report(lock_file, root)

            self.assertEqual(report["decision"], "accepted_content_lockfile_invalid")
            self.assertTrue(any("at least 3" in error for error in report["errors"]))

    def test_gate_hash_mismatch_invalidates_lockfile(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            lock_file = make_lock_tree(root)
            payload = json.loads((root / "harness/accepted_content/base-demo-smoke/acceptance_gate.json").read_text())
            payload["content_hash"] = "fnv1a64:badbadbad"
            write_json(root / "harness/accepted_content/base-demo-smoke/acceptance_gate.json", payload)

            report = build_report(lock_file, root)

            self.assertEqual(report["decision"], "accepted_content_lockfile_invalid")
            self.assertTrue(any("content_hash" in error for error in report["errors"]))

    def test_blocked_lockfile_can_be_structurally_valid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            lock_file = make_lock_tree(root, blocked=True)

            report = build_report(lock_file, root)

            self.assertEqual(report["decision"], "accepted_content_lockfile_blocked")
            self.assertEqual(report["blocked_count"], 1)

    def test_empty_blocked_lockfile_records_no_accepted_content_yet(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            accepted_dir = root / "harness/accepted_content"
            accepted_dir.mkdir(parents=True)
            lock_file = accepted_dir / "accepted_content.lock.json"
            write_json(
                lock_file,
                {
                    "lock_version": 1,
                    "status": "blocked",
                    "accepted_dir": "harness/accepted_content",
                    "lock_file": "harness/accepted_content/accepted_content.lock.json",
                    "runtime_content_root": "harness/accepted_content",
                    "candidate_count": 0,
                    "locked_count": 0,
                    "blocked_count": 0,
                    "entries": [],
                    "errors": ["no accepted content has passed human review yet"],
                },
            )

            report = build_report(lock_file, root)

            self.assertEqual(report["decision"], "accepted_content_lockfile_blocked")
            self.assertEqual(report["candidate_count"], 0)

    def test_cli_writes_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            lock_file = make_lock_tree(root)
            report_path = root / "report.json"
            markdown_path = root / "summary.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(lock_file),
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
            payload = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["decision"], "accepted_content_lockfile_valid")
            self.assertIn("Accepted Content Lockfile Validation", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
