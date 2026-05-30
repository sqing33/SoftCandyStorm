#!/usr/bin/env python3
"""Create an RL repair action plan from fixed-window failure analyses.

The plan combines 60 / 180 / 300 second high-pressure diagnostics and keeps
the output explicitly scoped to repair exploration. It does not train a model,
approve a policy candidate, or replace no-regression gates.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


BUCKET_STAGE_CONFIG = {
    "opening_lt_60": {
        "title": "opening retention repair",
        "train_seconds": 60,
        "priority": 10,
        "strategy": "Protect short-window movement before any mid or late continuation.",
    },
    "mid_60_to_180": {
        "title": "handoff and mid-window retention repair",
        "train_seconds": 180,
        "priority": 20,
        "strategy": "Repair post-opening handoff without regressing the 60 second gate.",
    },
    "late_180_to_300": {
        "title": "late conversion repair",
        "train_seconds": 300,
        "priority": 30,
        "strategy": "Improve late route recovery and 300 second conversion while preserving earlier windows.",
    },
    "post_300": {
        "title": "post-duration anomaly review",
        "train_seconds": 300,
        "priority": 40,
        "strategy": "Inspect impossible or post-duration failures before using them as training signal.",
    },
}


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def parse_labeled_path(value: str) -> tuple[str | None, Path]:
    if "=" not in value:
        return None, Path(value)
    label, raw_path = value.split("=", 1)
    label = label.strip()
    raw_path = raw_path.strip()
    if not label:
        raise argparse.ArgumentTypeError("analysis label must be non-empty")
    if not raw_path:
        raise argparse.ArgumentTypeError("analysis path must be non-empty")
    return label, Path(raw_path)


def format_seconds(value: int | float | None) -> str:
    if value is None:
        return "unknown"
    number = float(value)
    return str(int(number)) if number.is_integer() else str(number)


def parse_validation_windows(value: str) -> list[int]:
    windows: list[int] = []
    for raw_item in value.split(","):
        item = raw_item.strip()
        if not item:
            continue
        try:
            seconds = int(item)
        except ValueError as exc:
            raise ValueError("--validation-windows must be comma-separated integers") from exc
        if seconds <= 0:
            raise ValueError("--validation-windows values must be positive")
        if seconds not in windows:
            windows.append(seconds)
    if not windows:
        raise ValueError("--validation-windows must include at least one window")
    return windows


def shell_join(parts: list[str]) -> str:
    return " ".join(parts)


def stage_train_command(stage: dict[str, Any], reward_profile: str, train_map_selection: str) -> str:
    return shell_join(
        [
            "uv",
            "run",
            "--with-requirements",
            "python/train/requirements.txt",
            "python",
            "python/train/train_sb3.py",
            "--algorithm",
            "ppo",
            "--model-in",
            stage["model_in"],
            "--model-out",
            stage["model_out"],
            "--report-dir",
            stage["report_dir"],
            "--train-maps",
            ",".join(stage["train_maps"]),
            "--train-map-selection",
            train_map_selection,
            "--train-seconds",
            str(stage["train_seconds"]),
            "--timesteps",
            str(stage["timesteps"]),
            "--reward-profile",
            reward_profile,
            "--eval-episodes",
            "3",
            "--eval-seconds",
            str(stage["primary_eval_seconds"]),
            "--map-id",
            stage["primary_eval_map"],
            "--report",
            f"{stage['report_dir']}/ppo_training_report.json",
        ]
    )


def stage_compare_command(stage: dict[str, Any], eval_seconds: int) -> str:
    seconds_label = format_seconds(eval_seconds)
    return shell_join(
        [
            "uv",
            "run",
            "--with-requirements",
            "python/train/requirements.txt",
            "python",
            "python/train/train_sb3.py",
            "--algorithm",
            "ppo",
            "--compare-rule-bots",
            "--compare-map-preset",
            "high-pressure",
            "--model",
            stage["model_out"],
            "--eval-episodes",
            "3",
            "--eval-seconds",
            seconds_label,
            "--seed-start",
            str(stage["validation_seed_start"]),
            "--rule-bots",
            "random,kite,tank",
            "--report",
            f"{stage['report_dir']}/comparison_{seconds_label}s.json",
        ]
    )


def collect_failures(label: str, path: Path, payload: dict[str, Any]) -> list[dict[str, Any]]:
    seconds = payload.get("seconds")
    failures: list[dict[str, Any]] = []
    for map_report in payload.get("maps", []):
        if not isinstance(map_report, dict):
            continue
        map_id = map_report.get("map_id")
        if not isinstance(map_id, str) or not map_id:
            continue
        distribution = map_report.get("failure_time_bucket_distribution")
        if not isinstance(distribution, dict):
            continue
        for bucket, config in BUCKET_STAGE_CONFIG.items():
            bucket_payload = distribution.get(bucket)
            if not isinstance(bucket_payload, dict):
                continue
            count = int(bucket_payload.get("count", 0) or 0)
            if count <= 0:
                continue
            failures.append(
                {
                    "source_label": label,
                    "source": str(path),
                    "source_window_seconds": seconds,
                    "map_id": map_id,
                    "time_bucket": bucket,
                    "failure_count": count,
                    "failure_ratio": float(bucket_payload.get("ratio", 0.0) or 0.0),
                    "win_rate": map_report.get("win_rate"),
                    "average_failure_survival_seconds": map_report.get(
                        "average_failure_survival_seconds"
                    ),
                    "dominant_action": map_report.get("policy_dominant_action"),
                    "stage_priority": config["priority"],
                }
            )
    return failures


def build_plan(
    analysis_inputs: list[tuple[str | None, Path]],
    *,
    initial_model: str,
    output_dir: str,
    timesteps_per_stage: int,
    reward_profile: str,
    train_map_selection: str,
    validation_seed_start: int,
    validation_windows: list[int] | None = None,
) -> dict[str, Any]:
    validation_windows = validation_windows or [60, 180, 300]
    sources: list[dict[str, Any]] = []
    all_failures: list[dict[str, Any]] = []
    for index, (label, path) in enumerate(analysis_inputs, start=1):
        payload = load_json_object(path)
        source_label = label or f"{format_seconds(payload.get('seconds'))}s"
        failures = collect_failures(source_label, path, payload)
        sources.append(
            {
                "label": source_label,
                "path": str(path),
                "decision": payload.get("decision"),
                "gate_decision": payload.get("gate_decision"),
                "seconds": payload.get("seconds"),
                "failure_group_count": len(failures),
                "total_failure_count": sum(int(failure["failure_count"]) for failure in failures),
            }
        )
        all_failures.extend(failures)

    failures_by_bucket: dict[str, list[dict[str, Any]]] = {
        bucket: [] for bucket in BUCKET_STAGE_CONFIG
    }
    for failure in all_failures:
        failures_by_bucket[str(failure["time_bucket"])].append(failure)

    stages: list[dict[str, Any]] = []
    model_in = initial_model
    output_root = Path(output_dir)
    stage_number = 1
    for bucket, failures in sorted(
        failures_by_bucket.items(),
        key=lambda item: BUCKET_STAGE_CONFIG[item[0]]["priority"],
    ):
        if not failures:
            continue
        config = BUCKET_STAGE_CONFIG[bucket]
        train_maps = sorted({failure["map_id"] for failure in failures})
        source_windows = sorted(
            {
                int(failure["source_window_seconds"])
                for failure in failures
                if isinstance(failure.get("source_window_seconds"), (int, float))
            }
        )
        stage_id = f"stage_{stage_number:02d}_{bucket}"
        stage_dir = output_root / stage_id
        model_out = str(stage_dir / f"{stage_id}.zip")
        primary_eval_seconds = min(source_windows or [config["train_seconds"]])
        stage = {
            "stage": stage_number,
            "id": stage_id,
            "focus_bucket": bucket,
            "title": config["title"],
            "strategy": config["strategy"],
            "train_maps": train_maps,
            "train_seconds": config["train_seconds"],
            "timesteps": timesteps_per_stage,
            "model_in": model_in,
            "model_out": model_out,
            "report_dir": str(stage_dir),
            "primary_eval_map": train_maps[0],
            "primary_eval_seconds": primary_eval_seconds,
            "source_windows": source_windows,
            "source_failures": failures,
            "total_failure_count": sum(int(failure["failure_count"]) for failure in failures),
            "validation_seed_start": validation_seed_start + stage_number * 100,
            "required_validation_windows": validation_windows,
            "hard_rules": [
                "Run all required validation windows after any training attempt.",
                "Do not promote a checkpoint while any 60/180/300 high-pressure window regresses.",
                "Keep RL acceptance blocked until the dedicated acceptance gate passes.",
            ],
        }
        stage["train_command"] = stage_train_command(stage, reward_profile, train_map_selection)
        stage["compare_commands"] = [
            stage_compare_command(stage, seconds) for seconds in validation_windows
        ]
        stages.append(stage)
        model_in = model_out
        stage_number += 1

    decision = "rl_fixed_window_action_plan_ready" if stages else "rl_fixed_window_action_plan_no_failures"
    return {
        "report_version": 1,
        "decision": decision,
        "initial_model": initial_model,
        "output_dir": output_dir,
        "timesteps_per_stage": timesteps_per_stage,
        "reward_profile": reward_profile,
        "train_map_selection": train_map_selection,
        "validation_windows": validation_windows,
        "sources": sources,
        "failure_group_count": len(all_failures),
        "total_failure_count": sum(int(failure["failure_count"]) for failure in all_failures),
        "stage_count": len(stages),
        "stages": stages,
        "limitations": [
            "This plan is generated from existing fixed-window diagnostic reports only.",
            "It does not train, evaluate, or approve a policy.",
            "Every suggested follow-up must still pass fixed-window no-regression and RL acceptance gates.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# RL Fixed-window Action Plan",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Initial model: `{report['initial_model']}`",
        f"- Reward profile: `{report['reward_profile']}`",
        f"- Stages: {report['stage_count']}",
        f"- Validation windows: {', '.join(str(item) for item in report['validation_windows'])}",
        "",
        "## Sources",
        "",
        "| Label | Seconds | Decision | Failure Groups | Total Failures |",
        "|---|---:|---|---:|---:|",
    ]
    for source in report["sources"]:
        lines.append(
            "| {label} | {seconds} | `{decision}` | {groups} | {failures} |".format(
                label=f"`{source['label']}`",
                seconds=source.get("seconds"),
                decision=source.get("decision"),
                groups=source.get("failure_group_count", 0),
                failures=source.get("total_failure_count", 0),
            )
        )

    lines.extend(["", "## Stages", ""])
    if not report["stages"]:
        lines.append("- No failure stages were generated.")
    for stage in report["stages"]:
        lines.extend(
            [
                f"### {stage['id']}",
                "",
                f"- Focus: `{stage['focus_bucket']}`",
                f"- Title: {stage['title']}",
                f"- Strategy: {stage['strategy']}",
                f"- Train maps: {', '.join(f'`{item}`' for item in stage['train_maps'])}",
                f"- Source windows: {', '.join(str(item) for item in stage['source_windows'])}",
                f"- Total failures: {stage['total_failure_count']}",
                f"- Train command: `{stage['train_command']}`",
                "",
                "Validation commands:",
            ]
        )
        lines.extend(f"- `{command}`" for command in stage["compare_commands"])
        lines.append("")

    lines.extend(["## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an RL fixed-window repair action plan.")
    parser.add_argument("analyses", nargs="+", type=parse_labeled_path)
    parser.add_argument("--initial-model", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--timesteps-per-stage", type=int, default=256)
    parser.add_argument(
        "--reward-profile",
        choices=["late-survival", "long-run-retention", "late-route-recovery"],
        default="late-route-recovery",
    )
    parser.add_argument("--train-map-selection", choices=["cycle", "random"], default="random")
    parser.add_argument("--validation-seed-start", type=int, default=63300)
    parser.add_argument("--validation-windows", default="60,180,300")
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    args = parser.parse_args()

    validation_windows = parse_validation_windows(args.validation_windows)
    report = build_plan(
        args.analyses,
        initial_model=args.initial_model,
        output_dir=args.output_dir,
        timesteps_per_stage=args.timesteps_per_stage,
        reward_profile=args.reward_profile,
        train_map_selection=args.train_map_selection,
        validation_seed_start=args.validation_seed_start,
        validation_windows=validation_windows,
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(report, args.markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
