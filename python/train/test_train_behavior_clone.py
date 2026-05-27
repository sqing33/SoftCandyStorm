import json
from types import SimpleNamespace

import pytest

from python.train.train_behavior_clone import (
    build_sample_weights,
    diagnose_behavior_clone_policy_on_dataset,
    diagnose_sequence_dataset,
    filter_edge_recovery_samples_by_time_window,
    filter_risk_recovery_samples_by_time_window,
    filter_dataset_by_time_phase,
    load_trajectory_dataset,
    load_upgrade_choice_dataset,
    load_behavior_clone_policy,
    save_staged_behavior_clone_policy,
    summarize_dataset,
    summarize_upgrade_choice_dataset,
    train_behavior_clone,
)


pytest.importorskip("numpy")
pytest.importorskip("torch")


def tiny_dataset():
    observations = [
        [0.1, 0.0, 0.2],
        [0.2, 0.1, 0.3],
        [0.3, 0.1, 0.4],
        [0.4, 0.2, 0.5],
        [0.0, 0.3, 0.2],
        [0.1, 0.4, 0.3],
        [0.2, 0.5, 0.4],
        [0.3, 0.6, 0.5],
    ]
    actions = [0, 1, 1, 2, 2, 1, 0, 2]
    sample_metadata = []
    for index, observation in enumerate(observations):
        sample_metadata.append(
            {
                "path": "memory.jsonl",
                "seed": 1 if index < 4 else 2,
                "map_id": "soda-creek" if index < 4 else "caramel-workshop",
                "tick": index,
                "time_seconds": float(index),
                "health_ratio": 0.8,
                "level": 1,
                "kills": index,
            }
        )
    return {
        "paths": ["memory.jsonl"],
        "observations": observations,
        "actions": actions,
        "sample_metadata": sample_metadata,
        "metadata": [],
        "episode_count": 2,
        "skipped_upgrade_samples": 0,
        "observation_len": len(observations[0]),
        "action_count": 3,
    }


def args_for(tmp_path, *, architecture, context_frames=1, map_conditioning="none"):
    return SimpleNamespace(
        architecture=architecture,
        seed=123,
        context_frames=context_frames,
        map_conditioning=map_conditioning,
        time_phase_conditioning="none",
        time_phase_thresholds=[0.2, 0.6],
        validation_split=0.25,
        sample_weighting="none",
        danger_health_threshold=0.7,
        danger_low_health_weight=2.0,
        danger_late_start_seconds=60.0,
        danger_late_horizon_seconds=300.0,
        danger_late_weight=1.0,
        action_change_weight=2.0,
        edge_recovery_sample_weight=1.0,
        risk_recovery_sample_weight=1.0,
        entropy_regularization=0.0,
        class_weighting="none",
        batch_size=4,
        epochs=1,
        learning_rate=0.001,
        hidden_size=8,
        model_out=str(tmp_path / f"{architecture}.pt"),
    )


def test_gru_behavior_clone_checkpoint_can_predict_with_map_conditioning(tmp_path):
    report = train_behavior_clone(
        tiny_dataset(),
        args_for(tmp_path, architecture="gru", context_frames=3, map_conditioning="one_hot"),
    )

    assert report["status"] == "trained"
    assert report["training"]["architecture"] == "gru"
    assert report["training"]["context_frames"] == 3
    assert report["training"]["map_conditioning"]["mode"] == "one_hot"

    policy = load_behavior_clone_policy(report["model_path"])
    policy.set_map_id("soda-creek")
    action, _ = policy.predict([0.15, 0.05, 0.25])
    scores = policy.action_scores([0.15, 0.05, 0.25])

    assert 0 <= action < 3
    assert scores["kind"] == "probability"
    assert len(scores["scores"]) == 3


