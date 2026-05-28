# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_closed_loop_no_regression_probe_001/comparison_180s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_watch`
- Duration: `180.0` seconds
- Total failures: 4
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.3333 | 2 | 59.8327 | `2` / 38.50% | 0.4971 |
| `caramel-workshop` | 0.6667 | 1 | 27.9333 | `2` / 63.78% | 0.4247 |
| `cracked-star-jar` | 0.6667 | 1 | 112.4653 | `7` / 47.53% | 0.4614 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 1 (50.00%)
- `mid_60_to_180`: 1 (50.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 95.1989 | `mid_60_to_180` | `player_health_depleted` | 4 | 142 | 120.03 |
| 63101 | 24.4666 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.6299 |

### `caramel-workshop`

- `opening_lt_60`: 1 (100.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63101 | 27.9333 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.5166 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (100.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63101 | 112.4653 | `mid_60_to_180` | `player_health_depleted` | 4 | 144 | 120.0468 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
