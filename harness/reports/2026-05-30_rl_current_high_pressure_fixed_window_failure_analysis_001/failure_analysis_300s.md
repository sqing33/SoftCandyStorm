# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-29_rl_current_high_pressure_smoke_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 115.586 | `5` / 43.86% | 0.6389 |
| `caramel-workshop` | 0.0 | 3 | 215.6949 | `5` / 27.91% | 0.8103 |
| `cracked-star-jar` | 0.0 | 3 | 192.2798 | `5` / 34.21% | 0.7651 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 2 (66.67%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 1 (33.33%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63200 | 48.6329 | `opening_lt_60` | `player_health_depleted` | 1 | 42 | 120.4799 |
| 63201 | 254.3254 | `late_180_to_300` | `player_health_depleted` | 8 | 737 | 121.1366 |
| 63202 | 43.7997 | `opening_lt_60` | `player_health_depleted` | 2 | 49 | 120.0202 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63200 | 214.5502 | `late_180_to_300` | `player_health_depleted` | 6 | 331 | 120.1366 |
| 63201 | 212.9832 | `late_180_to_300` | `player_health_depleted` | 8 | 326 | 120.5169 |
| 63202 | 219.5513 | `late_180_to_300` | `player_health_depleted` | 6 | 340 | 120.6868 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63200 | 77.2992 | `mid_60_to_180` | `player_health_depleted` | 2 | 75 | 120.4332 |
| 63201 | 274.6545 | `late_180_to_300` | `player_health_depleted` | 8 | 608 | 120.3399 |
| 63202 | 224.8857 | `late_180_to_300` | `player_health_depleted` | 8 | 497 | 120.8267 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
