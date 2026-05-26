# RL Curriculum Stage 01 Corner Reward Retrain 20k

- Previous stage: `harness/reports/2026-05-27_rl_curriculum_time_bucket_stage01_retry_20k_001/summary.md`
- Decision: `rl_curriculum_stage01_corner_reward_retrain_recorded_needs_policy_repair`
- Model: `harness/reports/2026-05-27_rl_curriculum_stage01_corner_reward_retrain_20k_001/stage01_corner_reward_retrain_20k.zip`
- Failure case: `harness/failed_cases/fail_20260527_020_corner_reward_retrain_action8_collapse.json`

## Training

- Warm start: `harness/reports/2026-05-27_rl_curriculum_time_bucket_stage01_retry_20k_001/stage01_opening_retry_20k.zip`
- Maps: `cracked-star-jar`, `soda-creek`
- Map selection: `random`
- Train seconds: 60
- Requested timesteps: 20000
- Actual timesteps: 20224
- Entropy coefficient: 0.02
- Report: `harness/reports/2026-05-27_rl_curriculum_stage01_corner_reward_retrain_20k_001/ppo_training_report.json`

## Training Evaluation

- Evaluation map: `soda-creek`
- Episodes: 5
- Win rate: `0%`
- Average survival: `31.7399s`
- Dominant action: `8` / `92.90%`
- Normalized action entropy: `0.1166`
- Gate: `trained_needs_action_bias_repair`

## 60s High-pressure 10-seed Comparison

| Map | Win Rate | Avg Survival | Dominant Action | Entropy | Gate |
|---|---:|---:|---|---:|---|
| `soda-creek` | 10.00% | 33.3998s | `8` / 86.19% | 0.2577 | `comparison_recorded_needs_action_bias_repair` |
| `caramel-workshop` | 80.00% | 54.3728s | `8` / 82.32% | 0.3161 | `comparison_recorded_needs_action_bias_repair` |
| `cracked-star-jar` | 70.00% | 52.1629s | `8` / 73.46% | 0.4093 | `comparison_recorded_not_balance_gate` |

Overall comparison gate: `multimap_comparison_recorded_needs_policy_repair`.

## Failure Analysis

- Total failures: `14`
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`
- `soda-creek`: 9 failures, all `opening_lt_60`, average failure survival `30.4406s`
- `caramel-workshop`: 2 failures, all `opening_lt_60`
- `cracked-star-jar`: 3 failures, all `opening_lt_60`

## Conclusion

The targeted `corner_action_risk` field successfully avoided the previous average corner penalty during retraining, but the policy found a new deterministic failure surface by collapsing to action `8`. This is a repair regression, not a valid stage 01 fix.

## Next

- Do not continue to stage 02 from this checkpoint.
- Keep `stage01_corner_reward_retrain_20k.zip` as failed evidence only.
- Next repair should reduce the hard action-specific shaping risk, test smaller penalty or entropy schedule changes, and run a cheap deterministic evaluation before committing to another 20k warm-start.
