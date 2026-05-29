# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-29_rl_sb3_e30_map_late_split_180s_probe_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 152.2781 | `1` / 35.42% | 0.7432 |
| `caramel-workshop` | 0.0 | 3 | 158.4236 | `5` / 24.49% | 0.7801 |
| `cracked-star-jar` | 0.0 | 3 | 175.2583 | `5` / 24.56% | 0.8187 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 215.7505 | `late_180_to_300` | `player_health_depleted` | 7 | 537 | 120.03 |
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
| 63102 | 238.3886 | `late_180_to_300` | `player_health_depleted` | 11 | 521 | 120.0101 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
