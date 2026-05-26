# RL upgrade choice training smoke

## Summary

`python/train/train_upgrade_choice.py` now trains a small supervised upgrade-choice ranker from `upgrade_sample` records. Each upgrade prompt is expanded into one row per offered upgrade option, using the GameCore observation plus an upgrade-id one-hot feature; the positive row is the rule Bot's chosen upgrade.

This is a model-plumbing smoke only. It does not connect the checkpoint to Gym upgrade action mode, does not repair movement policy long-run failures, and is not an RL test Bot acceptance gate.

## Commands

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_upgrade_choice.py \
  --dataset harness/reports/2026-05-27_rl_upgrade_choice_export_smoke_001 \
  --dry-run \
  --report harness/reports/2026-05-27_rl_upgrade_choice_training_smoke_001/dry_run.json
```

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_upgrade_choice.py \
  --dataset harness/reports/2026-05-27_rl_upgrade_choice_export_smoke_001 \
  --epochs 20 \
  --batch-size 8 \
  --hidden-size 16 \
  --learning-rate 0.01 \
  --model-out harness/reports/2026-05-27_rl_upgrade_choice_training_smoke_001/upgrade_choice_smoke.pt \
  --report harness/reports/2026-05-27_rl_upgrade_choice_training_smoke_001/run_output.json
```

## Results

- Upgrade choices: 4
- Training rows: 12
- Positive rows: 4
- Negative rows: 8
- Observation length: 145
- Upgrade vocabulary size: 7
- Input length: 152
- Gate decision: `upgrade_choice_training_smoke_not_policy_gate`

Final epoch:

- Train loss: 0.800285
- Validation rows: 3
- Validation row accuracy: 0.3333
- Validation choice accuracy: 1.0

The validation set contains only one upgrade choice, so the accuracy is diagnostic output, not a quality claim.

## Evidence

- `dry_run.json`: dataset and row-shape validation.
- `run_output.json`: training report.
- `upgrade_choice_smoke.pt`: small supervised ranker checkpoint.

## Validation

```bash
python3 -m py_compile python/train/train_upgrade_choice.py python/train/test_train_upgrade_choice.py
uv run --with pytest --with-requirements python/train/requirements.txt pytest python/train/test_train_upgrade_choice.py
```

