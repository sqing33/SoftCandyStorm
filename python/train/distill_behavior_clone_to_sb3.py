import argparse
import json
import math
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from python.train.train_behavior_clone import (
    load_trajectory_dataset,
    parse_sample_path_weight_spec,
    recovery_top_k_distribution,
    summarize_dataset,
    normalize_sample_path_weights,
    sample_path_weight_for,
)
from python.train.train_sb3 import (
    algorithm_config,
    anchor_time_bucket_label,
    build_env,
    dependency_status,
    load_behavior_clone_policy_with_optional_opening,
    load_config,
    require_dependencies,
    stable_baselines_model_classes,
)


def one_hot(action, action_count, np_module):
    values = np_module.zeros(action_count, dtype=np_module.float32)
    values[int(action)] = 1.0
    return values


def normalized_probabilities(values, action_count, np_module):
    probabilities = np_module.asarray(values[:action_count], dtype=np_module.float32)
    probabilities = np_module.clip(probabilities, 0.0, 1.0)
    total = float(probabilities.sum())
    if total <= 0.0:
        raise ValueError("teacher returned an empty probability distribution")
    return probabilities / total


def target_entropy(probabilities, np_module):
    clipped = np_module.clip(probabilities, 1e-8, 1.0)
    return float(-(clipped * np_module.log(clipped)).sum())


def soften_probabilities(probabilities, temperature, np_module):
    if temperature == 1.0:
        return probabilities
    clipped = np_module.clip(probabilities, 1e-8, 1.0)
    logits = np_module.log(clipped) / temperature
    logits = logits - float(logits.max())
    softened = np_module.exp(logits)
    return softened / float(softened.sum())


def mix_with_uniform(probabilities, uniform_mix, np_module):
    if uniform_mix == 0.0:
        return probabilities
    action_count = int(len(probabilities))
    uniform = np_module.full(action_count, 1.0 / action_count, dtype=np_module.float32)
    mixed = probabilities * (1.0 - uniform_mix) + uniform * uniform_mix
    return mixed / float(mixed.sum())


def transform_target_probabilities(probabilities, temperature, uniform_mix, np_module):
    transformed = soften_probabilities(probabilities, temperature, np_module)
    return mix_with_uniform(transformed, uniform_mix, np_module)


def target_transform_report(temperature, uniform_mix):
    return {
        "teacher_temperature": temperature,
        "uniform_target_mix": uniform_mix,
    }


RECOVERY_SAMPLE_SOURCES = {
    "edge_recovery_supervision",
    "risk_recovery_supervision",
}

RECOVERY_TARGET_SOURCE_ALIASES = {
    "edge": "edge_recovery_supervision",
    "risk": "risk_recovery_supervision",
}

ACTION_DISTRIBUTION_GUARD_SCOPES = {
    "overall",
    "sample_sources",
    "sample_path_weights",
    "map_time_buckets",
}


def parse_recovery_target_sources(value):
    if value is None:
        return set(RECOVERY_SAMPLE_SOURCES)
    sources = set()
    for item in str(value).split(","):
        key = item.strip()
        if not key:
            continue
        if key not in RECOVERY_TARGET_SOURCE_ALIASES:
            raise ValueError(
                "--recovery-target-sources entries must be one of: "
                + ", ".join(sorted(RECOVERY_TARGET_SOURCE_ALIASES))
            )
        sources.add(RECOVERY_TARGET_SOURCE_ALIASES[key])
    if not sources:
        raise ValueError("--recovery-target-sources must include at least one source")
    return sources


def parse_recovery_target_maps(value):
    if value is None:
        return None
    maps = {item.strip() for item in str(value).split(",") if item.strip()}
    if not maps:
        raise ValueError("--recovery-target-maps must include at least one map id")
    return maps


def parse_action_distribution_guard_scope(value):
    if value is None:
        return [
            "overall",
            "sample_sources",
            "sample_path_weights",
            "map_time_buckets",
        ]
    if isinstance(value, str):
        scopes = [item.strip() for item in value.split(",") if item.strip()]
    else:
        scopes = [str(item).strip() for item in value if str(item).strip()]
    if not scopes:
        raise ValueError("--action-distribution-guard-scope must include a scope")
    unknown = sorted(set(scopes) - ACTION_DISTRIBUTION_GUARD_SCOPES)
    if unknown:
        raise ValueError(
            "--action-distribution-guard-scope contains unknown scope(s): "
            + ", ".join(unknown)
        )
    return list(dict.fromkeys(scopes))


def recovery_target_override_report(
    mode,
    primary_mass,
    top_k,
    sources,
    maps=None,
    min_seconds=None,
    max_seconds=None,
):
    return {
        "mode": mode,
        "sources": sorted(sources),
        "maps": sorted(maps) if maps is not None else None,
        "min_seconds": min_seconds,
        "max_seconds": max_seconds,
        "primary_mass": round(float(primary_mass), 6),
        "top_k": int(top_k),
        "overridden_sample_count": 0,
        "soft_sample_count": 0,
        "fallback_one_hot_count": 0,
        "source_scoped_out_sample_count": 0,
        "map_scoped_out_sample_count": 0,
        "time_scoped_out_sample_count": 0,
        "average_nonzero_actions": None,
    }


def normalize_dataset_action_target_paths(values):
    if not values:
        return []
    result = []
    for value in values:
        for item in str(value).split(","):
            path = item.strip()
            if path:
                result.append({"path": path, "weight": 1.0})
    return result


