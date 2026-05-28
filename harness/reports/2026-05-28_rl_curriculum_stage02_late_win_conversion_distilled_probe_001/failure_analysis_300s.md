# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_late_win_conversion_distilled_probe_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 8
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 69.222 | `1` / 58.06% | 0.5141 |
| `caramel-workshop` | 0.0 | 3 | 214.828 | `7` / 44.04% | 0.6914 |
| `cracked-star-jar` | 0.3333 | 2 | 208.2989 | `5` / 32.66% | 0.7599 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 2 (66.67%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 42.833 | `opening_lt_60` | `player_health_depleted` | 2 | 46 | 120.21 |
| 63101 | 29.7999 | `opening_lt_60` | `player_health_depleted` | 1 | 24 | 120.3101 |
| 63102 | 135.0332 | `mid_60_to_180` | `player_health_depleted` | 5 | 227 | 120.0334 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 215.217 | `late_180_to_300` | `player_health_depleted` | 7 | 333 | 120.8801 |
| 63101 | 214.1168 | `late_180_to_300` | `player_health_depleted` | 6 | 327 | 120.86 |
| 63102 | 215.1503 | `late_180_to_300` | `player_health_depleted` | 6 | 335 | 121.2501 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 215.7505 | `late_180_to_300` | `player_health_depleted` | 7 | 473 | 120.2969 |
| 63102 | 200.8473 | `late_180_to_300` | `player_health_depleted` | 7 | 410 | 120.0104 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
