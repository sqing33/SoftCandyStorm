# RL Curriculum Stage 02 Opening Edge Delta

- Previous attempt: `harness/reports/2026-05-27_rl_curriculum_stage02_seed62405_trace_compare_001/summary.md`
- Decision: `stage02_opening_edge_delta_opening_regression`
- Model: `harness/reports/2026-05-27_rl_curriculum_stage02_opening_edge_delta_001/stage02_opening_edge_delta.zip`
- Failure case: `harness/failed_cases/fail_20260527_026_stage02_opening_edge_delta_opening_regression.json`

## Change Under Test

- Added `opening_edge_risk_delta` to Gym reward breakdown.
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
| `soda-creek` | 50.00% | 46.2796s | `4` / 56.89% | 0.4325 |
| `caramel-workshop` | 100.00% | 60.0328s | `7` / 43.92% | 0.4702 |
| `cracked-star-jar` | 100.00% | 60.0328s | `4` / 43.44% | 0.4954 |

`soda-creek` failures:

- seed `62400` died at `24.0000s`
- seed `62401` died at `33.7332s`
- seed `62403` died at `24.5000s`
- seed `62405` died at `51.5662s`
- seed `62409` died at `28.8332s`

## Conclusion

`opening_edge_risk_delta` did not preserve the previous seed-replay repair. `soda-creek` regressed from 90% to 50% in the 60-second 10 seed opening gate, and most failing seeds again show action `4` dominance with negative `corner_risk_delta` / `opening_edge_risk_delta` reward breakdown.

This checkpoint cannot enter stage 03 and is not RL policy acceptance evidence. The 180-second three-map comparison was intentionally skipped because the hard opening gate failed.

## Next

- Generate failed-only snapshot traces for all five failed `soda-creek` seeds.
- Compare them with the stage 01 `corner_risk_delta` success behavior before changing reward weights again.
- Consider successful-trajectory replay, behavior constraints, a dedicated opening policy, or a narrower right-edge pressure regularizer instead of only adding another scalar reward term.
