import argparse
import json
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from python.train.train_behavior_clone import (
    load_trajectory_dataset,
    summarize_dataset,
)
from python.train.train_sb3 import (
    dependency_status,
    load_behavior_clone_policy_with_optional_opening,
    load_config,
    policy_action_scores,
    require_dependencies,
    stable_baselines_model_classes,
)


TIME_BUCKETS = [
    ("opening_lt_60", 0.0, 60.0),
    ("mid_60_to_180", 60.0, 180.0),
    ("late_180_to_300", 180.0, 300.0),
    ("post_300", 300.0, math.inf),
]


def probability_distribution(action_scores, action_count):
    kind = action_scores.get("kind") if isinstance(action_scores, dict) else None
    raw_scores = action_scores.get("scores") if isinstance(action_scores, dict) else None
    if not isinstance(raw_scores, list) or len(raw_scores) < action_count:
        raise ValueError("policy action_scores must contain scores for every action")
    values = [float(value) for value in raw_scores[:action_count]]
    if kind == "probability":
        clipped = [max(0.0, value) for value in values]
        total = sum(clipped)
        if total <= 0.0:
            raise ValueError("probability action_scores sum to zero")
        return [value / total for value in clipped]
    if kind == "q_value":
        max_value = max(values)
        exp_values = [math.exp(value - max_value) for value in values]
        total = sum(exp_values)
        return [value / total for value in exp_values]
    raise ValueError(f"unsupported action_scores kind `{kind}`")


def entropy_nats(probabilities):
    return -sum(
        value * math.log(max(value, 1e-12))
        for value in probabilities
        if value > 0.0
    )


def kl_divergence(anchor_probabilities, candidate_probabilities):
    return sum(
        anchor * (math.log(max(anchor, 1e-12)) - math.log(max(candidate, 1e-12)))
        for anchor, candidate in zip(anchor_probabilities, candidate_probabilities)
        if anchor > 0.0
    )


def argmax(values):
    return max(range(len(values)), key=lambda index: values[index])


def time_bucket_label(time_seconds):
    value = float(time_seconds or 0.0)
    for label, start, end in TIME_BUCKETS:
        if start <= value < end:
            return label
    return "unknown"


def empty_alignment_bucket():
    return {
        "sample_count": 0,
        "kl_total": 0.0,
        "max_kl": 0.0,
        "argmax_agreement_count": 0,
        "anchor_entropy_total": 0.0,
        "candidate_entropy_total": 0.0,
    }


def record_alignment(bucket, anchor_probabilities, candidate_probabilities):
    kl_value = kl_divergence(anchor_probabilities, candidate_probabilities)
    bucket["sample_count"] += 1
    bucket["kl_total"] += kl_value
    bucket["max_kl"] = max(bucket["max_kl"], kl_value)
    if argmax(anchor_probabilities) == argmax(candidate_probabilities):
        bucket["argmax_agreement_count"] += 1
    bucket["anchor_entropy_total"] += entropy_nats(anchor_probabilities)
    bucket["candidate_entropy_total"] += entropy_nats(candidate_probabilities)


def finalize_alignment_bucket(bucket):
    sample_count = int(bucket["sample_count"])
    if sample_count == 0:
        return {
            "sample_count": 0,
            "mean_kl": None,
            "max_kl": None,
            "argmax_agreement": None,
            "anchor_entropy_nats": None,
            "candidate_entropy_nats": None,
        }
    return {
        "sample_count": sample_count,
        "mean_kl": round(bucket["kl_total"] / sample_count, 6),
        "max_kl": round(bucket["max_kl"], 6),
        "argmax_agreement": round(bucket["argmax_agreement_count"] / sample_count, 4),
        "anchor_entropy_nats": round(bucket["anchor_entropy_total"] / sample_count, 6),
        "candidate_entropy_nats": round(bucket["candidate_entropy_total"] / sample_count, 6),
    }


def maybe_call(policy, method_name, *args):
    method = getattr(policy, method_name, None)
    if callable(method):
        method(*args)


def set_policy_context(policy, sample):
    maybe_call(
        policy,
        "set_step_context",
        {
            "time_seconds": sample.get("time_seconds", 0.0),
            "map_id": sample.get("map_id"),
            "seed": sample.get("seed"),
        },
    )