def dataset_action_target_override_report(paths, uniform_mix):
    normalized_paths = normalize_dataset_action_target_paths(paths)
    return {
        "enabled": bool(normalized_paths),
        "mode": "dataset_actions_by_path" if normalized_paths else "none",
        "paths": [item["path"] for item in normalized_paths],
        "uniform_target_mix": uniform_mix,
        "overridden_sample_count": 0,
        "average_nonzero_actions": None,
        "entries": [
            {
                "path": item["path"],
                "matched_sample_count": 0,
            }
            for item in normalized_paths
        ],
    }


def recovery_target_override_distribution(
    sample,
    action,
    action_count,
    mode,
    primary_mass,
    top_k,
    enabled_sources,
    enabled_maps,
    min_seconds,
    max_seconds,
    np_module,
):
    sample_source = sample.get("sample_source")
    if sample_source not in RECOVERY_SAMPLE_SOURCES:
        return None, False, "not_recovery"
    if sample_source not in enabled_sources:
        return None, False, "source"
    if enabled_maps is not None and str(sample.get("map_id")) not in enabled_maps:
        return None, False, "map"
    time_seconds = float(sample.get("time_seconds", 0.0))
    if min_seconds is not None and time_seconds < min_seconds:
        return None, False, "time"
    if max_seconds is not None and time_seconds >= max_seconds:
        return None, False, "time"
    if mode == "teacher_probs":
        return None, False, "teacher_probs"
    if mode == "dataset_actions":
        return one_hot(action, action_count, np_module), False, "matched"
    if mode == "top_k_scores":
        distribution = recovery_top_k_distribution(
            sample,
            action,
            action_count,
            primary_mass,
            top_k,
            np_module,
        )
        if distribution is not None:
            return distribution, True, "matched"
        return one_hot(action, action_count, np_module), False, "matched"
    raise ValueError(f"unsupported recovery target mode: {mode}")


