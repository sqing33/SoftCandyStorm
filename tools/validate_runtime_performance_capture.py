#!/usr/bin/env python3
"""Validate Runtime playtest capture performance evidence.

This validator inspects `game_runtime --playtest-report` output. It can support
local Runtime smoke evidence for frame pacing, entity counts, capture samples,
terminal metrics, and privacy defaults. It does not replace Steam Deck testing,
GPU profiling, memory growth checks, or human readability/playtest review.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


DEFAULT_MIN_AVERAGE_FPS = 45.0
DEFAULT_MIN_WORST_FRAME_FPS = 10.0
DEFAULT_MAX_SLOW_30FPS_RATIO = 0.10
DEFAULT_MAX_ENEMY_COUNT = 140
DEFAULT_MAX_PROJECTILE_COUNT = 220
DEFAULT_MAX_ACTIVE_EFFECTS = 96
DEFAULT_DURATION_TOLERANCE_SECONDS = 1.0
DEFAULT_PROFILE = "smoke"

PROFILE_DEFAULTS = {
    "smoke": {
        "min_average_fps": DEFAULT_MIN_AVERAGE_FPS,
        "min_worst_frame_fps": DEFAULT_MIN_WORST_FRAME_FPS,
        "max_slow_30fps_ratio": DEFAULT_MAX_SLOW_30FPS_RATIO,
        "max_enemy_count": DEFAULT_MAX_ENEMY_COUNT,
        "max_projectile_count": DEFAULT_MAX_PROJECTILE_COUNT,
        "max_active_effects": DEFAULT_MAX_ACTIVE_EFFECTS,
        "duration_tolerance_seconds": DEFAULT_DURATION_TOLERANCE_SECONDS,
        "min_target_duration_seconds": 0.0,
        "min_sample_count": 1,
        "required_input_mode": None,
        "expected_terminal_kind": None,
    },
    "release-local": {
        "min_average_fps": 55.0,
        "min_worst_frame_fps": DEFAULT_MIN_WORST_FRAME_FPS,
        "max_slow_30fps_ratio": 0.01,
        "max_enemy_count": DEFAULT_MAX_ENEMY_COUNT,
        "max_projectile_count": DEFAULT_MAX_PROJECTILE_COUNT,
        "max_active_effects": DEFAULT_MAX_ACTIVE_EFFECTS,
        "duration_tolerance_seconds": DEFAULT_DURATION_TOLERANCE_SECONDS,
        "min_target_duration_seconds": 600.0,
        "min_sample_count": 20,
        "required_input_mode": "demo",
        "expected_terminal_kind": "victory",
    },
}


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def is_finite_number(value: Any) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(float(value))


def finite_number(value: Any, label: str, errors: list[str]) -> float:
    if not is_finite_number(value):
        errors.append(f"{label}: must be a finite number")
        return 0.0
    return float(value)


def finite_int(value: Any, label: str, errors: list[str]) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        errors.append(f"{label}: must be an integer")
        return 0
    return value


def nonempty_string(value: Any, label: str, errors: list[str]) -> str:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}: must be a non-empty string")
        return ""
    return value


def close_enough(left: float, right: float, *, abs_tol: float = 0.01, rel_tol: float = 0.01) -> bool:
    return math.isclose(left, right, abs_tol=abs_tol, rel_tol=rel_tol)


def fps_from_frame_seconds(frame_seconds: float) -> float:
    return 1.0 / frame_seconds if frame_seconds > 0 else 0.0


def profile_defaults(profile: str) -> dict[str, Any]:
    if profile not in PROFILE_DEFAULTS:
        raise ValueError(f"unknown Runtime performance profile `{profile}`")
    return PROFILE_DEFAULTS[profile].copy()


def validate_frame_metrics(
    payload: dict[str, Any],
    *,
    min_average_fps: float,
    min_worst_frame_fps: float,
    max_slow_30fps_ratio: float,
    errors: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    frame_metrics = payload.get("frame_metrics")
    if not isinstance(frame_metrics, dict):
        errors.append("frame_metrics: must be an object")
        return {
            "frame_count": 0,
            "average_fps": 0.0,
            "worst_frame_fps": 0.0,
            "slow_frame_count_30fps": 0,
            "status": "invalid",
        }

    frame_count = finite_int(frame_metrics.get("frame_count"), "frame_metrics.frame_count", errors)
    total_frame_seconds = finite_number(
        frame_metrics.get("total_frame_seconds"), "frame_metrics.total_frame_seconds", errors
    )
    average_frame_seconds = finite_number(
        frame_metrics.get("average_frame_seconds"), "frame_metrics.average_frame_seconds", errors
    )
    average_fps = finite_number(frame_metrics.get("average_fps"), "frame_metrics.average_fps", errors)
    min_frame_seconds = finite_number(
        frame_metrics.get("min_frame_seconds"), "frame_metrics.min_frame_seconds", errors
    )
    max_frame_seconds = finite_number(
        frame_metrics.get("max_frame_seconds"), "frame_metrics.max_frame_seconds", errors
    )
    worst_frame_fps = finite_number(
        frame_metrics.get("worst_frame_fps"), "frame_metrics.worst_frame_fps", errors
    )
    slow_45 = finite_int(
        frame_metrics.get("slow_frame_count_45fps"), "frame_metrics.slow_frame_count_45fps", errors
    )
    slow_30 = finite_int(
        frame_metrics.get("slow_frame_count_30fps"), "frame_metrics.slow_frame_count_30fps", errors
    )

    if frame_count <= 0:
        errors.append("frame_metrics.frame_count: must be positive")
    if total_frame_seconds <= 0:
        errors.append("frame_metrics.total_frame_seconds: must be positive")
    if average_frame_seconds <= 0:
        errors.append("frame_metrics.average_frame_seconds: must be positive")
    if min_frame_seconds < 0 or max_frame_seconds < 0:
        errors.append("frame_metrics min/max frame seconds must be non-negative")
    if max_frame_seconds < min_frame_seconds:
        errors.append("frame_metrics.max_frame_seconds: must be >= min_frame_seconds")
    if slow_45 < 0 or slow_30 < 0:
        errors.append("frame_metrics slow frame counts must be non-negative")
    if slow_45 > frame_count or slow_30 > frame_count:
        errors.append("frame_metrics slow frame counts must be <= frame_count")

    if frame_count > 0 and total_frame_seconds > 0:
        expected_average_frame_seconds = total_frame_seconds / frame_count
        if not close_enough(average_frame_seconds, expected_average_frame_seconds):
            errors.append(
                "frame_metrics.average_frame_seconds: does not match total_frame_seconds/frame_count"
            )
    if average_frame_seconds > 0 and not close_enough(average_fps, fps_from_frame_seconds(average_frame_seconds)):
        errors.append("frame_metrics.average_fps: does not match average_frame_seconds")
    if max_frame_seconds > 0 and not close_enough(worst_frame_fps, fps_from_frame_seconds(max_frame_seconds)):
        errors.append("frame_metrics.worst_frame_fps: does not match max_frame_seconds")

    slow_30_ratio = slow_30 / frame_count if frame_count > 0 else 1.0
    if average_fps < min_average_fps:
        errors.append(
            f"frame_metrics.average_fps: {average_fps:.2f} is below local smoke floor {min_average_fps:.2f}"
        )
    if worst_frame_fps < min_worst_frame_fps:
        warnings.append(
            f"frame_metrics.worst_frame_fps: {worst_frame_fps:.2f} is below warning floor {min_worst_frame_fps:.2f}"
        )
    if slow_30_ratio > max_slow_30fps_ratio:
        errors.append(
            f"frame_metrics.slow_frame_count_30fps: ratio {slow_30_ratio:.3f} exceeds {max_slow_30fps_ratio:.3f}"
        )

    return {
        "frame_count": frame_count,
        "total_frame_seconds": total_frame_seconds,
        "average_fps": average_fps,
        "worst_frame_fps": worst_frame_fps,
        "slow_frame_count_45fps": slow_45,
        "slow_frame_count_30fps": slow_30,
        "slow_frame_ratio_30fps": slow_30_ratio,
        "status": "ok",
    }


def validate_samples(
    payload: dict[str, Any],
    *,
    max_enemy_count: int,
    max_projectile_count: int,
    max_active_effects: int,
    min_sample_count: int,
    errors: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    samples_payload = payload.get("samples")
    if not isinstance(samples_payload, list):
        errors.append("samples: must be a list")
        samples_payload = []
    if not samples_payload:
        errors.append("samples: must contain at least one sample")

    previous_time = -1.0
    sample_count = 0
    max_visible_enemies = 0
    max_visible_projectiles = 0
    max_effects = 0
    for index, sample in enumerate(samples_payload):
        if not isinstance(sample, dict):
            errors.append(f"samples[{index}]: must be an object")
            continue
        prefix = f"samples[{index}]"
        time_seconds = finite_number(sample.get("time_seconds"), f"{prefix}.time_seconds", errors)
        visible_enemies = finite_int(sample.get("visible_enemies"), f"{prefix}.visible_enemies", errors)
        visible_projectiles = finite_int(
            sample.get("visible_projectiles"), f"{prefix}.visible_projectiles", errors
        )
        active_effects = finite_int(sample.get("active_effects"), f"{prefix}.active_effects", errors)
        finite_number(sample.get("health"), f"{prefix}.health", errors)
        finite_number(sample.get("max_health"), f"{prefix}.max_health", errors)
        finite_int(sample.get("level"), f"{prefix}.level", errors)
        finite_int(sample.get("kills"), f"{prefix}.kills", errors)

        if time_seconds < previous_time:
            errors.append(f"{prefix}.time_seconds: must be non-decreasing")
        previous_time = time_seconds
        if visible_enemies < 0 or visible_projectiles < 0 or active_effects < 0:
            errors.append(f"{prefix}: counts must be non-negative")
        if visible_enemies > max_enemy_count:
            errors.append(f"{prefix}.visible_enemies: {visible_enemies} exceeds ceiling {max_enemy_count}")
        if visible_projectiles > max_projectile_count:
            errors.append(
                f"{prefix}.visible_projectiles: {visible_projectiles} exceeds ceiling {max_projectile_count}"
            )
        if active_effects > max_active_effects:
            errors.append(f"{prefix}.active_effects: {active_effects} exceeds ceiling {max_active_effects}")

        sample_count += 1
        max_visible_enemies = max(max_visible_enemies, visible_enemies)
        max_visible_projectiles = max(max_visible_projectiles, visible_projectiles)
        max_effects = max(max_effects, active_effects)

    if sample_count < min_sample_count:
        errors.append(f"samples: {sample_count} sample(s) below required minimum {min_sample_count}")
    if max_visible_enemies > int(max_enemy_count * 0.75):
        warnings.append(f"samples.visible_enemies: peak {max_visible_enemies} is near ceiling {max_enemy_count}")

    return {
        "sample_count": sample_count,
        "max_visible_enemies": max_visible_enemies,
        "max_visible_projectiles": max_visible_projectiles,
        "max_active_effects": max_effects,
    }


def validate_final_metrics(
    payload: dict[str, Any],
    *,
    duration_tolerance_seconds: float,
    min_target_duration_seconds: float,
    max_enemy_count: int,
    max_projectile_count: int,
    expected_terminal_kind: str | None,
    errors: list[str],
) -> dict[str, Any]:
    run_config = payload.get("run_config")
    if not isinstance(run_config, dict):
        errors.append("run_config: must be an object")
        run_config = {}
    target_duration = finite_number(
        run_config.get("duration_seconds"), "run_config.duration_seconds", errors
    )
    tick_rate = finite_int(run_config.get("tick_rate"), "run_config.tick_rate", errors)
    map_id = nonempty_string(run_config.get("map_id"), "run_config.map_id", errors)

    final_metrics = payload.get("final_metrics")
    if not isinstance(final_metrics, dict):
        errors.append("final_metrics: must be an object")
        return {"terminal": None, "duration_seconds": 0.0, "status": "invalid"}

    duration_seconds = finite_number(
        final_metrics.get("duration_seconds"), "final_metrics.duration_seconds", errors
    )
    metric_tick_rate = finite_int(final_metrics.get("tick_rate"), "final_metrics.tick_rate", errors)
    kills = finite_int(final_metrics.get("kills"), "final_metrics.kills", errors)
    level = finite_int(final_metrics.get("level"), "final_metrics.level", errors)
    max_enemy_observed = finite_int(
        final_metrics.get("max_enemy_count"), "final_metrics.max_enemy_count", errors
    )
    max_projectile_observed = finite_int(
        final_metrics.get("max_projectile_count"), "final_metrics.max_projectile_count", errors
    )
    finite_number(final_metrics.get("damage_taken"), "final_metrics.damage_taken", errors)

    if tick_rate <= 0 or metric_tick_rate <= 0:
        errors.append("tick_rate: must be positive")
    if tick_rate > 0 and metric_tick_rate > 0 and tick_rate != metric_tick_rate:
        errors.append("final_metrics.tick_rate: does not match run_config.tick_rate")
    if target_duration <= 0:
        errors.append("run_config.duration_seconds: must be positive")
    if target_duration < min_target_duration_seconds:
        errors.append(
            f"run_config.duration_seconds: {target_duration:.3f} is below required minimum "
            f"{min_target_duration_seconds:.3f}"
        )
    if duration_seconds < 0:
        errors.append("final_metrics.duration_seconds: must be non-negative")
    if target_duration > 0 and duration_seconds > target_duration + duration_tolerance_seconds:
        errors.append(
            f"final_metrics.duration_seconds: {duration_seconds:.3f} exceeds target "
            f"{target_duration:.3f} + tolerance {duration_tolerance_seconds:.3f}"
        )
    if kills < 0 or level < 0:
        errors.append("final_metrics kills/level must be non-negative")
    if max_enemy_observed > max_enemy_count:
        errors.append(f"final_metrics.max_enemy_count: {max_enemy_observed} exceeds ceiling {max_enemy_count}")
    if max_projectile_observed > max_projectile_count:
        errors.append(
            f"final_metrics.max_projectile_count: {max_projectile_observed} exceeds ceiling {max_projectile_count}"
        )

    terminal = final_metrics.get("terminal")
    terminal_kind = None
    if not isinstance(terminal, dict):
        errors.append("final_metrics.terminal: must be an object for Runtime performance smoke")
    else:
        terminal_kind = nonempty_string(terminal.get("kind"), "final_metrics.terminal.kind", errors)
        finite_number(terminal.get("time_seconds"), "final_metrics.terminal.time_seconds", errors)
        if terminal_kind not in {"victory", "defeat"}:
            errors.append(f"final_metrics.terminal.kind: expected victory or defeat, got `{terminal_kind}`")
        if expected_terminal_kind is not None and terminal_kind != expected_terminal_kind:
            errors.append(
                f"final_metrics.terminal.kind: expected `{expected_terminal_kind}` for this profile, "
                f"got `{terminal_kind}`"
            )

    return {
        "map_id": map_id,
        "target_duration_seconds": target_duration,
        "duration_seconds": duration_seconds,
        "terminal": terminal_kind,
        "kills": kills,
        "level": level,
        "max_enemy_count": max_enemy_observed,
        "max_projectile_count": max_projectile_observed,
    }


def validate_privacy(payload: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    privacy = payload.get("privacy")
    if not isinstance(privacy, dict):
        errors.append("privacy: must be an object")
        return {"local_capture_only": False, "upload_transport": None}

    local_capture_only = privacy.get("local_capture_only")
    upload_transport = nonempty_string(privacy.get("upload_transport"), "privacy.upload_transport", errors)
    if local_capture_only is not True:
        errors.append("privacy.local_capture_only: must be true for local Runtime performance smoke")
    for key in ["telemetry_upload_enabled", "raw_replay_upload_enabled", "crash_report_upload_enabled"]:
        if privacy.get(key) is not False:
            errors.append(f"privacy.{key}: must be false for local Runtime performance smoke")
    if upload_transport != "not_implemented":
        errors.append("privacy.upload_transport: expected `not_implemented` for current local Runtime")

    return {"local_capture_only": local_capture_only, "upload_transport": upload_transport}


def build_report(
    capture_path: Path,
    *,
    profile: str = DEFAULT_PROFILE,
    min_average_fps: float | None = None,
    min_worst_frame_fps: float | None = None,
    max_slow_30fps_ratio: float | None = None,
    max_enemy_count: int | None = None,
    max_projectile_count: int | None = None,
    max_active_effects: int | None = None,
    duration_tolerance_seconds: float | None = None,
    min_target_duration_seconds: float | None = None,
    min_sample_count: int | None = None,
    required_input_mode: str | None = None,
    expected_terminal_kind: str | None = None,
) -> dict[str, Any]:
    defaults = profile_defaults(profile)
    min_average_fps = float(defaults["min_average_fps"] if min_average_fps is None else min_average_fps)
    min_worst_frame_fps = float(
        defaults["min_worst_frame_fps"] if min_worst_frame_fps is None else min_worst_frame_fps
    )
    max_slow_30fps_ratio = float(
        defaults["max_slow_30fps_ratio"] if max_slow_30fps_ratio is None else max_slow_30fps_ratio
    )
    max_enemy_count = int(defaults["max_enemy_count"] if max_enemy_count is None else max_enemy_count)
    max_projectile_count = int(
        defaults["max_projectile_count"] if max_projectile_count is None else max_projectile_count
    )
    max_active_effects = int(defaults["max_active_effects"] if max_active_effects is None else max_active_effects)
    duration_tolerance_seconds = float(
        defaults["duration_tolerance_seconds"]
        if duration_tolerance_seconds is None
        else duration_tolerance_seconds
    )
    min_target_duration_seconds = float(
        defaults["min_target_duration_seconds"]
        if min_target_duration_seconds is None
        else min_target_duration_seconds
    )
    min_sample_count = int(defaults["min_sample_count"] if min_sample_count is None else min_sample_count)
    required_input_mode = defaults["required_input_mode"] if required_input_mode is None else required_input_mode
    expected_terminal_kind = (
        defaults["expected_terminal_kind"] if expected_terminal_kind is None else expected_terminal_kind
    )

    payload = load_json_object(capture_path)
    errors: list[str] = []
    warnings: list[str] = []

    kind = payload.get("kind")
    if kind != "runtime_playtest_capture":
        errors.append(f"kind: expected `runtime_playtest_capture`, got `{kind}`")
    report_version = finite_int(payload.get("report_version"), "report_version", errors)
    if report_version != 1:
        errors.append(f"report_version: expected 1, got {report_version}")
    input_mode = nonempty_string(payload.get("input_mode"), "input_mode", errors)
    if input_mode not in {"demo", "keyboard"}:
        errors.append(f"input_mode: expected demo or keyboard, got `{input_mode}`")
    if required_input_mode is not None and input_mode != required_input_mode:
        errors.append(f"input_mode: expected `{required_input_mode}` for profile `{profile}`, got `{input_mode}`")
    simulation_speed = finite_number(payload.get("simulation_speed"), "simulation_speed", errors)
    if simulation_speed <= 0:
        errors.append("simulation_speed: must be positive")

    frame_summary = validate_frame_metrics(
        payload,
        min_average_fps=min_average_fps,
        min_worst_frame_fps=min_worst_frame_fps,
        max_slow_30fps_ratio=max_slow_30fps_ratio,
        errors=errors,
        warnings=warnings,
    )
    sample_summary = validate_samples(
        payload,
        max_enemy_count=max_enemy_count,
        max_projectile_count=max_projectile_count,
        max_active_effects=max_active_effects,
        min_sample_count=min_sample_count,
        errors=errors,
        warnings=warnings,
    )
    final_summary = validate_final_metrics(
        payload,
        duration_tolerance_seconds=duration_tolerance_seconds,
        min_target_duration_seconds=min_target_duration_seconds,
        max_enemy_count=max_enemy_count,
        max_projectile_count=max_projectile_count,
        expected_terminal_kind=expected_terminal_kind,
        errors=errors,
    )
    privacy_summary = validate_privacy(payload, errors)

    decision = "runtime_performance_capture_valid" if not errors else "runtime_performance_capture_invalid"
    return {
        "report_version": 1,
        "source": str(capture_path),
        "profile": profile,
        "decision": decision,
        "thresholds": {
            "min_average_fps": min_average_fps,
            "min_worst_frame_fps": min_worst_frame_fps,
            "max_slow_30fps_ratio": max_slow_30fps_ratio,
            "max_enemy_count": max_enemy_count,
            "max_projectile_count": max_projectile_count,
            "max_active_effects": max_active_effects,
            "duration_tolerance_seconds": duration_tolerance_seconds,
            "min_target_duration_seconds": min_target_duration_seconds,
            "min_sample_count": min_sample_count,
            "required_input_mode": required_input_mode,
            "expected_terminal_kind": expected_terminal_kind,
        },
        "summary": {
            "kind": kind,
            "input_mode": input_mode,
            "simulation_speed": simulation_speed,
            "frame_metrics": frame_summary,
            "samples": sample_summary,
            "final_metrics": final_summary,
            "privacy": privacy_summary,
        },
        "errors": errors,
        "warnings": warnings,
        "limitations": [
            "This validates one local Runtime playtest capture only; it is not Steam Deck or broad hardware coverage.",
            "The release-local profile is stricter than smoke, but still remains a single-machine automated gate.",
            "Frame timing comes from Bevy runtime frame deltas and does not replace GPU profiling or memory growth checks.",
            "Manual playtest readability, fun, death clarity, and content acceptance remain separate human gates.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    frame = report["summary"]["frame_metrics"]
    samples = report["summary"]["samples"]
    final = report["summary"]["final_metrics"]
    lines = [
        "# Runtime Performance Capture Validation",
        "",
        f"- Source: `{report['source']}`",
        f"- Profile: `{report['profile']}`",
        f"- Decision: `{report['decision']}`",
        f"- Input mode: `{report['summary']['input_mode']}`",
        f"- Simulation speed: `{report['summary']['simulation_speed']}`",
        f"- Average FPS: `{frame['average_fps']:.2f}`",
        f"- Worst frame FPS: `{frame['worst_frame_fps']:.2f}`",
        f"- Slow frames below 30 FPS: `{frame['slow_frame_count_30fps']}` / `{frame['frame_count']}`",
        f"- Samples: `{samples['sample_count']}`",
        f"- Max visible enemies: `{samples['max_visible_enemies']}`",
        f"- Max visible projectiles: `{samples['max_visible_projectiles']}`",
        f"- Terminal: `{final['terminal']}`",
        f"- Duration: `{final['duration_seconds']:.2f}` / `{final['target_duration_seconds']:.2f}` seconds",
        "",
        "## Errors",
        "",
    ]
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
    parser = argparse.ArgumentParser(description="Validate Soft Candy Storm Runtime performance capture reports.")
    parser.add_argument("capture", type=Path, help="Runtime --playtest-report JSON")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON validation report")
    parser.add_argument("--markdown", type=Path, default=None, help="Write Markdown validation summary")
    parser.add_argument("--profile", choices=sorted(PROFILE_DEFAULTS), default=DEFAULT_PROFILE)
    parser.add_argument("--min-average-fps", type=float, default=None)
    parser.add_argument("--min-worst-frame-fps", type=float, default=None)
    parser.add_argument("--max-slow-30fps-ratio", type=float, default=None)
    parser.add_argument("--max-enemy-count", type=int, default=None)
    parser.add_argument("--max-projectile-count", type=int, default=None)
    parser.add_argument("--max-active-effects", type=int, default=None)
    parser.add_argument("--duration-tolerance-seconds", type=float, default=None)
    parser.add_argument("--min-target-duration-seconds", type=float, default=None)
    parser.add_argument("--min-sample-count", type=int, default=None)
    parser.add_argument("--required-input-mode", choices=["demo", "keyboard"], default=None)
    parser.add_argument("--expected-terminal-kind", choices=["victory", "defeat"], default=None)
    args = parser.parse_args()

    report = build_report(
        args.capture,
        profile=args.profile,
        min_average_fps=args.min_average_fps,
        min_worst_frame_fps=args.min_worst_frame_fps,
        max_slow_30fps_ratio=args.max_slow_30fps_ratio,
        max_enemy_count=args.max_enemy_count,
        max_projectile_count=args.max_projectile_count,
        max_active_effects=args.max_active_effects,
        duration_tolerance_seconds=args.duration_tolerance_seconds,
        min_target_duration_seconds=args.min_target_duration_seconds,
        min_sample_count=args.min_sample_count,
        required_input_mode=args.required_input_mode,
        expected_terminal_kind=args.expected_terminal_kind,
    )
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(report, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(report, indent=2, ensure_ascii=False))

    return 0 if report["decision"] == "runtime_performance_capture_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
