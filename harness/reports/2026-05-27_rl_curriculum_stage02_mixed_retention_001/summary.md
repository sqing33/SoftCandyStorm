# RL Curriculum Stage 02 Mixed Retention

- Previous attempt: `harness/reports/2026-05-27_rl_curriculum_stage02_corner_risk_delta_mid_001/summary.md`
- Decision: `stage02_mixed_retention_needs_opening_repair`
- Model: `harness/reports/2026-05-27_rl_curriculum_stage02_mixed_retention_001/stage02_mixed_retention.zip`
- Failure case: `harness/failed_cases/fail_20260527_023_stage02_mixed_retention_opening_regression.json`

## Change Under Test

- Warm-started from the stage 01 `corner_risk_delta` checkpoint.
- Trained stage 02 on mixed `soda-creek` + `caramel-workshop` maps to retain opening behavior while addressing mid-window pressure.
- Training duration: `180s`
- Requested timesteps: `5000`
- Actual timesteps: `5120`
- Entropy coefficient: `0.02`

## Training Evaluation

Evaluation on `caramel-workshop`:

- Win rate: `100%`
- Average survival: `180.0095s`
- Dominant action: `7` / `57.93%`
- Normalized action entropy: `0.4842`
- Gate: `trained_needs_rule_bot_comparison`

Compared with the single-map stage 02 attempt, this removes the severe `caramel-workshop` action `2` collapse.

## 60s Opening Regression

| Map | Win Rate | Avg Survival | Dominant Action | Entropy |
|---|---:|---:|---|---:|
| `soda-creek` | 80.00% | 58.3361s | `7` / 49.12% | 0.5103 |
| `caramel-workshop` | 100.00% | 60.0328s | `7` / 54.29% | 0.5191 |
| `cracked-star-jar` | 100.00% | 60.0328s | `7` / 52.20% | 0.4991 |

`soda-creek` failures:

- seed `62405` died at `47.3663s`
- seed `62407` died at `55.7328s`

## 180s High-pressure 3-seed Comparison

| Map | Win Rate | Avg Survival | Dominant Action | Entropy |
|---|---:|---:|---|---:|
| `soda-creek` | 66.67% | 145.1172s | `7` / 48.70% | 0.4864 |
| `caramel-workshop` | 100.00% | 180.0095s | `7` / 39.93% | 0.6041 |
| `cracked-star-jar` | 100.00% | 180.0095s | `7` / 62.46% | 0.4820 |

## Conclusion

Mixed retention improves action distribution and keeps the target mid-window map alive, but it still regresses `soda-creek` opening. Because stage 01 opening was the prerequisite for stage 02, this checkpoint cannot enter stage 03.

## Next

- Try a smaller stage 02 continuation, lower learning rate, or explicit opening replay/regularization.
- Keep the 60s high-pressure 10 seed opening regression as a hard gate after every stage 02 update.
