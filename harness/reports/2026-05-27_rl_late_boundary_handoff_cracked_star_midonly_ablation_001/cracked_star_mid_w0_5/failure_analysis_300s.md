# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-27_rl_late_boundary_handoff_cracked_star_midonly_ablation_001/cracked_star_mid_w0_5/high_pressure_300s_wrapper_comparison.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 15
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 5 | 119.2836 | `7` / 51.60% | 0.6513 |
| `caramel-workshop` | 0.0 | 5 | 215.3704 | `7` / 54.39% | 0.674 |
| `cracked-star-jar` | 0.0 | 5 | 174.6401 | `7` / 39.24% | 0.8054 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 4 (80.00%)
- `late_180_to_300`: 1 (20.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 70.7993 | `mid_60_to_180` | `player_health_depleted` | 2 | 81 | 120.4401 |
| 62401 | 71.2993 | `mid_60_to_180` | `player_health_depleted` | 3 | 66 | 120.7099 |
| 62402 | 239.3222 | `late_180_to_300` | `player_health_depleted` | 9 | 658 | 120.0432 |
| 62403 | 104.0321 | `mid_60_to_180` | `player_health_depleted` | 3 | 140 | 121.1167 |
| 62404 | 110.9653 | `mid_60_to_180` | `player_health_depleted` | 4 | 149 | 120.1034 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 5 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 219.3512 | `late_180_to_300` | `player_health_depleted` | 7 | 337 | 120.8036 |
| 62401 | 209.0824 | `late_180_to_300` | `player_health_depleted` | 7 | 314 | 120.227 |
| 62402 | 220.5181 | `late_180_to_300` | `player_health_depleted` | 8 | 339 | 120.06 |
| 62403 | 213.2833 | `late_180_to_300` | `player_health_depleted` | 7 | 324 | 120.55 |
| 62404 | 214.6169 | `late_180_to_300` | `player_health_depleted` | 6 | 319 | 120.9966 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 3 (60.00%)
- `late_180_to_300`: 2 (40.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 107.032 | `mid_60_to_180` | `player_health_depleted` | 3 | 134 | 120.2169 |
| 62401 | 124.9984 | `mid_60_to_180` | `player_health_depleted` | 5 | 178 | 120.6167 |
| 62402 | 293.3833 | `late_180_to_300` | `player_health_depleted` | 10 | 669 | 120.2634 |
| 62403 | 275.7209 | `late_180_to_300` | `player_health_depleted` | 12 | 621 | 120.1198 |
| 62404 | 72.0659 | `mid_60_to_180` | `player_health_depleted` | 3 | 68 | 120.0169 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
