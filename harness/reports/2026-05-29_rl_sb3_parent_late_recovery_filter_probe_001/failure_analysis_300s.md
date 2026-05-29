# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-29_rl_sb3_parent_late_recovery_filter_probe_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 8
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.3333 | 2 | 138.9792 | `1` / 26.94% | 0.8229 |
| `caramel-workshop` | 0.0 | 3 | 162.6801 | `3` / 21.43% | 0.8297 |
| `cracked-star-jar` | 0.0 | 3 | 190.7907 | `5` / 22.13% | 0.8552 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 1 (50.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 1 (50.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 253.4918 | `late_180_to_300` | `player_health_depleted` | 11 | 784 | 120.52 |
| 63101 | 24.4666 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.6299 |

### `caramel-workshop`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 226.5528 | `late_180_to_300` | `player_health_depleted` | 8 | 345 | 120.1499 |
| 63101 | 27.9333 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.5166 |
| 63102 | 233.5543 | `late_180_to_300` | `player_health_depleted` | 8 | 381 | 120.2334 |

### `cracked-star-jar`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 56.8661 | `opening_lt_60` | `player_health_depleted` | 2 | 59 | 120.7099 |
| 63101 | 284.1855 | `late_180_to_300` | `player_health_depleted` | 11 | 679 | 120.0769 |
| 63102 | 231.3204 | `late_180_to_300` | `player_health_depleted` | 9 | 523 | 120.0035 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
