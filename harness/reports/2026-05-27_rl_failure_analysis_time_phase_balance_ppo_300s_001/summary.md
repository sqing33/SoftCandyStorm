# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-27_rl_ppo_time_phase_balance_closed_loop_10k_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 8
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 91.3941 | `7` / 39.03% | 0.6456 |
| `caramel-workshop` | 0.0 | 3 | 180.7884 | `3` / 67.40% | 0.4196 |
| `cracked-star-jar` | 0.3333 | 2 | 118.2581 | `1` / 31.01% | 0.6419 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 2 (66.67%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 1 (33.33%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 61600 | 209.3158 | `late_180_to_300` | `player_health_depleted` | 8 | 477 | 120.1271 |
| 61601 | 41.5664 | `opening_lt_60` | `player_health_depleted` | 2 | 43 | 120.0032 |
| 61602 | 23.3 | `opening_lt_60` | `player_health_depleted` | 1 | 20 | 120.66 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 61600 | 214.917 | `late_180_to_300` | `player_health_depleted` | 7 | 328 | 120.9301 |
| 61601 | 211.4162 | `late_180_to_300` | `player_health_depleted` | 6 | 323 | 121.1067 |
| 61602 | 116.0319 | `mid_60_to_180` | `player_health_depleted` | 4 | 116 | 120.0165 |

### `cracked-star-jar`

- `opening_lt_60`: 1 (50.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 1 (50.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 61601 | 211.8496 | `late_180_to_300` | `player_health_depleted` | 7 | 440 | 120.8032 |
| 61602 | 24.6666 | `opening_lt_60` | `player_health_depleted` | 1 | 20 | 120.0334 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