def collect_distillation_targets(
    dataset,
    teacher_model,
    target_mode,
    teacher_temperature,
    uniform_target_mix,
    np_module,
    opening_algorithm="ppo",
    opening_model=None,
    opening_seconds=60.0,
    recovery_target_mode="teacher_probs",
    recovery_target_sources=None,
    recovery_target_maps=None,
    recovery_target_min_seconds=None,
    recovery_target_max_seconds=None,
    recovery_soft_target_primary_mass=0.65,
    recovery_soft_target_top_k=3,
    dataset_action_target_paths=None,
):
    action_count = int(dataset["action_count"])
    enabled_recovery_sources = set(recovery_target_sources or RECOVERY_SAMPLE_SOURCES)
    enabled_recovery_maps = (
        set(recovery_target_maps) if recovery_target_maps is not None else None
    )
    normalized_dataset_action_paths = normalize_dataset_action_target_paths(
        dataset_action_target_paths
    )
    if target_mode == "dataset_actions":
        targets = [
            transform_target_probabilities(
                one_hot(action, action_count, np_module),
                1.0,
                uniform_target_mix,
                np_module,
            )
            for action in dataset["actions"]
        ]
        return np_module.asarray(targets, dtype=np_module.float32), {
            "mode": target_mode,
            "teacher_model": None,
            "opening_model": None,
            "opening_seconds": None,
            "teacher_argmax_agreement": None,
            "target_transform": target_transform_report(1.0, uniform_target_mix),
            "recovery_target_override": recovery_target_override_report(
                "not_applicable_global_dataset_actions",
                recovery_soft_target_primary_mass,
                recovery_soft_target_top_k,
                enabled_recovery_sources,
                enabled_recovery_maps,
                recovery_target_min_seconds,
                recovery_target_max_seconds,
            ),
            "dataset_action_target_override": dataset_action_target_override_report(
                [],
                uniform_target_mix,
            ),
            "target_entropy_nats": round(
                sum(target_entropy(target, np_module) for target in targets)
                / max(1, len(targets)),
                6,
            ),
            "target_argmax_distribution": action_distribution(
                [int(action) for action in dataset["actions"]],
                action_count,
            ),
        }

    teacher = load_behavior_clone_policy_with_optional_opening(
        opening_algorithm,
        teacher_model,
        opening_model_path=opening_model,
        opening_seconds=opening_seconds,
    )
    targets = []
    teacher_argmax_actions = []
    agreement_count = 0
    active_episode = None
    override_report = recovery_target_override_report(
        recovery_target_mode,
        recovery_soft_target_primary_mass,
        recovery_soft_target_top_k,
        enabled_recovery_sources,
        enabled_recovery_maps,
        recovery_target_min_seconds,
        recovery_target_max_seconds,
    )
    override_nonzero_action_total = 0
    dataset_action_override_report = dataset_action_target_override_report(
        dataset_action_target_paths,
        uniform_target_mix,
    )
    dataset_action_override_entries = {
        item["path"]: item for item in dataset_action_override_report["entries"]
    }
    dataset_action_override_nonzero_action_total = 0
    for observation, action, sample in zip(
        dataset["observations"],
        dataset["actions"],
        dataset["sample_metadata"],
    ):
        episode_key = (sample.get("path"), sample.get("seed"))
        if episode_key != active_episode:
            teacher.reset()
            set_map_id = getattr(teacher, "set_map_id", None)
            if callable(set_map_id):
                set_map_id(sample.get("map_id"))
            active_episode = episode_key
        set_step_context = getattr(teacher, "set_step_context", None)
        if callable(set_step_context):
            set_step_context(
                {
                    "time_seconds": sample.get("time_seconds", 0.0),
                    "map_id": sample.get("map_id"),
                    "seed": sample.get("seed"),
                }
            )
        predicted_action, _state = teacher.predict(observation, deterministic=True)
        scores = teacher.action_scores(observation)
        if scores.get("kind") != "probability":
            raise ValueError(
                "teacher model must expose probability action_scores for soft distillation"
            )
        probabilities = normalized_probabilities(
            scores.get("scores", []),
            action_count,
            np_module,
        )
        probabilities = transform_target_probabilities(
            probabilities,
            teacher_temperature,
            uniform_target_mix,
            np_module,
        )
        (
            override_distribution,
            used_soft_target,
            override_scope,
        ) = recovery_target_override_distribution(
            sample,
            action,
            action_count,
            recovery_target_mode,
            recovery_soft_target_primary_mass,
            recovery_soft_target_top_k,
            enabled_recovery_sources,
            enabled_recovery_maps,
            recovery_target_min_seconds,
            recovery_target_max_seconds,
            np_module,
        )
        if override_scope == "source":
            override_report["source_scoped_out_sample_count"] += 1
        elif override_scope == "map":
            override_report["map_scoped_out_sample_count"] += 1
        elif override_scope == "time":
            override_report["time_scoped_out_sample_count"] += 1
        if override_distribution is not None:
            probabilities = override_distribution
            override_report["overridden_sample_count"] += 1
            if used_soft_target:
                override_report["soft_sample_count"] += 1
            else:
                override_report["fallback_one_hot_count"] += 1
            override_nonzero_action_total += int((probabilities > 0.0).sum())
        if normalized_dataset_action_paths:
            _multiplier, matched_paths = sample_path_weight_for(
                sample.get("path"),
                normalized_dataset_action_paths,
            )
            if matched_paths:
                probabilities = transform_target_probabilities(
                    one_hot(action, action_count, np_module),
                    1.0,
                    uniform_target_mix,
                    np_module,
                )
                dataset_action_override_report["overridden_sample_count"] += 1
                dataset_action_override_nonzero_action_total += int(
                    (probabilities > 0.0).sum()
                )
                for path in matched_paths:
                    dataset_action_override_entries[path]["matched_sample_count"] += 1
        targets.append(probabilities)
        teacher_argmax = int(predicted_action)
        teacher_argmax_actions.append(teacher_argmax)
        if teacher_argmax == int(action):
            agreement_count += 1

    if override_report["overridden_sample_count"]:
        override_report["average_nonzero_actions"] = round(
            override_nonzero_action_total / override_report["overridden_sample_count"],
            4,
        )
    if dataset_action_override_report["overridden_sample_count"]:
        dataset_action_override_report["average_nonzero_actions"] = round(
            dataset_action_override_nonzero_action_total
            / dataset_action_override_report["overridden_sample_count"],
            4,
        )

    return np_module.asarray(targets, dtype=np_module.float32), {
        "mode": target_mode,
        "teacher_model": str(teacher_model),
        "opening_model": str(opening_model) if opening_model else None,
        "opening_seconds": opening_seconds if opening_model else None,
        "teacher_argmax_agreement": round(
            agreement_count / max(1, len(dataset["actions"])),
            4,
        ),
        "target_transform": target_transform_report(
            teacher_temperature,
            uniform_target_mix,
        ),
        "recovery_target_override": override_report,
        "dataset_action_target_override": dataset_action_override_report,
        "target_entropy_nats": round(
            sum(target_entropy(target, np_module) for target in targets)
            / max(1, len(targets)),
            6,
        ),
        "target_argmax_distribution": action_distribution(
            teacher_argmax_actions,
            action_count,
        ),
    }


def action_distribution(actions, action_count):
    counts = {str(action): 0 for action in range(action_count)}
    for action in actions:
        counts[str(action)] = counts.get(str(action), 0) + 1
    total = max(1, len(actions))
    return {
        action: {
            "count": count,
            "ratio": round(count / total, 4),
        }
        for action, count in counts.items()
    }


def dominant_action(distribution):
    action, value = max(
        distribution.items(),
        key=lambda item: item[1]["ratio"],
        default=(None, None),
    )
    if action is None:
        return None
    return {
        "action": action,
        "count": value["count"],
        "ratio": value["ratio"],
    }


def action_entropy_bits(distribution):
    entropy = 0.0
    for value in distribution.values():
        ratio = value["ratio"]
        if ratio > 0.0:
            entropy -= ratio * math.log2(ratio)
    return round(entropy, 4)


def normalized_action_entropy(distribution):
    action_count = max(1, len(distribution))
    max_entropy = math.log2(action_count) if action_count > 1 else 1.0
    if max_entropy <= 0.0:
        return 0.0
    return round(action_entropy_bits(distribution) / max_entropy, 4)


def tensor_distribution_logits(model, observations, torch_module):
    distribution = model.policy.get_distribution(observations)
    torch_distribution = getattr(distribution, "distribution", None)
    logits = getattr(torch_distribution, "logits", None)
    if logits is None:
        probabilities = getattr(torch_distribution, "probs", None)
        if probabilities is None:
            raise ValueError("SB3 policy distribution does not expose logits or probs")
        logits = torch_module.log(probabilities.clamp_min(1e-8))
    return logits


