# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_late_repair_probe_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 101.8055 | `3` / 34.38% | 0.8144 |
| `caramel-workshop` | 0.0 | 3 | 221.6073 | `1` / 53.06% | 0.5901 |
| `cracked-star-jar` | 0.0 | 3 | 164.4128 | `1` / 39.46% | 0.7162 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 2 (66.67%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 1 (33.33%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62900 | 216.784 | `late_180_to_300` | `player_health_depleted` | 8 | 504 | 120.3366 |
| 62901 | 40.2997 | `opening_lt_60` | `player_health_depleted` | 2 | 34 | 120.21 |
| 62902 | 48.3329 | `opening_lt_60` | `player_health_depleted` | 2 | 47 | 120.7503 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62900 | 224.9858 | `late_180_to_300` | `player_health_depleted` | 7 | 353 | 121.01 |
| 62901 | 214.2168 | `late_180_to_300` | `player_health_depleted` | 5 | 322 | 121.097 |
| 62902 | 225.6192 | `late_180_to_300` | `player_health_depleted` | 6 | 355 | 120.1498 |

### `cracked-star-jar`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62900 | 218.6177 | `late_180_to_300` | `player_health_depleted` | 8 | 452 | 120.1836 |
| 62901 | 40.6997 | `opening_lt_60` | `player_health_depleted` | 2 | 36 | 120.2334 |
| 62902 | 233.921 | `late_180_to_300` | `player_health_depleted` | 9 | 536 | 120.6572 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
