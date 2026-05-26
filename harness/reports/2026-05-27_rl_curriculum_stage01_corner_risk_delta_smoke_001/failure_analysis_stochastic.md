# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-27_rl_curriculum_stage01_corner_risk_delta_smoke_001/comparison_60s_10seed_stochastic.json`
- Decision: `rl_policy_failure_analysis_no_failures`
- Gate decision: `multimap_comparison_recorded_not_balance_gate`
- Duration: `60.0` seconds
- Total failures: 0
- Repair maps: None

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 1.0 | 0 | None | `7` / 30.76% | 0.8257 |
| `caramel-workshop` | 1.0 | 0 | None | `7` / 26.60% | 0.8462 |
| `cracked-star-jar` | 1.0 | 0 | None | `7` / 28.55% | 0.834 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
