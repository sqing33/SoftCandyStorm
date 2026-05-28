#!/usr/bin/env python3
"""Create a staged RL curriculum plan from failure analysis output."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


BUCKET_STAGE_CONFIG = {
    "opening_lt_60": {
        "title": "opening survival repair",
        "train_seconds": 60,
        "eval_seconds": 60,
        "priority": 10,
    },
    "mid_60_to_180": {
        "title": "mid-run recovery repair",
        "train_seconds": 180,
        "eval_seconds": 180,
        "priority": 20,
    },
    "late_180_to_300": {
        "title": "late-run endurance repair",
        "train_seconds": 300,
        "eval_seconds": 300,
        "priority": 30,
    },
    "post_300": {
        "title": "post-duration anomaly review",
        "train_seconds": 300,
        "eval_seconds": 300,
        "priority": 40,
    },
}


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def bucket_maps(analysis: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    buckets: dict[str, list[dict[str, Any]]] = {
        bucket: [] for bucket in BUCKET_STAGE_CONFIG
    }
    for map_report in analysis.get("maps", []):
        map_id = map_report.get("map_id")
        if not isinstance(map_id, str):
            continue
        distribution = map_report.get("failure_time_bucket_distribution", {})
        for bucket in BUCKET_STAGE_CONFIG:
            value = distribution.get(bucket, {})
            count = int(value.get("count", 0)) if isinstance(value, dict) else 0
            if count <= 0:
                continue
            buckets[bucket].append(
                {
                    "map_id": map_id,
                    "failure_count": count,
                    "failure_ratio": float(value.get("ratio", 0.0)),
                    "average_failure_survival_seconds": map_report.get(
                        "average_failure_survival_seconds"
                    ),
                    "dominant_action": map_report.get("policy_dominant_action"),
                }
            )
    return buckets


def shell_join(parts: list[str]) -> str:
    return " ".join(parts)


def format_seconds(value: int | float) -> str:
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
            raise ValueError("--validation-windows must be a comma-separated list of integers") from exc
        if seconds <= 0:
            raise ValueError("--validation-windows values must be greater than zero")
        if seconds not in windows:
            windows.append(seconds)
    if not windows:
        raise ValueError("--validation-windows must include at least one value")
    return windows


def stage_command(
    stage: dict[str, Any],
    *,
    ent_coef: float,
    train_map_selection: str,
    reward_profile: str,
) -> str:
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
            "--ent-coef",
            str(ent_coef),
            "--reward-profile",
            reward_profile,
            "--eval-episodes",
            "3",
            "--eval-seconds",
            format_seconds(stage["eval_seconds"]),
            "--map-id",
            stage["primary_eval_map"],
            "--report",
            f"{stage['report_dir']}/ppo_training_report.json",
        ]
    )


def compare_command(stage: dict[str, Any], eval_seconds: int | float) -> str:
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


def build_plan(
    analysis_path: Path,
    *,
    initial_model: str,
    output_dir: str,
    timesteps_per_stage: int,
    ent_coef: float,
    train_map_selection: str,
    validation_seed_start: int,
    reward_profile: str = "late-route-recovery",
    validation_windows: list[int] | None = None,
) -> dict[str, Any]:
    analysis = load_json_object(analysis_path)
    buckets = bucket_maps(analysis)
    stages: list[dict[str, Any]] = []
    model_in = initial_model
    output_root = Path(output_dir)
    validation_windows = validation_windows or [60, 180, 300]
    stage_number = 1
    for bucket, entries in sorted(
        buckets.items(),
        key=lambda item: BUCKET_STAGE_CONFIG[item[0]]["priority"],
    ):
        if not entries:
            continue
        stage_id = f"stage_{stage_number:02d}_{bucket}"
        stage_dir = output_root / stage_id
        map_ids = sorted({entry["map_id"] for entry in entries})
        model_out = str(stage_dir / f"{stage_id}.zip")
        config = BUCKET_STAGE_CONFIG[bucket]
        stage = {
            "stage": stage_number,
            "id": stage_id,
            "focus_bucket": bucket,
            "title": config["title"],
            "train_maps": map_ids,
            "train_seconds": config["train_seconds"],
            "eval_seconds": config["eval_seconds"],
            "timesteps": timesteps_per_stage,
            "ent_coef": ent_coef,
            "model_in": model_in,
            "model_out": model_out,
            "report_dir": str(stage_dir),
            "primary_eval_map": map_ids[0],
            "validation_seed_start": validation_seed_start + stage_number * 100,
            "source_failures": entries,
            "reason": (
                f"{len(entries)} map(s) recorded {bucket} failures; train this stage "
                "separately so early deaths and late collapses do not hide each other."
            ),
        }
        stage["train_command"] = stage_command(
            stage,
            ent_coef=ent_coef,
            train_map_selection=train_map_selection,
            reward_profile=reward_profile,
        )
        stage["compare_commands"] = [
            compare_command(stage, eval_seconds=window_seconds)
            for window_seconds in validation_windows
        ]
        stage["compare_command"] = compare_command(stage, eval_seconds=stage["eval_seconds"])
        stages.append(stage)
        model_in = model_out
        stage_number += 1

    return {
        "report_version": 1,
        "source": str(analysis_path),
        "decision": "rl_curriculum_plan_created" if stages else "rl_curriculum_plan_no_failures",
        "initial_model": initial_model,
        "output_dir": output_dir,
        "timesteps_per_stage": timesteps_per_stage,
        "ent_coef": ent_coef,
        "reward_profile": reward_profile,
        "train_map_selection": train_map_selection,
        "validation_windows": validation_windows,
        "stage_count": len(stages),
        "stages": stages,
        "limitations": [
            "This manifest plans staged training commands only; it does not run PPO.",
            "Each stage must still be trained, compared against rule Bots, and recorded with failure cases if it fails.",
            "Stage ordering is based on failure time buckets and should be revised if new comparison evidence contradicts it.",
        ],
    }


def write_markdown(plan: dict[str, Any], path: Path) -> None:
    lines = [
        "# RL Curriculum Plan",
        "",
        f"- Source: `{plan['source']}`",
        f"- Decision: `{plan['decision']}`",
        f"- Initial model: `{plan['initial_model']}`",
        f"- Stage count: {plan['stage_count']}",
        "",
        "## Stages",
        "",
        "| Stage | Focus | Maps | Train Seconds | Eval Seconds | Timesteps |",
        "|---:|---|---|---:|---:|---:|",
    ]
    for stage in plan["stages"]:
        maps = ", ".join(f"`{item}`" for item in stage["train_maps"])
        lines.append(
            f"| {stage['stage']} | `{stage['focus_bucket']}` | {maps} | {stage['train_seconds']} | {stage['eval_seconds']} | {stage['timesteps']} |"
        )

    for stage in plan["stages"]:
        lines.extend(
            [
                "",
                f"## `{stage['id']}`",
                "",
                f"- Reason: {stage['reason']}",
                f"- Model in: `{stage['model_in']}`",
                f"- Model out: `{stage['model_out']}`",
                "",
                "Train:",
                "",
                "```bash",
                stage["train_command"],
                "```",
                "",
                "Compare:",
                "",
            ]
        )
        for command in stage["compare_commands"]:
            lines.extend(["```bash", command, "```", ""])

    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in plan["limitations"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an RL curriculum plan from failure analysis.")
    parser.add_argument("analysis", type=Path)
    parser.add_argument("--initial-model", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--timesteps-per-stage", type=int, default=5000)
    parser.add_argument("--ent-coef", type=float, default=0.02)
    parser.add_argument(
        "--reward-profile",
        choices=["late-survival", "long-run-retention", "late-route-recovery"],
        default="late-route-recovery",
    )
    parser.add_argument("--train-map-selection", choices=["cycle", "random"], default="random")
    parser.add_argument("--validation-seed-start", type=int, default=62000)
    parser.add_argument(
        "--validation-windows",
        default="60,180,300",
        help="Comma-separated deterministic validation windows in seconds.",
    )
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--markdown", type=Path, default=None)
    args = parser.parse_args()

    if args.timesteps_per_stage <= 0:
        parser.error("--timesteps-per-stage must be greater than zero")
    if args.ent_coef < 0.0:
        parser.error("--ent-coef must be greater than or equal to zero")
    try:
        validation_windows = parse_validation_windows(args.validation_windows)
    except ValueError as exc:
        parser.error(str(exc))

    plan = build_plan(
        args.analysis,
        initial_model=args.initial_model,
        output_dir=args.output_dir,
        timesteps_per_stage=args.timesteps_per_stage,
        ent_coef=args.ent_coef,
        reward_profile=args.reward_profile,
        train_map_selection=args.train_map_selection,
        validation_seed_start=args.validation_seed_start,
        validation_windows=validation_windows,
    )
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown is not None:
        write_markdown(plan, args.markdown)
    if args.report is None and args.markdown is None:
        print(json.dumps(plan, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
