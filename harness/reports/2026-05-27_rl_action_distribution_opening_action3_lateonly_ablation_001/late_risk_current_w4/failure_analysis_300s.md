# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-27_rl_action_distribution_opening_action3_lateonly_ablation_001/late_risk_current_w4/high_pressure_300s_comparison.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 14
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 5 | 144.1104 | `1` / 48.39% | 0.736 |
| `caramel-workshop` | 0.0 | 5 | 215.6305 | `1` / 33.34% | 0.8453 |
| `cracked-star-jar` | 0.2 | 4 | 185.1489 | `1` / 44.00% | 0.7311 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 2 (40.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (60.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 223.8855 | `late_180_to_300` | `player_health_depleted` | 8 | 539 | 120.7236 |
| 62401 | 34.7998 | `opening_lt_60` | `player_health_depleted` | 2 | 30 | 120.3299 |
| 62402 | 213.5166 | `late_180_to_300` | `player_health_depleted` | 7 | 489 | 121.3366 |
| 62403 | 213.7834 | `late_180_to_300` | `player_health_depleted` | 7 | 492 | 121.0501 |
| 62404 | 34.5665 | `opening_lt_60` | `player_health_depleted` | 2 | 32 | 120.3901 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 5 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 214.1835 | `late_180_to_300` | `player_health_depleted` | 8 | 321 | 120.3601 |
| 62401 | 213.6167 | `late_180_to_300` | `player_health_depleted` | 7 | 323 | 120.6801 |
| 62402 | 212.6498 | `late_180_to_300` | `player_health_depleted` | 6 | 322 | 120.5133 |
| 62403 | 218.9845 | `late_180_to_300` | `player_health_depleted` | 7 | 330 | 120.5102 |
| 62404 | 218.7178 | `late_180_to_300` | `player_health_depleted` | 7 | 339 | 120.7568 |

### `cracked-star-jar`

- `opening_lt_60`: 1 (25.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (75.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62401 | 229.42 | `late_180_to_300` | `player_health_depleted` | 8 | 475 | 120.3234 |
| 62402 | 241.3226 | `late_180_to_300` | `player_health_depleted` | 9 | 537 | 120.3032 |
| 62403 | 41.2997 | `opening_lt_60` | `player_health_depleted` | 2 | 39 | 120.59 |
| 62404 | 228.5532 | `late_180_to_300` | `player_health_depleted` | 8 | 470 | 120.1298 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
