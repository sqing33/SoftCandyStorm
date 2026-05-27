# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-27_rl_late_boundary_opening_wrapper_probe_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 14
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 5 | 130.4361 | `7` / 40.96% | 0.5375 |
| `caramel-workshop` | 0.0 | 5 | 200.4405 | `7` / 41.30% | 0.5524 |
| `cracked-star-jar` | 0.2 | 4 | 156.2005 | `7` / 55.11% | 0.4428 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 4 (80.00%)
- `late_180_to_300`: 1 (20.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 70.7993 | `mid_60_to_180` | `player_health_depleted` | 2 | 81 | 120.4401 |
| 62401 | 120.2318 | `mid_60_to_180` | `player_health_depleted` | 4 | 158 | 120.0602 |
| 62402 | 218.0843 | `late_180_to_300` | `player_health_depleted` | 8 | 507 | 120.0699 |
| 62403 | 109.732 | `mid_60_to_180` | `player_health_depleted` | 3 | 134 | 120.3634 |
| 62404 | 133.3329 | `mid_60_to_180` | `player_health_depleted` | 4 | 166 | 120.0 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (20.00%)
- `late_180_to_300`: 4 (80.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 212.0497 | `late_180_to_300` | `player_health_depleted` | 7 | 323 | 120.5002 |
| 62401 | 133.1995 | `mid_60_to_180` | `player_health_depleted` | 5 | 156 | 120.2271 |
| 62402 | 224.0522 | `late_180_to_300` | `player_health_depleted` | 7 | 349 | 121.0732 |
| 62403 | 217.4508 | `late_180_to_300` | `player_health_depleted` | 7 | 340 | 120.8167 |
| 62404 | 215.4504 | `late_180_to_300` | `player_health_depleted` | 7 | 340 | 120.4434 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 2 (50.00%)
- `late_180_to_300`: 2 (50.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 107.032 | `mid_60_to_180` | `player_health_depleted` | 3 | 134 | 120.2169 |
| 62402 | 225.3192 | `late_180_to_300` | `player_health_depleted` | 9 | 505 | 120.0131 |
| 62403 | 220.3848 | `late_180_to_300` | `player_health_depleted` | 8 | 482 | 120.0569 |
| 62404 | 72.0659 | `mid_60_to_180` | `player_health_depleted` | 3 | 68 | 120.0169 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