def test_mlp_behavior_clone_checkpoint_stays_loadable(tmp_path):
    report = train_behavior_clone(
        tiny_dataset(),
        args_for(tmp_path, architecture="mlp", context_frames=2),
    )

    policy = load_behavior_clone_policy(report["model_path"])
    action, _ = policy.predict([0.15, 0.05, 0.25])

    assert report["training"]["architecture"] == "mlp"
    assert 0 <= action < 3


def test_offline_policy_diagnostic_flags_dominant_action_bias():
    class ConstantPolicy:
        action_count = 3

        def reset(self):
            pass

        def set_map_id(self, map_id):
            pass

        def action_scores(self, observation):
            return {"kind": "probability", "scores": [0.05, 0.9, 0.05]}

        def predict(self, observation, deterministic=True):
            return 1, None

    report = diagnose_behavior_clone_policy_on_dataset(
        ConstantPolicy(),
        tiny_dataset(),
        model_path="memory.pt",
        dominant_action_threshold=0.75,
    )

    assert report["gate_decision"] == "offline_policy_diagnostic_recorded_needs_action_bias_repair"
    assert report["overall"]["dominant_predicted_action"]["action"] == "1"
    assert report["overall"]["dominant_predicted_action"]["ratio"] == 1.0
    assert any(finding["id"] == "offline_dominant_action_bias" for finding in report["findings"])


def test_sequence_diagnostics_report_context_padding_and_transitions():
    diagnostics = diagnose_sequence_dataset(
        tiny_dataset(),
        context_frames=3,
        late_start_seconds=4.0,
        low_health_threshold=0.9,
    )

    assert diagnostics["context_frames"] == 3
    assert diagnostics["padding"]["total_missing_frames"] == 6
    assert diagnostics["padding"]["fully_seeded_samples"] == 4
    assert diagnostics["padding"]["fully_seeded_ratio"] == 0.5
    assert diagnostics["action_transitions"]["transition_count"] == 6
    assert diagnostics["action_transitions"]["same_action_count"] == 1
    assert diagnostics["late_low_health"]["sample_count"] == 4
    assert set(diagnostics["per_map"]) == {"caramel-workshop", "soda-creek"}
    assert diagnostics["per_map"]["soda-creek"]["sample_count"] == 4
    assert diagnostics["per_map"]["caramel-workshop"]["sample_count"] == 4


def test_entropy_regularization_is_reported(tmp_path):
    args = args_for(tmp_path, architecture="mlp", context_frames=2)
    args.entropy_regularization = 0.05
    report = train_behavior_clone(tiny_dataset(), args)

    assert report["training"]["entropy_regularization"] == 0.05
    assert report["final"]["train_entropy_nats"] > 0.0
    assert report["final"]["validation_entropy_nats"] > 0.0
    assert report["final"]["train_cross_entropy_loss"] >= report["final"]["train_loss"]


def test_action_change_sample_weighting_boosts_transition_samples(tmp_path):
    import numpy as np

    args = args_for(tmp_path, architecture="mlp")
    args.sample_weighting = "action_change"
    args.action_change_weight = 3.0

    weights, report = build_sample_weights(
        tiny_dataset(),
        list(range(len(tiny_dataset()["actions"]))),
        args,
        np,
    )

    assert report["mode"] == "action_change"
    assert report["action_change_sample_count"] == 5
    assert report["action_change_sample_ratio"] == 0.625
    assert weights.tolist() == [1.0, 4.0, 1.0, 4.0, 1.0, 4.0, 4.0, 4.0]


