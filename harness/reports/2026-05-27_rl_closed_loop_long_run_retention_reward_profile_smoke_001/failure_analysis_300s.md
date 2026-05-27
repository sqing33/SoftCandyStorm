# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-27_rl_closed_loop_long_run_retention_reward_profile_smoke_001/comparison_300s_3seed.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 110.616 | `4` / 52.56% | 0.4912 |
| `caramel-workshop` | 0.0 | 3 | 152.6998 | `4` / 53.09% | 0.5066 |
| `cracked-star-jar` | 0.0 | 3 | 210.5605 | `4` / 51.26% | 0.4647 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 1 (33.33%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62300 | 210.1826 | `late_180_to_300` | `player_health_depleted` | 7 | 496 | 120.2769 |
| 62301 | 62.8327 | `mid_60_to_180` | `player_health_depleted` | 2 | 67 | 120.2601 |
| 62302 | 58.8328 | `opening_lt_60` | `player_health_depleted` | 2 | 59 | 120.0901 |

### `caramel-workshop`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62300 | 33.2332 | `opening_lt_60` | `player_health_depleted` | 2 | 22 | 120.0333 |
| 62301 | 214.1501 | `late_180_to_300` | `player_health_depleted` | 7 | 331 | 120.0669 |
| 62302 | 210.716 | `late_180_to_300` | `player_health_depleted` | 7 | 327 | 120.23 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62300 | 193.9125 | `late_180_to_300` | `player_health_depleted` | 7 | 426 | 120.0571 |
| 62301 | 215.4837 | `late_180_to_300` | `player_health_depleted` | 8 | 462 | 120.367 |
| 62302 | 222.2852 | `late_180_to_300` | `player_health_depleted` | 9 | 474 | 120.6802 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
