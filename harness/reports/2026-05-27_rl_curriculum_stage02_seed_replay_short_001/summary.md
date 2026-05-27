# RL Curriculum Stage 02 Seed Replay Short

- Previous attempt: `harness/reports/2026-05-27_rl_curriculum_stage02_low_lr_short_001/summary.md`
- Decision: `stage02_seed_replay_short_opening_regression`
- Model: `harness/reports/2026-05-27_rl_curriculum_stage02_seed_replay_short_001/stage02_seed_replay_short.zip`
- Failure case: `harness/failed_cases/fail_20260527_025_stage02_seed_replay_short_opening_regression.json`

## Change Under Test

- Warm-started from the stage 01 `corner_risk_delta` checkpoint.
- Kept mixed `soda-creek` + `caramel-workshop` training maps.
- Replayed the opening gate seeds `62400` through `62409` during training resets.
- Reduced the PPO learning rate to `0.0001` and kept entropy coefficient at `0.02`.
- Training duration: `180s`
- Requested timesteps: `1024`
- Actual timesteps: `1024`

## 60s Opening Regression

| Map | Win Rate | Avg Survival | Dominant Action | Entropy |
|---|---:|---:|---|---:|
| `soda-creek` | 90.00% | 58.7628s | `7` / 40.08% | 0.4982 |
| `caramel-workshop` | 100.00% | 60.0328s | `7` / 47.98% | 0.5247 |
| `cracked-star-jar` | 100.00% | 60.0328s | `7` / 41.22% | 0.5217 |

`soda-creek` failure:

- seed `62405` died at `47.3330s`

## Conclusion

Training seed replay improved the opening regression from the previous low-learning-rate short run: `soda-creek` moved from 80% to 90% and only seed `62405` remained failing. It still did not pass the hard 60-second opening gate, so the 180-second three-map comparison was intentionally skipped.

This checkpoint cannot enter stage 03 and is not RL policy acceptance evidence.

## Next

- Focus the next repair on seed `62405` with failed-only traces or stronger opening regularization.
- Keep the full 60-second high-pressure 10 seed opening gate as the prerequisite before any 180-second stage 02 comparison.
