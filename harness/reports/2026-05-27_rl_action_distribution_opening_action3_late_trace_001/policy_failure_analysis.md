# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-27_rl_action_distribution_opening_action3_late_trace_001/comparison_300s_trace.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 15
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 5 | 143.2769 | `1` / 55.33% | 0.6385 |
| `caramel-workshop` | 0.0 | 5 | 218.5377 | `1` / 42.11% | 0.7291 |
| `cracked-star-jar` | 0.0 | 5 | 183.7876 | `1` / 58.47% | 0.5966 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 2 (40.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (60.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 218.051 | `late_180_to_300` | `player_health_depleted` | 7 | 500 | 120.8669 |
| 62401 | 34.7998 | `opening_lt_60` | `player_health_depleted` | 2 | 30 | 120.3299 |
| 62402 | 217.9176 | `late_180_to_300` | `player_health_depleted` | 8 | 542 | 120.4767 |
| 62403 | 211.0495 | `late_180_to_300` | `player_health_depleted` | 7 | 487 | 120.5201 |
| 62404 | 34.5665 | `opening_lt_60` | `player_health_depleted` | 2 | 32 | 120.3901 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 5 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 219.4512 | `late_180_to_300` | `player_health_depleted` | 8 | 341 | 121.1 |
| 62401 | 213.9501 | `late_180_to_300` | `player_health_depleted` | 6 | 327 | 120.38 |
| 62402 | 222.1518 | `late_180_to_300` | `player_health_depleted` | 5 | 341 | 120.7765 |
| 62403 | 215.2837 | `late_180_to_300` | `player_health_depleted` | 6 | 332 | 120.6935 |
| 62404 | 221.8518 | `late_180_to_300` | `player_health_depleted` | 7 | 346 | 120.98 |

### `cracked-star-jar`

- `opening_lt_60`: 1 (20.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 4 (80.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 222.6186 | `late_180_to_300` | `player_health_depleted` | 8 | 497 | 120.2267 |
| 62401 | 225.3525 | `late_180_to_300` | `player_health_depleted` | 7 | 477 | 120.2069 |
| 62402 | 212.7165 | `late_180_to_300` | `player_health_depleted` | 8 | 442 | 120.6901 |
| 62403 | 41.2997 | `opening_lt_60` | `player_health_depleted` | 2 | 39 | 120.59 |
| 62404 | 216.9507 | `late_180_to_300` | `player_health_depleted` | 6 | 429 | 120.98 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
