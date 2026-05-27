# RL Curriculum Stage 02 Low LR Short

- Previous attempt: `harness/reports/2026-05-27_rl_curriculum_stage02_mixed_retention_001/summary.md`
- Decision: `stage02_low_lr_short_opening_regression`
- Model: `harness/reports/2026-05-27_rl_curriculum_stage02_low_lr_short_001/stage02_low_lr_short.zip`
- Failure case: `harness/failed_cases/fail_20260527_024_stage02_low_lr_short_opening_regression.json`

## Change Under Test

- Warm-started from the stage 01 `corner_risk_delta` checkpoint.
- Kept mixed `soda-creek` + `caramel-workshop` training maps.
- Reduced the PPO learning rate to `0.0001` through `--learning-rate`.
- Kept entropy coefficient at `0.02`.
- Training duration: `180s`
- Requested timesteps: `1024`
- Actual timesteps: `1024`

## 60s Opening Regression

| Map | Win Rate | Avg Survival | Dominant Action | Entropy |
|---|---:|---:|---|---:|
| `soda-creek` | 80.00% | 55.4928s | `7` / 44.91% | 0.4691 |
| `caramel-workshop` | 100.00% | 60.0328s | `2` / 47.07% | 0.5072 |
| `cracked-star-jar` | 100.00% | 60.0328s | `2` / 49.38% | 0.4437 |

`soda-creek` failures:

- seed `62400` died at `24.5666s`
- seed `62407` died at `50.0996s`

## Conclusion

Lowering the learning rate and shortening the continuation did not preserve the stage 01 opening gate. `soda-creek` remained at 80% win rate, and one failure moved earlier than the previous mixed-retention attempt. Because the hard 60-second opening regression failed, the 180-second three-map comparison was intentionally skipped.

This checkpoint cannot enter stage 03 and is not RL policy acceptance evidence.

## Next

- Add explicit opening replay / regularization instead of relying on generic mixed-map PPO continuation.
- Re-run the 60-second high-pressure 10 seed opening gate before any future stage 02 long-window comparison.
