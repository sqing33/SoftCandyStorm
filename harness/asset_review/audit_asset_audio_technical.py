#!/usr/bin/env python3
"""Audit generated asset candidate audio technical metadata.

This probe compares recorded candidate manifest metadata against local audio
files. It is deliberately not a human loudness/listening gate; it only catches
missing files, stale duration/sample-rate/channel metadata, and obvious duration
shape issues before a reviewer listens.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import wave
from pathlib import Path
from typing import Any


AUDIO_TYPES = {"audio", "music", "speech", "sound", "sfx", "voice"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}
DEFAULT_DURATION_TOLERANCE_SECONDS = 0.15
DEFAULT_MAX_EFFECT_SECONDS = 12.0
DEFAULT_MAX_VOICE_SECONDS = 5.0
DEFAULT_MIN_SAMPLE_RATE_HZ = 32000


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def as_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def parse_float(value: Any) -> float | None:
    if not is_nonempty_string(value):
        return None
    try:
        return float(str(value))
    except ValueError:
        return None


def parse_int(value: Any) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if not is_nonempty_string(value):
        return None
    try:
        return int(str(value))
    except ValueError:
        return None


def discover_manifests(root: Path) -> list[Path]:
    if root.name == "manifest.json" and root.exists():
        return [root]
    if (root / "metadata" / "manifest.json").exists():
        return [root / "metadata" / "manifest.json"]
    return sorted(root.glob("*/metadata/manifest.json"))


def batch_dir_for_manifest(manifest_path: Path) -> Path:
    return manifest_path.parents[1]


def is_audio_asset(asset: Any) -> bool:
    if not isinstance(asset, dict):
        return False
    asset_type = str(asset.get("type", "")).lower()
    if asset_type in AUDIO_TYPES:
        return True
    for field in ("path", "source_path", "processed_path"):
        value = asset.get(field)
        if is_nonempty_string(value) and Path(str(value)).suffix.lower() in AUDIO_EXTENSIONS:
            return True
    return False


def asset_audio_path(batch_dir: Path, asset: dict[str, Any]) -> tuple[str | None, Path | None]:
    for field in ("path", "processed_path", "source_path"):
        value = asset.get(field)
        if not is_nonempty_string(value):
            continue
        path = batch_dir / str(value)
        if path.suffix.lower() in AUDIO_EXTENSIONS:
            return field, path
    return None, None


def probe_wav(path: Path) -> dict[str, Any]:
    with wave.open(str(path), "rb") as handle:
        frame_count = handle.getnframes()
        sample_rate = handle.getframerate()
        channels = handle.getnchannels()
        sample_width = handle.getsampwidth()
    return {
        "probe": "wave",
        "codec_name": "pcm",
        "duration_seconds": round(frame_count / sample_rate, 6) if sample_rate else None,
        "sample_rate_hz": sample_rate,
        "channels": channels,
        "sample_width_bytes": sample_width,
        "bitrate_bps": None,
    }


def probe_ffprobe(path: Path, ffprobe_path: str) -> tuple[dict[str, Any] | None, str | None]:
    result = subprocess.run(
        [
            ffprobe_path,
            "-v",
            "error",
            "-show_entries",
            "stream=codec_name,sample_rate,channels",
            "-show_entries",
            "format=duration,bit_rate",
            "-of",
            "json",
            str(path),
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        return None, result.stderr.strip() or result.stdout.strip()
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return None, str(exc)
    streams = [stream for stream in payload.get("streams", []) if isinstance(stream, dict)]
    stream = streams[0] if streams else {}
    fmt = payload.get("format") if isinstance(payload.get("format"), dict) else {}
    duration = parse_float(fmt.get("duration"))
    bitrate = parse_float(fmt.get("bit_rate"))
    sample_rate = parse_int(stream.get("sample_rate"))
    channels = parse_int(stream.get("channels"))
    return (
        {
            "probe": "ffprobe",
            "codec_name": stream.get("codec_name"),
            "duration_seconds": round(duration, 6) if duration is not None else None,
            "sample_rate_hz": sample_rate,
            "channels": channels,
            "bitrate_bps": int(bitrate) if bitrate is not None else None,
        },
        None,
    )


def probe_audio(path: Path, ffprobe_path: str | None) -> tuple[dict[str, Any] | None, str | None]:
    if path.suffix.lower() == ".wav":
        try:
            return probe_wav(path), None
        except wave.Error as exc:
            return None, str(exc)
    if ffprobe_path is None:
        return None, "ffprobe is required for non-wav audio files"
    return probe_ffprobe(path, ffprobe_path)


def compare_manifest_metadata(
    asset_id: str,
    asset: dict[str, Any],
    probe: dict[str, Any],
    *,
    duration_tolerance_seconds: float,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    recorded_duration = as_number(asset.get("duration_seconds"))
    actual_duration = as_number(probe.get("duration_seconds"))
    if recorded_duration is not None and actual_duration is not None:
        delta = abs(recorded_duration - actual_duration)
        if delta > duration_tolerance_seconds:
            errors.append(
                f"{asset_id}: recorded duration {recorded_duration:g}s differs from file {actual_duration:g}s by {delta:g}s"
            )
    recorded_sample_rate = asset.get("sample_rate_hz")
    actual_sample_rate = probe.get("sample_rate_hz")
    if isinstance(recorded_sample_rate, int) and isinstance(actual_sample_rate, int):
        if recorded_sample_rate != actual_sample_rate:
            errors.append(
                f"{asset_id}: recorded sample_rate_hz {recorded_sample_rate} differs from file {actual_sample_rate}"
            )
    recorded_channels = asset.get("channels")
    actual_channels = probe.get("channels")
    if isinstance(recorded_channels, int) and isinstance(actual_channels, int):
        if recorded_channels != actual_channels:
            errors.append(f"{asset_id}: recorded channels {recorded_channels} differs from file {actual_channels}")
    if actual_duration is None:
        warnings.append(f"{asset_id}: probe did not report duration")
    if actual_sample_rate is None:
        warnings.append(f"{asset_id}: probe did not report sample rate")
    return errors, warnings


def duration_shape_warnings(
    asset_id: str,
    asset: dict[str, Any],
    probe: dict[str, Any],
    *,
    max_effect_seconds: float,
    max_voice_seconds: float,
    min_sample_rate_hz: int,
) -> list[str]:
    warnings: list[str] = []
    duration = as_number(probe.get("duration_seconds"))
    sample_rate = probe.get("sample_rate_hz")
    asset_type = str(asset.get("type", "")).lower()
    qa_status = str(asset.get("qa_status", "")).lower()
    path_text = str(asset.get("path", asset.get("source_path", ""))).lower()
    is_source_repair = qa_status == "repair_trim" or asset_id.endswith("_source") or path_text.startswith("music/")

    if isinstance(sample_rate, int) and sample_rate < min_sample_rate_hz:
        warnings.append(f"{asset_id}: sample rate {sample_rate} is below {min_sample_rate_hz}")
    if duration is None:
        return warnings
    if asset_type in {"speech", "voice"} and duration > max_voice_seconds:
        warnings.append(f"{asset_id}: voice duration {duration:g}s is above {max_voice_seconds:g}s")
    if asset_type in {"music", "sound", "sfx", "audio"} and duration > max_effect_seconds and not is_source_repair:
        warnings.append(f"{asset_id}: effect duration {duration:g}s is above {max_effect_seconds:g}s")
    return warnings


def audit_manifest(
    manifest_path: Path,
    *,
    ffprobe_path: str | None,
    duration_tolerance_seconds: float,
    max_effect_seconds: float,
    max_voice_seconds: float,
    min_sample_rate_hz: int,
) -> dict[str, Any]:
    payload = load_json_object(manifest_path)
    batch_dir = batch_dir_for_manifest(manifest_path)
    errors: list[str] = []
    warnings: list[str] = []
    audio_reports: list[dict[str, Any]] = []
    assets = payload.get("assets")
    if not isinstance(assets, list):
        errors.append("manifest.assets must be a list")
        assets = []

    for index, asset in enumerate(assets):
        if not is_audio_asset(asset):
            continue
        asset_id = str(asset.get("id") if is_nonempty_string(asset.get("id")) else f"assets[{index}]")
        path_field, path = asset_audio_path(batch_dir, asset)
        item_report: dict[str, Any] = {
            "id": asset_id,
            "type": asset.get("type"),
            "path_field": path_field,
            "path": str(path.relative_to(batch_dir)) if path is not None else None,
            "exists": path.exists() if path is not None else False,
            "probe": None,
        }
        if path is None:
            errors.append(f"{asset_id}: no audio path found")
            audio_reports.append(item_report)
            continue
        if not path.exists():
            errors.append(f"{asset_id}: audio path does not exist: {path.relative_to(batch_dir)}")
            audio_reports.append(item_report)
            continue
        probe, probe_error = probe_audio(path, ffprobe_path)
        if probe is None:
            errors.append(f"{asset_id}: audio probe failed: {probe_error}")
            audio_reports.append(item_report)
            continue
        item_report["probe"] = probe
        metadata_errors, metadata_warnings = compare_manifest_metadata(
            asset_id,
            asset,
            probe,
            duration_tolerance_seconds=duration_tolerance_seconds,
        )
        errors.extend(metadata_errors)
        warnings.extend(metadata_warnings)
        warnings.extend(
            duration_shape_warnings(
                asset_id,
                asset,
                probe,
                max_effect_seconds=max_effect_seconds,
                max_voice_seconds=max_voice_seconds,
                min_sample_rate_hz=min_sample_rate_hz,
            )
        )
        audio_reports.append(item_report)

    return {
        "batch_id": payload.get("batch_id", batch_dir.name),
        "manifest": str(manifest_path),
        "audio_asset_count": len(audio_reports),
        "errors": errors,
        "warnings": warnings,
        "audio_assets": audio_reports,
    }


def build_report(
    root: Path,
    *,
    ffprobe_path: str | None = None,
    duration_tolerance_seconds: float = DEFAULT_DURATION_TOLERANCE_SECONDS,
    max_effect_seconds: float = DEFAULT_MAX_EFFECT_SECONDS,
    max_voice_seconds: float = DEFAULT_MAX_VOICE_SECONDS,
    min_sample_rate_hz: int = DEFAULT_MIN_SAMPLE_RATE_HZ,
) -> dict[str, Any]:
    ffprobe_path = ffprobe_path or shutil.which("ffprobe")
    manifests = discover_manifests(root)
    batches = [
        audit_manifest(
            manifest,
            ffprobe_path=ffprobe_path,
            duration_tolerance_seconds=duration_tolerance_seconds,
            max_effect_seconds=max_effect_seconds,
            max_voice_seconds=max_voice_seconds,
            min_sample_rate_hz=min_sample_rate_hz,
        )
        for manifest in manifests
    ]
    errors = [f"{batch['batch_id']}: {error}" for batch in batches for error in batch["errors"]]
    warnings = [f"{batch['batch_id']}: {warning}" for batch in batches for warning in batch["warnings"]]
    if not manifests:
        errors.append(f"no asset candidate manifests found under {root}")
    audio_asset_count = sum(batch["audio_asset_count"] for batch in batches)
    return {
        "report_version": 1,
        "root": str(root),
        "ffprobe_path": ffprobe_path,
        "decision": "asset_audio_technical_probe_valid" if not errors else "asset_audio_technical_probe_invalid",
        "batch_count": len(batches),
        "audio_asset_count": audio_asset_count,
        "errors": errors,
        "warnings": warnings,
        "batches": batches,
        "limitations": [
            "This probe checks local file metadata only; it does not judge listening quality, mix balance, clipping by ear, or fatigue.",
            "A valid technical probe cannot satisfy asset_audio_loudness_review, Runtime preview, final human acceptance, accepted_content, or release gates.",
            "Non-wav audio requires ffprobe to be available on PATH or passed explicitly.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Asset Audio Technical Probe",
        "",
        f"- Root: `{report['root']}`",
        f"- Decision: `{report['decision']}`",
        f"- Batches: {report['batch_count']}",
        f"- Audio assets: {report['audio_asset_count']}",
        f"- ffprobe: `{report['ffprobe_path']}`",
        "",
        "## Batches",
        "",
        "| Batch | Audio assets | Errors | Warnings |",
        "|---|---:|---:|---:|",
    ]
    for batch in report["batches"]:
        lines.append(
            f"| `{batch['batch_id']}` | {batch['audio_asset_count']} | "
            f"{len(batch['errors'])} | {len(batch['warnings'])} |"
        )

    lines.extend(["", "## Audio Assets", "", "| Batch | Asset | Type | Path | Duration | Sample rate | Channels |", "|---|---|---|---|---:|---:|---:|"])
    for batch in report["batches"]:
        for asset in batch["audio_assets"]:
            probe = asset.get("probe") or {}
            lines.append(
                f"| `{batch['batch_id']}` | `{asset['id']}` | `{asset['type']}` | `{asset['path']}` | "
                f"{probe.get('duration_seconds')} | {probe.get('sample_rate_hz')} | {probe.get('channels')} |"
            )

    lines.extend(["", "## Errors", ""])
    if report["errors"]:
        lines.extend(f"- {error}" for error in report["errors"])
    else:
        lines.append("- None")

    lines.extend(["", "## Warnings", ""])
    if report["warnings"]:
        lines.extend(f"- {warning}" for warning in report["warnings"])
    else:
        lines.append("- None")

    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit technical metadata for generated asset candidate audio.")
    parser.add_argument(
        "root",
        type=Path,
        nargs="?",
        default=Path("asset/generated_candidates"),
        help="Generated asset candidate root, batch directory, or manifest path",
    )
    parser.add_argument("--ffprobe", default=None, help="Path to ffprobe for non-wav audio")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON probe report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown probe summary")
    args = parser.parse_args()

    report = build_report(args.root, ffprobe_path=args.ffprobe)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["decision"] == "asset_audio_technical_probe_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
