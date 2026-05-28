# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_late_pressure_expanded_lateonly_ablation_001/pressure_late_w0_5_no_ranker/high_pressure_300s_comparison.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 14
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 5 | 144.1837 | `1` / 55.53% | 0.6407 |
| `caramel-workshop` | 0.0 | 5 | 220.1047 | `1` / 37.92% | 0.7585 |
| `cracked-star-jar` | 0.2 | 4 | 190.9493 | `1` / 51.33% | 0.6695 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 2 (40.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (60.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 217.1174 | `late_180_to_300` | `player_health_depleted` | 7 | 499 | 120.0403 |
| 62401 | 34.7998 | `opening_lt_60` | `player_health_depleted` | 2 | 30 | 120.3299 |
| 62402 | 216.2839 | `late_180_to_300` | `player_health_depleted` | 8 | 529 | 120.1633 |
| 62403 | 218.151 | `late_180_to_300` | `player_health_depleted` | 8 | 531 | 120.3835 |
| 62404 | 34.5665 | `opening_lt_60` | `player_health_depleted` | 2 | 32 | 120.3901 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 5 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 226.9862 | `late_180_to_300` | `player_health_depleted` | 8 | 357 | 120.2832 |
| 62401 | 213.9501 | `late_180_to_300` | `player_health_depleted` | 6 | 327 | 120.38 |
| 62402 | 213.7167 | `late_180_to_300` | `player_health_depleted` | 8 | 325 | 120.6933 |
| 62403 | 213.4833 | `late_180_to_300` | `player_health_depleted` | 9 | 328 | 120.2603 |
| 62404 | 232.3873 | `late_180_to_300` | `player_health_depleted` | 8 | 372 | 120.0132 |

### `cracked-star-jar`

- `opening_lt_60`: 1 (25.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (75.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 234.0544 | `late_180_to_300` | `player_health_depleted` | 8 | 521 | 121.1635 |
| 62401 | 225.1525 | `late_180_to_300` | `player_health_depleted` | 7 | 476 | 120.3102 |
| 62403 | 41.2997 | `opening_lt_60` | `player_health_depleted` | 2 | 39 | 120.59 |
| 62404 | 263.2906 | `late_180_to_300` | `player_health_depleted` | 8 | 576 | 120.0968 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
