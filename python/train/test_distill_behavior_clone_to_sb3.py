import pytest

from pathlib import Path

from python.train import distill_behavior_clone_to_sb3 as distill_module
from python.train.distill_behavior_clone_to_sb3 import (
    action_distribution_guard_config,
    build_distillation_sample_weights,
    build_distillation_validation_slice_groups,
    collect_distillation_targets,
    evaluate_action_distribution_guard,
    load_distillation_dataset,
    mix_with_uniform,
    parse_action_distribution_guard_scope,
    parse_dataset_action_target_maps,
    parse_recovery_target_maps,
    parse_recovery_target_sources,
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


def test_collect_targets_overrides_recovery_samples_with_top_k_scores(monkeypatch):
    class FakeTeacher:
        def reset(self):
            pass

        def set_map_id(self, map_id):
            pass

        def set_step_context(self, info):
            pass

        def predict(self, observation, deterministic=True):
            return 0, None

        def action_scores(self, observation):
            return {"kind": "probability", "scores": [0.9, 0.05, 0.05]}

    monkeypatch.setattr(
        distill_module,
        "load_behavior_clone_policy_with_optional_opening",
        lambda *args, **kwargs: FakeTeacher(),
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
            {
                "path": "risk.jsonl",
                "seed": 2,
                "map_id": "soda-creek",
                "time_seconds": 210.0,
                "sample_source": "risk_recovery_supervision",
                "action_scores": {
                    "top_actions": [
                        {"action": 0, "score": 3.0},
                        {"action": 1, "score": 1.0},
                    ]
                },
            },
        ],
    }

    targets, report = collect_distillation_targets(
        dataset,
        Path("fallback.pt"),
        "teacher_probs",
        1.0,
        0.0,
        np,
        recovery_target_mode="top_k_scores",
        recovery_soft_target_primary_mass=0.7,
        recovery_soft_target_top_k=3,
    )

    assert targets[0].tolist() == pytest.approx([0.9, 0.05, 0.05])
    assert targets[1].tolist() == pytest.approx([0.225, 0.075, 0.7])
    assert report["recovery_target_override"]["mode"] == "top_k_scores"
    assert report["recovery_target_override"]["overridden_sample_count"] == 1
    assert report["recovery_target_override"]["soft_sample_count"] == 1
    assert report["recovery_target_override"]["fallback_one_hot_count"] == 0
    assert report["recovery_target_override"]["average_nonzero_actions"] == 3.0


def test_recovery_target_sources_can_limit_override_to_risk_samples(monkeypatch):
    class FakeTeacher:
        def reset(self):
            pass

        def predict(self, observation, deterministic=True):
            return 0, None

        def action_scores(self, observation):
            return {"kind": "probability", "scores": [0.8, 0.1, 0.1]}

    monkeypatch.setattr(
        distill_module,
        "load_behavior_clone_policy_with_optional_opening",
        lambda *args, **kwargs: FakeTeacher(),
    )
    dataset = {
        "action_count": 3,
        "observations": [
            np.asarray([0.0, 0.1], dtype=np.float32),
            np.asarray([0.2, 0.3], dtype=np.float32),
        ],
        "actions": [1, 2],
        "sample_metadata": [
            {"sample_source": "edge_recovery_supervision"},
            {"sample_source": "risk_recovery_supervision"},
        ],
    }

    targets, report = collect_distillation_targets(
        dataset,
        Path("fallback.pt"),
        "teacher_probs",
        1.0,
        0.0,
        np,
        recovery_target_mode="dataset_actions",
        recovery_target_sources=parse_recovery_target_sources("risk"),
    )

    assert targets[0].tolist() == pytest.approx([0.8, 0.1, 0.1])
    assert targets[1].tolist() == pytest.approx([0.0, 0.0, 1.0])
    assert report["recovery_target_override"]["sources"] == [
        "risk_recovery_supervision"
    ]
    assert report["recovery_target_override"]["overridden_sample_count"] == 1