def build_threshold_blockers(report, max_mean_kl, min_argmax_agreement, max_bucket_mean_kl):
    blockers = []
    overall = report["overall"]
    if max_mean_kl is not None and overall["mean_kl"] is not None:
        if overall["mean_kl"] > max_mean_kl:
            blockers.append(
                f"overall mean_kl {overall['mean_kl']} exceeds {max_mean_kl}"
            )
    if min_argmax_agreement is not None and overall["argmax_agreement"] is not None:
        if overall["argmax_agreement"] < min_argmax_agreement:
            blockers.append(
                "overall argmax_agreement "
                f"{overall['argmax_agreement']} below {min_argmax_agreement}"
            )
    if max_bucket_mean_kl is not None:
        for section_name in ("by_map", "by_time_bucket"):
            for key, item in report[section_name].items():
                mean_kl = item.get("mean_kl")
                if mean_kl is not None and mean_kl > max_bucket_mean_kl:
                    blockers.append(
                        f"{section_name}/{key}: mean_kl {mean_kl} exceeds {max_bucket_mean_kl}"
                    )
    return blockers


def compare_policies_to_anchor(
    dataset,
    candidate_policy,
    anchor_policy,
    sample_stride=1,
    limit_samples=None,
):
    if sample_stride <= 0:
        raise ValueError("sample_stride must be greater than 0")
    if limit_samples is not None and limit_samples <= 0:
        raise ValueError("limit_samples must be greater than 0")

    action_count = int(dataset["action_count"])
    overall = empty_alignment_bucket()
    by_map = {}
    by_time_bucket = {}
    active_episode = None
    compared = 0

    for index, (observation, sample) in enumerate(
        zip(dataset["observations"], dataset["sample_metadata"])
    ):
        if index % sample_stride != 0:
            continue
        if limit_samples is not None and compared >= limit_samples:
            break

        episode_key = (sample.get("path"), sample.get("seed"), sample.get("map_id"))
        if episode_key != active_episode:
            for policy in (candidate_policy, anchor_policy):
                maybe_call(policy, "reset")
                maybe_call(policy, "set_map_id", sample.get("map_id"))
            active_episode = episode_key

        for policy in (candidate_policy, anchor_policy):
            set_policy_context(policy, sample)

        anchor_probabilities = probability_distribution(
            policy_action_scores(anchor_policy, observation),
            action_count,
        )
        candidate_probabilities = probability_distribution(
            policy_action_scores(candidate_policy, observation),
            action_count,
        )

        map_id = sample.get("map_id") or "unknown"
        bucket_label = time_bucket_label(sample.get("time_seconds", 0.0))
        by_map.setdefault(map_id, empty_alignment_bucket())
        by_time_bucket.setdefault(bucket_label, empty_alignment_bucket())

        for bucket in (overall, by_map[map_id], by_time_bucket[bucket_label]):
            record_alignment(bucket, anchor_probabilities, candidate_probabilities)
        compared += 1

    return {
        "overall": finalize_alignment_bucket(overall),
        "by_map": {
            key: finalize_alignment_bucket(value)
            for key, value in sorted(by_map.items())
        },
        "by_time_bucket": {
            key: finalize_alignment_bucket(value)
            for key, value in sorted(by_time_bucket.items())
        },
    }


def decision_for(blockers, thresholds_enabled):
    if blockers:
        return "behavior_clone_anchor_alignment_failed"
    if thresholds_enabled:
        return "behavior_clone_anchor_alignment_within_thresholds"
    return "behavior_clone_anchor_alignment_recorded"


