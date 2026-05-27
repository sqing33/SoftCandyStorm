# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-27_rl_late_route_recovery_reward_profile_smoke_001/comparison_180s_3seed.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `180.0` seconds
- Total failures: 6
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.3333 | 2 | 62.9827 | `7` / 44.67% | 0.4795 |
| `caramel-workshop` | 0.6667 | 1 | 102.6654 | `4` / 55.33% | 0.5218 |
| `cracked-star-jar` | 0.0 | 3 | 71.5437 | `4` / 47.17% | 0.426 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 1 (50.00%)
- `mid_60_to_180`: 1 (50.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62300 | 58.4661 | `opening_lt_60` | `player_health_depleted` | 2 | 53 | 120.08 |
| 62302 | 67.4993 | `mid_60_to_180` | `player_health_depleted` | 2 | 57 | 120.1 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (100.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62302 | 102.6654 | `mid_60_to_180` | `player_health_depleted` | 4 | 81 | 120.3833 |

### `cracked-star-jar`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 2 (66.67%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62300 | 50.9329 | `opening_lt_60` | `player_health_depleted` | 2 | 43 | 120.4001 |
| 62301 | 66.566 | `mid_60_to_180` | `player_health_depleted` | 3 | 79 | 120.0137 |
| 62302 | 97.1322 | `mid_60_to_180` | `player_health_depleted` | 4 | 87 | 120.2167 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
