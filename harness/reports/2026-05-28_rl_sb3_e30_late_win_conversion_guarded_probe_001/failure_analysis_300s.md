# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_sb3_e30_late_win_conversion_guarded_probe_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 8
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 157.5437 | `5` / 44.77% | 0.7458 |
| `caramel-workshop` | 0.0 | 3 | 156.2343 | `5` / 49.57% | 0.6791 |
| `cracked-star-jar` | 0.3333 | 2 | 240.6891 | `5` / 29.64% | 0.799 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 1 (33.33%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 177.3423 | `mid_60_to_180` | `player_health_depleted` | 4 | 380 | 120.0201 |
| 63101 | 24.4666 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.6299 |
| 63102 | 270.8221 | `late_180_to_300` | `player_health_depleted` | 10 | 794 | 120.4669 |

### `caramel-workshop`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 226.3527 | `late_180_to_300` | `player_health_depleted` | 9 | 359 | 120.1498 |
| 63101 | 27.9333 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.5166 |
| 63102 | 214.4168 | `late_180_to_300` | `player_health_depleted` | 7 | 324 | 120.31 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 249.4243 | `late_180_to_300` | `player_health_depleted` | 8 | 570 | 120.6597 |
| 63101 | 231.9539 | `late_180_to_300` | `player_health_depleted` | 8 | 530 | 120.0834 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
