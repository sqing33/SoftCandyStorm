# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_soda_cracked_retention_probe_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 178.7894 | `7` / 42.57% | 0.5209 |
| `caramel-workshop` | 0.0 | 3 | 219.4068 | `4` / 39.14% | 0.5138 |
| `cracked-star-jar` | 0.0 | 3 | 237.5218 | `7` / 43.74% | 0.4914 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 42.5997 | `opening_lt_60` | `player_health_depleted` | 2 | 43 | 120.0833 |
| 63101 | 210.9161 | `late_180_to_300` | `player_health_depleted` | 8 | 506 | 120.3368 |
| 63102 | 282.8525 | `late_180_to_300` | `player_health_depleted` | 10 | 935 | 120.0835 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 220.2181 | `late_180_to_300` | `player_health_depleted` | 7 | 345 | 120.2069 |
| 63101 | 211.6496 | `late_180_to_300` | `player_health_depleted` | 8 | 336 | 121.1336 |
| 63102 | 226.3527 | `late_180_to_300` | `player_health_depleted` | 7 | 368 | 120.5098 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 221.9184 | `late_180_to_300` | `player_health_depleted` | 5 | 477 | 120.6233 |
| 63101 | 252.1582 | `late_180_to_300` | `player_health_depleted` | 9 | 561 | 120.097 |
| 63102 | 238.4887 | `late_180_to_300` | `player_health_depleted` | 9 | 513 | 120.3571 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