def test_time_phase_balance_weighting_boosts_underrepresented_phase(tmp_path):
    import numpy as np

    args = args_for(tmp_path, architecture="mlp")
    args.sample_weighting = "time_phase_balance"
    args.time_phase_thresholds = [0.2, 0.6]

    weights, report = build_sample_weights(
        tiny_dataset(),
        list(range(len(tiny_dataset()["actions"]))),
        args,
        np,
    )

    assert report["mode"] == "time_phase_balance"
    assert report["time_phase_balance"]["phase_distribution"]["opening"]["count"] == 3
    assert report["time_phase_balance"]["phase_distribution"]["mid"]["count"] == 5
    assert report["time_phase_balance"]["phase_distribution"]["late"]["count"] == 0
    assert report["time_phase_balance"]["phase_multipliers"]["opening"] == pytest.approx(1.333333)
    assert report["time_phase_balance"]["phase_multipliers"]["mid"] == pytest.approx(0.8)
    assert weights.tolist() == pytest.approx(
        [1.333333, 0.8, 0.8, 0.8, 1.333333, 1.333333, 0.8, 0.8],
        rel=1e-5,
    )


def test_edge_recovery_sample_weight_boosts_repair_samples(tmp_path):
    import numpy as np

    dataset = tiny_dataset()
    dataset["sample_metadata"] = [dict(item) for item in dataset["sample_metadata"]]
    dataset["sample_metadata"][1]["sample_source"] = "edge_recovery_supervision"
    dataset["sample_metadata"][5]["sample_source"] = "edge_recovery_supervision"
    args = args_for(tmp_path, architecture="mlp")
    args.edge_recovery_sample_weight = 3.5

    weights, report = build_sample_weights(
        dataset,
        list(range(len(dataset["actions"]))),
        args,
        np,
    )

    assert report["mode"] == "edge_recovery_auxiliary"
    assert report["base_mode"] == "none"
    assert report["edge_recovery_sample_weight"] == 3.5
    assert report["edge_recovery_weighted_sample_count"] == 2
    assert weights.tolist() == pytest.approx(
        [1.0, 3.5, 1.0, 1.0, 1.0, 3.5, 1.0, 1.0],
        rel=1e-6,
    )


def test_risk_recovery_sample_weight_boosts_late_repair_samples(tmp_path):
    import numpy as np

    dataset = tiny_dataset()
    dataset["risk_recovery_sample_records"] = 2
    dataset["sample_metadata"] = [dict(item) for item in dataset["sample_metadata"]]
    dataset["sample_metadata"][3]["sample_source"] = "risk_recovery_supervision"
    dataset["sample_metadata"][7]["sample_source"] = "risk_recovery_supervision"
    args = args_for(tmp_path, architecture="mlp")
    args.risk_recovery_sample_weight = 4.0

    weights, report = build_sample_weights(
        dataset,
        list(range(len(dataset["actions"]))),
        args,
        np,
    )

    assert report["mode"] == "risk_recovery_auxiliary"
    assert report["risk_recovery_sample_weight"] == 4.0
    assert report["risk_recovery_weighted_sample_count"] == 2
    assert weights.tolist() == pytest.approx(
        [1.0, 1.0, 1.0, 4.0, 1.0, 1.0, 1.0, 4.0],
        rel=1e-6,
    )


def test_time_phase_conditioning_stays_loadable_online(tmp_path):
    args = args_for(
        tmp_path,
        architecture="gru",
        context_frames=2,
        map_conditioning="one_hot",
    )
    args.time_phase_conditioning = "one_hot"
    args.time_phase_thresholds = [0.15, 0.3]
    report = train_behavior_clone(tiny_dataset(), args)

    phase_report = report["training"]["time_phase_conditioning"]
    assert phase_report["mode"] == "one_hot"
    assert phase_report["dimension"] == 3
    assert phase_report["phase_distribution"]["late"]["count"] > 0

    policy = load_behavior_clone_policy(report["model_path"])
    policy.set_map_id("caramel-workshop")
    action, _ = policy.predict([0.8, 0.2, 0.3])
    scores = policy.action_scores([0.8, 0.2, 0.3])

    assert 0 <= action < 3
    assert len(scores["scores"]) == 3


