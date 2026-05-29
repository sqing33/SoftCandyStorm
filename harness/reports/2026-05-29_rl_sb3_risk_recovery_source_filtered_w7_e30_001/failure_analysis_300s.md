# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-29_rl_sb3_risk_recovery_source_filtered_w7_e30_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 122.2834 | `5` / 26.80% | 0.7275 |
| `caramel-workshop` | 0.0 | 3 | 155.7675 | `5` / 32.35% | 0.7837 |
| `cracked-star-jar` | 0.0 | 3 | 217.662 | `5` / 39.45% | 0.7614 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 1 (33.33%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 120.8985 | `mid_60_to_180` | `player_health_depleted` | 4 | 207 | 120.04 |
| 63101 | 24.4666 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.6299 |
| 63102 | 221.485 | `late_180_to_300` | `player_health_depleted` | 7 | 546 | 120.9967 |

### `caramel-workshop`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 219.1845 | `late_180_to_300` | `player_health_depleted` | 7 | 340 | 120.5168 |
| 63101 | 27.9333 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.5166 |
| 63102 | 220.1847 | `late_180_to_300` | `player_health_depleted` | 7 | 339 | 120.41 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 224.0189 | `late_180_to_300` | `player_health_depleted` | 7 | 487 | 120.1767 |
| 63101 | 183.8103 | `late_180_to_300` | `player_health_depleted` | 7 | 366 | 120.0001 |
| 63102 | 245.1567 | `late_180_to_300` | `player_health_depleted` | 7 | 558 | 120.0761 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
