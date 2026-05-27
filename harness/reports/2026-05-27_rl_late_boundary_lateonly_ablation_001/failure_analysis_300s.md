# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-27_rl_late_boundary_lateonly_ablation_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 13
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 5 | 156.1263 | `1` / 48.86% | 0.7313 |
| `caramel-workshop` | 0.0 | 5 | 225.9526 | `1` / 35.55% | 0.7916 |
| `cracked-star-jar` | 0.4 | 3 | 170.558 | `1` / 45.66% | 0.7293 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 2 (40.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (60.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 251.0913 | `late_180_to_300` | `player_health_depleted` | 10 | 664 | 120.1536 |
| 62401 | 34.7998 | `opening_lt_60` | `player_health_depleted` | 2 | 30 | 120.3299 |
| 62402 | 219.1512 | `late_180_to_300` | `player_health_depleted` | 8 | 548 | 120.1068 |
| 62403 | 241.0225 | `late_180_to_300` | `player_health_depleted` | 10 | 665 | 120.0236 |
| 62404 | 34.5665 | `opening_lt_60` | `player_health_depleted` | 2 | 32 | 120.3901 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 5 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 225.7859 | `late_180_to_300` | `player_health_depleted` | 8 | 356 | 120.1266 |
| 62401 | 213.9501 | `late_180_to_300` | `player_health_depleted` | 7 | 325 | 120.0467 |
| 62402 | 232.8875 | `late_180_to_300` | `player_health_depleted` | 9 | 375 | 120.1965 |
| 62403 | 225.5192 | `late_180_to_300` | `player_health_depleted` | 8 | 356 | 120.46 |
| 62404 | 231.6205 | `late_180_to_300` | `player_health_depleted` | 8 | 366 | 120.0732 |

### `cracked-star-jar`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 210.8161 | `late_180_to_300` | `player_health_depleted` | 7 | 447 | 120.6636 |
| 62401 | 259.5582 | `late_180_to_300` | `player_health_depleted` | 9 | 581 | 120.5901 |
| 62403 | 41.2997 | `opening_lt_60` | `player_health_depleted` | 2 | 39 | 120.59 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
