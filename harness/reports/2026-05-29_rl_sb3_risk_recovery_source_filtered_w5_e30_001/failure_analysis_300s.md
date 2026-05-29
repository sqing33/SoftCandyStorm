# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-29_rl_sb3_risk_recovery_source_filtered_w5_e30_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 128.762 | `5` / 31.19% | 0.767 |
| `caramel-workshop` | 0.0 | 3 | 155.7231 | `5` / 33.89% | 0.7971 |
| `cracked-star-jar` | 0.0 | 3 | 185.6123 | `5` / 46.19% | 0.6891 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 1 (33.33%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 195.7795 | `late_180_to_300` | `player_health_depleted` | 7 | 442 | 120.0535 |
| 63101 | 24.4666 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.6299 |
| 63102 | 166.0398 | `mid_60_to_180` | `player_health_depleted` | 6 | 332 | 120.0669 |

### `caramel-workshop`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 219.8847 | `late_180_to_300` | `player_health_depleted` | 6 | 342 | 120.1834 |
| 63101 | 27.9333 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.5166 |
| 63102 | 219.3512 | `late_180_to_300` | `player_health_depleted` | 7 | 351 | 120.9768 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 224.1523 | `late_180_to_300` | `player_health_depleted` | 6 | 486 | 121.0366 |
| 63101 | 225.5525 | `late_180_to_300` | `player_health_depleted` | 6 | 502 | 120.907 |
| 63102 | 107.132 | `mid_60_to_180` | `player_health_depleted` | 4 | 116 | 120.1136 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
