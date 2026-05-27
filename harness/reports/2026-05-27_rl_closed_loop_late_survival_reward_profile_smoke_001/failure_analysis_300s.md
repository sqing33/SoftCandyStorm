# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-27_rl_closed_loop_late_survival_reward_profile_smoke_001/comparison_300s_3seed.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 155.9 | `4` / 45.63% | 0.5373 |
| `caramel-workshop` | 0.0 | 3 | 213.4611 | `3` / 65.65% | 0.4252 |
| `cracked-star-jar` | 0.0 | 3 | 209.827 | `4` / 39.37% | 0.5346 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62300 | 216.584 | `late_180_to_300` | `player_health_depleted` | 8 | 537 | 120.6569 |
| 62301 | 39.6997 | `opening_lt_60` | `player_health_depleted` | 2 | 33 | 120.0065 |
| 62302 | 211.4162 | `late_180_to_300` | `player_health_depleted` | 7 | 445 | 120.5401 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62300 | 212.2831 | `late_180_to_300` | `player_health_depleted` | 6 | 322 | 120.6332 |
| 62301 | 216.584 | `late_180_to_300` | `player_health_depleted` | 6 | 334 | 121.0134 |
| 62302 | 211.5162 | `late_180_to_300` | `player_health_depleted` | 7 | 338 | 120.0238 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62300 | 211.3162 | `late_180_to_300` | `player_health_depleted` | 7 | 446 | 120.6202 |
| 62301 | 197.78 | `late_180_to_300` | `player_health_depleted` | 7 | 423 | 120.0737 |
| 62302 | 220.3848 | `late_180_to_300` | `player_health_depleted` | 9 | 456 | 122.0903 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
