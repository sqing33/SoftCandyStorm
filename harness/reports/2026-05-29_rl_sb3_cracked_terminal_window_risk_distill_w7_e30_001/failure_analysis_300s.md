# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-29_rl_sb3_cracked_terminal_window_risk_distill_w7_e30_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 93.0391 | `7` / 30.34% | 0.7479 |
| `caramel-workshop` | 0.0 | 3 | 156.0009 | `5` / 36.72% | 0.6885 |
| `cracked-star-jar` | 0.0 | 3 | 222.0185 | `5` / 43.00% | 0.7447 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 2 (66.67%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 1 (33.33%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 36.8664 | `opening_lt_60` | `player_health_depleted` | 3 | 44 | 120.0699 |
| 63101 | 24.4666 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.6299 |
| 63102 | 217.7842 | `late_180_to_300` | `player_health_depleted` | 7 | 467 | 120.2937 |

### `caramel-workshop`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 214.4835 | `late_180_to_300` | `player_health_depleted` | 6 | 328 | 120.8634 |
| 63101 | 27.9333 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.5166 |
| 63102 | 225.5859 | `late_180_to_300` | `player_health_depleted` | 4 | 344 | 120.1531 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 222.6519 | `late_180_to_300` | `player_health_depleted` | 8 | 508 | 120.2335 |
| 63101 | 217.9176 | `late_180_to_300` | `player_health_depleted` | 9 | 488 | 120.2437 |
| 63102 | 225.4859 | `late_180_to_300` | `player_health_depleted` | 7 | 492 | 120.2102 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