def build_report(
    *,
    dataset,
    alignment,
    candidate_model,
    anchor_model,
    opening_model,
    opening_seconds,
    sample_stride,
    limit_samples,
    max_mean_kl,
    min_argmax_agreement,
    max_bucket_mean_kl,
):
    report = {
        "report_version": 1,
        "candidate_model": str(candidate_model),
        "anchor_model": str(anchor_model),
        "opening_model": str(opening_model) if opening_model else None,
        "opening_seconds": opening_seconds if opening_model else None,
        "dataset": summarize_dataset(dataset),
        "sample_stride": sample_stride,
        "limit_samples": limit_samples,
        "dependency_status": dependency_status(),
        "thresholds": {
            "max_mean_kl": max_mean_kl,
            "min_argmax_agreement": min_argmax_agreement,
            "max_bucket_mean_kl": max_bucket_mean_kl,
        },
        **alignment,
        "blockers": [],
        "warnings": [],
        "limitations": [
            "This report checks policy-anchor alignment on supplied offline samples only.",
            "A passing alignment threshold is repair evidence, not RL policy acceptance.",
            "The candidate still requires deterministic high-pressure comparison and no-regression checks.",
        ],
    }
    report["blockers"] = build_threshold_blockers(
        report,
        max_mean_kl,
        min_argmax_agreement,
        max_bucket_mean_kl,
    )
    thresholds_enabled = any(
        value is not None
        for value in (max_mean_kl, min_argmax_agreement, max_bucket_mean_kl)
    )
    if not thresholds_enabled:
        report["warnings"].append("no thresholds were provided; report is diagnostic only")
    report["decision"] = decision_for(report["blockers"], thresholds_enabled)
    report["gate_decision"] = report["decision"]
    return report


def compare_from_args(args):
    require_dependencies()
    config = load_config(args.config)
    dataset = load_trajectory_dataset(args.dataset, limit=args.dataset_limit)
    model_class = stable_baselines_model_classes()[args.algorithm]
    candidate_policy = model_class.load(args.model)
    anchor_policy = load_behavior_clone_policy_with_optional_opening(
        args.opening_algorithm,
        Path(args.anchor_model),
        opening_model_path=Path(args.opening_model) if args.opening_model else None,
        opening_seconds=args.opening_seconds,
    )
    alignment = compare_policies_to_anchor(
        dataset,
        candidate_policy,
        anchor_policy,
        sample_stride=args.sample_stride,
        limit_samples=args.limit_samples,
    )
    return build_report(
        dataset=dataset,
        alignment=alignment,
        candidate_model=Path(args.model),
        anchor_model=Path(args.anchor_model),
        opening_model=Path(args.opening_model) if args.opening_model else None,
        opening_seconds=args.opening_seconds,
        sample_stride=args.sample_stride,
        limit_samples=args.limit_samples,
        max_mean_kl=args.max_mean_kl,
        min_argmax_agreement=args.min_argmax_agreement,
        max_bucket_mean_kl=args.max_bucket_mean_kl,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Compare an SB3 policy against a behavior-clone anchor on offline samples."
    )
    parser.add_argument("--config", default="python/train/rl_training_config.json")
    parser.add_argument("--algorithm", choices=["dqn", "ppo"], default="ppo")
    parser.add_argument("--model", required=True)
    parser.add_argument("--anchor-model", required=True)
    parser.add_argument(
        "--opening-model",
        default=None,
        help="Optional SB3 zip used by the anchor before --opening-seconds.",
    )
    parser.add_argument(
        "--opening-algorithm",
        choices=["dqn", "ppo"],
        default="ppo",
        help="SB3 algorithm class used to load --opening-model.",
    )
    parser.add_argument("--opening-seconds", type=float, default=60.0)
    parser.add_argument("--dataset", action="append", required=True)
    parser.add_argument("--dataset-limit", type=int, default=None)
    parser.add_argument("--sample-stride", type=int, default=1)
    parser.add_argument("--limit-samples", type=int, default=None)
    parser.add_argument("--max-mean-kl", type=float, default=None)
    parser.add_argument("--min-argmax-agreement", type=float, default=None)
    parser.add_argument("--max-bucket-mean-kl", type=float, default=None)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()

    if args.opening_seconds <= 0.0:
        parser.error("--opening-seconds must be greater than zero")
    if args.dataset_limit is not None and args.dataset_limit <= 0:
        parser.error("--dataset-limit must be greater than zero")
    if args.sample_stride <= 0:
        parser.error("--sample-stride must be greater than zero")
    if args.limit_samples is not None and args.limit_samples <= 0:
        parser.error("--limit-samples must be greater than zero")
    if args.max_mean_kl is not None and args.max_mean_kl < 0.0:
        parser.error("--max-mean-kl must be non-negative")
    if args.max_bucket_mean_kl is not None and args.max_bucket_mean_kl < 0.0:
        parser.error("--max-bucket-mean-kl must be non-negative")
    if args.min_argmax_agreement is not None and not (0.0 <= args.min_argmax_agreement <= 1.0):
        parser.error("--min-argmax-agreement must be between 0 and 1")

    report = compare_from_args(args)
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
