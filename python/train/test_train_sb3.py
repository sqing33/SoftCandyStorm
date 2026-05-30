import json
import random
from types import SimpleNamespace

import pytest

import python.train.train_sb3 as train_sb3
from python.train.train_sb3 import (
    EdgeRecoveryBranchPolicy,
    EdgeRecoveryFilterPolicy,
    LateRecoveryFilterPolicy,
    MapLateSplitPolicy,
    StagedOpeningPolicy,
    TerminalConversionBranchPolicy,
    action_pushes_into_edge,
    algorithm_parameters_source_label,
    algorithm_overrides_from_args,
    apply_loaded_model_overrides,
    build_anchor_sample_weights,
    build_edge_recovery_sample,
    build_env,
    build_trace_step,
    collect_anchor_regularization_targets,
    compact_action_score,
    consume_policy_adapter_decision,
    derived_edge_recovery_samples_path,
    evaluate_anchor_validation_guard,
    evaluation_gate_decision,
    filter_anchor_dataset_by_time_buckets,
    merge_algorithm_parameters,
    load_behavior_clone_policy_with_optional_opening,
    parse_anchor_time_bucket_list,
    parse_anchor_time_bucket_weights,
    parse_edge_recovery_branch_map_overrides,
    parse_terminal_conversion_map_overrides,
    policy_quality_findings,
    resolve_train_seed_values,
    seed_stochastic_action_sampling,
    should_record_trace_step,
    validate_anchor_validation_guard_thresholds,
    validate_anchor_regularization_request,
    validate_eval_random_seed,
    write_edge_recovery_samples,
    write_episode_trace,
)


class DummyPolicy:
    def __init__(self, action):
        self.action = action
        self.reset_count = 0
        self.map_id = None
        self.contexts = []
        self.random_seed = None

    def reset(self):
        self.reset_count += 1

    def set_map_id(self, map_id):
        self.map_id = map_id

    def set_step_context(self, info):
        self.contexts.append(dict(info))

    def set_random_seed(self, seed):
        self.random_seed = seed

    def predict(self, observation, deterministic=True):
        return self.action, None

    def action_scores(self, observation):
        return {
            "kind": "probability",
            "scores": [1.0 if index == self.action else 0.0 for index in range(9)],
        }


class ContextAnchorPolicy:
    def __init__(self):
        self.reset_count = 0
        self.map_ids = []
        self.contexts = []

    def reset(self):
        self.reset_count += 1

    def set_map_id(self, map_id):
        self.map_ids.append(map_id)

    def set_step_context(self, info):
        self.contexts.append(dict(info))

    def action_scores(self, observation):
        if observation[0] > 0.5:
            return {"kind": "probability", "scores": [0.1, 0.8, 0.1]}
        return {"kind": "probability", "scores": [0.7, 0.2, 0.1]}


def test_merge_algorithm_parameters_preserves_base_and_applies_overrides():
    merged = merge_algorithm_parameters(
        {"learning_rate": 0.0003, "gamma": 0.99, "ent_coef": 0.0},
        {"learning_rate": 0.0001, "ent_coef": 0.02},
    )

    assert merged == {"learning_rate": 0.0001, "gamma": 0.99, "ent_coef": 0.02}


def test_algorithm_overrides_accepts_learning_rate():
    args = SimpleNamespace(
        algorithm="ppo",
        learning_rate=0.0001,
        ent_coef=None,
    )

    assert algorithm_overrides_from_args(args) == {"learning_rate": 0.0001}


def test_algorithm_overrides_rejects_non_positive_learning_rate():
    args = SimpleNamespace(
        algorithm="ppo",
        learning_rate=0.0,
        ent_coef=None,
    )

    with pytest.raises(ValueError, match="--learning-rate"):
        algorithm_overrides_from_args(args)


def test_resolve_train_seed_values_accepts_range():
    assert resolve_train_seed_values(None, 62400, 3) == [62400, 62401, 62402]


def test_resolve_train_seed_values_accepts_explicit_list():
    assert resolve_train_seed_values("62400,62407", None, None) == [62400, 62407]


def test_resolve_train_seed_values_rejects_mixed_sources():
    with pytest.raises(ValueError, match="--train-seeds"):
        resolve_train_seed_values("62400", 62400, 2)


def test_parse_edge_recovery_branch_map_overrides_accepts_windows_and_thresholds():
    overrides = parse_edge_recovery_branch_map_overrides(
        "soda-creek:0:60,caramel-workshop:30:45:0.2:0.0:0.75"
    )

    assert overrides["soda-creek"] == {
        "min_seconds": 0.0,
        "max_seconds": 60.0,
    }
    assert overrides["caramel-workshop"] == {
        "min_seconds": 30.0,
        "max_seconds": 45.0,
        "min_pressure": 0.2,
        "min_low_health_risk": 0.0,
        "min_boundary_edge_risk": 0.75,
    }
    with pytest.raises(ValueError, match="max_seconds"):
        parse_edge_recovery_branch_map_overrides("soda-creek:60:30")
    with pytest.raises(ValueError, match="duplicates"):
        parse_edge_recovery_branch_map_overrides("soda-creek:0:60,soda-creek:30:45")


def test_parse_terminal_conversion_map_overrides_accepts_windows_and_thresholds():
    overrides = parse_terminal_conversion_map_overrides(
        "cracked-star-jar:210:240,caramel-workshop:240:300:0.4:0.5"
    )

    assert overrides["cracked-star-jar"] == {
        "min_seconds": 210.0,
        "max_seconds": 240.0,
    }
    assert overrides["caramel-workshop"] == {
        "min_seconds": 240.0,
        "max_seconds": 300.0,
        "min_pressure": 0.4,
        "min_low_health_risk": 0.5,
    }
    with pytest.raises(ValueError, match="max_seconds"):
        parse_terminal_conversion_map_overrides("caramel-workshop:300:240")
    with pytest.raises(ValueError, match="duplicates"):
        parse_terminal_conversion_map_overrides(
            "caramel-workshop:240:300,caramel-workshop:210:240"
        )


def test_validate_eval_random_seed_requires_stochastic_evaluation():
    assert validate_eval_random_seed(17, deterministic=False) == 17
    assert validate_eval_random_seed(None, deterministic=True) is None
    with pytest.raises(ValueError, match="--eval-random-seed"):
        validate_eval_random_seed(17, deterministic=True)
    with pytest.raises(ValueError, match="non-negative"):
        validate_eval_random_seed(-1, deterministic=False)


def test_validate_anchor_regularization_requires_model_and_dataset_together():
    assert not validate_anchor_regularization_request()
    with pytest.raises(ValueError, match="--anchor-model"):
        validate_anchor_regularization_request(anchor_model="anchor.pt")
    with pytest.raises(ValueError, match="--anchor-model"):
        validate_anchor_regularization_request(anchor_datasets=["samples.jsonl"])
    with pytest.raises(ValueError, match="--anchor-sample-weighting"):
        validate_anchor_regularization_request(
            anchor_model="anchor.pt",
            anchor_datasets=["samples.jsonl"],
            anchor_sample_weighting="bad",
        )
    with pytest.raises(ValueError, match="unknown bucket"):
        validate_anchor_regularization_request(
            anchor_model="anchor.pt",
            anchor_datasets=["samples.jsonl"],
            anchor_include_time_buckets=["bad_bucket"],
        )
    with pytest.raises(ValueError, match="greater than 0"):
        validate_anchor_regularization_request(
            anchor_model="anchor.pt",
            anchor_datasets=["samples.jsonl"],
            anchor_time_bucket_weights={"opening_lt_60": 0.0},
        )
    assert validate_anchor_regularization_request(
        anchor_model="anchor.pt",
        anchor_datasets=["samples.jsonl"],
        anchor_regularization_weight=0.5,
        anchor_regularization_interval=128,
        anchor_regularization_epochs=1,
        anchor_regularization_batch_size=16,
        anchor_sample_weighting="time_bucket_balance",
        anchor_include_time_buckets=["opening_lt_60", "mid_60_to_180"],
        anchor_time_bucket_weights={"opening_lt_60": 2.0},
    )


def test_parse_anchor_time_bucket_controls_preserve_known_buckets():
    assert parse_anchor_time_bucket_list("opening_lt_60,mid_60_to_180") == [
        "opening_lt_60",
        "mid_60_to_180",
    ]
    assert parse_anchor_time_bucket_list(
        ["opening_lt_60", "opening_lt_60", "late_180_to_300"]
    ) == ["opening_lt_60", "late_180_to_300"]
    assert parse_anchor_time_bucket_weights(
        "opening_lt_60=2,late_180_to_300=0.5"
    ) == {
        "opening_lt_60": 2.0,
        "late_180_to_300": 0.5,
    }