def test_recovery_target_scope_limits_override_by_map_and_time(monkeypatch):
    class FakeTeacher:
        def reset(self):
            pass

        def predict(self, observation, deterministic=True):
            return 0, None

        def action_scores(self, observation):
            return {"kind": "probability", "scores": [0.8, 0.1, 0.1]}

    monkeypatch.setattr(
        distill_module,
        "load_behavior_clone_policy_with_optional_opening",
        lambda *args, **kwargs: FakeTeacher(),
    )
    dataset = {
        "action_count": 3,
        "observations": [
            np.asarray([0.0, 0.1], dtype=np.float32),
            np.asarray([0.2, 0.3], dtype=np.float32),
            np.asarray([0.4, 0.5], dtype=np.float32),
            np.asarray([0.6, 0.7], dtype=np.float32),
        ],
        "actions": [1, 2, 1, 2],
        "sample_metadata": [
            {
                "sample_source": "risk_recovery_supervision",
                "map_id": "cracked-star-jar",
                "time_seconds": 210.0,
            },
            {
                "sample_source": "risk_recovery_supervision",
                "map_id": "soda-creek",
                "time_seconds": 210.0,
            },
            {
                "sample_source": "risk_recovery_supervision",
                "map_id": "cracked-star-jar",
                "time_seconds": 120.0,
            },
            {
                "sample_source": "edge_recovery_supervision",
                "map_id": "cracked-star-jar",
                "time_seconds": 210.0,
            },
        ],
    }

    targets, report = collect_distillation_targets(
        dataset,
        Path("fallback.pt"),
        "teacher_probs",
        1.0,
        0.0,
        np,
        recovery_target_mode="dataset_actions",
        recovery_target_sources=parse_recovery_target_sources("risk"),
        recovery_target_maps=parse_recovery_target_maps("cracked-star-jar"),
        recovery_target_min_seconds=180.0,
        recovery_target_max_seconds=300.0,
    )

    assert targets[0].tolist() == pytest.approx([0.0, 1.0, 0.0])
    assert targets[1].tolist() == pytest.approx([0.8, 0.1, 0.1])
    assert targets[2].tolist() == pytest.approx([0.8, 0.1, 0.1])
    assert targets[3].tolist() == pytest.approx([0.8, 0.1, 0.1])
    override = report["recovery_target_override"]
    assert override["maps"] == ["cracked-star-jar"]
    assert override["min_seconds"] == 180.0
    assert override["max_seconds"] == 300.0
    assert override["overridden_sample_count"] == 1
    assert override["map_scoped_out_sample_count"] == 1
    assert override["time_scoped_out_sample_count"] == 1
    assert override["source_scoped_out_sample_count"] == 1


def test_dataset_action_target_path_overrides_teacher_targets(monkeypatch):
    class FakeTeacher:
        def reset(self):
            pass

        def predict(self, observation, deterministic=True):
            return 0, None

        def action_scores(self, observation):
            return {"kind": "probability", "scores": [0.8, 0.1, 0.1]}

    monkeypatch.setattr(
        distill_module,
        "load_behavior_clone_policy_with_optional_opening",
        lambda *args, **kwargs: FakeTeacher(),
    )
    dataset = {
        "action_count": 3,
        "observations": [
            np.asarray([0.0, 0.1], dtype=np.float32),
            np.asarray([0.2, 0.3], dtype=np.float32),
        ],
        "actions": [1, 2],
        "sample_metadata": [
            {"path": "harness/reports/full_anchor/a.jsonl"},
            {"path": "harness/reports/victory/terminal.jsonl"},
        ],
    }

    targets, report = collect_distillation_targets(
        dataset,
        Path("fallback.pt"),
        "teacher_probs",
        1.0,
        0.0,
        np,
        dataset_action_target_paths=["harness/reports/victory"],
    )

    assert targets[0].tolist() == pytest.approx([0.8, 0.1, 0.1])
    assert targets[1].tolist() == pytest.approx([0.0, 0.0, 1.0])
    override = report["dataset_action_target_override"]
    assert override["enabled"] is True
    assert override["paths"] == ["harness/reports/victory"]
    assert override["overridden_sample_count"] == 1
    assert override["entries"][0]["matched_sample_count"] == 1
    assert override["average_nonzero_actions"] == 1.0


