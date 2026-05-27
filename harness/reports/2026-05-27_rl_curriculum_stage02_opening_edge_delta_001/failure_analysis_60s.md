# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-27_rl_curriculum_stage02_opening_edge_delta_001/comparison_60s_10seed.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_not_balance_gate`
- Duration: `60.0` seconds
- Total failures: 5
- Repair maps: `soda-creek`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.5 | 5 | 32.5265 | `4` / 56.89% | 0.4325 |
| `caramel-workshop` | 1.0 | 0 | None | `7` / 43.92% | 0.4702 |
| `cracked-star-jar` | 1.0 | 0 | None | `4` / 43.44% | 0.4954 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 5 (100.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 24.0 | `opening_lt_60` | `player_health_depleted` | 2 | 19 | 120.3201 |
| 62401 | 33.7332 | `opening_lt_60` | `player_health_depleted` | 1 | 27 | 120.42 |
| 62403 | 24.5 | `opening_lt_60` | `player_health_depleted` | 2 | 22 | 120.7999 |
| 62405 | 51.5662 | `opening_lt_60` | `player_health_depleted` | 3 | 58 | 120.0302 |
| 62409 | 28.8332 | `opening_lt_60` | `player_health_depleted` | 1 | 25 | 120.1198 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