def test_filter_anchor_dataset_by_time_buckets_keeps_selected_phases():
    dataset = {
        "paths": ["samples.jsonl"],
        "observations": [[0.1], [0.2], [0.3]],
        "actions": [0, 1, 2],
        "sample_metadata": [
            {"time_seconds": 10.0, "map_id": "soda-creek"},
            {"time_seconds": 90.0, "map_id": "soda-creek"},
            {"time_seconds": 240.0, "map_id": "soda-creek"},
        ],
        "metadata": [],
        "episode_count": 1,
        "skipped_upgrade_samples": 0,
        "observation_len": 1,
        "action_count": 3,
    }

    filtered, report = filter_anchor_dataset_by_time_buckets(
        dataset,
        ["opening_lt_60", "late_180_to_300"],
    )

    assert filtered["observations"] == [[0.1], [0.3]]
    assert filtered["actions"] == [0, 2]
    assert report["mode"] == "include_time_buckets"
    assert report["sample_count_before"] == 3
    assert report["sample_count_after"] == 2
    assert report["dropped_sample_count"] == 1
    assert report["bucket_counts_after"] == {
        "opening_lt_60": 1,
        "late_180_to_300": 1,
    }


def test_collect_anchor_regularization_targets_sets_context_and_probabilities():
    dataset = {
        "action_count": 3,
        "observations": [[0.1], [0.8]],
        "actions": [0, 1],
        "sample_metadata": [
            {
                "path": "samples.jsonl",
                "seed": 1,
                "map_id": "soda-creek",
                "time_seconds": 1.0,
            },
            {
                "path": "samples.jsonl",
                "seed": 1,
                "map_id": "soda-creek",
                "time_seconds": 2.0,
            },
        ],
    }
    np = pytest.importorskip("numpy")
    anchor = ContextAnchorPolicy()

    observations, targets, report = collect_anchor_regularization_targets(
        dataset,
        anchor,
        np,
    )

    assert observations.shape == (2, 1)
    assert targets[0].tolist() == pytest.approx([0.7, 0.2, 0.1])
    assert targets[1].tolist() == pytest.approx([0.1, 0.8, 0.1])
    assert anchor.reset_count == 1
    assert anchor.map_ids == ["soda-creek"]
    assert [context["time_seconds"] for context in anchor.contexts] == [1.0, 2.0]
    assert report["anchor_argmax_agreement_with_dataset_actions"] == 1.0


def test_build_anchor_sample_weights_balances_time_buckets():
    np = pytest.importorskip("numpy")
    sample_metadata = [
        {"map_id": "soda-creek", "time_seconds": 10.0},
        {"map_id": "soda-creek", "time_seconds": 30.0},
        {"map_id": "soda-creek", "time_seconds": 210.0},
    ]

    weights, report = build_anchor_sample_weights(
        sample_metadata,
        np,
        "time_bucket_balance",
    )

    assert weights.tolist() == pytest.approx([0.75, 0.75, 1.5])
    assert report["mode"] == "time_bucket_balance"
    assert report["groups"]["opening_lt_60"]["sample_count"] == 2
    assert report["groups"]["late_180_to_300"]["weight_multiplier"] == 1.5


def test_build_anchor_sample_weights_balances_map_time_buckets():
    np = pytest.importorskip("numpy")
    sample_metadata = [
        {"map_id": "soda-creek", "time_seconds": 10.0},
        {"map_id": "soda-creek", "time_seconds": 20.0},
        {"map_id": "caramel-workshop", "time_seconds": 20.0},
    ]

    weights, report = build_anchor_sample_weights(
        sample_metadata,
        np,
        "map_time_bucket_balance",
    )

    assert weights.tolist() == pytest.approx([0.75, 0.75, 1.5])
    assert report["group_count"] == 2
    assert report["groups"]["caramel-workshop::opening_lt_60"]["sample_count"] == 1


def test_build_anchor_sample_weights_applies_time_bucket_multipliers():
    np = pytest.importorskip("numpy")
    sample_metadata = [
        {"map_id": "soda-creek", "time_seconds": 10.0},
        {"map_id": "soda-creek", "time_seconds": 90.0},
        {"map_id": "soda-creek", "time_seconds": 240.0},
    ]

    weights, report = build_anchor_sample_weights(
        sample_metadata,
        np,
        "none",
        {"opening_lt_60": 2.0, "late_180_to_300": 0.5},
    )

    assert weights.tolist() == pytest.approx([2.0, 1.0, 0.5])
    assert report["time_bucket_weights"]["mode"] == "custom_multipliers"
    assert report["time_bucket_weights"]["matched_sample_counts"] == {
        "late_180_to_300": 1,
        "opening_lt_60": 1,
    }
    assert report["min"] == 0.5
    assert report["max"] == 2.0


def test_build_env_passes_reward_profile(monkeypatch):
    captured = {}

    class DummyEnv:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(train_sb3, "SoftCandyStormEnv", DummyEnv)
    config = {
        "environment": {
            "seed": 12345,
            "seconds": 300,
            "tick_rate": 30,
            "map_id": "soda-creek",
            "observation_version": 2,
            "content_dir": "content/base_demo",
        }
    }

    env = build_env(config, reward_profile="long-run-retention")

    assert isinstance(env, DummyEnv)
    assert captured["reward_profile"] == "long-run-retention"


def test_build_env_passes_late_route_recovery_reward_profile(monkeypatch):
    captured = {}

    class DummyEnv:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(train_sb3, "SoftCandyStormEnv", DummyEnv)
    config = {
        "environment": {
            "seed": 12345,
            "seconds": 300,
            "tick_rate": 30,
            "map_id": "soda-creek",
            "observation_version": 2,
            "content_dir": "content/base_demo",
        }
    }

    env = build_env(config, reward_profile="late-route-recovery")

    assert isinstance(env, DummyEnv)
    assert captured["reward_profile"] == "late-route-recovery"


def test_training_uses_upgrade_choice_model(monkeypatch, tmp_path):
    captured = {}
    upgrade_policy = object()

    class DummyEnv:
        def close(self):
            captured["env_closed"] = True

    class DummyModel:
        def __init__(self, policy, env, verbose=0, **kwargs):
            captured["model_policy"] = policy
            captured["model_env"] = env
            captured["model_kwargs"] = kwargs
            self.num_timesteps = 0

        def learn(self, total_timesteps):
            self.num_timesteps = total_timesteps

        def save(self, path):
            captured["model_saved"] = str(path)
            path.write_text("dummy model", encoding="utf-8")

    def fake_build_env(config, **kwargs):
        captured["build_env_kwargs"] = kwargs
        return DummyEnv()

    def fake_evaluate_model(model, config, **kwargs):
        captured["evaluate_kwargs"] = kwargs
        return {
            "action_selection": "deterministic",
            "action_random_seed": None,
            "map_id": "soda-creek",
            "upgrade_policy": {
                "mode": "upgrade_choice_ranker",
                "model_path": "ranker.pt",
            },
            "summary": {
                "episodes": 1,
                "win_rate": 0.0,
                "average_survival_seconds": 1.0,
                "average_level": 1.0,
                "average_kills": 1.0,
                "average_reward": 0.0,
                "damage_taken_average": 0.0,
                "action_distribution": {
                    str(index): {
                        "count": 1 if index == 0 else 0,
                        "ratio": 1.0 if index == 0 else 0.0,
                    }
                    for index in range(9)
                },
                "normalized_action_entropy": 1.0,
                "reward_breakdown_average": {"terminal": 0.0, "total": 0.0},
                "upgrade_policy_decision_count": 1,
            },
        }

    monkeypatch.setattr(train_sb3, "require_dependencies", lambda: {})
    monkeypatch.setattr(train_sb3, "stable_baselines_model_classes", lambda: {"ppo": DummyModel})
    monkeypatch.setattr(train_sb3, "load_upgrade_choice_policy", lambda path: upgrade_policy)
    monkeypatch.setattr(train_sb3, "build_env", fake_build_env)
    monkeypatch.setattr(train_sb3, "evaluate_model", fake_evaluate_model)
    monkeypatch.setattr(train_sb3, "dependency_status", lambda: {})

    config = {
        "phase": "test",
        "environment": {
            "seed": 12345,
            "seconds": 300,
            "tick_rate": 30,
            "map_id": "soda-creek",
            "observation_version": 2,
            "observation_len": 145,
            "content_dir": "content/base_demo",
        },
        "algorithms": {
            "ppo": {
                "enabled": True,
                "policy": "MlpPolicy",
                "total_timesteps": 2,
                "n_steps": 1,
            }
        },
        "outputs": {
            "model_dir": str(tmp_path / "models"),
            "report_dir": str(tmp_path / "reports"),
            "metadata_file": "{algorithm}_metadata.json",
        },
        "evaluation": {
            "episodes": 1,
            "seconds": 1,
            "seed_start": 1,
        },
    }

    report = train_sb3.train(
        config,
        "ppo",
        total_timesteps=2,
        model_out=tmp_path / "model.zip",
        report_dir_out=tmp_path / "reports",
        upgrade_choice_model=tmp_path / "ranker.pt",
    )

    assert captured["build_env_kwargs"]["upgrade_policy"] is upgrade_policy
    assert captured["evaluate_kwargs"]["upgrade_policy"] is upgrade_policy
    assert report["training"]["upgrade_choice_model"].endswith("ranker.pt")
    assert report["upgrade_policy"]["mode"] == "upgrade_choice_ranker"
    assert captured["env_closed"] is True


