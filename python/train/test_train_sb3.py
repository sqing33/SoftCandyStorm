import json
from types import SimpleNamespace

import pytest

from python.train.train_sb3 import (
    algorithm_parameters_source_label,
    apply_loaded_model_overrides,
    build_trace_step,
    compact_action_score,
    merge_algorithm_parameters,
    should_record_trace_step,
    write_episode_trace,
)


def test_merge_algorithm_parameters_preserves_base_and_applies_overrides():
    merged = merge_algorithm_parameters(
        {"learning_rate": 0.0003, "ent_coef": 0.0},
        {"ent_coef": 0.02},
    )

    assert merged == {"learning_rate": 0.0003, "ent_coef": 0.02}


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
