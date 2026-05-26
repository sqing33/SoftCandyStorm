# RL upgrade choice export smoke

## Summary

`game_harness export-bot-trajectories` now supports optional upgrade-choice supervision records through `--include-upgrade-samples true`. The default movement dataset remains unchanged: regular behavior-clone loading skips `upgrade_sample` records and only counts them as side-channel records, while `load_upgrade_choice_dataset` reads upgrade-choice samples separately.

This smoke proves the data entry point and loader split only. It does not prove an upgrade-choice model, RL policy repair, long-run generalization, balance quality, or player-facing fun.

## Command

```bash
cargo run -q -p game_harness -- export-bot-trajectories \
  --bot kite \
  --seed-start 56000 \
  --seeds 2 \
  --map-id soda-creek \
  --seconds 60 \
  --tick-rate 30 \
  --observation-version 2 \
  --sample-stride 15 \
  --include-upgrade-samples true \
  --out harness/reports/2026-05-27_rl_upgrade_choice_export_smoke_001/kite_soda_upgrade_samples.jsonl
```

## Results

- Movement samples: 241
- Upgrade-choice samples: 4
- Upgrade prompt states skipped from movement samples: 4
- Episodes: 2
- Victories: 2
- Observation length: 145
- Content hash: `fnv1a64:4ad1c52ac3f1285b`

Upgrade choice distribution:

- `cream-clockwork`: 2
- `bubble-shoes`: 1
- `candy-crystal-lance`: 1

## Evidence

- `export_report.json`: Harness export report.
- `kite_soda_upgrade_samples.jsonl`: mixed JSONL with `metadata`, movement `sample`, optional `upgrade_sample`, `episode`, and `summary` records.
- `upgrade_dataset_summary.json`: Python loader smoke summary confirming 241 movement samples and 4 separately loaded upgrade samples.

## Validation

Already run for this feature:

```bash
cargo fmt --check
cargo test -p game_harness
python3 -m py_compile python/train/train_behavior_clone.py python/train/test_train_behavior_clone.py
uv run --with pytest --with-requirements python/train/requirements.txt pytest python/train/test_train_behavior_clone.py
```

