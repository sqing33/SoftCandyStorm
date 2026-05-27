# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-27_rl_late_route_action4_midlate_ablation_001/action4_w0_5/high_pressure_300s_comparison.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 15
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 5 | 137.6423 | `3` / 30.91% | 0.7703 |
| `caramel-workshop` | 0.0 | 5 | 221.4517 | `3` / 32.13% | 0.7329 |
| `cracked-star-jar` | 0.0 | 5 | 184.4544 | `5` / 26.34% | 0.8364 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 2 (40.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (60.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 189.2115 | `late_180_to_300` | `player_health_depleted` | 7 | 409 | 120.2336 |
| 62401 | 34.7998 | `opening_lt_60` | `player_health_depleted` | 2 | 30 | 120.3299 |
| 62402 | 217.4842 | `late_180_to_300` | `player_health_depleted` | 7 | 510 | 120.5033 |
| 62403 | 212.1497 | `late_180_to_300` | `player_health_depleted` | 8 | 498 | 120.517 |
| 62404 | 34.5665 | `opening_lt_60` | `player_health_depleted` | 2 | 32 | 120.3901 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 5 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 213.6167 | `late_180_to_300` | `player_health_depleted` | 6 | 324 | 120.8733 |
| 62401 | 225.7859 | `late_180_to_300` | `player_health_depleted` | 6 | 351 | 120.1032 |
| 62402 | 230.6536 | `late_180_to_300` | `player_health_depleted` | 9 | 359 | 120.0032 |
| 62403 | 220.5515 | `late_180_to_300` | `player_health_depleted` | 8 | 340 | 120.2136 |
| 62404 | 216.6507 | `late_180_to_300` | `player_health_depleted` | 8 | 333 | 120.1034 |

### `cracked-star-jar`

- `opening_lt_60`: 1 (20.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 4 (80.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 222.7186 | `late_180_to_300` | `player_health_depleted` | 8 | 500 | 121.2503 |
| 62401 | 215.6504 | `late_180_to_300` | `player_health_depleted` | 8 | 432 | 121.2698 |
| 62402 | 219.6846 | `late_180_to_300` | `player_health_depleted` | 8 | 484 | 120.8932 |
| 62403 | 41.2997 | `opening_lt_60` | `player_health_depleted` | 2 | 39 | 120.59 |
| 62404 | 222.9187 | `late_180_to_300` | `player_health_depleted` | 9 | 469 | 120.1836 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
