import json

import pytest

from python.train.rank_behavior_clone_dataset_episodes import (
    rank_traces_against_dataset,
)
from python.train.train_behavior_clone import load_trajectory_dataset
from python.train.test_train_behavior_clone import tiny_dataset


pytest.importorskip("numpy")


def test_episode_ranker_prefers_episode_with_matching_nearest_actions(tmp_path):
    trace_path = tmp_path / "trace.json"
    trace_path.write_text(
        json.dumps(
            {
                "episode": {"map_id": "soda-creek"},
                "steps": [
                    {
                        "step": 1,
                        "time_seconds": 0.0,
                        "action": 0,
                        "observation": [0.1, 0.0, 0.2],
                    },
                    {
                        "step": 2,
                        "time_seconds": 1.0,
                        "action": 1,
                        "observation": [0.2, 0.1, 0.3],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    dataset = tiny_dataset()

    report = rank_traces_against_dataset(
        [
            {
                "path": str(trace_path),
                "episode": {"map_id": "soda-creek"},
                "steps": json.loads(trace_path.read_text(encoding="utf-8"))["steps"],
                "observations": [[0.1, 0.0, 0.2], [0.2, 0.1, 0.3]],
            }
        ],
        dataset,
        same_map_only=True,
        offline_min_seconds=0.0,
        offline_max_seconds=3.0,
        nearest_k=1,
        top_limit=3,
    )

    assert report["gate_decision"] == "dataset_episode_ranking_recorded_watch_only"
    assert report["traces"][0]["summary"]["top1_nearest_target_matches_online_action_ratio"] == 1.0
    top = report["combined"]["ranked_episodes"][0]
    assert top["map_id"] == "soda-creek"
    assert top["seed"] == "1"
    assert top["bot"] == "unknown"
    assert top["top1_hit_count"] == 2
    assert top["top1_action_match_count"] == 2
    assert top["top1_action_match_ratio"] == 1.0


def test_trajectory_loader_preserves_bot_metadata_for_ranker(tmp_path):
    path = tmp_path / "trajectory.jsonl"
    rows = [
        {
            "record_type": "metadata",
            "observation_len": 3,
            "action_count": 9,
        },
        {
            "record_type": "sample",
            "seed": 42,
            "map_id": "caramel-workshop",
            "bot": "route",
            "tick": 1,
            "time_seconds": 210.0,
            "health_ratio": 0.5,
            "level": 3,
            "kills": 10,
            "action": 7,
            "observation": [0.1, 0.2, 0.3],
        },
    ]
    path.write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n",
        encoding="utf-8",
    )

    dataset = load_trajectory_dataset(path)

    assert dataset["sample_metadata"][0]["bot"] == "route"
