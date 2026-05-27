# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-27_rl_late_boundary_handoff_opening_wrapper_probe_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 15
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 5 | 195.4408 | `3` / 30.09% | 0.8074 |
| `caramel-workshop` | 0.0 | 5 | 191.9871 | `3` / 34.65% | 0.783 |
| `cracked-star-jar` | 0.0 | 5 | 167.9412 | `3` / 23.88% | 0.8339 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (20.00%)
- `late_180_to_300`: 4 (80.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 214.0168 | `late_180_to_300` | `player_health_depleted` | 8 | 487 | 120.7702 |
| 62401 | 99.2322 | `mid_60_to_180` | `player_health_depleted` | 3 | 90 | 120.0334 |
| 62402 | 237.2551 | `late_180_to_300` | `player_health_depleted` | 10 | 648 | 120.3165 |
| 62403 | 211.7496 | `late_180_to_300` | `player_health_depleted` | 8 | 495 | 120.4767 |
| 62404 | 214.9503 | `late_180_to_300` | `player_health_depleted` | 9 | 478 | 120.2668 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (20.00%)
- `late_180_to_300`: 4 (80.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 219.3512 | `late_180_to_300` | `player_health_depleted` | 8 | 340 | 120.5602 |
| 62401 | 91.3323 | `mid_60_to_180` | `player_health_depleted` | 3 | 58 | 120.6835 |
| 62402 | 216.3839 | `late_180_to_300` | `player_health_depleted` | 7 | 331 | 120.9267 |
| 62403 | 214.4502 | `late_180_to_300` | `player_health_depleted` | 8 | 324 | 121.0768 |
| 62404 | 218.4177 | `late_180_to_300` | `player_health_depleted` | 8 | 336 | 121.0601 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 3 (60.00%)
- `late_180_to_300`: 2 (40.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 281.053 | `late_180_to_300` | `player_health_depleted` | 11 | 692 | 120.2438 |
| 62401 | 107.0654 | `mid_60_to_180` | `player_health_depleted` | 3 | 120 | 120.8767 |
| 62402 | 215.8505 | `late_180_to_300` | `player_health_depleted` | 9 | 482 | 120.7733 |
| 62403 | 157.438 | `mid_60_to_180` | `player_health_depleted` | 6 | 258 | 120.1601 |
| 62404 | 78.2991 | `mid_60_to_180` | `player_health_depleted` | 3 | 71 | 120.0169 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
