import json

import pytest

from python.train.compare_behavior_clone_trace_to_dataset import (
    compare_trace_to_dataset,
    load_trace,
)
from python.train.test_train_behavior_clone import tiny_dataset


pytest.importorskip("numpy")


def test_trace_dataset_comparison_conditions_short_window_progress(tmp_path):
    trace_path = tmp_path / "trace.json"
    trace_path.write_text(
        json.dumps(
            {
                "episode": {"map_id": "soda-creek"},
                "steps": [
                    {
                        "step": 1,
                        "time_seconds": 30.0,
                        "action": 1,
                        "observation": [0.95, 0.0, 0.2],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    dataset = tiny_dataset()
    dataset["actions"][0] = 1
    dataset["observations"][1] = [0.1, 0.0, 0.2]
    dataset["actions"][1] = 1
    dataset["sample_metadata"][1]["map_id"] = "soda-creek"
    dataset["sample_metadata"][1]["time_seconds"] = 30.0

    report = compare_trace_to_dataset(
        load_trace(trace_path),
        dataset,
        phase_duration_seconds=300.0,
        same_map_only=True,
        offline_min_seconds=0.0,
        offline_max_seconds=60.0,
        nearest_k=1,
    )

    assert report["gate_decision"] == "trace_dataset_nearest_neighbor_recorded_watch_only"
    assert report["summary"]["nearest_target_matches_online_action_ratio"] == 1.0
    assert report["examples"][0]["conditioned_progress"] == 0.1
