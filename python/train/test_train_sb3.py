import json
from types import SimpleNamespace

import pytest

from python.train.train_sb3 import (
    algorithm_parameters_source_label,
    algorithm_overrides_from_args,
    apply_loaded_model_overrides,
    build_trace_step,
    compact_action_score,
    merge_algorithm_parameters,
    resolve_train_seed_values,
    should_record_trace_step,
    write_episode_trace,
)


def test_merge_algorithm_parameters_preserves_base_and_applies_overrides():
    merged = merge_algorithm_parameters(
        {"learning_rate": 0.0003, "gamma": 0.99, "ent_coef": 0.0},
        {"learning_rate": 0.0001, "ent_coef": 0.02},
    )

    assert merged == {"learning_rate": 0.0001, "gamma": 0.99, "ent_coef": 0.02}


def test_algorithm_overrides_accepts_learning_rate():
    args = SimpleNamespace(
        algorithm="ppo",
        learning_rate=0.0001,
        ent_coef=None,
    )

    assert algorithm_overrides_from_args(args) == {"learning_rate": 0.0001}


def test_algorithm_overrides_rejects_non_positive_learning_rate():
    args = SimpleNamespace(
        algorithm="ppo",
        learning_rate=0.0,
        ent_coef=None,
    )

    with pytest.raises(ValueError, match="--learning-rate"):
        algorithm_overrides_from_args(args)


def test_resolve_train_seed_values_accepts_range():
    assert resolve_train_seed_values(None, 62400, 3) == [62400, 62401, 62402]


def test_resolve_train_seed_values_accepts_explicit_list():
    assert resolve_train_seed_values("62400,62407", None, None) == [62400, 62407]


def test_resolve_train_seed_values_rejects_mixed_sources():
    with pytest.raises(ValueError, match="--train-seeds"):
        resolve_train_seed_values("62400", 62400, 2)


def test_algorithm_parameter_source_records_warm_start_overrides():
    source = algorithm_parameters_source_label(
        warm_start_metadata={"algorithm_parameters": {"ent_coef": 0.0}},
        warm_start_model="model.zip",
        overrides={"ent_coef": 0.02},
    )

    assert source == "warm_start_metadata_with_overrides"


def test_apply_loaded_model_overrides_updates_supported_parameters():
    model = SimpleNamespace(ent_coef=0.0)

    apply_loaded_model_overrides(model, {"ent_coef": 0.03})

    assert model.ent_coef == 0.03


def test_apply_loaded_model_overrides_refreshes_learning_rate_schedule():
    class LoadedModel:
        def __init__(self):
            self.learning_rate = 0.0003
            self.lr_schedule = None

        def _setup_lr_schedule(self):
            self.lr_schedule = f"schedule:{self.learning_rate}"

    model = LoadedModel()

    apply_loaded_model_overrides(model, {"learning_rate": 0.0001})

    assert model.learning_rate == 0.0001
    assert model.lr_schedule == "schedule:0.0001"


def test_apply_loaded_model_overrides_rejects_unknown_parameters():
    with pytest.raises(ValueError, match="does not expose"):
        apply_loaded_model_overrides(SimpleNamespace(), {"ent_coef": 0.03})


def test_trace_step_sampling_records_first_stride_and_terminal_steps():
    assert not should_record_trace_step(None, 1, False, False, 30)
    assert should_record_trace_step("traces", 1, False, False, 30)
    assert should_record_trace_step("traces", 60, False, False, 30)
    assert should_record_trace_step("traces", 17, True, False, 30)
    assert not should_record_trace_step("traces", 17, False, False, 30)


def test_build_trace_step_compacts_policy_scores():
    info = {
        "tick": 30,
        "time_seconds": 1.0,
        "health": 91.5,
        "level": 2,
        "kills": 3,
        "xp_collected": 4.25,
        "damage_taken": 8.5,
        "upgrade_options": ["mint"],
        "events": ["hit"],
        "terminal": None,
        "reward_breakdown": {"survival": 0.1, "total": -0.25},
        "diagnostics": {
            "player_position": {"x": 12.0, "y": -3.0},
            "boundary": {"min_distance": 42.0, "edge_risk": 0.0},
            "nearest_enemy": {"enemy_id": "soda-bubble", "hitbox_distance": 55.0},
        },
    }

    step = build_trace_step(
        30,
        4,
        -0.25,
        info,
        {"kind": "probability", "scores": [0.1, 0.2, 0.05, 0.15, 0.5]},
    )

    assert step["action"] == 4
    assert step["health"] == 91.5
    assert step["reward_breakdown"] == {"survival": 0.1, "total": -0.25}
    assert step["action_score"]["chosen_action_score"] == 0.5
    assert step["action_score"]["top_actions"][0] == {"action": "4", "score": 0.5}
    assert step["diagnostics"]["nearest_enemy"]["enemy_id"] == "soda-bubble"


def test_write_episode_trace_respects_failed_only(tmp_path):
    victory = {"seed": 1, "map_id": "soda-creek", "terminal_kind": "victory"}
    failure = {
        "seed": 2,
        "map_id": "soda-creek",
        "terminal_kind": "defeat",
        "terminal_reason": "player_health_depleted",
    }

    assert write_episode_trace(tmp_path, victory, [], failed_only=True) is None
    trace_path = write_episode_trace(
        tmp_path,
        failure,
        [{"step": 1, "action": 4}],
        failed_only=True,
    )

    payload = json.loads((tmp_path / "soda-creek_seed2_trace.json").read_text())
    assert trace_path.endswith("soda-creek_seed2_trace.json")
    assert payload["record_type"] == "policy_episode_trace"
    assert payload["sample_count"] == 1
    assert payload["episode"]["terminal_kind"] == "defeat"