def test_training_can_apply_anchor_regularization(monkeypatch, tmp_path):
    captured = {}

    class DummyEnv:
        def close(self):
            captured["env_closed"] = True

    class DummyModel:
        def __init__(self, policy, env, verbose=0, **kwargs):
            self.num_timesteps = 0

        def learn(self, total_timesteps):
            captured["plain_learn"] = total_timesteps

        def save(self, path):
            path.write_text("dummy model", encoding="utf-8")

    def fake_evaluate_model(model, config, **kwargs):
        return {
            "action_selection": "deterministic",
            "action_random_seed": None,
            "map_id": "soda-creek",
            "upgrade_policy": {"mode": "bridge_default_first_option"},
            "summary": {
                "episodes": 1,
                "win_rate": 0.0,
                "average_survival_seconds": 1.0,
                "average_level": 1.0,
                "average_kills": 1.0,
                "average_reward": 0.0,
                "damage_taken_average": 0.0,
                "action_distribution": {
                    str(index): {
                        "count": 1 if index == 0 else 0,
                        "ratio": 1.0 if index == 0 else 0.0,
                    }
                    for index in range(9)
                },
                "normalized_action_entropy": 1.0,
                "reward_breakdown_average": {"terminal": 0.0, "total": 0.0},
                "upgrade_policy_decision_count": 0,
            },
        }

    def fake_prepare_anchor_regularization(config, algorithm, **kwargs):
        captured["anchor_prepare_kwargs"] = kwargs
        return {
            "report": {
                "mode": "behavior_clone_anchor_kl_regularization",
                "anchor_model": str(kwargs["anchor_model"]),
            }
        }

    def fake_anchor_learn(model, total_timesteps, anchor_regularization):
        captured["anchor_learn_timesteps"] = total_timesteps
        model.num_timesteps = total_timesteps
        return {
            **anchor_regularization["report"],
            "status": "applied",
            "final_validation": {"mean_kl": 0.123, "argmax_agreement": 0.9},
        }

    monkeypatch.setattr(train_sb3, "require_dependencies", lambda: {})
    monkeypatch.setattr(train_sb3, "stable_baselines_model_classes", lambda: {"ppo": DummyModel})
    monkeypatch.setattr(train_sb3, "build_env", lambda *args, **kwargs: DummyEnv())
    monkeypatch.setattr(train_sb3, "evaluate_model", fake_evaluate_model)
    monkeypatch.setattr(train_sb3, "dependency_status", lambda: {})
    monkeypatch.setattr(
        train_sb3,
        "prepare_anchor_regularization",
        fake_prepare_anchor_regularization,
    )
    monkeypatch.setattr(
        train_sb3,
        "learn_model_with_anchor_regularization",
        fake_anchor_learn,
    )

    config = {
        "phase": "test",
        "environment": {
            "seed": 12345,
            "seconds": 300,
            "tick_rate": 30,
            "map_id": "soda-creek",
            "observation_version": 2,
            "observation_len": 145,
            "content_dir": "content/base_demo",
        },
        "algorithms": {
            "ppo": {
                "enabled": True,
                "policy": "MlpPolicy",
                "total_timesteps": 32,
                "n_steps": 16,
            }
        },
        "outputs": {
            "model_dir": str(tmp_path / "models"),
            "report_dir": str(tmp_path / "reports"),
            "metadata_file": "{algorithm}_metadata.json",
        },
        "evaluation": {
            "episodes": 1,
            "seconds": 1,
            "seed_start": 1,
        },
    }

    report = train_sb3.train(
        config,
        "ppo",
        total_timesteps=32,
        model_out=tmp_path / "model.zip",
        report_dir_out=tmp_path / "reports",
        anchor_model=tmp_path / "anchor.pt",
        anchor_datasets=[tmp_path / "samples.jsonl"],
        anchor_regularization_interval=16,
        anchor_sample_weighting="map_time_bucket_balance",
        anchor_include_time_buckets=["opening_lt_60", "mid_60_to_180"],
        anchor_time_bucket_weights={"opening_lt_60": 2.0},
        anchor_guard_max_validation_kl=0.25,
        anchor_guard_min_argmax_agreement=0.8,
    )

    assert "plain_learn" not in captured
    assert captured["anchor_learn_timesteps"] == 32
    assert captured["anchor_prepare_kwargs"]["anchor_regularization_interval"] == 16
    assert captured["anchor_prepare_kwargs"]["anchor_sample_weighting"] == "map_time_bucket_balance"
    assert captured["anchor_prepare_kwargs"]["anchor_include_time_buckets"] == [
        "opening_lt_60",
        "mid_60_to_180",
    ]
    assert captured["anchor_prepare_kwargs"]["anchor_time_bucket_weights"] == {
        "opening_lt_60": 2.0,
    }
    assert captured["anchor_prepare_kwargs"]["anchor_guard_max_validation_kl"] == 0.25
    assert captured["anchor_prepare_kwargs"]["anchor_guard_min_argmax_agreement"] == 0.8
    assert report["anchor_regularization"]["status"] == "applied"
    assert report["training"]["anchor_regularization"]["final_validation"]["mean_kl"] == 0.123
    assert captured["env_closed"] is True


def test_seed_stochastic_action_sampling_replays_python_random_sequence():
    report = seed_stochastic_action_sampling(1234)
    first = random.random()
    seed_stochastic_action_sampling(1234)
    second = random.random()

    assert first == second
    assert report["seed"] == 1234
    assert "python_random" in report["seeded_sources"]


def test_action_pushes_into_edge_detects_wallward_movement():
    diagnostics = {
        "boundary": {
            "left_distance": 0.0,
            "right_distance": 400.0,
            "bottom_distance": 50.0,
            "top_distance": 400.0,
        }
    }

    assert action_pushes_into_edge(7, diagnostics, 32.0)
    assert action_pushes_into_edge(8, diagnostics, 32.0)
    assert not action_pushes_into_edge(3, diagnostics, 32.0)
    assert not action_pushes_into_edge(0, diagnostics, 32.0)


def test_edge_recovery_filter_chooses_best_non_wallward_action():
    policy = EdgeRecoveryFilterPolicy(DummyPolicy(7), edge_distance=32.0)
    policy.set_step_context(
        {
            "diagnostics": {
                "boundary": {
                    "left_distance": 0.0,
                    "right_distance": 400.0,
                    "bottom_distance": 400.0,
                    "top_distance": 400.0,
                }
            }
        }
    )

    action, _state = policy.predict(None, deterministic=True)

    assert action == 0
    assert policy.policy_adapter_report()["mode"] == "edge_recovery_filter"


def test_edge_recovery_filter_records_consumable_recovery_decision():
    policy = EdgeRecoveryFilterPolicy(DummyPolicy(7), edge_distance=32.0)
    policy.set_step_context(
        {
            "diagnostics": {
                "boundary": {
                    "left_distance": 0.0,
                    "right_distance": 400.0,
                    "bottom_distance": 400.0,
                    "top_distance": 400.0,
                }
            }
        }
    )

    action, _state = policy.predict(None, deterministic=True)
    decision = consume_policy_adapter_decision(policy)

    assert action == 0
    assert decision["mode"] == "edge_recovery_filter"
    assert decision["original_action"] == 7
    assert decision["target_action"] == 0
    assert decision["target_rank"] == 2
    assert consume_policy_adapter_decision(policy) is None


def test_edge_recovery_filter_does_not_override_stochastic_actions():
    policy = EdgeRecoveryFilterPolicy(DummyPolicy(7), edge_distance=32.0)
    policy.set_step_context(
        {
            "diagnostics": {
                "boundary": {
                    "left_distance": 0.0,
                    "right_distance": 400.0,
                    "bottom_distance": 400.0,
                    "top_distance": 400.0,
                }
            }
        }
    )

    action, _state = policy.predict(None, deterministic=False)

    assert action == 7
    assert consume_policy_adapter_decision(policy) is None


def test_late_recovery_filter_redirects_wallward_hazard_action():
    observation = [0.0] * 145
    observation[130] = 0.3
    observation[131] = -0.3
    observation[132] = 0.4
    policy = LateRecoveryFilterPolicy(
        DummyPolicy(4),
        min_seconds=180.0,
        edge_distance=32.0,
        hazard_threshold=0.2,
    )
    policy.set_step_context(
        {
            "time_seconds": 220.0,
            "diagnostics": {
                "player_position": {"x": 1150.0, "y": -850.0},
                "boundary": {
                    "left_distance": 2300.0,
                    "right_distance": 0.0,
                    "bottom_distance": 0.0,
                    "top_distance": 1700.0,
                },
                "hazard_pressure_risk": 1.0,
                "boss_pressure_risk": 0.0,
                "enemy_pressure_risk": 0.0,
                "low_health_risk": 0.5,
            },
        }
    )

    action, _state = policy.predict(observation, deterministic=True)
    decision = consume_policy_adapter_decision(policy)

    assert action == 1
    assert decision["mode"] == "late_recovery_filter"
    assert decision["original_action"] == 4
    assert decision["target_action"] == 1
    assert "wallward_edge" in decision["risk_reasons"]
    assert "toward_hazard" in decision["risk_reasons"]


