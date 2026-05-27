# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-27_rl_late_boundary_handoff_opening_wrapper_midonly_ablation_001/handoff_60_90_mid_w0_5/high_pressure_300s_wrapper_comparison.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 13
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.2 | 4 | 115.0284 | `7` / 32.96% | 0.8341 |
| `caramel-workshop` | 0.2 | 4 | 204.8148 | `7` / 33.79% | 0.8267 |
| `cracked-star-jar` | 0.0 | 5 | 127.8633 | `7` / 54.19% | 0.5954 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 3 (75.00%)
- `late_180_to_300`: 1 (25.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 70.7993 | `mid_60_to_180` | `player_health_depleted` | 2 | 81 | 120.4401 |
| 62401 | 71.2993 | `mid_60_to_180` | `player_health_depleted` | 3 | 66 | 120.7099 |
| 62403 | 211.1161 | `late_180_to_300` | `player_health_depleted` | 8 | 497 | 120.1903 |
| 62404 | 106.8987 | `mid_60_to_180` | `player_health_depleted` | 4 | 130 | 120.0799 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (25.00%)
- `late_180_to_300`: 3 (75.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62401 | 159.3384 | `mid_60_to_180` | `player_health_depleted` | 5 | 213 | 120.1206 |
| 62402 | 222.7186 | `late_180_to_300` | `player_health_depleted` | 6 | 344 | 120.5166 |
| 62403 | 215.8171 | `late_180_to_300` | `player_health_depleted` | 7 | 332 | 120.0168 |
| 62404 | 221.385 | `late_180_to_300` | `player_health_depleted` | 8 | 332 | 120.1732 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 4 (80.00%)
- `late_180_to_300`: 1 (20.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 99.8655 | `mid_60_to_180` | `player_health_depleted` | 4 | 118 | 120.0102 |
| 62401 | 124.9984 | `mid_60_to_180` | `player_health_depleted` | 5 | 178 | 120.6167 |
| 62402 | 234.8212 | `late_180_to_300` | `player_health_depleted` | 11 | 554 | 120.6499 |
| 62403 | 107.5654 | `mid_60_to_180` | `player_health_depleted` | 3 | 135 | 120.6833 |
| 62404 | 72.0659 | `mid_60_to_180` | `player_health_depleted` | 3 | 68 | 120.0169 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
