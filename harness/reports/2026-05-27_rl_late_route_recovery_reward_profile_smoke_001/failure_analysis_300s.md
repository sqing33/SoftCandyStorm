# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-27_rl_late_route_recovery_reward_profile_smoke_001/comparison_300s_3seed.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 113.9497 | `4` / 42.78% | 0.5034 |
| `caramel-workshop` | 0.0 | 3 | 176.7107 | `4` / 50.91% | 0.5448 |
| `cracked-star-jar` | 0.0 | 3 | 71.5437 | `4` / 47.17% | 0.426 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 1 (33.33%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62300 | 58.4661 | `opening_lt_60` | `player_health_depleted` | 2 | 53 | 120.08 |
| 62301 | 215.8838 | `late_180_to_300` | `player_health_depleted` | 9 | 523 | 120.5336 |
| 62302 | 67.4993 | `mid_60_to_180` | `player_health_depleted` | 2 | 57 | 120.1 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62300 | 213.3166 | `late_180_to_300` | `player_health_depleted` | 8 | 329 | 120.4035 |
| 62301 | 214.1501 | `late_180_to_300` | `player_health_depleted` | 7 | 330 | 120.5168 |
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
