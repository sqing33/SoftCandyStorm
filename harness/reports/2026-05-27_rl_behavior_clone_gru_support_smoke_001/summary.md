# Behavior Clone GRU Support Smoke

- Decision: `gru_support_smoke_pass`
- Scope: `python/train/train_behavior_clone.py`
- Command: `uv run --with-requirements python/train/requirements.txt python python/train/train_behavior_clone.py --check-deps`

## Checks

- Added `--architecture gru` training path for sequence-shaped context frames.
- Added checkpoint loading support so `train_sb3.py --behavior-clone-model` can evaluate GRU behavior clone policies.
- Added focused pytest coverage for GRU map-conditioned prediction and legacy MLP checkpoint loading.

## Verification

- `python3 -m py_compile python/train/train_behavior_clone.py python/train/train_sb3.py`
- `uv run --with pytest --with-requirements python/train/requirements.txt python -m pytest python/train/test_train_behavior_clone.py`

## Limitations

- This report validates support code only; it does not prove a GRU candidate is a useful RL test Bot.
- A trained GRU checkpoint still needs 60/300 second high-pressure comparison and RL policy acceptance validation.
