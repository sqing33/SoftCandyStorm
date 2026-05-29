# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-29_rl_sb3_risk_recovery_source_filtered_w10_e30_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 8
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 95.917 | `3` / 43.37% | 0.7147 |
| `caramel-workshop` | 0.0 | 3 | 99.0055 | `5` / 29.00% | 0.7804 |
| `cracked-star-jar` | 0.3333 | 2 | 255.6715 | `5` / 28.74% | 0.7798 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 2 (66.67%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 1 (33.33%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 43.533 | `opening_lt_60` | `player_health_depleted` | 1 | 41 | 120.8499 |
| 63101 | 24.4666 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.6299 |
| 63102 | 219.7513 | `late_180_to_300` | `player_health_depleted` | 7 | 523 | 121.2199 |

### `caramel-workshop`

- `opening_lt_60`: 2 (66.67%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 1 (33.33%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 53.6995 | `opening_lt_60` | `player_health_depleted` | 1 | 30 | 120.7835 |
| 63101 | 27.9333 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.5166 |
| 63102 | 215.3837 | `late_180_to_300` | `player_health_depleted` | 6 | 326 | 120.7634 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 274.0213 | `late_180_to_300` | `player_health_depleted` | 9 | 650 | 120.2966 |
| 63102 | 237.3217 | `late_180_to_300` | `player_health_depleted` | 8 | 588 | 120.6898 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
