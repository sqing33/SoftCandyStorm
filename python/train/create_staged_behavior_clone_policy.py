#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from python.train.train_behavior_clone import (
    DEFAULT_TIME_PHASE_THRESHOLDS,
    save_staged_behavior_clone_policy,
)


def write_report(path, payload):
    if path is None:
        print(json.dumps(payload, ensure_ascii=False))
        return
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Package opening/mid/late behavior clones as a staged policy.")
    parser.add_argument("--opening-model", required=True)
    parser.add_argument("--mid-model", required=True)
    parser.add_argument("--late-model", required=True)
    parser.add_argument("--time-phase-thresholds", type=float, nargs=2, default=DEFAULT_TIME_PHASE_THRESHOLDS)
    parser.add_argument(
        "--phase-duration-seconds",
        type=float,
        default=None,
        help="Optional absolute episode horizon used to dispatch staged phases from time_seconds during evaluation.",
    )
    parser.add_argument("--model-out", required=True)
    parser.add_argument("--report", default=None)
    args = parser.parse_args()

    report = save_staged_behavior_clone_policy(
        args.model_out,
        {
            "opening": args.opening_model,
            "mid": args.mid_model,
            "late": args.late_model,
        },
        args.time_phase_thresholds,
        phase_duration_seconds=args.phase_duration_seconds,
    )
    write_report(args.report, report)


if __name__ == "__main__":
    main()
