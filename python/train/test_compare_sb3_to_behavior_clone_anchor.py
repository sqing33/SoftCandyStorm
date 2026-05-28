import pytest

from python.train.compare_sb3_to_behavior_clone_anchor import (
    compare_policies_to_anchor,
    probability_distribution,
    time_bucket_label,
)


class ContextPolicy:
    def __init__(self, opening_scores, late_scores):
        self.opening_scores = opening_scores
        self.late_scores = late_scores
        self.contexts = []
        self.map_ids = []
        self.reset_count = 0
        self.active_time_seconds = 0.0

    def reset(self):
        self.reset_count += 1

    def set_map_id(self, map_id):
        self.map_ids.append(map_id)

    def set_step_context(self, info):
        self.contexts.append(info)
        self.active_time_seconds = float(info.get("time_seconds", 0.0))

    def action_scores(self, observation):
        scores = self.opening_scores if self.active_time_seconds < 60.0 else self.late_scores
        return {"kind": "probability", "scores": scores}


def test_probability_distribution_normalizes_probabilities():
    payload = {"kind": "probability", "scores": [0.2, 0.2, 0.0]}

    assert probability_distribution(payload, 3) == pytest.approx([0.5, 0.5, 0.0])


def test_probability_distribution_softmaxes_q_values():
    payload = {"kind": "q_value", "scores": [1.0, 2.0]}

    values = probability_distribution(payload, 2)

    assert sum(values) == pytest.approx(1.0)
    assert values[1] > values[0]


def test_time_bucket_label_uses_absolute_seconds():
    assert time_bucket_label(12.0) == "opening_lt_60"
    assert time_bucket_label(90.0) == "mid_60_to_180"
    assert time_bucket_label(240.0) == "late_180_to_300"
    assert time_bucket_label(301.0) == "post_300"


def test_compare_policies_to_anchor_passes_context_and_groups_metrics():
    anchor = ContextPolicy([0.9, 0.1], [0.2, 0.8])
    candidate = ContextPolicy([0.8, 0.2], [0.7, 0.3])
    dataset = {
        "action_count": 2,
        "observations": [[0.0], [1.0]],
        "sample_metadata": [
            {
                "path": "episode_a",
                "seed": 7,
                "map_id": "soda-creek",
                "time_seconds": 30.0,
            },
            {
                "path": "episode_a",
                "seed": 7,
                "map_id": "soda-creek",
                "time_seconds": 210.0,
            },
        ],
    }

    report = compare_policies_to_anchor(dataset, candidate, anchor)

    assert anchor.reset_count == 1
    assert candidate.reset_count == 1
    assert anchor.map_ids == ["soda-creek"]
    assert [item["time_seconds"] for item in candidate.contexts] == [30.0, 210.0]
    assert report["overall"]["sample_count"] == 2
    assert report["overall"]["argmax_agreement"] == 0.5
    assert report["by_map"]["soda-creek"]["sample_count"] == 2
    assert report["by_time_bucket"]["opening_lt_60"]["argmax_agreement"] == 1.0
    assert report["by_time_bucket"]["late_180_to_300"]["argmax_agreement"] == 0.0