def load_distillation_dataset(
    dataset_paths,
    *,
    limit=None,
    include_anchor_drift_samples=False,
):
    return load_trajectory_dataset(
        dataset_paths,
        limit=limit,
        include_anchor_drift_samples=include_anchor_drift_samples,
    )


def build_distillation_sample_weights(dataset, indices, sample_path_weights, np_module):
    normalized_path_weights = normalize_sample_path_weights(sample_path_weights)
    if not normalized_path_weights:
        return None, {
            "mode": "none",
            "min": 1.0,
            "max": 1.0,
            "mean": 1.0,
            "sample_path_weights": {
                "enabled": False,
                "weighted_sample_count": 0,
                "weighted_sample_ratio": 0.0,
                "entries": [],
            },
        }

    path_weight_matches = {
        item["path"]: {
            "path": item["path"],
            "weight": item["weight"],
            "matched_train_samples": 0,
        }
        for item in normalized_path_weights
    }
    values = []
    weighted_sample_count = 0
    for index in indices:
        sample = dataset["sample_metadata"][int(index)]
        multiplier, matched_paths = sample_path_weight_for(
            sample.get("path"),
            normalized_path_weights,
        )
        if matched_paths:
            weighted_sample_count += 1
            for path in matched_paths:
                path_weight_matches[path]["matched_train_samples"] += 1
        values.append(multiplier)

    weights = np_module.asarray(values, dtype=np_module.float32)
    return weights, {
        "mode": "sample_path_auxiliary",
        "min": round(float(weights.min()), 6),
        "max": round(float(weights.max()), 6),
        "mean": round(float(weights.mean()), 6),
        "sample_path_weights": {
            "enabled": True,
            "weighted_sample_count": int(weighted_sample_count),
            "weighted_sample_ratio": round(
                weighted_sample_count / max(1, len(indices)),
                4,
            ),
            "entries": list(path_weight_matches.values()),
        },
    }


def evaluate_supervised(model, observations, targets, torch_module):
    model.policy.set_training_mode(False)
    with torch_module.no_grad():
        logits = tensor_distribution_logits(model, observations, torch_module)
        log_probs = torch_module.log_softmax(logits, dim=-1)
        loss = -(targets * log_probs).sum(dim=1).mean()
        predictions = logits.argmax(dim=1)
        labels = targets.argmax(dim=1)
        accuracy = (predictions == labels).float().mean()
        entropy = -(torch_module.softmax(logits, dim=-1) * log_probs).sum(dim=1).mean()
        predicted_actions = [int(action) for action in predictions.cpu().tolist()]
    model.policy.set_training_mode(True)
    prediction_distribution = action_distribution(
        predicted_actions,
        int(targets.shape[1]),
    )
    return {
        "loss": round(float(loss.item()), 6),
        "argmax_accuracy": round(float(accuracy.item()), 4),
        "policy_entropy_nats": round(float(entropy.item()), 6),
        "policy_argmax_action_distribution": prediction_distribution,
        "dominant_policy_argmax_action": dominant_action(prediction_distribution),
        "policy_argmax_action_entropy_bits": action_entropy_bits(prediction_distribution),
        "normalized_policy_argmax_action_entropy": normalized_action_entropy(
            prediction_distribution
        ),
    }


def build_distillation_validation_slice_groups(dataset, indices, sample_path_weights):
    validation_indices = [int(index) for index in indices]
    sample_metadata = dataset["sample_metadata"]
    source_groups = {}
    for index in validation_indices:
        sample = sample_metadata[index]
        source = sample.get("sample_source") or "trajectory"
        source_groups.setdefault(source, []).append(index)

    map_time_groups = {}
    for index in validation_indices:
        sample = sample_metadata[index]
        map_id = str(sample.get("map_id") or "unknown_map")
        bucket = anchor_time_bucket_label(sample.get("time_seconds", 0.0))
        map_time_groups.setdefault(f"{map_id}::{bucket}", []).append(index)

    normalized_path_weights = normalize_sample_path_weights(sample_path_weights)
    path_groups = [
        {
            "path": item["path"],
            "weight": item["weight"],
            "indices": [],
        }
        for item in normalized_path_weights
    ]
    path_group_by_path = {item["path"]: item for item in path_groups}
    if normalized_path_weights:
        for index in validation_indices:
            sample = sample_metadata[index]
            _multiplier, matched_paths = sample_path_weight_for(
                sample.get("path"),
                normalized_path_weights,
            )
            for path in matched_paths:
                path_group_by_path[path]["indices"].append(index)

    return {
        "sample_sources": source_groups,
        "map_time_buckets": map_time_groups,
        "sample_path_weights": path_groups,
    }


def evaluate_supervised_indices(model, observations, targets, indices, torch_module):
    selected_indices = [int(index) for index in indices]
    if not selected_indices:
        return {
            "sample_count": 0,
            "loss": None,
            "argmax_accuracy": None,
            "policy_entropy_nats": None,
        }
    selected_observations = torch_module.from_numpy(observations[selected_indices])
    selected_targets = torch_module.from_numpy(targets[selected_indices])
    metrics = evaluate_supervised(
        model,
        selected_observations,
        selected_targets,
        torch_module,
    )
    return {
        "sample_count": len(selected_indices),
        **metrics,
    }


