# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/stages/stage_01_opening_lt_60/comparison_180s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_watch`
- Duration: `180.0` seconds
- Total failures: 3
- Repair maps: `soda-creek`, `caramel-workshop`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.6667 | 1 | 37.4664 | `5` / 40.93% | 0.7693 |
| `caramel-workshop` | 0.3333 | 2 | 86.3494 | `7` / 48.04% | 0.6821 |
| `cracked-star-jar` | 1.0 | 0 | None | `3` / 21.46% | 0.8713 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 1 (100.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63402 | 37.4664 | `opening_lt_60` | `player_health_depleted` | 1 | 34 | 120.0499 |

### `caramel-workshop`

- `opening_lt_60`: 1 (50.00%)
- `mid_60_to_180`: 1 (50.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63401 | 131.3991 | `mid_60_to_180` | `player_health_depleted` | 5 | 149 | 120.2267 |
| 63402 | 41.2997 | `opening_lt_60` | `player_health_depleted` | 1 | 25 | 120.9169 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
