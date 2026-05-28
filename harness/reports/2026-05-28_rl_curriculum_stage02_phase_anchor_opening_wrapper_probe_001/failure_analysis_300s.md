# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_phase_anchor_opening_wrapper_probe_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 153.8861 | `7` / 36.37% | 0.6612 |
| `caramel-workshop` | 0.0 | 3 | 153.5671 | `7` / 36.20% | 0.6394 |
| `cracked-star-jar` | 0.0 | 3 | 190.101 | `7` / 36.82% | 0.7547 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 2 (66.67%)
- `late_180_to_300`: 1 (33.33%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 163.5393 | `mid_60_to_180` | `player_health_depleted` | 5 | 339 | 120.1234 |
| 63101 | 70.1326 | `mid_60_to_180` | `player_health_depleted` | 2 | 69 | 120.1001 |
| 63102 | 227.9864 | `late_180_to_300` | `player_health_depleted` | 8 | 558 | 120.4435 |

### `caramel-workshop`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 218.6511 | `late_180_to_300` | `player_health_depleted` | 6 | 339 | 120.9302 |
| 63101 | 27.9333 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.5166 |
| 63102 | 214.1168 | `late_180_to_300` | `player_health_depleted` | 7 | 323 | 121.42 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 230.8537 | `late_180_to_300` | `player_health_depleted` | 9 | 525 | 120.9367 |
| 63101 | 121.4985 | `mid_60_to_180` | `player_health_depleted` | 4 | 183 | 120.1768 |
| 63102 | 217.9509 | `late_180_to_300` | `player_health_depleted` | 8 | 492 | 120.5672 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
