# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-29_rl_sb3_terminal_victory_multimap_path_target_w1_e30_001/comparison_parent_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 155.5233 | `1` / 34.68% | 0.736 |
| `caramel-workshop` | 0.0 | 3 | 158.4236 | `5` / 24.49% | 0.7801 |
| `cracked-star-jar` | 0.0 | 3 | 185.0253 | `5` / 33.72% | 0.7954 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 225.4859 | `late_180_to_300` | `player_health_depleted` | 8 | 570 | 120.3466 |
| 63101 | 24.4666 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.6299 |
| 63102 | 216.6173 | `late_180_to_300` | `player_health_depleted` | 7 | 525 | 120.6903 |

### `caramel-workshop`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 221.385 | `late_180_to_300` | `player_health_depleted` | 6 | 344 | 120.4899 |
| 63101 | 27.9333 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.5166 |
| 63102 | 225.9526 | `late_180_to_300` | `player_health_depleted` | 7 | 355 | 120.5165 |

### `cracked-star-jar`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 56.8661 | `opening_lt_60` | `player_health_depleted` | 2 | 59 | 120.7099 |
| 63101 | 230.5203 | `late_180_to_300` | `player_health_depleted` | 8 | 495 | 120.6871 |
| 63102 | 267.6895 | `late_180_to_300` | `player_health_depleted` | 9 | 604 | 120.7302 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
