# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-30_rl_edge_branch_late_filter_high_pressure_001/chain_comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 5
- Repair maps: `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 1.0 | 0 | None | `7` / 24.49% | 0.8465 |
| `caramel-workshop` | 0.0 | 3 | 163.3014 | `7` / 28.65% | 0.8272 |
| `cracked-star-jar` | 0.3333 | 2 | 284.6021 | `7` / 22.12% | 0.8879 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

### `caramel-workshop`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63400 | 213.2166 | `late_180_to_300` | `player_health_depleted` | 7 | 320 | 120.4665 |
| 63401 | 235.3546 | `late_180_to_300` | `player_health_depleted` | 9 | 374 | 120.4667 |
| 63402 | 41.333 | `opening_lt_60` | `player_health_depleted` | 1 | 25 | 121.0002 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63400 | 293.5499 | `late_180_to_300` | `player_health_depleted` | 11 | 716 | 120.9233 |
| 63402 | 275.6543 | `late_180_to_300` | `player_health_depleted` | 10 | 649 | 120.0467 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
