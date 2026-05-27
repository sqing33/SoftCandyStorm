# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-27_rl_late_boundary_closed_loop_curriculum_smoke_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 13
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 5 | 77.9831 | `7` / 46.31% | 0.4336 |
| `caramel-workshop` | 0.0 | 5 | 139.9067 | `4` / 41.62% | 0.5514 |
| `cracked-star-jar` | 0.4 | 3 | 212.9499 | `7` / 46.92% | 0.4706 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 3 (60.00%)
- `mid_60_to_180`: 1 (20.00%)
- `late_180_to_300`: 1 (20.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 24.0333 | `opening_lt_60` | `player_health_depleted` | 2 | 23 | 120.0101 |
| 62401 | 33.7332 | `opening_lt_60` | `player_health_depleted` | 1 | 27 | 120.42 |
| 62402 | 215.017 | `late_180_to_300` | `player_health_depleted` | 9 | 528 | 120.6102 |
| 62403 | 24.3666 | `opening_lt_60` | `player_health_depleted` | 1 | 22 | 120.8799 |
| 62404 | 92.7656 | `mid_60_to_180` | `player_health_depleted` | 3 | 88 | 120.0502 |

### `caramel-workshop`

- `opening_lt_60`: 1 (20.00%)
- `mid_60_to_180`: 2 (40.00%)
- `late_180_to_300`: 2 (40.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 57.5328 | `opening_lt_60` | `player_health_depleted` | 2 | 31 | 120.2005 |
| 62401 | 129.432 | `mid_60_to_180` | `player_health_depleted` | 5 | 145 | 120.0505 |
| 62402 | 226.7528 | `late_180_to_300` | `player_health_depleted` | 7 | 362 | 120.5065 |
| 62403 | 213.6167 | `late_180_to_300` | `player_health_depleted` | 7 | 325 | 120.5502 |
| 62404 | 72.1992 | `mid_60_to_180` | `player_health_depleted` | 2 | 48 | 120.2503 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 185.344 | `late_180_to_300` | `player_health_depleted` | 7 | 382 | 120.0637 |
| 62402 | 219.1178 | `late_180_to_300` | `player_health_depleted` | 9 | 472 | 122.3367 |
| 62403 | 234.3878 | `late_180_to_300` | `player_health_depleted` | 10 | 513 | 120.0768 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
