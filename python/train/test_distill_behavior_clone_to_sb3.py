import pytest

from pathlib import Path

from python.train import distill_behavior_clone_to_sb3 as distill_module
from python.train.distill_behavior_clone_to_sb3 import (
    build_distillation_sample_weights,
    collect_distillation_targets,
    load_distillation_dataset,
    mix_with_uniform,
    soften_probabilities,
    transform_target_probabilities,
)


np = pytest.importorskip("numpy")


def entropy(probabilities):
    clipped = np.clip(probabilities, 1e-8, 1.0)
    return float(-(clipped * np.log(clipped)).sum())


def test_teacher_temperature_softens_confident_targets():
    original = np.asarray([0.94, 0.03, 0.03], dtype=np.float32)

    softened = soften_probabilities(original, 2.0, np)

    assert softened[0] < original[0]
    assert entropy(softened) > entropy(original)
    assert softened.sum() == pytest.approx(1.0)


def test_uniform_mix_raises_entropy_without_changing_shape():
    original = np.asarray([1.0, 0.0, 0.0], dtype=np.float32)

    mixed = mix_with_uniform(original, 0.3, np)

    assert mixed.tolist() == pytest.approx([0.8, 0.1, 0.1])
    assert entropy(mixed) > entropy(original)
    assert mixed.sum() == pytest.approx(1.0)


def test_target_transform_keeps_default_behavior():
    original = np.asarray([0.2, 0.5, 0.3], dtype=np.float32)

    transformed = transform_target_probabilities(original, 1.0, 0.0, np)

    assert transformed.tolist() == pytest.approx(original.tolist())


def test_collect_targets_passes_opening_teacher_context(monkeypatch):
    calls = {"contexts": [], "map_ids": [], "loader": None}

    class FakeTeacher:
        def __init__(self):
            self.active_time_seconds = 0.0

        def reset(self):
            self.active_time_seconds = 0.0

        def set_map_id(self, map_id):
            calls["map_ids"].append(map_id)

        def set_step_context(self, info):
            calls["contexts"].append(info)
            self.active_time_seconds = float(info["time_seconds"])

        def predict(self, observation, deterministic=True):
            return (1 if self.active_time_seconds < 60.0 else 2), None

        def action_scores(self, observation):
            if self.active_time_seconds < 60.0:
                return {"kind": "probability", "scores": [0.1, 0.8, 0.1]}
            return {"kind": "probability", "scores": [0.1, 0.1, 0.8]}

    def fake_loader(algorithm, behavior_clone_model_path, opening_model_path=None, opening_seconds=60.0):
        calls["loader"] = {
            "algorithm": algorithm,
            "behavior_clone_model_path": behavior_clone_model_path,
            "opening_model_path": opening_model_path,
            "opening_seconds": opening_seconds,
        }
        return FakeTeacher()

    monkeypatch.setattr(
        distill_module,
        "load_behavior_clone_policy_with_optional_opening",
        fake_loader,
    )
    dataset = {
        "action_count": 3,
        "observations": [
            np.asarray([0.0, 0.1], dtype=np.float32),
            np.asarray([0.2, 0.3], dtype=np.float32),
        ],
        "actions": [1, 2],
        "sample_metadata": [
            {"path": "episode_a", "seed": 1, "map_id": "soda-creek", "time_seconds": 30.0},
            {"path": "episode_a", "seed": 1, "map_id": "soda-creek", "time_seconds": 90.0},
        ],
    }

    targets, report = collect_distillation_targets(
        dataset,
        Path("fallback.pt"),
        "teacher_probs",
        1.0,
        0.0,
        np,
        opening_algorithm="ppo",
        opening_model=Path("opening.zip"),
        opening_seconds=60.0,
    )

    assert calls["loader"]["algorithm"] == "ppo"
    assert calls["loader"]["behavior_clone_model_path"] == Path("fallback.pt")
    assert calls["loader"]["opening_model_path"] == Path("opening.zip")
    assert calls["loader"]["opening_seconds"] == 60.0
    assert calls["map_ids"] == ["soda-creek"]
    assert [context["time_seconds"] for context in calls["contexts"]] == [30.0, 90.0]
    assert targets.argmax(axis=1).tolist() == [1, 2]
    assert report["opening_model"] == "opening.zip"
    assert report["opening_seconds"] == 60.0
    assert report["teacher_argmax_agreement"] == 1.0


def test_load_distillation_dataset_can_include_anchor_drift_samples(tmp_path):
    path = tmp_path / "drift.jsonl"
    path.write_text(
        "\n".join(
            [
                '{"record_type":"anchor_drift_sample","sample_role":"repair_diagnostics","observation":[0.1,0.2,0.3],"anchor_action":8,"candidate_action":4,"dataset_action":4,"map_id":"soda-creek","time_seconds":90.0,"health_ratio":1.0}',
                "",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="include_anchor_drift_samples"):
        load_distillation_dataset(path)

    dataset = load_distillation_dataset(path, include_anchor_drift_samples=True)

    assert dataset["anchor_drift_sample_records"] == 1
    assert dataset["action_count"] == 9
    assert dataset["actions"] == [8]
    assert dataset["sample_metadata"][0]["sample_source"] == "anchor_drift_diagnostic"


def test_build_distillation_sample_weights_matches_path_prefix():
    dataset = {
        "sample_metadata": [
            {"path": "harness/reports/full_anchor/a.jsonl"},
            {"path": "harness/reports/drift/mid_anchor_drift_training_samples.jsonl"},
            {"path": "harness/reports/drift/other.jsonl"},
        ],
    }

    weights, report = build_distillation_sample_weights(
        dataset,
        np.asarray([0, 1, 2]),
        [{"path": "harness/reports/drift", "weight": 6.0}],
        np,
    )

    assert weights.tolist() == pytest.approx([1.0, 6.0, 6.0])
    assert report["mode"] == "sample_path_auxiliary"
    assert report["sample_path_weights"]["weighted_sample_count"] == 2
    assert report["sample_path_weights"]["entries"][0]["matched_train_samples"] == 2