def test_late_recovery_filter_ignores_opening_window():
    policy = LateRecoveryFilterPolicy(DummyPolicy(4), min_seconds=180.0)
    policy.set_step_context(
        {
            "time_seconds": 60.0,
            "diagnostics": {
                "boundary": {
                    "right_distance": 0.0,
                    "bottom_distance": 0.0,
                },
                "hazard_pressure_risk": 1.0,
            },
        }
    )

    action, _state = policy.predict([0.0] * 145, deterministic=True)

    assert action == 4
    assert consume_policy_adapter_decision(policy) is None


def test_late_recovery_filter_skips_non_target_map():
    observation = [0.0] * 145
    observation[130] = 0.3
    observation[131] = -0.3
    observation[132] = 0.4
    policy = LateRecoveryFilterPolicy(
        DummyPolicy(4),
        min_seconds=180.0,
        target_maps=["caramel-workshop"],
    )
    policy.set_map_id("soda-creek")
    policy.set_step_context(
        {
            "map_id": "soda-creek",
            "time_seconds": 220.0,
            "diagnostics": {
                "boundary": {
                    "right_distance": 0.0,
                    "bottom_distance": 0.0,
                },
                "hazard_pressure_risk": 1.0,
                "low_health_risk": 0.5,
            },
        }
    )

    action, _state = policy.predict(observation, deterministic=True)
    report = policy.policy_adapter_report()

    assert action == 4
    assert consume_policy_adapter_decision(policy) is None
    assert report["target_maps"] == ["caramel-workshop"]


def test_late_recovery_filter_delegates_inner_branch_decision_before_late_window():
    inner = EdgeRecoveryBranchPolicy(
        DummyPolicy(5),
        DummyPolicy(7),
        ["soda-creek"],
        0.0,
        60.0,
        32.0,
        0.2,
        0.0,
        0.75,
        "base.zip",
        "branch.zip",
    )
    policy = LateRecoveryFilterPolicy(inner, min_seconds=180.0)
    policy.set_map_id("soda-creek")
    policy.set_step_context(
        {
            "map_id": "soda-creek",
            "time_seconds": 36.0,
            "diagnostics": {
                "boundary_edge_risk": 1.0,
                "enemy_pressure_risk": 0.3,
                "boundary": {
                    "left_distance": 400.0,
                    "right_distance": 400.0,
                    "bottom_distance": 0.0,
                    "top_distance": 400.0,
                },
            },
        }
    )

    action, _state = policy.predict([0.0] * 145, deterministic=True)
    decision = consume_policy_adapter_decision(policy)
    report = policy.policy_adapter_report()

    assert action == 7
    assert decision["mode"] == "edge_recovery_branch"
    assert decision["original_action"] == 5
    assert decision["target_action"] == 7
    assert report["mode"] == "late_recovery_filter"
    assert report["wrapped_policy_kind"] == "edge_recovery_branch"
    assert report["wrapped_policy_adapter"]["mode"] == "edge_recovery_branch"


def test_late_recovery_filter_clears_inner_branch_decision_when_overriding():
    inner = EdgeRecoveryBranchPolicy(
        DummyPolicy(5),
        DummyPolicy(7),
        ["soda-creek"],
        0.0,
        300.0,
        32.0,
        0.2,
        0.0,
        0.75,
        "base.zip",
        "branch.zip",
    )
    policy = LateRecoveryFilterPolicy(
        inner,
        min_seconds=0.0,
        hazard_threshold=0.2,
        low_health_threshold=0.25,
    )
    observation = [0.0] * 145
    observation[130] = -1.0
    observation[131] = 0.0
    observation[132] = 1.0
    policy.set_map_id("soda-creek")
    policy.set_step_context(
        {
            "map_id": "soda-creek",
            "time_seconds": 220.0,
            "diagnostics": {
                "boundary_edge_risk": 1.0,
                "enemy_pressure_risk": 0.3,
                "hazard_pressure_risk": 1.0,
                "low_health_risk": 0.0,
                "boundary": {
                    "left_distance": 400.0,
                    "right_distance": 400.0,
                    "bottom_distance": 0.0,
                    "top_distance": 400.0,
                },
            },
        }
    )

    action, _state = policy.predict(observation, deterministic=True)
    decision = consume_policy_adapter_decision(policy)

    assert action == 1
    assert decision["mode"] == "late_recovery_filter"
    assert decision["original_action"] == 7
    assert decision["target_action"] == 1
    assert consume_policy_adapter_decision(policy) is None


def test_build_edge_recovery_sample_includes_observation_and_diagnostics():
    sample = build_edge_recovery_sample(
        episode_seed=62201,
        step_number=1801,
        observation=[0.1, 0.2, 0.3],
        info={
            "map_id": "soda-creek",
            "tick": 1800,
            "time_seconds": 60.0,
            "diagnostics": {
                "boundary": {
                    "left_distance": 0.0,
                    "right_distance": 2400.0,
                    "bottom_distance": 900.0,
                    "top_distance": 900.0,
                }
            },
        },
        adapter_decision={
            "mode": "edge_recovery_filter",
            "edge_distance": 32.0,
            "original_action": 7,
            "target_action": 0,
            "score_kind": "probability",
            "original_action_score": 0.9,
            "target_action_score": 0.1,
            "score_margin": -0.8,
            "target_rank": 2,
        },
        action_scores={
            "kind": "probability",
            "scores": [0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.0],
        },
        config={"environment": {"observation_version": 2}},
    )

    assert sample["record_type"] == "edge_recovery_supervision_sample"
    assert sample["sample_role"] == "repair_training_input"
    assert sample["observation_len"] == 3
    assert sample["original_action"] == 7
    assert sample["target_action"] == 0
    assert sample["diagnostics"]["boundary"]["left_distance"] == 0.0


def test_build_late_recovery_sample_uses_risk_record_type():
    sample = build_edge_recovery_sample(
        episode_seed=62300,
        step_number=6601,
        observation=[0.1, 0.2, 0.3],
        info={
            "map_id": "caramel-workshop",
            "tick": 6600,
            "time_seconds": 220.0,
            "diagnostics": {"hazard_pressure_risk": 1.0},
        },
        adapter_decision={
            "mode": "late_recovery_filter",
            "original_action": 4,
            "target_action": 1,
            "risk_reasons": ["wallward_edge", "toward_hazard"],
        },
        action_scores={
            "kind": "probability",
            "scores": [0.1, 0.2, 0.0, 0.0, 0.7, 0.0, 0.0, 0.0, 0.0],
        },
        config={"environment": {"observation_version": 2}},
    )

    assert sample["record_type"] == "risk_recovery_supervision_sample"
    assert sample["target_source"] == "late_recovery_filter"
    assert sample["target_label"] == "highest_scored_late_safe_action"


def test_build_edge_branch_sample_records_branch_target_source():
    sample = build_edge_recovery_sample(
        episode_seed=63402,
        step_number=1080,
        observation=[0.1, 0.2, 0.3],
        info={
            "map_id": "soda-creek",
            "tick": 1079,
            "time_seconds": 36.0,
            "diagnostics": {"boundary_edge_risk": 1.0},
        },
        adapter_decision={
            "mode": "edge_recovery_branch",
            "original_action": 5,
            "target_action": 7,
        },
        action_scores={
            "kind": "probability",
            "scores": [0.0, 0.0, 0.0, 0.0, 0.0, 0.1, 0.0, 0.9, 0.0],
        },
        config={"environment": {"observation_version": 2}},
    )

    assert sample["record_type"] == "edge_recovery_supervision_sample"
    assert sample["target_source"] == "edge_recovery_branch"
    assert sample["target_label"] == "branch_conditioned_non_wallward_action"


def test_write_edge_recovery_samples_writes_jsonl(tmp_path):
    target = tmp_path / "edge_samples.jsonl"
    report = write_edge_recovery_samples(
        target,
        [
            {
                "record_type": "edge_recovery_supervision_sample",
                "target_action": 0,
            }
        ],
    )

    lines = target.read_text(encoding="utf-8").splitlines()
    assert report["sample_count"] == 1
    assert json.loads(lines[0])["target_action"] == 0


def test_derived_edge_recovery_samples_path_uses_map_suffix():
    assert (
        derived_edge_recovery_samples_path("samples.jsonl", "soda-creek").name
        == "samples_soda-creek.jsonl"
    )
    assert (
        derived_edge_recovery_samples_path("samples", "soda-creek").name
        == "soda-creek_edge_recovery_samples.jsonl"
    )


def test_algorithm_parameter_source_records_warm_start_overrides():
    source = algorithm_parameters_source_label(
        warm_start_metadata={"algorithm_parameters": {"ent_coef": 0.0}},
        warm_start_model="model.zip",
        overrides={"ent_coef": 0.02},
    )

    assert source == "warm_start_metadata_with_overrides"


def test_apply_loaded_model_overrides_updates_supported_parameters():
    model = SimpleNamespace(ent_coef=0.0)

    apply_loaded_model_overrides(model, {"ent_coef": 0.03})

    assert model.ent_coef == 0.03


