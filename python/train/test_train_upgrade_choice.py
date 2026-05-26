from types import SimpleNamespace

import pytest

from python.train.train_behavior_clone import load_upgrade_choice_dataset
from python.train.train_upgrade_choice import (
    build_upgrade_choice_rows,
    load_upgrade_choice_policy,
    summarize_upgrade_choice_rows,
    train_upgrade_choice_model,
)


pytest.importorskip("numpy")
pytest.importorskip("torch")


def tiny_upgrade_dataset():
    return {
        "paths": ["memory.jsonl"],
        "metadata": [
            {
                "path": "memory.jsonl",
                "bot": "kite",
                "map_id": "soda-creek",
                "observation_version": 2,
                "observation_len": 3,
                "include_upgrade_samples": True,
                "content_hash": "fixture",
            }
        ],
        "samples": [
            {
                "path": "memory.jsonl",
                "seed": 1,
                "map_id": "soda-creek",
                "bot": "kite",
                "tick": 100,
                "time_seconds": 3.0,
                "health_ratio": 1.0,
                "level": 2,
                "kills": 5,
                "upgrade_options": ["bubble-shoes", "cream-clockwork", "gum-shield"],
                "chosen_index": 1,
                "chosen_upgrade_id": "cream-clockwork",
                "observation": [0.1, 0.2, 0.3],
            },
            {
                "path": "memory.jsonl",
                "seed": 2,
                "map_id": "soda-creek",
                "bot": "kite",
                "tick": 200,
                "time_seconds": 6.0,
                "health_ratio": 0.8,
                "level": 2,
                "kills": 8,
                "upgrade_options": ["bubble-shoes", "cream-clockwork", "gum-shield"],
                "chosen_index": 0,
                "chosen_upgrade_id": "bubble-shoes",
                "observation": [0.2, 0.1, 0.4],
            },
            {
                "path": "memory.jsonl",
                "seed": 3,
                "map_id": "caramel-workshop",
                "bot": "kite",
                "tick": 300,
                "time_seconds": 9.0,
                "health_ratio": 0.7,
                "level": 3,
                "kills": 12,
                "upgrade_options": ["candy-crystal-lance", "cream-clockwork", "gum-shield"],
                "chosen_index": 2,
                "chosen_upgrade_id": "gum-shield",
                "observation": [0.3, 0.1, 0.5],
            },
            {
                "path": "memory.jsonl",
                "seed": 4,
                "map_id": "caramel-workshop",
                "bot": "kite",
                "tick": 400,
                "time_seconds": 12.0,
                "health_ratio": 0.9,
                "level": 3,
                "kills": 16,
                "upgrade_options": ["candy-crystal-lance", "cream-clockwork", "gum-shield"],
                "chosen_index": 0,
                "chosen_upgrade_id": "candy-crystal-lance",
                "observation": [0.4, 0.2, 0.6],
            },
        ],
    }


def args_for(tmp_path):
    return SimpleNamespace(
        seed=123,
        epochs=2,
        batch_size=4,
        hidden_size=8,
        learning_rate=0.01,
        validation_split=0.25,
        model_out=str(tmp_path / "upgrade_choice.pt"),
    )


def test_upgrade_choice_rows_expand_each_option_once():
    rows = build_upgrade_choice_rows(tiny_upgrade_dataset())
    summary = summarize_upgrade_choice_rows(rows)

    assert summary["choice_count"] == 4
    assert summary["row_count"] == 12
    assert summary["positive_row_count"] == 4
    assert summary["upgrade_vocabulary_size"] == 4
    assert summary["input_len"] == 7


def test_upgrade_choice_training_smoke_writes_checkpoint(tmp_path):
    report = train_upgrade_choice_model(tiny_upgrade_dataset(), args_for(tmp_path))
    policy = load_upgrade_choice_policy(report["model_path"])
    decision = policy.choose(
        [0.1, 0.2, 0.3],
        ["bubble-shoes", "cream-clockwork", "unknown-upgrade"],
    )

    assert report["status"] == "trained"
    assert report["gate_decision"] == "upgrade_choice_training_smoke_not_policy_gate"
    assert report["rows"]["choice_count"] == 4
    assert report["training"]["validation_choice_count"] == 1
    assert (tmp_path / "upgrade_choice.pt").exists()
    assert 0 <= decision["choice_index"] < 3
    assert decision["scores"][2]["score"] < -1000.0


def test_upgrade_choice_loader_rejects_mismatched_choice(tmp_path):
    dataset_path = tmp_path / "bad.jsonl"
    dataset_path.write_text(
        "\n".join(
            [
                '{"record_type":"metadata","include_upgrade_samples":true}',
                '{"record_type":"upgrade_sample","upgrade_options":["a","b"],"chosen_index":0,"chosen_upgrade_id":"b","observation":[0.1]}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    dataset = load_upgrade_choice_dataset(dataset_path)
    with pytest.raises(ValueError, match="does not match chosen_index"):
        build_upgrade_choice_rows(dataset)
