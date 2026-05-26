from types import SimpleNamespace

import pytest

from python.train.train_sb3 import (
    algorithm_parameters_source_label,
    apply_loaded_model_overrides,
    merge_algorithm_parameters,
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
