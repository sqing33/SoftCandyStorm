#!/usr/bin/env python3
"""Regression tests for asset audio technical probes.

Run with:
    python3 harness/asset_review/test_audit_asset_audio_technical.py
"""

from __future__ import annotations

import json
import math
import struct
import subprocess
import sys
import tempfile
import unittest
import wave
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
PROBE = SCRIPT_DIR / "audit_asset_audio_technical.py"

sys.path.insert(0, str(SCRIPT_DIR))

from audit_asset_audio_technical import build_report  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_wav(path: Path, *, duration_seconds: float = 1.0, sample_rate: int = 44100, channels: int = 1) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame_count = int(duration_seconds * sample_rate)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(channels)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        frames = bytearray()
        for frame in range(frame_count):
            value = int(1000 * math.sin(2 * math.pi * 440 * frame / sample_rate))
            packed = struct.pack("<h", value)
            frames.extend(packed * channels)
        handle.writeframes(bytes(frames))


def make_batch(root: Path, *, missing_audio: bool = False, duration_seconds: float = 1.0) -> Path:
    batch = root / "asset" / "generated_candidates" / "fixture_audio_batch"
    audio_path = batch / "audio" / "voice.wav"
    if not missing_audio:
        write_wav(audio_path, duration_seconds=duration_seconds)
    write_json(
        batch / "metadata" / "manifest.json",
        {
            "batch_id": "fixture_audio_batch",
            "generated_at": "2026-05-26",
            "project_rules": {
                "candidate_only": True,
                "accepted_content": False,
                "runtime_integrated": False,
                "required_next_steps": ["human listening review"],
            },
            "assets": [
                {
                    "id": "voice_fixture",
                    "type": "speech",
                    "path": "audio/voice.wav",
                    "duration_seconds": duration_seconds,
                    "sample_rate_hz": 44100,
                    "channels": 1,
                    "qa_status": "needs_listening_review",
                    "qa_notes": ["Fixture audio."],
                }
            ],
        },
    )
    return batch


class AssetAudioTechnicalProbeTests(unittest.TestCase):
    def test_wav_manifest_metadata_matches(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            batch = make_batch(Path(temp_dir))

            report = build_report(batch)

            self.assertEqual(report["decision"], "asset_audio_technical_probe_valid")
            self.assertEqual(report["audio_asset_count"], 1)
            self.assertEqual(report["errors"], [])

    def test_missing_audio_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            batch = make_batch(Path(temp_dir), missing_audio=True)

            report = build_report(batch)

            self.assertEqual(report["decision"], "asset_audio_technical_probe_invalid")
            self.assertTrue(any("does not exist" in error for error in report["errors"]))

    def test_duration_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            batch = make_batch(Path(temp_dir), duration_seconds=1.0)
            manifest = batch / "metadata" / "manifest.json"
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["assets"][0]["duration_seconds"] = 2.0
            write_json(manifest, payload)

            report = build_report(batch)

            self.assertEqual(report["decision"], "asset_audio_technical_probe_invalid")
            self.assertTrue(any("recorded duration" in error for error in report["errors"]))

    def test_long_voice_is_warning_not_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            batch = make_batch(Path(temp_dir), duration_seconds=7.0)

            report = build_report(batch)

            self.assertEqual(report["decision"], "asset_audio_technical_probe_valid")
            self.assertTrue(any("voice duration" in warning for warning in report["warnings"]))

    def test_cli_writes_report_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            batch = make_batch(root)
            report_path = root / "report.json"
            markdown_path = root / "summary.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(PROBE),
                    str(batch),
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
            self.assertEqual(
                json.loads(report_path.read_text(encoding="utf-8"))["decision"],
                "asset_audio_technical_probe_valid",
            )
            self.assertIn("Asset Audio Technical Probe", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
