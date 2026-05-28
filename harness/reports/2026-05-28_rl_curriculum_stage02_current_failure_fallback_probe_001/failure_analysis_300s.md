# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_current_failure_fallback_probe_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 8
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 172.1335 | `1` / 22.56% | 0.8454 |
| `caramel-workshop` | 0.0 | 3 | 161.9466 | `3` / 40.68% | 0.7064 |
| `cracked-star-jar` | 0.3333 | 2 | 177.5423 | `5` / 24.54% | 0.8217 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 216.3506 | `late_180_to_300` | `player_health_depleted` | 7 | 525 | 120.8734 |
| 63101 | 82.9991 | `mid_60_to_180` | `player_health_depleted` | 2 | 81 | 120.0801 |
| 63102 | 217.0507 | `late_180_to_300` | `player_health_depleted` | 6 | 492 | 121.4999 |

### `caramel-workshop`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 226.3861 | `late_180_to_300` | `player_health_depleted` | 7 | 355 | 120.5 |
| 63101 | 27.9333 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.5166 |
| 63102 | 231.5205 | `late_180_to_300` | `player_health_depleted` | 7 | 368 | 120.3665 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (50.00%)
- `late_180_to_300`: 1 (50.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63101 | 136.0001 | `mid_60_to_180` | `player_health_depleted` | 4 | 241 | 120.0502 |
| 63102 | 219.0845 | `late_180_to_300` | `player_health_depleted` | 7 | 468 | 120.8502 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