def test_apply_loaded_model_overrides_refreshes_learning_rate_schedule():
    class LoadedModel:
        def __init__(self):
            self.learning_rate = 0.0003
            self.lr_schedule = None

        def _setup_lr_schedule(self):
            self.lr_schedule = f"schedule:{self.learning_rate}"

    model = LoadedModel()

    apply_loaded_model_overrides(model, {"learning_rate": 0.0001})

    assert model.learning_rate == 0.0001
    assert model.lr_schedule == "schedule:0.0001"


def test_apply_loaded_model_overrides_rejects_unknown_parameters():
    with pytest.raises(ValueError, match="does not expose"):
        apply_loaded_model_overrides(SimpleNamespace(), {"ent_coef": 0.03})


def test_trace_step_sampling_records_first_stride_and_terminal_steps():
    assert not should_record_trace_step(None, 1, False, False, 30)
    assert should_record_trace_step("traces", 1, False, False, 30)
    assert should_record_trace_step("traces", 60, False, False, 30)
    assert should_record_trace_step("traces", 17, True, False, 30)
    assert not should_record_trace_step("traces", 17, False, False, 30)


def test_build_trace_step_compacts_policy_scores():
    info = {
        "tick": 30,
        "time_seconds": 1.0,
        "health": 91.5,
        "level": 2,
        "kills": 3,
        "xp_collected": 4.25,
        "damage_taken": 8.5,
        "upgrade_options": ["mint"],
        "events": ["hit"],
        "terminal": None,
        "reward_breakdown": {"survival": 0.1, "total": -0.25},
        "diagnostics": {
            "player_position": {"x": 12.0, "y": -3.0},
            "boundary": {"min_distance": 42.0, "edge_risk": 0.0},
            "nearest_enemy": {"enemy_id": "soda-bubble", "hitbox_distance": 55.0},
        },
    }

    step = build_trace_step(
        30,
        4,
        -0.25,
        info,
        {"kind": "probability", "scores": [0.1, 0.2, 0.05, 0.15, 0.5]},
    )

    assert step["action"] == 4
    assert step["health"] == 91.5
    assert step["reward_breakdown"] == {"survival": 0.1, "total": -0.25}
    assert step["action_score"]["chosen_action_score"] == 0.5
    assert step["action_score"]["top_actions"][0] == {"action": "4", "score": 0.5}
    assert step["diagnostics"]["nearest_enemy"]["enemy_id"] == "soda-bubble"


def test_build_trace_step_can_include_observation_for_repair_sampling():
    step = build_trace_step(
        1,
        3,
        0.25,
        {
            "tick": 1,
            "time_seconds": 0.0333,
            "health": 120.0,
            "level": 1,
            "kills": 0,
            "xp_collected": 0.0,
            "damage_taken": 0.0,
            "reward_breakdown": {"route_recovery": -0.002},
        },
        {"kind": "probability", "scores": [0.1, 0.2, 0.3, 0.4]},
        observation=[0.1, 0.2, 0.3],
        observation_version=2,
        include_observation=True,
    )

    assert step["observation_version"] == 2
    assert step["observation_len"] == 3
    assert step["observation"] == [0.1, 0.2, 0.3]


def test_write_episode_trace_respects_failed_only(tmp_path):
    victory = {"seed": 1, "map_id": "soda-creek", "terminal_kind": "victory"}
    failure = {
        "seed": 2,
        "map_id": "soda-creek",
        "terminal_kind": "defeat",
        "terminal_reason": "player_health_depleted",
    }

    assert write_episode_trace(tmp_path, victory, [], failed_only=True) is None
    trace_path = write_episode_trace(
        tmp_path,
        failure,
        [{"step": 1, "action": 4}],
        failed_only=True,
    )

    payload = json.loads((tmp_path / "soda-creek_seed2_trace.json").read_text())
    assert trace_path.endswith("soda-creek_seed2_trace.json")
    assert payload["record_type"] == "policy_episode_trace"
    assert payload["sample_count"] == 1
    assert payload["episode"]["terminal_kind"] == "defeat"


def test_staged_opening_policy_switches_after_opening_seconds():
    opening = DummyPolicy(7)
    fallback = DummyPolicy(4)
    policy = StagedOpeningPolicy(
        opening,
        fallback,
        60.0,
        "opening.zip",
        "fallback.zip",
    )

    policy.reset()
    policy.set_map_id("soda-creek")
    policy.set_step_context({"time_seconds": 59.9})
    opening_action, _ = policy.predict(None)
    opening_scores = policy.action_scores(None)
    policy.set_step_context({"time_seconds": 60.0})
    fallback_action, _ = policy.predict(None)

    assert opening.reset_count == 1
    assert fallback.reset_count == 1
    assert opening.map_id == "soda-creek"
    assert fallback.map_id == "soda-creek"
    assert [context["time_seconds"] for context in opening.contexts] == [59.9, 60.0]
    assert [context["time_seconds"] for context in fallback.contexts] == [59.9, 60.0]
    assert opening_action == 7
    assert opening_scores["scores"][7] == 1.0
    assert fallback_action == 4
    assert policy.opening_policy_report()["mode"] == "staged_sb3_opening"


def test_map_late_split_policy_switches_only_on_target_map_late_window():
    base = DummyPolicy(1)
    late = DummyPolicy(5)
    policy = MapLateSplitPolicy(
        base,
        late,
        240.0,
        ["cracked-star-jar"],
        "base.zip",
        "late.zip",
    )

    policy.reset()
    policy.set_random_seed(777)
    policy.set_map_id("soda-creek")
    policy.set_step_context({"map_id": "soda-creek", "time_seconds": 260.0})
    non_target_action, _ = policy.predict(None)
    policy.set_map_id("cracked-star-jar")
    policy.set_step_context({"map_id": "cracked-star-jar", "time_seconds": 239.9})
    early_target_action, _ = policy.predict(None)
    policy.set_step_context({"map_id": "cracked-star-jar", "time_seconds": 240.0})
    late_target_action, _ = policy.predict(None)
    late_scores = policy.action_scores(None)

    assert base.reset_count == 1
    assert late.reset_count == 1
    assert base.random_seed == 777
    assert late.random_seed == 777
    assert base.map_id == "cracked-star-jar"
    assert late.map_id == "cracked-star-jar"
    assert [context["time_seconds"] for context in base.contexts] == [
        260.0,
        239.9,
        240.0,
    ]
    assert [context["time_seconds"] for context in late.contexts] == [
        260.0,
        239.9,
        240.0,
    ]
    assert non_target_action == 1
    assert early_target_action == 1
    assert late_target_action == 5
    assert late_scores["scores"][5] == 1.0
    assert policy.opening_policy_report()["mode"] == "single_policy"
    assert policy.policy_adapter_report()["mode"] == "map_late_split"
    assert policy.policy_adapter_report()["target_maps"] == ["cracked-star-jar"]


def test_map_late_split_policy_rejects_empty_target_maps():
    with pytest.raises(ValueError, match="target_maps"):
        MapLateSplitPolicy(
            DummyPolicy(1),
            DummyPolicy(5),
            240.0,
            [],
            "base.zip",
            "late.zip",
        )


def test_terminal_conversion_branch_switches_on_target_window_and_pressure():
    base = DummyPolicy(1)
    terminal = DummyPolicy(6)
    policy = TerminalConversionBranchPolicy(
        base,
        terminal,
        ["cracked-star-jar"],
        210.0,
        240.0,
        0.25,
        0.5,
        "base.zip",
        "terminal.zip",
    )

    policy.reset()
    policy.set_random_seed(888)
    policy.set_map_id("soda-creek")
    policy.set_step_context(
        {
            "map_id": "soda-creek",
            "time_seconds": 220.0,
            "diagnostics": {"enemy_pressure_risk": 0.9},
        }
    )
    non_target_action, _ = policy.predict(None)
    policy.set_map_id("cracked-star-jar")
    policy.set_step_context(
        {
            "map_id": "cracked-star-jar",
            "time_seconds": 209.9,
            "diagnostics": {"enemy_pressure_risk": 0.9},
        }
    )
    early_action, _ = policy.predict(None)
    policy.set_step_context(
        {
            "map_id": "cracked-star-jar",
            "time_seconds": 220.0,
            "diagnostics": {"enemy_pressure_risk": 0.1},
        }
    )
    low_pressure_action, _ = policy.predict(None)
    policy.set_step_context(
        {
            "map_id": "cracked-star-jar",
            "time_seconds": 220.0,
            "diagnostics": {"enemy_pressure_risk": 0.3},
        }
    )
    terminal_action, _ = policy.predict(None)
    terminal_scores = policy.action_scores(None)
    policy.set_step_context(
        {
            "map_id": "cracked-star-jar",
            "time_seconds": 240.1,
            "diagnostics": {"enemy_pressure_risk": 0.9},
        }
    )
    after_window_action, _ = policy.predict(None)

    assert base.reset_count == 1
    assert terminal.reset_count == 1
    assert base.random_seed == 888
    assert terminal.random_seed == 888
    assert non_target_action == 1
    assert early_action == 1
    assert low_pressure_action == 1
    assert terminal_action == 6
    assert terminal_scores["scores"][6] == 1.0
    assert after_window_action == 1
    report = policy.policy_adapter_report()
    assert report["mode"] == "terminal_conversion_branch"
    assert report["target_maps"] == ["cracked-star-jar"]
    assert report["min_seconds"] == 210.0
    usage = report["usage"]
    assert usage["total_decisions"] == 5
    assert usage["base_decisions"] == 4
    assert usage["terminal_decisions"] == 1
    assert usage["terminal_ratio"] == 0.2
    assert usage["by_map"]["cracked-star-jar"]["total_decisions"] == 4
    assert usage["by_map"]["cracked-star-jar"]["terminal_decisions"] == 1
    assert usage["by_map"]["soda-creek"]["terminal_decisions"] == 0
    assert usage["by_time_bucket"]["late_180_to_300"]["terminal_decisions"] == 1


