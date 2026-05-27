# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-27_rl_route_recovery_reward_profile_smoke_001/comparison_300s_3seed.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 95.7056 | `4` / 48.74% | 0.515 |
| `caramel-workshop` | 0.0 | 3 | 84.0546 | `4` / 50.59% | 0.5135 |
| `cracked-star-jar` | 0.0 | 3 | 138.0804 | `4` / 45.99% | 0.4474 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 2 (66.67%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 1 (33.33%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62300 | 215.5838 | `late_180_to_300` | `player_health_depleted` | 7 | 529 | 120.1867 |
| 62301 | 29.0332 | `opening_lt_60` | `player_health_depleted` | 1 | 24 | 120.4532 |
| 62302 | 42.4997 | `opening_lt_60` | `player_health_depleted` | 2 | 36 | 120.1398 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 3 (100.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62300 | 95.5656 | `mid_60_to_180` | `player_health_depleted` | 3 | 81 | 120.1332 |
| 62301 | 87.8657 | `mid_60_to_180` | `player_health_depleted` | 3 | 53 | 120.1334 |
| 62302 | 68.7326 | `mid_60_to_180` | `player_health_depleted` | 2 | 45 | 120.0336 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 2 (66.67%)
- `late_180_to_300`: 1 (33.33%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62300 | 185.3773 | `late_180_to_300` | `player_health_depleted` | 7 | 366 | 120.1969 |
| 62301 | 103.9321 | `mid_60_to_180` | `player_health_depleted` | 4 | 132 | 120.0404 |
| 62302 | 124.9318 | `mid_60_to_180` | `player_health_depleted` | 5 | 165 | 120.1971 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
