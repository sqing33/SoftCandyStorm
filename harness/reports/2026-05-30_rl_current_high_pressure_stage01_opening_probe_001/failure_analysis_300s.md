# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/stages/stage_01_opening_lt_60/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 155.789 | `5` / 27.26% | 0.7904 |
| `caramel-workshop` | 0.0 | 3 | 156.0777 | `5` / 45.95% | 0.7178 |
| `cracked-star-jar` | 0.0 | 3 | 242.9744 | `1` / 41.38% | 0.7571 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63400 | 219.1512 | `late_180_to_300` | `player_health_depleted` | 8 | 538 | 121.5333 |
| 63401 | 210.6494 | `late_180_to_300` | `player_health_depleted` | 7 | 490 | 120.0837 |
| 63402 | 37.5664 | `opening_lt_60` | `player_health_depleted` | 1 | 34 | 121.1499 |

### `caramel-workshop`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63400 | 213.9167 | `late_180_to_300` | `player_health_depleted` | 6 | 331 | 120.1699 |
| 63401 | 213.4166 | `late_180_to_300` | `player_health_depleted` | 3 | 323 | 120.0134 |
| 63402 | 40.8997 | `opening_lt_60` | `player_health_depleted` | 1 | 25 | 120.3833 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63400 | 218.7844 | `late_180_to_300` | `player_health_depleted` | 6 | 463 | 121.43 |
| 63401 | 282.4526 | `late_180_to_300` | `player_health_depleted` | 8 | 692 | 120.7199 |
| 63402 | 227.6863 | `late_180_to_300` | `player_health_depleted` | 7 | 477 | 120.0005 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