def test_dataset_action_target_path_can_be_scoped_to_maps(monkeypatch):
    class FakeTeacher:
        def reset(self):
            pass

        def predict(self, observation, deterministic=True):
            return 0, None

        def action_scores(self, observation):
            return {"kind": "probability", "scores": [0.8, 0.1, 0.1]}

    monkeypatch.setattr(
        distill_module,
        "load_behavior_clone_policy_with_optional_opening",
        lambda *args, **kwargs: FakeTeacher(),
    )
    dataset = {
        "action_count": 3,
        "observations": [
            np.asarray([0.0, 0.1], dtype=np.float32),
            np.asarray([0.2, 0.3], dtype=np.float32),
            np.asarray([0.4, 0.5], dtype=np.float32),
        ],
        "actions": [1, 2, 1],
        "sample_metadata": [
            {
                "path": "harness/reports/victory/terminal.jsonl",
                "map_id": "soda-creek",
            },
            {
                "path": "harness/reports/victory/terminal.jsonl",
                "map_id": "caramel-workshop",
            },
            {
                "path": "harness/reports/full_anchor/a.jsonl",
                "map_id": "soda-creek",
            },
        ],
    }

    targets, report = collect_distillation_targets(
        dataset,
        Path("fallback.pt"),
        "teacher_probs",
        1.0,
        0.0,
        np,
        dataset_action_target_paths=["harness/reports/victory"],
        dataset_action_target_maps=parse_dataset_action_target_maps("soda-creek"),
    )

    assert targets[0].tolist() == pytest.approx([0.0, 1.0, 0.0])
    assert targets[1].tolist() == pytest.approx([0.8, 0.1, 0.1])
    assert targets[2].tolist() == pytest.approx([0.8, 0.1, 0.1])
    override = report["dataset_action_target_override"]
    assert override["maps"] == ["soda-creek"]
    assert override["overridden_sample_count"] == 1
    assert override["map_scoped_out_sample_count"] == 1
    assert override["entries"][0]["matched_sample_count"] == 1
    assert override["entries"][0]["map_scoped_out_sample_count"] == 1


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


def test_build_distillation_validation_slice_groups_tracks_sources_and_paths():
    dataset = {
        "sample_metadata": [
            {
                "path": "harness/reports/full_anchor/a.jsonl",
                "map_id": "soda-creek",
                "time_seconds": 30.0,
            },
            {
                "path": "harness/reports/drift/mid_anchor_drift_training_samples.jsonl",
                "sample_source": "anchor_drift_diagnostic",
                "map_id": "caramel-workshop",
                "time_seconds": 90.0,
            },
            {
                "path": "harness/reports/drift/other.jsonl",
                "sample_source": "anchor_drift_diagnostic",
                "map_id": "caramel-workshop",
                "time_seconds": 210.0,
            },
        ],
    }

    groups = build_distillation_validation_slice_groups(
        dataset,
        np.asarray([0, 1, 2]),
        [{"path": "harness/reports/drift", "weight": 6.0}],
    )

    assert groups["sample_sources"]["trajectory"] == [0]
    assert groups["sample_sources"]["anchor_drift_diagnostic"] == [1, 2]
    assert groups["map_time_buckets"]["soda-creek::opening_lt_60"] == [0]
    assert groups["map_time_buckets"]["caramel-workshop::mid_60_to_180"] == [1]
    assert groups["map_time_buckets"]["caramel-workshop::late_180_to_300"] == [2]
    assert groups["sample_path_weights"][0]["indices"] == [1, 2]


