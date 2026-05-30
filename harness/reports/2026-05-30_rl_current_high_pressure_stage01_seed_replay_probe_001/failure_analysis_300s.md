# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-30_rl_current_high_pressure_stage01_seed_replay_probe_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 171.9807 | `5` / 37.88% | 0.7624 |
| `caramel-workshop` | 0.0 | 3 | 157.4668 | `3` / 51.67% | 0.6682 |
| `cracked-star-jar` | 0.0 | 3 | 222.7297 | `1` / 28.06% | 0.8205 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63400 | 260.4913 | `late_180_to_300` | `player_health_depleted` | 9 | 692 | 120.1301 |
| 63401 | 217.8509 | `late_180_to_300` | `player_health_depleted` | 9 | 533 | 120.0502 |
| 63402 | 37.5998 | `opening_lt_60` | `player_health_depleted` | 1 | 34 | 120.3666 |

### `caramel-workshop`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63400 | 210.2826 | `late_180_to_300` | `player_health_depleted` | 3 | 320 | 120.3165 |
| 63401 | 219.5513 | `late_180_to_300` | `player_health_depleted` | 6 | 338 | 120.1535 |
| 63402 | 42.5664 | `opening_lt_60` | `player_health_depleted` | 1 | 27 | 120.2167 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63400 | 225.3192 | `late_180_to_300` | `player_health_depleted` | 9 | 488 | 120.0005 |
| 63401 | 226.7861 | `late_180_to_300` | `player_health_depleted` | 8 | 533 | 120.0998 |
| 63402 | 216.0839 | `late_180_to_300` | `player_health_depleted` | 7 | 427 | 120.567 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
