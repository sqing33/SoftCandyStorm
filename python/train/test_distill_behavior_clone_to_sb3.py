import pytest

from python.train.distill_behavior_clone_to_sb3 import (
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