def test_action_distribution_guard_blocks_dominant_validation_slices():
    validation_slices = {
        "overall": {
            "sample_count": 30,
            "dominant_policy_argmax_action": {
                "action": "3",
                "count": 10,
                "ratio": 0.8333,
            },
            "normalized_policy_argmax_action_entropy": 0.25,
        },
        "sample_sources": {},
        "sample_path_weights": {"entries": []},
        "map_time_buckets": {
            "caramel-workshop::opening_lt_60": {
                "sample_count": 12,
                "dominant_policy_argmax_action": {
                    "action": "3",
                    "count": 10,
                    "ratio": 0.8333,
                },
                "normalized_policy_argmax_action_entropy": 0.25,
            }
        },
    }

    report = evaluate_action_distribution_guard(
        validation_slices,
        action_distribution_guard_config(
            max_dominant_ratio=0.7,
            min_normalized_entropy=0.35,
            min_sample_count=8,
        ),
    )

    assert report["decision"] == "action_distribution_guard_failed"
    assert report["checked_slice_count"] == 2
    assert any("overall" in blocker for blocker in report["blockers"])
    assert any(
        "caramel-workshop::opening_lt_60" in blocker
        for blocker in report["blockers"]
    )


def test_action_distribution_guard_ignores_small_slices_and_can_pass():
    validation_slices = {
        "overall": {
            "sample_count": 12,
            "dominant_policy_argmax_action": {
                "action": "1",
                "count": 6,
                "ratio": 0.5,
            },
            "normalized_policy_argmax_action_entropy": 0.9,
        },
        "sample_sources": {},
        "sample_path_weights": {"entries": []},
        "map_time_buckets": {
            "tiny-map::opening_lt_60": {
                "sample_count": 2,
                "dominant_policy_argmax_action": {
                    "action": "1",
                    "count": 2,
                    "ratio": 1.0,
                },
                "normalized_policy_argmax_action_entropy": 0.0,
            }
        },
    }

    report = evaluate_action_distribution_guard(
        validation_slices,
        action_distribution_guard_config(
            max_dominant_ratio=0.7,
            min_normalized_entropy=0.35,
            min_sample_count=8,
        ),
    )

    assert report["decision"] == "action_distribution_guard_passed"
    assert report["checked_slice_count"] == 1


def test_action_distribution_guard_scope_can_focus_map_time_buckets():
    validation_slices = {
        "overall": {
            "sample_count": 30,
            "dominant_policy_argmax_action": {
                "action": "1",
                "count": 5,
                "ratio": 0.4167,
            },
            "normalized_policy_argmax_action_entropy": 0.85,
        },
        "sample_sources": {
            "anchor_drift_diagnostic": {
                "sample_count": 36,
                "dominant_policy_argmax_action": {
                    "action": "8",
                    "count": 32,
                    "ratio": 0.8889,
                },
                "normalized_policy_argmax_action_entropy": 0.1872,
            }
        },
        "sample_path_weights": {"entries": []},
        "map_time_buckets": {
            "caramel-workshop::opening_lt_60": {
                "sample_count": 401,
                "dominant_policy_argmax_action": {
                    "action": "2",
                    "count": 127,
                    "ratio": 0.3167,
                },
                "normalized_policy_argmax_action_entropy": 0.7524,
            }
        },
    }

    report = evaluate_action_distribution_guard(
        validation_slices,
        action_distribution_guard_config(
            max_dominant_ratio=0.45,
            min_normalized_entropy=0.55,
            min_sample_count=24,
            scope=["overall", "map_time_buckets"],
        ),
    )

    assert report["decision"] == "action_distribution_guard_passed"
    assert report["checked_slice_count"] == 2
    assert all("anchor_drift" not in item["label"] for item in report["slices"])


def test_parse_action_distribution_guard_scope_rejects_unknown_scope():
    assert parse_action_distribution_guard_scope("overall,map_time_buckets") == [
        "overall",
        "map_time_buckets",
    ]
    with pytest.raises(ValueError, match="unknown scope"):
        parse_action_distribution_guard_scope("overall,bad")