def test_terminal_conversion_branch_can_switch_on_low_health_risk():
    policy = TerminalConversionBranchPolicy(
        DummyPolicy(1),
        DummyPolicy(6),
        ["cracked-star-jar"],
        210.0,
        240.0,
        0.8,
        0.4,
        "base.zip",
        "terminal.zip",
    )

    policy.set_map_id("cracked-star-jar")
    policy.set_step_context(
        {
            "map_id": "cracked-star-jar",
            "time_seconds": 220.0,
            "diagnostics": {
                "enemy_pressure_risk": 0.1,
                "low_health_risk": 0.5,
            },
        }
    )

    action, _ = policy.predict(None)

    assert action == 6


def test_terminal_conversion_branch_uses_map_specific_windows_and_thresholds():
    policy = TerminalConversionBranchPolicy(
        DummyPolicy(1),
        DummyPolicy(6),
        ["cracked-star-jar", "caramel-workshop"],
        210.0,
        240.0,
        0.25,
        0.0,
        "base.zip",
        "terminal.zip",
        map_overrides={
            "caramel-workshop": {
                "min_seconds": 240.0,
                "max_seconds": 300.0,
                "min_pressure": 0.4,
            }
        },
    )

    policy.set_step_context(
        {
            "map_id": "cracked-star-jar",
            "time_seconds": 220.0,
            "diagnostics": {"enemy_pressure_risk": 0.3},
        }
    )
    cracked_action, _ = policy.predict(None)

    policy.set_step_context(
        {
            "map_id": "caramel-workshop",
            "time_seconds": 220.0,
            "diagnostics": {"enemy_pressure_risk": 0.9},
        }
    )
    early_caramel_action, _ = policy.predict(None)

    policy.set_step_context(
        {
            "map_id": "caramel-workshop",
            "time_seconds": 260.0,
            "diagnostics": {"enemy_pressure_risk": 0.3},
        }
    )
    low_pressure_caramel_action, _ = policy.predict(None)

    policy.set_step_context(
        {
            "map_id": "caramel-workshop",
            "time_seconds": 260.0,
            "diagnostics": {"enemy_pressure_risk": 0.5},
        }
    )
    caramel_action, _ = policy.predict(None)
    report = policy.policy_adapter_report()

    assert cracked_action == 6
    assert early_caramel_action == 1
    assert low_pressure_caramel_action == 1
    assert caramel_action == 6
    assert report["map_overrides"]["caramel-workshop"]["min_seconds"] == 240.0
    assert (
        report["effective_map_configs"]["cracked-star-jar"]["max_seconds"]
        == 240.0
    )
    assert (
        report["effective_map_configs"]["caramel-workshop"]["min_pressure"]
        == 0.4
    )


def test_edge_recovery_branch_switches_only_for_wallward_target_context():
    base = DummyPolicy(5)
    branch = DummyPolicy(7)
    policy = EdgeRecoveryBranchPolicy(
        base,
        branch,
        ["soda-creek"],
        0.0,
        60.0,
        32.0,
        0.2,
        0.0,
        0.75,
        "base.zip",
        "branch.zip",
    )

    policy.reset()
    policy.set_random_seed(999)
    policy.set_map_id("soda-creek")
    policy.set_step_context(
        {
            "map_id": "soda-creek",
            "time_seconds": 36.0,
            "diagnostics": {
                "boundary_edge_risk": 1.0,
                "enemy_pressure_risk": 0.3,
                "boundary": {
                    "left_distance": 400.0,
                    "right_distance": 400.0,
                    "bottom_distance": 0.0,
                    "top_distance": 400.0,
                },
            },
        }
    )
    branch_action, _ = policy.predict(None)
    decision = consume_policy_adapter_decision(policy)
    branch_scores = policy.action_scores(None)
    policy.set_step_context(
        {
            "map_id": "soda-creek",
            "time_seconds": 36.0,
            "diagnostics": {
                "boundary_edge_risk": 1.0,
                "enemy_pressure_risk": 0.3,
                "boundary": {
                    "left_distance": 0.0,
                    "right_distance": 400.0,
                    "bottom_distance": 400.0,
                    "top_distance": 400.0,
                },
            },
        }
    )
    unsafe_branch_action, _ = policy.predict(None)

    assert base.reset_count == 1
    assert branch.reset_count == 1
    assert base.random_seed == 999
    assert branch.random_seed == 999
    assert branch_action == 7
    assert branch_scores["scores"][7] == 1.0
    assert decision["mode"] == "edge_recovery_branch"
    assert decision["original_action"] == 5
    assert decision["target_action"] == 7
    assert unsafe_branch_action == 5
    report = policy.policy_adapter_report()
    assert report["mode"] == "edge_recovery_branch"
    assert report["usage"]["total_decisions"] == 2
    assert report["usage"]["base_decisions"] == 1
    assert report["usage"]["branch_decisions"] == 1


def test_edge_recovery_branch_uses_map_specific_windows():
    policy = EdgeRecoveryBranchPolicy(
        DummyPolicy(5),
        DummyPolicy(7),
        ["soda-creek", "caramel-workshop"],
        0.0,
        60.0,
        32.0,
        0.2,
        0.0,
        0.75,
        "base.zip",
        "branch.zip",
        map_overrides={
            "caramel-workshop": {
                "min_seconds": 30.0,
                "max_seconds": 45.0,
            }
        },
    )

    common_diagnostics = {
        "boundary_edge_risk": 1.0,
        "enemy_pressure_risk": 0.3,
        "boundary": {
            "left_distance": 400.0,
            "right_distance": 400.0,
            "bottom_distance": 0.0,
            "top_distance": 400.0,
        },
    }
    policy.set_step_context(
        {
            "map_id": "soda-creek",
            "time_seconds": 20.0,
            "diagnostics": common_diagnostics,
        }
    )
    soda_action, _ = policy.predict(None)
    soda_decision = consume_policy_adapter_decision(policy)

    policy.set_step_context(
        {
            "map_id": "caramel-workshop",
            "time_seconds": 20.0,
            "diagnostics": common_diagnostics,
        }
    )
    early_caramel_action, _ = policy.predict(None)
    early_caramel_decision = consume_policy_adapter_decision(policy)

    policy.set_step_context(
        {
            "map_id": "caramel-workshop",
            "time_seconds": 36.0,
            "diagnostics": common_diagnostics,
        }
    )
    caramel_action, _ = policy.predict(None)
    caramel_decision = consume_policy_adapter_decision(policy)
    report = policy.policy_adapter_report()

    assert soda_action == 7
    assert soda_decision["min_seconds"] == 0.0
    assert soda_decision["max_seconds"] == 60.0
    assert early_caramel_action == 5
    assert early_caramel_decision is None
    assert caramel_action == 7
    assert caramel_decision["min_seconds"] == 30.0
    assert caramel_decision["max_seconds"] == 45.0
    assert report["map_overrides"]["caramel-workshop"]["min_seconds"] == 30.0
    assert (
        report["effective_map_configs"]["soda-creek"]["max_seconds"]
        == 60.0
    )


def test_edge_recovery_branch_reports_nested_base_policy_adapter():
    base_policy = TerminalConversionBranchPolicy(
        DummyPolicy(5),
        DummyPolicy(6),
        ["caramel-workshop"],
        210.0,
        240.0,
        0.2,
        0.25,
        "base.zip",
        "terminal.zip",
        map_overrides={
            "caramel-workshop": {
                "min_seconds": 210.0,
                "max_seconds": 300.0,
            }
        },
    )
    policy = EdgeRecoveryBranchPolicy(
        base_policy,
        DummyPolicy(7),
        ["caramel-workshop"],
        30.0,
        45.0,
        32.0,
        0.2,
        0.0,
        0.75,
        "base.zip",
        "branch.zip",
    )

    report = policy.policy_adapter_report()

    assert report["base_policy_kind"] == "terminal_conversion_branch"
    assert report["base_policy_adapter"]["mode"] == "terminal_conversion_branch"
    terminal_config = report["base_policy_adapter"]["effective_map_configs"][
        "caramel-workshop"
    ]
    assert terminal_config["max_seconds"] == 300.0


