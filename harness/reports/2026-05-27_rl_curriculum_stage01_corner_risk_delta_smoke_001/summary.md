# RL Curriculum Stage 01 Corner Risk Delta Smoke

- Previous smoke: `harness/reports/2026-05-27_rl_curriculum_stage01_corner_reward_directional_smoke_001/summary.md`
- Decision: `stage01_opening_corner_risk_delta_smoke_passed_short_window`
- Model: `harness/reports/2026-05-27_rl_curriculum_stage01_corner_risk_delta_smoke_001/stage01_corner_risk_delta_smoke.zip`
- Failure analysis: `harness/reports/2026-05-27_rl_curriculum_stage01_corner_risk_delta_smoke_001/failure_analysis.json`

## Change Under Test

- Replaced per-step action-specific `corner_action_risk` shaping with state-based `corner_risk_delta`.
- `corner_risk_delta` rewards lowering opening corner pressure and penalizes increasing it, independent of the chosen diagonal action.
- `corner_action_risk` remains serialized as a compatibility field but is no longer used for this repair reward.

## Training Smoke

- Warm start: `harness/reports/2026-05-27_rl_curriculum_time_bucket_stage01_retry_20k_001/stage01_opening_retry_20k.zip`
- Requested timesteps: `2048`
- Actual timesteps: `2048`
- Training maps: `cracked-star-jar`, `soda-creek`
- Training seconds: `60`
- Entropy coefficient: `0.02`

Training evaluation on `soda-creek`:

- Win rate: `60%`
- Average survival: `55.1862s`
- Dominant action: `4` / `39.36%`
- Normalized action entropy: `0.4928`
- Average `corner_risk_delta`: `-0.0046`
- Gate: `trained_needs_rule_bot_comparison`

## 60s High-pressure 10-seed Comparison

Deterministic policy actions:

| Map | Win Rate | Avg Survival | Dominant Action | Entropy |
|---|---:|---:|---|---:|
| `soda-creek` | 100.00% | 60.0328s | `7` / 49.37% | 0.4951 |
| `caramel-workshop` | 100.00% | 60.0328s | `7` / 38.71% | 0.5161 |
| `cracked-star-jar` | 100.00% | 60.0328s | `4` / 33.10% | 0.5715 |

Stochastic policy actions:

| Map | Win Rate | Avg Survival | Dominant Action | Entropy |
|---|---:|---:|---|---:|
| `soda-creek` | 100.00% | 60.0328s | `7` / 30.76% | 0.8257 |
| `caramel-workshop` | 100.00% | 60.0328s | `7` / 26.60% | 0.8462 |
| `cracked-star-jar` | 100.00% | 60.0328s | `7` / 28.55% | 0.8340 |

Comparison gate: `multimap_comparison_recorded_not_balance_gate`.

## Failure Analysis

- Deterministic total failures: `0`
- Stochastic total failures: `0`
- Repair maps: none

## Conclusion

The state-based `corner_risk_delta` smoke fixes the stage 01 opening blocker in the short 60-second high-pressure window used by the current curriculum check. It restores `soda-creek` from 70% in the directional action smoke to 100%, avoids action `8` collapse, and also passes stochastic sampling on the same 10 seeds.

This is stage 01 opening repair evidence only. It is not full RL policy acceptance and does not prove 180s or 300s stability.

## Next

- Use this checkpoint as the stage 01 opening baseline for the next stage 02 mid-window experiment.
- Before promoting any RL test Bot candidate, run 180s and 300s high-pressure comparisons, rule Bot review, replay/failure analysis, and the usual policy acceptance gates.
