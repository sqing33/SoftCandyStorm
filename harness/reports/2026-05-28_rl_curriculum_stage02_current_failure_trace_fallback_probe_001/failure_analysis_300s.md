# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_current_failure_trace_fallback_probe_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 153.8508 | `3` / 39.38% | 0.7359 |
| `caramel-workshop` | 0.0 | 3 | 154.7006 | `3` / 37.98% | 0.7273 |
| `cracked-star-jar` | 0.0 | 3 | 211.0341 | `8` / 36.97% | 0.7351 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 2 (66.67%)
- `late_180_to_300`: 1 (33.33%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 103.6654 | `mid_60_to_180` | `player_health_depleted` | 4 | 169 | 120.0168 |
| 63101 | 82.9991 | `mid_60_to_180` | `player_health_depleted` | 2 | 81 | 120.0801 |
| 63102 | 274.8878 | `late_180_to_300` | `player_health_depleted` | 10 | 903 | 120.5299 |

### `caramel-workshop`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 220.7182 | `late_180_to_300` | `player_health_depleted` | 4 | 338 | 120.2666 |
| 63101 | 27.9333 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.5166 |
| 63102 | 215.4504 | `late_180_to_300` | `player_health_depleted` | 7 | 334 | 120.3434 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 284.1189 | `late_180_to_300` | `player_health_depleted` | 10 | 680 | 120.5901 |
| 63101 | 130.5323 | `mid_60_to_180` | `player_health_depleted` | 4 | 215 | 120.0901 |
| 63102 | 218.451 | `late_180_to_300` | `player_health_depleted` | 7 | 473 | 120.5238 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
