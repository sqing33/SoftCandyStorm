# RL Curriculum Stage 01 Directional Corner Reward Smoke

- Previous failed attempt: `harness/reports/2026-05-27_rl_curriculum_stage01_corner_reward_retrain_20k_001/summary.md`
- Decision: `directional_corner_reward_smoke_needs_opening_repair`
- Model: `harness/reports/2026-05-27_rl_curriculum_stage01_corner_reward_directional_smoke_001/stage01_corner_reward_directional_smoke.zip`
- Failure case: `harness/failed_cases/fail_20260527_021_directional_corner_reward_smoke_soda_gap.json`

## Change Under Test

- `corner_action_risk` now penalizes any diagonal action that pushes the player deeper into the currently pressured corner.
- The penalty was reduced from `-0.006` to `-0.003`.
- Unit coverage now checks both right-bottom action `4` and left-top action `8`.

## Training Smoke

- Warm start: `harness/reports/2026-05-27_rl_curriculum_time_bucket_stage01_retry_20k_001/stage01_opening_retry_20k.zip`
- Requested timesteps: `2048`
- Actual timesteps: `2048`
- Training maps: `cracked-star-jar`, `soda-creek`
- Training seconds: `60`
- Entropy coefficient: `0.02`

Training evaluation on `soda-creek`:

- Win rate: `40%`
- Average survival: `49.2063s`
- Dominant action: `7` / `51.35%`
- Normalized action entropy: `0.3683`
- Average `corner_action_risk`: `-0.4104`
- Gate: `trained_needs_rule_bot_comparison`

## 60s High-pressure 10-seed Comparison

| Map | Win Rate | Avg Survival | Dominant Action | Entropy |
|---|---:|---:|---|---:|
| `soda-creek` | 70.00% | 52.3995s | `2` / 50.65% | 0.3565 |
| `caramel-workshop` | 90.00% | 57.3528s | `2` / 62.07% | 0.3500 |
| `cracked-star-jar` | 100.00% | 60.0328s | `2` / 55.81% | 0.3241 |

Comparison gate: `multimap_comparison_recorded_not_balance_gate`.

## Failure Analysis

- Total failures: `4`
- Repair maps by failure count: `soda-creek`, `caramel-workshop`
- `soda-creek` still has 3 opening deaths at seeds `62400`, `62407`, and `62408`.
- `caramel-workshop` has 1 opening death at seed `62408`.

## Conclusion

Directional corner shaping avoids the previous action `8` collapse in the cheap smoke, but it does not restore the stage 01 retry baseline. `soda-creek` falls from the previous 80% retry result to 70%, so this is not a valid opening repair.

## Next

- Keep this as smoke-only evidence.
- Do not run a full 20k retrain from this exact setting yet.
- Next repair should either soften the penalty further, make it risk-delta based instead of per-step action based, or add a short stochastic diagnostic before deterministic training.
