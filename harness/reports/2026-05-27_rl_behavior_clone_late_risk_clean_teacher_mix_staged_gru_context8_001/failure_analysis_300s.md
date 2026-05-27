# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-27_rl_behavior_clone_late_risk_clean_teacher_mix_staged_gru_context8_001/comparison_300s_3seed.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 231.6205 | `3` / 27.27% | 0.8458 |
| `caramel-workshop` | 0.0 | 3 | 220.3737 | `1` / 22.87% | 0.9073 |
| `cracked-star-jar` | 0.0 | 3 | 227.2076 | `3` / 24.42% | 0.885 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62300 | 224.419 | `late_180_to_300` | `player_health_depleted` | 9 | 563 | 121.1734 |
| 62301 | 255.8257 | `late_180_to_300` | `player_health_depleted` | 9 | 776 | 120.2171 |
| 62302 | 214.6169 | `late_180_to_300` | `player_health_depleted` | 8 | 454 | 121.3133 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62300 | 215.1503 | `late_180_to_300` | `player_health_depleted` | 8 | 325 | 120.05 |
| 62301 | 218.5177 | `late_180_to_300` | `player_health_depleted` | 7 | 340 | 120.4033 |
| 62302 | 227.453 | `late_180_to_300` | `player_health_depleted` | 7 | 371 | 120.13 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62300 | 194.946 | `late_180_to_300` | `player_health_depleted` | 8 | 411 | 120.1405 |
| 62301 | 261.5244 | `late_180_to_300` | `player_health_depleted` | 9 | 568 | 120.0971 |
| 62302 | 225.1525 | `late_180_to_300` | `player_health_depleted` | 7 | 449 | 121.5533 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
