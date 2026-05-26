# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-27_rl_curriculum_stage01_corner_reward_directional_smoke_001/comparison_60s_10seed.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_not_balance_gate`
- Duration: `60.0` seconds
- Total failures: 4
- Repair maps: `soda-creek`, `caramel-workshop`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.7 | 3 | 34.5887 | `2` / 50.65% | 0.3565 |
| `caramel-workshop` | 0.9 | 1 | 33.2332 | `2` / 62.07% | 0.35 |
| `cracked-star-jar` | 1.0 | 0 | None | `2` / 55.81% | 0.3241 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 3 (100.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 24.5666 | `opening_lt_60` | `player_health_depleted` | 2 | 21 | 121.0533 |
| 62407 | 50.0996 | `opening_lt_60` | `player_health_depleted` | 2 | 50 | 120.4001 |
| 62408 | 29.0999 | `opening_lt_60` | `player_health_depleted` | 1 | 25 | 120.6466 |

### `caramel-workshop`

- `opening_lt_60`: 1 (100.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62408 | 33.2332 | `opening_lt_60` | `player_health_depleted` | 2 | 20 | 120.0665 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
