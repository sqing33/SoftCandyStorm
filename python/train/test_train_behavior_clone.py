from types import SimpleNamespace

import pytest

from python.train.train_behavior_clone import (
    load_behavior_clone_policy,
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
        validation_split=0.25,
        sample_weighting="none",
        danger_health_threshold=0.7,
        danger_low_health_weight=2.0,
        danger_late_start_seconds=60.0,
        danger_late_horizon_seconds=300.0,
        danger_late_weight=1.0,
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
