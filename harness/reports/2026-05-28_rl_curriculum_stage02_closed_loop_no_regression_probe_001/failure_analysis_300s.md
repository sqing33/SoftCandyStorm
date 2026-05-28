# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_closed_loop_no_regression_probe_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 122.9299 | `2` / 39.48% | 0.4917 |
| `caramel-workshop` | 0.0 | 3 | 153.2114 | `2` / 67.25% | 0.4155 |
| `cracked-star-jar` | 0.0 | 3 | 226.0568 | `7` / 46.15% | 0.4777 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 1 (33.33%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 95.1989 | `mid_60_to_180` | `player_health_depleted` | 4 | 142 | 120.03 |
| 63101 | 24.4666 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.6299 |
| 63102 | 249.1242 | `late_180_to_300` | `player_health_depleted` | 8 | 651 | 120.1736 |

### `caramel-workshop`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 213.35 | `late_180_to_300` | `player_health_depleted` | 8 | 324 | 120.477 |
| 63101 | 27.9333 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.5166 |
| 63102 | 218.351 | `late_180_to_300` | `player_health_depleted` | 7 | 353 | 120.58 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 270.6555 | `late_180_to_300` | `player_health_depleted` | 10 | 634 | 120.0869 |
| 63101 | 112.4986 | `mid_60_to_180` | `player_health_depleted` | 4 | 146 | 120.0702 |
| 63102 | 295.0162 | `late_180_to_300` | `player_health_depleted` | 8 | 676 | 120.0303 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
