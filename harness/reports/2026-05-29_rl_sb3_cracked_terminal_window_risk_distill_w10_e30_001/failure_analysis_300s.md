# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-29_rl_sb3_cracked_terminal_window_risk_distill_w10_e30_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 155.1454 | `1` / 43.55% | 0.658 |
| `caramel-workshop` | 0.0 | 3 | 161.88 | `7` / 36.74% | 0.7519 |
| `cracked-star-jar` | 0.0 | 3 | 226.4749 | `1` / 23.43% | 0.7972 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 217.5175 | `late_180_to_300` | `player_health_depleted` | 7 | 511 | 120.5667 |
| 63101 | 24.4666 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.6299 |
| 63102 | 223.4521 | `late_180_to_300` | `player_health_depleted` | 8 | 546 | 120.4 |

### `caramel-workshop`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 232.3207 | `late_180_to_300` | `player_health_depleted` | 7 | 364 | 120.4631 |
| 63101 | 27.9333 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.5166 |
| 63102 | 225.3859 | `late_180_to_300` | `player_health_depleted` | 8 | 371 | 120.3032 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 221.7517 | `late_180_to_300` | `player_health_depleted` | 8 | 493 | 120.6836 |
| 63101 | 217.9509 | `late_180_to_300` | `player_health_depleted` | 9 | 488 | 120.097 |
| 63102 | 239.7222 | `late_180_to_300` | `player_health_depleted` | 9 | 530 | 120.0503 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
