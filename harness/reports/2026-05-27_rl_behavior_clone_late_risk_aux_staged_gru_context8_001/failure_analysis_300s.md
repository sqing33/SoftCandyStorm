# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-27_rl_behavior_clone_late_risk_aux_staged_gru_context8_001/comparison_300s_3seed_trace.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 229.4423 | `3` / 24.39% | 0.8452 |
| `caramel-workshop` | 0.0 | 3 | 221.5628 | `1` / 17.98% | 0.9173 |
| `cracked-star-jar` | 0.0 | 3 | 258.4569 | `8` / 20.53% | 0.8665 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62300 | 216.6507 | `late_180_to_300` | `player_health_depleted` | 9 | 518 | 120.1134 |
| 62301 | 223.7188 | `late_180_to_300` | `player_health_depleted` | 8 | 569 | 120.1303 |
| 62302 | 247.9573 | `late_180_to_300` | `player_health_depleted` | 9 | 646 | 120.9068 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62300 | 217.2174 | `late_180_to_300` | `player_health_depleted` | 7 | 332 | 121.8167 |
| 62301 | 232.5207 | `late_180_to_300` | `player_health_depleted` | 7 | 369 | 120.5198 |
| 62302 | 214.9503 | `late_180_to_300` | `player_health_depleted` | 7 | 340 | 120.6502 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62300 | 245.8902 | `late_180_to_300` | `player_health_depleted` | 9 | 547 | 120.2672 |
| 62301 | 269.4891 | `late_180_to_300` | `player_health_depleted` | 10 | 606 | 120.3705 |
| 62302 | 259.9914 | `late_180_to_300` | `player_health_depleted` | 9 | 592 | 120.9564 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