def test_edge_recovery_branch_rejects_non_target_or_low_pressure_contexts():
    policy = EdgeRecoveryBranchPolicy(
        DummyPolicy(5),
        DummyPolicy(7),
        ["soda-creek"],
        10.0,
        60.0,
        32.0,
        0.2,
        0.0,
        0.75,
        "base.zip",
        "branch.zip",
    )

    scenarios = [
        ("caramel-workshop", 36.0, 1.0, 0.3),
        ("soda-creek", 9.9, 1.0, 0.3),
        ("soda-creek", 36.0, 0.4, 0.3),
        ("soda-creek", 36.0, 1.0, 0.1),
    ]
    for map_id, time_seconds, boundary_edge_risk, enemy_pressure_risk in scenarios:
        policy.set_map_id(map_id)
        policy.set_step_context(
            {
                "map_id": map_id,
                "time_seconds": time_seconds,
                "diagnostics": {
                    "boundary_edge_risk": boundary_edge_risk,
                    "enemy_pressure_risk": enemy_pressure_risk,
                    "boundary": {
                        "left_distance": 400.0,
                        "right_distance": 400.0,
                        "bottom_distance": 0.0,
                        "top_distance": 400.0,
                    },
                },
            }
        )
        action, _ = policy.predict(None)
        assert action == 5
        assert consume_policy_adapter_decision(policy) is None


def test_multimap_policy_adapter_report_aggregates_terminal_usage():
    adapter_a = {
        "mode": "terminal_conversion_branch",
        "target_maps": ["soda-creek", "cracked-star-jar"],
        "usage": {
            "total_decisions": 10,
            "base_decisions": 7,
            "terminal_decisions": 3,
            "terminal_ratio": 0.3,
            "by_map": {
                "soda-creek": {
                    "total_decisions": 10,
                    "base_decisions": 7,
                    "terminal_decisions": 3,
                    "terminal_ratio": 0.3,
                }
            },
            "by_time_bucket": {
                "late_180_to_300": {
                    "total_decisions": 10,
                    "base_decisions": 7,
                    "terminal_decisions": 3,
                    "terminal_ratio": 0.3,
                }
            },
        },
    }
    adapter_b = {
        "mode": "terminal_conversion_branch",
        "target_maps": ["soda-creek", "cracked-star-jar"],
        "usage": {
            "total_decisions": 5,
            "base_decisions": 5,
            "terminal_decisions": 0,
            "terminal_ratio": 0.0,
            "by_map": {
                "cracked-star-jar": {
                    "total_decisions": 5,
                    "base_decisions": 5,
                    "terminal_decisions": 0,
                    "terminal_ratio": 0.0,
                }
            },
            "by_time_bucket": {
                "late_180_to_300": {
                    "total_decisions": 5,
                    "base_decisions": 5,
                    "terminal_decisions": 0,
                    "terminal_ratio": 0.0,
                }
            },
        },
    }

    report = train_sb3.summarize_multimap_policy_adapter(
        [{"policy_adapter": adapter_a}, {"policy_adapter": adapter_b}]
    )

    assert report["usage_scope"] == "multimap_aggregate"
    assert report["usage"]["total_decisions"] == 15
    assert report["usage"]["base_decisions"] == 12
    assert report["usage"]["terminal_decisions"] == 3
    assert report["usage"]["terminal_ratio"] == 0.2
    assert report["usage"]["by_map"]["soda-creek"]["terminal_decisions"] == 3
    assert report["usage"]["by_map"]["cracked-star-jar"]["base_decisions"] == 5
    assert (
        report["usage"]["by_time_bucket"]["late_180_to_300"]["total_decisions"]
        == 15
    )


def test_multimap_policy_adapter_report_aggregates_edge_branch_usage():
    adapter_a = {
        "mode": "edge_recovery_branch",
        "target_maps": ["soda-creek"],
        "usage": {
            "total_decisions": 10,
            "base_decisions": 8,
            "branch_decisions": 2,
            "branch_ratio": 0.2,
            "by_map": {
                "soda-creek": {
                    "total_decisions": 10,
                    "base_decisions": 8,
                    "branch_decisions": 2,
                    "branch_ratio": 0.2,
                }
            },
            "by_time_bucket": {
                "opening_lt_60": {
                    "total_decisions": 10,
                    "base_decisions": 8,
                    "branch_decisions": 2,
                    "branch_ratio": 0.2,
                }
            },
        },
    }
    adapter_b = {
        "mode": "edge_recovery_branch",
        "target_maps": ["soda-creek"],
        "usage": {
            "total_decisions": 5,
            "base_decisions": 4,
            "branch_decisions": 1,
            "branch_ratio": 0.2,
            "by_map": {
                "soda-creek": {
                    "total_decisions": 5,
                    "base_decisions": 4,
                    "branch_decisions": 1,
                    "branch_ratio": 0.2,
                }
            },
            "by_time_bucket": {
                "opening_lt_60": {
                    "total_decisions": 5,
                    "base_decisions": 4,
                    "branch_decisions": 1,
                    "branch_ratio": 0.2,
                }
            },
        },
    }

    report = train_sb3.summarize_multimap_policy_adapter(
        [{"policy_adapter": adapter_a}, {"policy_adapter": adapter_b}]
    )

    assert report["usage_scope"] == "multimap_aggregate"
    assert report["usage"]["total_decisions"] == 15
    assert report["usage"]["base_decisions"] == 12
    assert report["usage"]["branch_decisions"] == 3
    assert report["usage"]["branch_ratio"] == 0.2
    assert report["usage"]["by_map"]["soda-creek"]["branch_decisions"] == 3


def test_compare_policy_to_rule_bots_forwards_late_recovery_options(monkeypatch):
    captured = {}

    def fake_evaluate_policy_model(config, algorithm, **kwargs):
        captured.update(kwargs)
        return {
            "policy_kind": "late_recovery_filter",
            "opening_policy": None,
            "policy_adapter": {"mode": "late_recovery_filter"},
            "edge_recovery_samples": None,
            "upgrade_policy": None,
            "action_selection": "deterministic",
            "summary": {
                "episodes": 1,
                "win_rate": 1.0,
                "average_kills": 5.0,
                "dominant_action_ratio": 0.1,
                "normalized_action_entropy": 1.0,
            },
        }

    monkeypatch.setattr(train_sb3, "evaluate_policy_model", fake_evaluate_policy_model)
    monkeypatch.setattr(
        train_sb3,
        "run_rule_bot_matrix",
        lambda config, bots, seed_start, episodes, seconds, map_id: {
            "stdout": {"bots": []},
            "command": ["game_harness", "matrix"],
            "stderr": "",
        },
    )

    report = train_sb3.compare_policy_to_rule_bots(
        {
            "phase": "test",
            "evaluation": {"episodes": 1, "seconds": 5, "seed_start": 10},
            "environment": {"tick_rate": 30},
            "models": {"ppo": "unused.zip"},
            "outputs": {"model_dir": "python/train/models"},
        },
        "ppo",
        late_recovery_filter=True,
        late_recovery_min_seconds=180.0,
        late_recovery_hazard_threshold=0.3,
        late_recovery_boss_threshold=0.2,
        late_recovery_enemy_threshold=0.1,
        late_recovery_low_health_threshold=0.4,
        late_recovery_toward_dot_threshold=0.25,
        late_recovery_maps=["caramel-workshop"],
    )

    assert captured["late_recovery_filter"] is True
    assert captured["late_recovery_hazard_threshold"] == 0.3
    assert captured["late_recovery_boss_threshold"] == 0.2
    assert captured["late_recovery_enemy_threshold"] == 0.1
    assert captured["late_recovery_low_health_threshold"] == 0.4
    assert captured["late_recovery_toward_dot_threshold"] == 0.25
    assert captured["late_recovery_maps"] == ["caramel-workshop"]
    assert report["policy_adapter"]["mode"] == "late_recovery_filter"


def test_compare_policy_to_rule_bots_forwards_late_split_options(monkeypatch):
    captured = {}

    def fake_evaluate_policy_model(config, algorithm, **kwargs):
        captured.update(kwargs)
        return {
            "policy_kind": "map_late_split",
            "opening_policy": None,
            "policy_adapter": {"mode": "map_late_split"},
            "edge_recovery_samples": None,
            "upgrade_policy": None,
            "action_selection": "deterministic",
            "summary": {
                "episodes": 1,
                "win_rate": 1.0,
                "average_kills": 5.0,
                "dominant_action_ratio": 0.1,
                "normalized_action_entropy": 1.0,
            },
        }

    monkeypatch.setattr(train_sb3, "evaluate_policy_model", fake_evaluate_policy_model)
    monkeypatch.setattr(
        train_sb3,
        "run_rule_bot_matrix",
        lambda config, bots, seed_start, episodes, seconds, map_id: {
            "stdout": {"bots": []},
            "command": ["game_harness", "matrix"],
            "stderr": "",
        },
    )

    report = train_sb3.compare_policy_to_rule_bots(
        {
            "phase": "test",
            "evaluation": {"episodes": 1, "seconds": 5, "seed_start": 10},
            "environment": {"tick_rate": 30},
            "models": {"ppo": "unused.zip"},
            "outputs": {"model_dir": "python/train/models"},
        },
        "ppo",
        late_split_model_path="late.zip",
        late_split_seconds=240.0,
        late_split_maps=["cracked-star-jar"],
    )

    assert captured["late_split_model_path"] == "late.zip"
    assert captured["late_split_seconds"] == 240.0
    assert captured["late_split_maps"] == ["cracked-star-jar"]
    assert report["policy_adapter"]["mode"] == "map_late_split"