def test_time_phase_filter_keeps_only_requested_samples():
    filtered, report = filter_dataset_by_time_phase(
        tiny_dataset(),
        "mid",
        [0.25, 0.35],
    )

    assert report["mode"] == "mid"
    assert report["after_sample_count"] == 2
    assert filtered["observations"] == [[0.3, 0.1, 0.4], [0.3, 0.6, 0.5]]


def test_time_phase_filter_recounts_edge_recovery_samples():
    dataset = tiny_dataset()
    dataset["edge_recovery_sample_records"] = 2
    dataset["sample_metadata"] = [dict(item) for item in dataset["sample_metadata"]]
    dataset["sample_metadata"][0]["sample_source"] = "edge_recovery_supervision"
    dataset["sample_metadata"][2]["sample_source"] = "edge_recovery_supervision"

    filtered, _ = filter_dataset_by_time_phase(
        dataset,
        "opening",
        [0.25, 0.35],
    )

    assert filtered["edge_recovery_sample_records"] == 1


def test_edge_recovery_time_window_filter_only_drops_repair_samples():
    dataset = tiny_dataset()
    dataset["edge_recovery_sample_records"] = 2
    dataset["sample_metadata"] = [dict(item) for item in dataset["sample_metadata"]]
    dataset["sample_metadata"][1]["sample_source"] = "edge_recovery_supervision"
    dataset["sample_metadata"][5]["sample_source"] = "edge_recovery_supervision"

    filtered, report = filter_edge_recovery_samples_by_time_window(
        dataset,
        min_seconds=4.0,
        max_seconds=6.0,
    )

    assert report["mode"] == "time_window"
    assert report["before_sample_count"] == 8
    assert report["after_sample_count"] == 7
    assert report["before_edge_recovery_sample_count"] == 2
    assert report["after_edge_recovery_sample_count"] == 1
    assert report["dropped_edge_recovery_sample_count"] == 1
    assert filtered["edge_recovery_sample_records"] == 1
    assert filtered["actions"] == [0, 1, 2, 2, 1, 0, 2]


def test_risk_recovery_time_window_filter_only_drops_late_repair_samples():
    dataset = tiny_dataset()
    dataset["risk_recovery_sample_records"] = 2
    dataset["sample_metadata"] = [dict(item) for item in dataset["sample_metadata"]]
    dataset["sample_metadata"][2]["sample_source"] = "risk_recovery_supervision"
    dataset["sample_metadata"][6]["sample_source"] = "risk_recovery_supervision"

    filtered, report = filter_risk_recovery_samples_by_time_window(
        dataset,
        min_seconds=5.0,
        max_seconds=7.0,
    )

    assert report["mode"] == "time_window"
    assert report["before_risk_recovery_sample_count"] == 2
    assert report["after_risk_recovery_sample_count"] == 1
    assert report["dropped_risk_recovery_sample_count"] == 1
    assert filtered["risk_recovery_sample_records"] == 1
    assert filtered["actions"] == [0, 1, 2, 2, 1, 0, 2]


def test_staged_behavior_clone_dispatches_between_phase_models(tmp_path):
    phase_paths = {}
    thresholds = [0.15, 0.25]
    for phase in ("opening", "mid", "late"):
        dataset, _ = filter_dataset_by_time_phase(tiny_dataset(), phase, thresholds)
        args = args_for(tmp_path / phase, architecture="mlp", context_frames=1)
        args.time_phase_filter = phase
        report = train_behavior_clone(dataset, args)
        phase_paths[phase] = report["model_path"]

    staged_path = tmp_path / "staged.pt"
    package_report = save_staged_behavior_clone_policy(staged_path, phase_paths, thresholds)
    policy = load_behavior_clone_policy(package_report["model_path"])
    policy.set_map_id("soda-creek")

    for observation in ([0.1, 0.0, 0.2], [0.3, 0.1, 0.4], [0.4, 0.2, 0.5]):
        action, _ = policy.predict(observation)
        scores = policy.action_scores(observation)
        assert 0 <= action < 3
        assert len(scores["scores"]) == 3


