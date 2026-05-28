# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 8
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 230.2514 | `7` / 42.39% | 0.4927 |
| `caramel-workshop` | 0.0 | 3 | 212.3275 | `2` / 58.69% | 0.4913 |
| `cracked-star-jar` | 0.3333 | 2 | 221.5016 | `7` / 39.48% | 0.4973 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62800 | 270.1556 | `late_180_to_300` | `player_health_depleted` | 9 | 813 | 120.2534 |
| 62801 | 210.4827 | `late_180_to_300` | `player_health_depleted` | 7 | 467 | 120.2102 |
| 62802 | 210.1159 | `late_180_to_300` | `player_health_depleted` | 7 | 472 | 120.0636 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62800 | 211.4162 | `late_180_to_300` | `player_health_depleted` | 8 | 323 | 120.507 |
| 62801 | 212.7498 | `late_180_to_300` | `player_health_depleted` | 7 | 324 | 121.85 |
| 62802 | 212.8165 | `late_180_to_300` | `player_health_depleted` | 6 | 338 | 121.1734 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62800 | 225.5525 | `late_180_to_300` | `player_health_depleted` | 7 | 513 | 120.7267 |
| 62802 | 217.4508 | `late_180_to_300` | `player_health_depleted` | 8 | 450 | 120.1669 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