def test_compare_policy_to_rule_bots_forwards_terminal_conversion_options(monkeypatch):
    captured = {}

    def fake_evaluate_policy_model(config, algorithm, **kwargs):
        captured.update(kwargs)
        return {
            "policy_kind": "terminal_conversion_branch",
            "opening_policy": None,
            "policy_adapter": {"mode": "terminal_conversion_branch"},
            "edge_recovery_samples": None,
            "upgrade_policy": None,
            "action_selection": "deterministic",
            "summary": {
                "episodes": 1,
                "win_rate": 1.0,
                "average_kills": 5.0,
                "dominant_action_ratio": 0.1,
                "normalized_action_entropy": 1.0,
            },
        }

    monkeypatch.setattr(train_sb3, "evaluate_policy_model", fake_evaluate_policy_model)
    monkeypatch.setattr(
        train_sb3,
        "run_rule_bot_matrix",
        lambda config, bots, seed_start, episodes, seconds, map_id: {
            "stdout": {"bots": []},
            "command": ["game_harness", "matrix"],
            "stderr": "",
        },
    )

    report = train_sb3.compare_policy_to_rule_bots(
        {
            "phase": "test",
            "evaluation": {"episodes": 1, "seconds": 5, "seed_start": 10},
            "environment": {"tick_rate": 30},
            "models": {"ppo": "unused.zip"},
            "outputs": {"model_dir": "python/train/models"},
        },
        "ppo",
        terminal_conversion_model_path="terminal.zip",
        terminal_conversion_maps=["cracked-star-jar", "caramel-workshop"],
        terminal_conversion_min_seconds=210.0,
        terminal_conversion_max_seconds=240.0,
        terminal_conversion_min_pressure=0.25,
        terminal_conversion_min_low_health_risk=0.4,
        terminal_conversion_map_overrides={
            "caramel-workshop": {
                "min_seconds": 240.0,
                "max_seconds": 300.0,
            },
        },
    )

    assert captured["terminal_conversion_model_path"] == "terminal.zip"
    assert captured["terminal_conversion_maps"] == [
        "cracked-star-jar",
        "caramel-workshop",
    ]
    assert captured["terminal_conversion_min_seconds"] == 210.0
    assert captured["terminal_conversion_max_seconds"] == 240.0
    assert captured["terminal_conversion_min_pressure"] == 0.25
    assert captured["terminal_conversion_min_low_health_risk"] == 0.4
    assert captured["terminal_conversion_map_overrides"] == {
        "caramel-workshop": {
            "min_seconds": 240.0,
            "max_seconds": 300.0,
        },
    }
    assert report["policy_adapter"]["mode"] == "terminal_conversion_branch"


def test_compare_policy_to_rule_bots_forwards_edge_recovery_branch_options(monkeypatch):
    captured = {}

    def fake_evaluate_policy_model(config, algorithm, **kwargs):
        captured.update(kwargs)
        return {
            "policy_kind": "edge_recovery_branch",
            "opening_policy": None,
            "policy_adapter": {"mode": "edge_recovery_branch"},
            "edge_recovery_samples": None,
            "upgrade_policy": None,
            "action_selection": "deterministic",
            "summary": {
                "episodes": 1,
                "win_rate": 1.0,
                "average_kills": 5.0,
                "dominant_action_ratio": 0.1,
                "normalized_action_entropy": 1.0,
            },
        }

    monkeypatch.setattr(train_sb3, "evaluate_policy_model", fake_evaluate_policy_model)
    monkeypatch.setattr(
        train_sb3,
        "run_rule_bot_matrix",
        lambda config, bots, seed_start, episodes, seconds, map_id: {
            "stdout": {"bots": []},
            "command": ["game_harness", "matrix"],
            "stderr": "",
        },
    )

    report = train_sb3.compare_policy_to_rule_bots(
        {
            "phase": "test",
            "evaluation": {"episodes": 1, "seconds": 5, "seed_start": 10},
            "environment": {"tick_rate": 30},
            "models": {"ppo": "unused.zip"},
            "outputs": {"model_dir": "python/train/models"},
        },
        "ppo",
        edge_recovery_branch_model_path="branch.zip",
        edge_recovery_branch_maps=["soda-creek"],
        edge_recovery_branch_min_seconds=5.0,
        edge_recovery_branch_max_seconds=45.0,
        edge_recovery_branch_distance=24.0,
        edge_recovery_branch_min_pressure=0.2,
        edge_recovery_branch_min_low_health_risk=0.3,
        edge_recovery_branch_min_boundary_risk=0.75,
        edge_recovery_branch_map_overrides={
            "caramel-workshop": {
                "min_seconds": 30.0,
                "max_seconds": 45.0,
            },
        },
    )

    assert captured["edge_recovery_branch_model_path"] == "branch.zip"
    assert captured["edge_recovery_branch_maps"] == ["soda-creek"]
    assert captured["edge_recovery_branch_min_seconds"] == 5.0
    assert captured["edge_recovery_branch_max_seconds"] == 45.0
    assert captured["edge_recovery_branch_distance"] == 24.0
    assert captured["edge_recovery_branch_min_pressure"] == 0.2
    assert captured["edge_recovery_branch_min_low_health_risk"] == 0.3
    assert captured["edge_recovery_branch_min_boundary_risk"] == 0.75
    assert captured["edge_recovery_branch_map_overrides"] == {
        "caramel-workshop": {
            "min_seconds": 30.0,
            "max_seconds": 45.0,
        },
    }
    assert report["policy_adapter"]["mode"] == "edge_recovery_branch"


def test_evaluation_gate_flags_deterministic_action_collapse():
    findings = policy_quality_findings(
        {
            "action_distribution": {
                "7": {"count": 151, "ratio": 1.0},
                "4": {"count": 0, "ratio": 0.0},
            },
            "normalized_action_entropy": 0.0,
            "reward_breakdown_average": {"total": 0.1, "terminal": 0.0},
        }
    )

    assert {finding["id"] for finding in findings} >= {
        "dominant_action_bias",
        "low_action_entropy",
    }
    assert evaluation_gate_decision(findings) == "evaluation_recorded_needs_action_bias_repair"


def test_behavior_clone_fallback_can_be_wrapped_with_sb3_opening(monkeypatch):
    class DummyModelClass:
        @staticmethod
        def load(path):
            assert str(path) == "opening.zip"
            return DummyPolicy(7)

    monkeypatch.setattr(
        train_sb3,
        "stable_baselines_model_classes",
        lambda: {"ppo": DummyModelClass},
    )
    monkeypatch.setattr(
        train_sb3,
        "load_behavior_clone_policy",
        lambda path: DummyPolicy(4),
    )

    policy = load_behavior_clone_policy_with_optional_opening(
        "ppo",
        "fallback.pt",
        opening_model_path="opening.zip",
        opening_seconds=60.0,
    )

    policy.set_step_context({"time_seconds": 10.0})
    opening_action, _ = policy.predict(None)
    policy.set_step_context({"time_seconds": 60.0})
    fallback_action, _ = policy.predict(None)

    assert opening_action == 7
    assert fallback_action == 4
    assert policy.opening_policy_report()["fallback_model_path"] == "fallback.pt"


def test_anchor_validation_guard_reports_threshold_failures():
    guard = {
        "enabled": True,
        "max_validation_kl": 0.2,
        "min_argmax_agreement": 0.9,
    }

    report = evaluate_anchor_validation_guard(
        {"mean_kl": 0.35, "argmax_agreement": 0.75},
        guard,
    )

    assert report["decision"] == "anchor_validation_guard_failed"
    assert len(report["blockers"]) == 2
    assert "validation_mean_kl" in report["blockers"][0]


def test_anchor_validation_guard_can_pass_or_be_disabled():
    assert (
        evaluate_anchor_validation_guard(
            {"mean_kl": 0.1, "argmax_agreement": 0.95},
            {"enabled": True, "max_validation_kl": 0.2, "min_argmax_agreement": 0.9},
        )["decision"]
        == "anchor_validation_guard_passed"
    )
    assert (
        evaluate_anchor_validation_guard(
            {"mean_kl": 9.0, "argmax_agreement": 0.0},
            {"enabled": False},
        )["decision"]
        == "anchor_validation_guard_not_configured"
    )


def test_anchor_validation_guard_rejects_invalid_thresholds():
    with pytest.raises(ValueError):
        validate_anchor_validation_guard_thresholds(max_validation_kl=-0.1)
    with pytest.raises(ValueError):
        validate_anchor_validation_guard_thresholds(min_argmax_agreement=1.1)