def test_staged_behavior_clone_can_dispatch_by_absolute_time(tmp_path):
    phase_paths = {}
    thresholds = [0.15, 0.25]
    for phase in ("opening", "mid", "late"):
        dataset, _ = filter_dataset_by_time_phase(tiny_dataset(), phase, thresholds)
        args = args_for(tmp_path / phase, architecture="mlp", context_frames=1)
        args.time_phase_filter = phase
        report = train_behavior_clone(dataset, args)
        phase_paths[phase] = report["model_path"]

    staged_path = tmp_path / "staged_absolute.pt"
    package_report = save_staged_behavior_clone_policy(
        staged_path,
        phase_paths,
        thresholds,
        phase_duration_seconds=300.0,
    )
    policy = load_behavior_clone_policy(package_report["model_path"])
    observation = [0.95, 0.0, 0.2]

    assert package_report["phase_dispatch"] == "absolute_time_seconds"
    assert package_report["phase_duration_seconds"] == 300.0
    assert policy._policy_for_observation(observation) is policy.subpolicies["late"]

    policy.set_step_context({"time_seconds": 44.9})
    assert policy._policy_for_observation(observation) is policy.subpolicies["opening"]
    policy.set_step_context({"time_seconds": 45.0})
    assert policy._policy_for_observation(observation) is policy.subpolicies["mid"]
    policy.set_step_context({"time_seconds": 75.0})
    assert policy._policy_for_observation(observation) is policy.subpolicies["late"]


def test_behavior_clone_time_phase_conditioning_uses_absolute_step_context(tmp_path):
    import numpy as np

    args = args_for(tmp_path, architecture="mlp", context_frames=1)
    args.time_phase_conditioning = "one_hot"
    report = train_behavior_clone(tiny_dataset(), args)
    policy = load_behavior_clone_policy(report["model_path"])
    values = np.asarray([0.95, 0.0, 0.2], dtype=np.float32)

    assert policy._time_phase_features(values, np).tolist() == [0.0, 0.0, 1.0]

    policy.set_step_context({"time_seconds": 30.0, "phase_duration_seconds": 300.0})
    assert policy._time_phase_features(values, np).tolist() == [1.0, 0.0, 0.0]
    assert policy._conditioning_values(values)[0] == pytest.approx(0.1)


def test_upgrade_samples_are_loaded_separately_from_movement_dataset(tmp_path):
    dataset_path = tmp_path / "trajectory.jsonl"
    records = [
        {
            "record_type": "metadata",
            "bot": "kite",
            "map_id": "soda-creek",
            "observation_version": 2,
            "observation_len": 3,
            "action_count": 9,
            "include_upgrade_samples": True,
            "content_hash": "fixture",
        },
        {
            "record_type": "sample",
            "seed": 1,
            "map_id": "soda-creek",
            "bot": "kite",
            "tick": 10,
            "time_seconds": 1.0,
            "health_ratio": 1.0,
            "level": 1,
            "kills": 2,
            "action": 3,
            "movement": [1.0, 0.0],
            "observation": [0.1, 0.2, 0.3],
        },
        {
            "record_type": "upgrade_sample",
            "seed": 1,
            "map_id": "soda-creek",
            "bot": "kite",
            "tick": 20,
            "time_seconds": 2.0,
            "health_ratio": 0.9,
            "level": 2,
            "kills": 4,
            "upgrade_options": ["rainbow-candy-shot-level-2", "gum-shield-level-1"],
            "chosen_index": 1,
            "chosen_upgrade_id": "gum-shield-level-1",
            "observation": [0.2, 0.3, 0.4],
        },
        {
            "record_type": "episode",
            "seed": 1,
            "map_id": "soda-creek",
            "bot": "kite",
            "terminal": "victory",
            "reason": "duration_reached",
            "duration_seconds": 60.0,
            "kills": 4,
            "level": 2,
            "damage_taken": 1.0,
            "samples": 1,
            "upgrade_samples": 1,
            "skipped_upgrade_samples": 1,
        },
    ]
    dataset_path.write_text(
        "\n".join(json.dumps(record) for record in records) + "\n",
        encoding="utf-8",
    )

    movement_dataset = load_trajectory_dataset(dataset_path)
    movement_summary = summarize_dataset(movement_dataset)
    upgrade_dataset = load_upgrade_choice_dataset(dataset_path)
    upgrade_summary = summarize_upgrade_choice_dataset(upgrade_dataset)

    assert movement_summary["sample_count"] == 1
    assert movement_summary["upgrade_sample_records"] == 1
    assert upgrade_summary["sample_count"] == 1
    assert upgrade_summary["chosen_upgrade_distribution"]["gum-shield-level-1"]["count"] == 1


