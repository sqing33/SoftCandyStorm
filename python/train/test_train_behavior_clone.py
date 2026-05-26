import json
from types import SimpleNamespace

import pytest

from python.train.train_behavior_clone import (
    build_sample_weights,
    diagnose_sequence_dataset,
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