def evaluate_distillation_validation_slices(
    model,
    observations,
    targets,
    dataset,
    validation_indices,
    sample_path_weights,
    torch_module,
):
    groups = build_distillation_validation_slice_groups(
        dataset,
        validation_indices,
        sample_path_weights,
    )
    return {
        "overall": evaluate_supervised_indices(
            model,
            observations,
            targets,
            validation_indices,
            torch_module,
        ),
        "sample_sources": {
            source: evaluate_supervised_indices(
                model,
                observations,
                targets,
                indices,
                torch_module,
            )
            for source, indices in sorted(groups["sample_sources"].items())
        },
        "map_time_buckets": {
            label: evaluate_supervised_indices(
                model,
                observations,
                targets,
                indices,
                torch_module,
            )
            for label, indices in sorted(groups["map_time_buckets"].items())
        },
        "sample_path_weights": {
            "enabled": bool(groups["sample_path_weights"]),
            "entries": [
                {
                    "path": item["path"],
                    "weight": item["weight"],
                    **evaluate_supervised_indices(
                        model,
                        observations,
                        targets,
                        item["indices"],
                        torch_module,
                    ),
                }
                for item in groups["sample_path_weights"]
            ],
        },
    }


def validate_action_distribution_guard_thresholds(
    max_dominant_ratio=None,
    min_normalized_entropy=None,
    min_sample_count=1,
):
    if max_dominant_ratio is not None and not (0.0 <= max_dominant_ratio <= 1.0):
        raise ValueError(
            "--action-distribution-guard-max-dominant-ratio must be between 0 and 1"
        )
    if min_normalized_entropy is not None and not (
        0.0 <= min_normalized_entropy <= 1.0
    ):
        raise ValueError(
            "--action-distribution-guard-min-normalized-entropy must be between 0 and 1"
        )
    if min_sample_count <= 0:
        raise ValueError("--action-distribution-guard-min-sample-count must be positive")
    return max_dominant_ratio is not None or min_normalized_entropy is not None


def action_distribution_guard_config(
    max_dominant_ratio=None,
    min_normalized_entropy=None,
    min_sample_count=1,
    scope=None,
):
    enabled = validate_action_distribution_guard_thresholds(
        max_dominant_ratio=max_dominant_ratio,
        min_normalized_entropy=min_normalized_entropy,
        min_sample_count=min_sample_count,
    )
    parsed_scope = parse_action_distribution_guard_scope(scope)
    return {
        "enabled": enabled,
        "max_dominant_ratio": max_dominant_ratio,
        "min_normalized_entropy": min_normalized_entropy,
        "min_sample_count": int(min_sample_count),
        "scope": parsed_scope,
        "notes": [
            "This guard checks offline validation argmax action concentration after supervised SB3 distillation.",
            "It blocks limited follow-up evidence only; deterministic high-pressure and no-regression gates are still required.",
        ],
    }


def iter_action_distribution_guard_slices(validation_slices, scope):
    enabled_scope = set(scope)
    overall = validation_slices.get("overall")
    if "overall" in enabled_scope and isinstance(overall, dict):
        yield "overall", overall
    if "sample_sources" in enabled_scope:
        for source, metrics in validation_slices.get("sample_sources", {}).items():
            if isinstance(metrics, dict):
                yield f"sample_source:{source}", metrics
    if "sample_path_weights" in enabled_scope:
        path_section = validation_slices.get("sample_path_weights", {})
        for entry in path_section.get("entries", []):
            if isinstance(entry, dict):
                yield f"sample_path_weight:{entry.get('path')}", entry
    if "map_time_buckets" in enabled_scope:
        for label, metrics in validation_slices.get("map_time_buckets", {}).items():
            if isinstance(metrics, dict):
                yield f"map_time_bucket:{label}", metrics


def evaluate_action_distribution_guard(validation_slices, guard_config):
    if not guard_config.get("enabled"):
        return {
            "decision": "action_distribution_guard_not_configured",
            "config": guard_config,
            "checked_slice_count": 0,
            "blockers": [],
            "slices": [],
        }

    blockers = []
    checked_slices = []
    min_sample_count = int(guard_config.get("min_sample_count") or 1)
    max_dominant_ratio = guard_config.get("max_dominant_ratio")
    min_normalized_entropy = guard_config.get("min_normalized_entropy")
    scope = parse_action_distribution_guard_scope(guard_config.get("scope"))
    for label, metrics in iter_action_distribution_guard_slices(validation_slices, scope):
        sample_count = int(metrics.get("sample_count") or 0)
        if sample_count < min_sample_count:
            continue
        dominant = metrics.get("dominant_policy_argmax_action")
        dominant_ratio = dominant.get("ratio") if isinstance(dominant, dict) else None
        normalized_entropy = metrics.get("normalized_policy_argmax_action_entropy")
        slice_blockers = []
        if max_dominant_ratio is not None:
            if dominant_ratio is None:
                slice_blockers.append("missing dominant policy argmax ratio")
            elif dominant_ratio > max_dominant_ratio:
                slice_blockers.append(
                    "dominant_policy_argmax_action_ratio "
                    f"{dominant_ratio} above max {max_dominant_ratio}"
                )
        if min_normalized_entropy is not None:
            if normalized_entropy is None:
                slice_blockers.append("missing normalized policy argmax action entropy")
            elif normalized_entropy < min_normalized_entropy:
                slice_blockers.append(
                    "normalized_policy_argmax_action_entropy "
                    f"{normalized_entropy} below min {min_normalized_entropy}"
                )
        if slice_blockers:
            blockers.extend(f"{label}: {item}" for item in slice_blockers)
        checked_slices.append(
            {
                "label": label,
                "sample_count": sample_count,
                "dominant_policy_argmax_action": dominant,
                "normalized_policy_argmax_action_entropy": normalized_entropy,
                "status": "blocked" if slice_blockers else "pass",
                "blockers": slice_blockers,
            }
        )

    decision = (
        "action_distribution_guard_failed"
        if blockers
        else "action_distribution_guard_passed"
    )
    return {
        "decision": decision,
        "config": guard_config,
        "checked_slice_count": len(checked_slices),
        "blockers": blockers,
        "slices": checked_slices,
    }


