# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_current_failure_trace_incremental_probe_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 8
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.3333 | 2 | 154.1758 | `5` / 23.64% | 0.8268 |
| `caramel-workshop` | 0.0 | 3 | 153.7671 | `5` / 26.11% | 0.8293 |
| `cracked-star-jar` | 0.0 | 3 | 245.9284 | `5` / 38.60% | 0.7738 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (50.00%)
- `late_180_to_300`: 1 (50.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 225.3192 | `late_180_to_300` | `player_health_depleted` | 8 | 554 | 120.2867 |
| 63101 | 83.0324 | `mid_60_to_180` | `player_health_depleted` | 2 | 83 | 120.0601 |

### `caramel-workshop`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 213.1832 | `late_180_to_300` | `player_health_depleted` | 6 | 314 | 120.9569 |
| 63101 | 27.9333 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.5166 |
| 63102 | 220.1847 | `late_180_to_300` | `player_health_depleted` | 6 | 337 | 120.37 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 297.2157 | `late_180_to_300` | `player_health_depleted` | 11 | 722 | 120.4968 |
| 63101 | 197.9467 | `late_180_to_300` | `player_health_depleted` | 6 | 399 | 120.1634 |
| 63102 | 242.6229 | `late_180_to_300` | `player_health_depleted` | 8 | 519 | 120.3635 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
