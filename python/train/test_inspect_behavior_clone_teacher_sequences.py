import json

import pytest

from python.train.inspect_behavior_clone_teacher_sequences import (
    inspect_teacher_sequences,
    load_trace,
)
from python.train.test_train_behavior_clone import tiny_dataset


pytest.importorskip("numpy")


def test_teacher_sequence_inspection_reports_mismatch_context(tmp_path):
    trace_path = tmp_path / "trace.json"
    trace_path.write_text(
        json.dumps(
            {
                "episode": {"map_id": "soda-creek"},
                "steps": [
                    {
                        "step": 1,
                        "time_seconds": 25.0,
                        "action": 5,
                        "observation": [0.95, 0.0, 0.2],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    dataset = tiny_dataset()
    dataset["sample_metadata"][0]["map_id"] = "soda-creek"
    dataset["sample_metadata"][0]["seed"] = 77
    dataset["sample_metadata"][0]["time_seconds"] = 24.0
    dataset["observations"][1] = [0.0833333333, 0.0, 0.2]
    dataset["actions"][1] = 3
    dataset["sample_metadata"][1]["map_id"] = "soda-creek"
    dataset["sample_metadata"][1]["seed"] = 77
    dataset["sample_metadata"][1]["time_seconds"] = 25.0
    dataset["sample_metadata"][2]["map_id"] = "soda-creek"
    dataset["sample_metadata"][2]["seed"] = 77
    dataset["sample_metadata"][2]["time_seconds"] = 26.0

    report = inspect_teacher_sequences(
        load_trace(trace_path),
        dataset,
        time_windows=[(20.0, 30.0)],
        phase_duration_seconds=300.0,
        same_map_only=True,
        offline_min_seconds=0.0,
        offline_max_seconds=60.0,
        sequence_radius=1,
        examples_per_window=1,
    )

    window = report["windows"][0]
    assert report["gate_decision"] == "teacher_sequence_diagnostic_recorded_watch_only"
    assert window["nearest_target_matches_online_action_ratio"] == 0.0
    assert window["nearest_target_action_distribution"]["3"]["count"] == 1
    assert window["examples"][0]["online_action"] == 5
    assert window["examples"][0]["nearest"]["target_action"] == 3
    assert len(window["examples"][0]["teacher_sequence"]) == 3