def distill(config, args):
    require_dependencies()
    import numpy as np
    import torch
    from torch.utils.data import DataLoader, TensorDataset

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    dataset = load_distillation_dataset(
        args.dataset,
        limit=args.limit_samples,
        include_anchor_drift_samples=args.include_anchor_drift_samples,
    )
    targets, target_report = collect_distillation_targets(
        dataset,
        Path(args.teacher_model) if args.teacher_model else None,
        args.target_mode,
        args.teacher_temperature,
        args.uniform_target_mix,
        np,
        opening_algorithm=args.opening_algorithm,
        opening_model=Path(args.opening_model) if args.opening_model else None,
        opening_seconds=args.opening_seconds,
        recovery_target_mode=args.recovery_target_mode,
        recovery_target_sources=parse_recovery_target_sources(
            args.recovery_target_sources
        ),
        recovery_target_maps=parse_recovery_target_maps(args.recovery_target_maps),
        recovery_target_min_seconds=args.recovery_target_min_seconds,
        recovery_target_max_seconds=args.recovery_target_max_seconds,
        recovery_soft_target_primary_mass=args.recovery_soft_target_primary_mass,
        recovery_soft_target_top_k=args.recovery_soft_target_top_k,
        dataset_action_target_paths=args.dataset_action_target_paths,
    )
    observations = np.asarray(dataset["observations"], dtype=np.float32)
    if observations.shape[1] != int(config["environment"]["observation_len"]):
        raise ValueError(
            "dataset observation length does not match rl_training_config observation_len"
        )

    indices = np.arange(len(observations))
    np.random.default_rng(args.seed).shuffle(indices)
    validation_count = int(round(len(indices) * args.validation_split))
    validation_count = min(max(validation_count, 1), max(1, len(indices) - 1))
    validation_indices = indices[:validation_count]
    train_indices = indices[validation_count:]
    train_weights, sample_weight_report = build_distillation_sample_weights(
        dataset,
        train_indices,
        args.sample_path_weights,
        np,
    )

    selected = algorithm_config(config, "ppo")
    ignored_keys = {"enabled", "policy", "total_timesteps"}
    algorithm_parameters = {
        key: value for key, value in selected.items() if key not in ignored_keys
    }
    env = build_env(
        config,
        seed=config["environment"]["seed"],
        seconds=args.env_seconds or config["environment"]["seconds"],
    )
    model_path = Path(args.model_out)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    started_at = datetime.now(timezone.utc).isoformat()
    try:
        model = stable_baselines_model_classes()["ppo"](
            selected["policy"],
            env,
            verbose=0,
            **algorithm_parameters,
        )
        optimizer = torch.optim.Adam(model.policy.parameters(), lr=args.learning_rate)
        train_weight_tensor = (
            torch.from_numpy(train_weights)
            if train_weights is not None
            else torch.ones(len(train_indices), dtype=torch.float32)
        )
        train_dataset = TensorDataset(
            torch.from_numpy(observations[train_indices]),
            torch.from_numpy(targets[train_indices]),
            train_weight_tensor,
        )
        train_loader = DataLoader(
            train_dataset,
            batch_size=args.batch_size,
            shuffle=True,
        )
        validation_x = torch.from_numpy(observations[validation_indices])
        validation_y = torch.from_numpy(targets[validation_indices])
        history = []
        for epoch in range(1, args.epochs + 1):
            model.policy.set_training_mode(True)
            total_loss = 0.0
            total_weight = 0.0
            total_weighted_correct = 0.0
            for batch_x, batch_y, batch_weight in train_loader:
                logits = tensor_distribution_logits(model, batch_x, torch)
                log_probs = torch.log_softmax(logits, dim=-1)
                per_sample_loss = -(batch_y * log_probs).sum(dim=1)
                weight_sum = batch_weight.sum().clamp_min(1e-8)
                loss = (per_sample_loss * batch_weight).sum() / weight_sum
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                total_loss += float((per_sample_loss * batch_weight).sum().item())
                total_weight += float(weight_sum.item())
                batch_correct = (logits.argmax(dim=1) == batch_y.argmax(dim=1)).float()
                total_weighted_correct += float((batch_correct * batch_weight).sum().item())
            validation_metrics = evaluate_supervised(model, validation_x, validation_y, torch)
            history.append(
                {
                    "epoch": epoch,
                    "train_loss": round(total_loss / max(1e-8, total_weight), 6),
                    "train_argmax_accuracy": round(
                        total_weighted_correct / max(1e-8, total_weight),
                        4,
                    ),
                    "validation_loss": validation_metrics["loss"],
                    "validation_argmax_accuracy": validation_metrics["argmax_accuracy"],
                    "validation_policy_entropy_nats": validation_metrics[
                        "policy_entropy_nats"
                    ],
                }
            )
        completed_at = datetime.now(timezone.utc).isoformat()
        model.save(model_path)
        validation_slices = evaluate_distillation_validation_slices(
            model,
            observations,
            targets,
            dataset,
            validation_indices,
            args.sample_path_weights,
            torch,
        )
    finally:
        env.close()

    action_distribution_guard = evaluate_action_distribution_guard(
        validation_slices,
        action_distribution_guard_config(
            max_dominant_ratio=args.action_distribution_guard_max_dominant_ratio,
            min_normalized_entropy=args.action_distribution_guard_min_normalized_entropy,
            min_sample_count=args.action_distribution_guard_min_sample_count,
            scope=args.action_distribution_guard_scope,
        ),
    )
    gate_decision = (
        "sb3_distillation_action_distribution_guard_failed_not_policy_gate"
        if action_distribution_guard["decision"] == "action_distribution_guard_failed"
        else "sb3_distillation_smoke_only_not_policy_gate"
    )

    metadata_path = model_path.with_name(f"{model_path.stem}_metadata.json")
    metadata = {
        "model_version": 1,
        "algorithm": "ppo",
        "phase": config["phase"],
        "model_path": str(model_path),
        "config_file": str(args.config),
        "distillation_source": target_report,
        "observation_version": config["environment"].get("observation_version", 2),
        "observation_len": config["environment"]["observation_len"],
        "algorithm_parameters": algorithm_parameters,
        "started_at": started_at,
        "completed_at": completed_at,
    }
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    return {
        "status": "trained",
        "algorithm": "ppo",
        "model_path": str(model_path),
        "metadata_path": str(metadata_path),
        "gate_decision": gate_decision,
        "dependency_status": dependency_status(),
        "dataset": summarize_dataset(dataset),
        "target": target_report,
        "training": {
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "learning_rate": args.learning_rate,
            "teacher_temperature": args.teacher_temperature,
            "uniform_target_mix": args.uniform_target_mix,
            "seed": args.seed,
            "train_samples": int(len(train_indices)),
            "validation_samples": int(len(validation_indices)),
            "started_at": started_at,
            "completed_at": completed_at,
        },
        "sample_weights": sample_weight_report,
        "validation_slices": validation_slices,
        "action_distribution_guard": action_distribution_guard,
        "history": history,
        "final": history[-1] if history else {},
        "limitations": [
            "This script distills supervised targets into a PPO MlpPolicy initialization; it does not run PPO environment optimization.",
            "A distilled model must still pass high-pressure comparison and RL policy acceptance before it can become an RL test Bot candidate.",
        ],
    }


