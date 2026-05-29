# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-29_rl_sb3_cracked_late_scoped_risk_distill_w10_e30_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 151.8447 | `1` / 29.18% | 0.7984 |
| `caramel-workshop` | 0.0 | 3 | 152.4001 | `3` / 29.54% | 0.778 |
| `cracked-star-jar` | 0.0 | 3 | 224.5856 | `5` / 45.11% | 0.7691 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 212.3831 | `late_180_to_300` | `player_health_depleted` | 7 | 499 | 120.0467 |
| 63101 | 24.4666 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.6299 |
| 63102 | 218.6844 | `late_180_to_300` | `player_health_depleted` | 8 | 511 | 120.2266 |

### `caramel-workshop`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 213.4833 | `late_180_to_300` | `player_health_depleted` | 8 | 326 | 121.0937 |
| 63101 | 27.9333 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.5166 |
| 63102 | 215.7838 | `late_180_to_300` | `player_health_depleted` | 8 | 350 | 120.3834 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 222.2518 | `late_180_to_300` | `player_health_depleted` | 6 | 473 | 120.83 |
| 63101 | 214.7502 | `late_180_to_300` | `player_health_depleted` | 8 | 473 | 121.0502 |
| 63102 | 236.7549 | `late_180_to_300` | `player_health_depleted` | 8 | 555 | 120.0001 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