def test_edge_recovery_samples_load_as_repair_movement_targets(tmp_path):
    dataset_path = tmp_path / "edge_recovery_samples.jsonl"
    records = [
        {
            "record_type": "edge_recovery_supervision_sample",
            "schema_version": 1,
            "sample_role": "repair_training_input",
            "target_source": "edge_recovery_filter",
            "seed": 62201,
            "map_id": "soda-creek",
            "tick": 1800,
            "time_seconds": 60.0,
            "observation_version": 2,
            "observation_len": 3,
            "observation": [0.1, 0.2, 0.3],
            "original_action": 7,
            "target_action": 0,
            "adapter_decision": {
                "mode": "edge_recovery_filter",
                "edge_distance": 32.0,
                "original_action": 7,
                "target_action": 0,
            },
            "diagnostics": {
                "boundary": {
                    "left_distance": 0.0,
                    "right_distance": 2400.0,
                    "bottom_distance": 900.0,
                    "top_distance": 900.0,
                }
            },
        }
    ]
    dataset_path.write_text(
        "\n".join(json.dumps(record) for record in records) + "\n",
        encoding="utf-8",
    )

    dataset = load_trajectory_dataset(dataset_path)
    summary = summarize_dataset(dataset)

    assert dataset["actions"] == [0]
    assert dataset["action_count"] == 9
    assert summary["edge_recovery_sample_records"] == 1
    assert summary["sample_summary"]["sample_source_distribution"]["edge_recovery_supervision"]["count"] == 1


def test_risk_recovery_samples_load_as_repair_movement_targets(tmp_path):
    dataset_path = tmp_path / "risk_recovery_samples.jsonl"
    records = [
        {
            "record_type": "risk_recovery_supervision_sample",
            "schema_version": 1,
            "sample_role": "repair_training_input",
            "target_source": "late_recovery_filter",
            "seed": 62300,
            "map_id": "caramel-workshop",
            "tick": 6600,
            "time_seconds": 220.0,
            "observation_version": 2,
            "observation_len": 3,
            "observation": [0.8, 0.2, 0.3],
            "original_action": 4,
            "target_action": 7,
            "adapter_decision": {
                "mode": "late_recovery_filter",
                "original_action": 4,
                "target_action": 7,
                "risk_reasons": ["wallward_edge", "toward_hazard"],
            },
            "diagnostics": {
                "hazard_pressure_risk": 1.0,
                "boss_pressure_risk": 0.2,
            },
        }
    ]
    dataset_path.write_text(
        "\n".join(json.dumps(record) for record in records) + "\n",
        encoding="utf-8",
    )

    dataset = load_trajectory_dataset(dataset_path)
    summary = summarize_dataset(dataset)

    assert dataset["actions"] == [7]
    assert dataset["action_count"] == 9
    assert summary["risk_recovery_sample_records"] == 1
    assert summary["sample_summary"]["sample_source_distribution"]["risk_recovery_supervision"]["count"] == 1