def write_report(path, payload):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Distill behavior clone or trajectory actions into an SB3 PPO policy."
    )
    parser.add_argument("--config", default="python/train/rl_training_config.json")
    parser.add_argument("--dataset", action="append", required=True)
    parser.add_argument("--teacher-model", default=None)
    parser.add_argument(
        "--opening-model",
        default=None,
        help="Optional SB3 zip used as teacher before --opening-seconds when target-mode is teacher_probs.",
    )
    parser.add_argument(
        "--opening-algorithm",
        choices=["dqn", "ppo"],
        default="ppo",
        help="SB3 algorithm class used to load --opening-model.",
    )
    parser.add_argument(
        "--opening-seconds",
        type=float,
        default=60.0,
        help="Duration for --opening-model before falling back to --teacher-model.",
    )
    parser.add_argument(
        "--target-mode",
        choices=["teacher_probs", "dataset_actions"],
        default="teacher_probs",
    )
    parser.add_argument(
        "--recovery-target-mode",
        choices=["teacher_probs", "dataset_actions", "top_k_scores"],
        default="teacher_probs",
        help=(
            "Override edge/risk recovery supervision rows while keeping regular "
            "retention samples on the selected target mode."
        ),
    )
    parser.add_argument(
        "--recovery-target-sources",
        default="edge,risk",
        help=(
            "Comma-separated recovery supervision sources to override: "
            "edge, risk, or edge,risk."
        ),
    )
    parser.add_argument(
        "--recovery-target-maps",
        default=None,
        help=(
            "Optional comma-separated map ids where recovery target overrides may apply. "
            "Other recovery samples keep the base teacher target."
        ),
    )
    parser.add_argument(
        "--recovery-target-min-seconds",
        type=float,
        default=None,
        help="Optional inclusive lower time bound for recovery target overrides.",
    )
    parser.add_argument(
        "--recovery-target-max-seconds",
        type=float,
        default=None,
        help="Optional exclusive upper time bound for recovery target overrides.",
    )
    parser.add_argument(
        "--recovery-soft-target-primary-mass",
        type=float,
        default=0.65,
        help="Primary target action mass when --recovery-target-mode=top_k_scores.",
    )
    parser.add_argument(
        "--recovery-soft-target-top-k",
        type=int,
        default=3,
        help="Maximum recovery actions kept when --recovery-target-mode=top_k_scores.",
    )
    parser.add_argument("--limit-samples", type=int, default=None)
    parser.add_argument(
        "--include-anchor-drift-samples",
        action="store_true",
        help="Allow anchor_drift_sample JSONL rows exported with observations.",
    )
    parser.add_argument(
        "--sample-path-weight",
        dest="sample_path_weights",
        action="append",
        type=parse_sample_path_weight_spec,
        default=[],
        help="Multiply supervised loss for samples whose source path matches PATH=WEIGHT.",
    )
    parser.add_argument(
        "--dataset-action-target-path",
        dest="dataset_action_target_paths",
        action="append",
        default=[],
        help=(
            "Use dataset action labels as final targets for samples whose source "
            "path matches PATH or a directory prefix while other samples keep "
            "the selected target mode."
        ),
    )
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--learning-rate", type=float, default=0.0003)
    parser.add_argument(
        "--teacher-temperature",
        type=float,
        default=1.0,
        help="Soften teacher probability targets before supervised PPO distillation.",
    )
    parser.add_argument(
        "--uniform-target-mix",
        type=float,
        default=0.0,
        help="Mix target probabilities with a uniform distribution to raise entropy.",
    )
    parser.add_argument("--validation-split", type=float, default=0.2)
    parser.add_argument(
        "--action-distribution-guard-max-dominant-ratio",
        type=float,
        default=None,
        help=(
            "Mark the distillation report as guard-failed when any checked "
            "validation slice exceeds this predicted argmax action ratio."
        ),
    )
    parser.add_argument(
        "--action-distribution-guard-min-normalized-entropy",
        type=float,
        default=None,
        help=(
            "Mark the distillation report as guard-failed when any checked "
            "validation slice falls below this normalized predicted argmax entropy."
        ),
    )
    parser.add_argument(
        "--action-distribution-guard-min-sample-count",
        type=int,
        default=16,
        help="Minimum validation slice sample count before action-distribution guard thresholds apply.",
    )
    parser.add_argument(
        "--action-distribution-guard-scope",
        default=None,
        help=(
            "Comma-separated validation slice scopes to check: overall, "
            "sample_sources, sample_path_weights, map_time_buckets. Defaults to all."
        ),
    )
    parser.add_argument("--seed", type=int, default=12345)
    parser.add_argument("--env-seconds", type=float, default=None)
    parser.add_argument("--model-out", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()

    if args.target_mode == "teacher_probs" and not args.teacher_model:
        parser.error("--target-mode teacher_probs requires --teacher-model")
    if args.opening_model and args.target_mode != "teacher_probs":
        parser.error("--opening-model requires --target-mode teacher_probs")
    if args.opening_model and args.opening_seconds <= 0.0:
        parser.error("--opening-seconds must be greater than zero")
    if args.limit_samples is not None and args.limit_samples <= 0:
        parser.error("--limit-samples must be greater than zero")
    if args.epochs <= 0:
        parser.error("--epochs must be greater than zero")
    if args.batch_size <= 0:
        parser.error("--batch-size must be greater than zero")
    if args.learning_rate <= 0.0:
        parser.error("--learning-rate must be greater than zero")
    if args.teacher_temperature <= 0.0:
        parser.error("--teacher-temperature must be greater than zero")
    if not (0.0 <= args.uniform_target_mix <= 1.0):
        parser.error("--uniform-target-mix must be between 0 and 1")
    try:
        parse_recovery_target_sources(args.recovery_target_sources)
    except ValueError as exc:
        parser.error(str(exc))
    try:
        parse_recovery_target_maps(args.recovery_target_maps)
    except ValueError as exc:
        parser.error(str(exc))
    if (
        args.recovery_target_min_seconds is not None
        and args.recovery_target_min_seconds < 0.0
    ):
        parser.error("--recovery-target-min-seconds must be non-negative")
    if (
        args.recovery_target_max_seconds is not None
        and args.recovery_target_max_seconds <= 0.0
    ):
        parser.error("--recovery-target-max-seconds must be greater than zero")
    if (
        args.recovery_target_min_seconds is not None
        and args.recovery_target_max_seconds is not None
        and args.recovery_target_max_seconds <= args.recovery_target_min_seconds
    ):
        parser.error(
            "--recovery-target-max-seconds must be greater than --recovery-target-min-seconds"
        )
    if not (0.0 < args.recovery_soft_target_primary_mass <= 1.0):
        parser.error("--recovery-soft-target-primary-mass must be in (0, 1]")
    if args.recovery_soft_target_top_k < 2:
        parser.error("--recovery-soft-target-top-k must be at least 2")
    if not (0.0 < args.validation_split < 1.0):
        parser.error("--validation-split must be between 0 and 1")
    try:
        validate_action_distribution_guard_thresholds(
            max_dominant_ratio=args.action_distribution_guard_max_dominant_ratio,
            min_normalized_entropy=args.action_distribution_guard_min_normalized_entropy,
            min_sample_count=args.action_distribution_guard_min_sample_count,
        )
    except ValueError as exc:
        parser.error(str(exc))
    try:
        parse_action_distribution_guard_scope(args.action_distribution_guard_scope)
    except ValueError as exc:
        parser.error(str(exc))
    if args.env_seconds is not None and args.env_seconds <= 0.0:
        parser.error("--env-seconds must be greater than zero")

    config = load_config(args.config)
    report = distill(config, args)
    write_report(args.report, report)


if __name__ == "__main__":
    main()
