# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_late_pressure_expanded_lateonly_ablation_001/pressure_late_w0_5/high_pressure_300s_comparison.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 13
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 5 | 168.002 | `1` / 54.91% | 0.6357 |
| `caramel-workshop` | 0.0 | 5 | 161.4553 | `1` / 48.50% | 0.6621 |
| `cracked-star-jar` | 0.4 | 3 | 232.6185 | `1` / 42.94% | 0.7508 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 1 (20.00%)
- `mid_60_to_180`: 2 (40.00%)
- `late_180_to_300`: 2 (40.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 148.3361 | `mid_60_to_180` | `player_health_depleted` | 6 | 272 | 120.2205 |
| 62401 | 212.5164 | `late_180_to_300` | `player_health_depleted` | 7 | 491 | 120.2366 |
| 62402 | 284.2188 | `late_180_to_300` | `player_health_depleted` | 10 | 949 | 120.0533 |
| 62403 | 160.472 | `mid_60_to_180` | `player_health_depleted` | 5 | 330 | 120.1037 |
| 62404 | 34.4665 | `opening_lt_60` | `player_health_depleted` | 2 | 31 | 120.1501 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 3 (60.00%)
- `late_180_to_300`: 2 (40.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 213.8167 | `late_180_to_300` | `player_health_depleted` | 7 | 317 | 121.2636 |
| 62401 | 215.8838 | `late_180_to_300` | `player_health_depleted` | 9 | 336 | 121.0168 |
| 62402 | 158.6383 | `mid_60_to_180` | `player_health_depleted` | 6 | 192 | 120.047 |
| 62403 | 157.8048 | `mid_60_to_180` | `player_health_depleted` | 6 | 200 | 120.2169 |
| 62404 | 61.1327 | `mid_60_to_180` | `player_health_depleted` | 2 | 41 | 120.2666 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 213.7834 | `late_180_to_300` | `player_health_depleted` | 8 | 451 | 120.0068 |
| 62402 | 213.2166 | `late_180_to_300` | `player_health_depleted` | 8 | 458 | 120.447 |
| 62403 | 270.8554 | `late_180_to_300` | `player_health_depleted` | 9 | 652 | 120.0267 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
