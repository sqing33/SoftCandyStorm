# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_staged_fallback_late_retention_probe_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 8
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 134.8829 | `8` / 25.97% | 0.7873 |
| `caramel-workshop` | 0.0 | 3 | 154.9896 | `3` / 47.30% | 0.6994 |
| `cracked-star-jar` | 0.3333 | 2 | 161.0085 | `3` / 40.96% | 0.7153 |

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
| 63102 | 217.9843 | `late_180_to_300` | `player_health_depleted` | 9 | 502 | 120.4303 |

### `caramel-workshop`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 215.1837 | `late_180_to_300` | `player_health_depleted` | 6 | 325 | 120.1168 |
| 63101 | 27.9333 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.5166 |
| 63102 | 221.8518 | `late_180_to_300` | `player_health_depleted` | 5 | 338 | 120.5065 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (50.00%)
- `late_180_to_300`: 1 (50.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63101 | 101.9655 | `mid_60_to_180` | `player_health_depleted` | 4 | 141 | 120.1235 |
| 63102 | 220.0514 | `late_180_to_300` | `player_health_depleted` | 9 | 479 | 120.1635 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
