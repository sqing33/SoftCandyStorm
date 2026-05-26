# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-27_rl_curriculum_stage01_corner_reward_retrain_20k_001/comparison_60s_10seed.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `60.0` seconds
- Total failures: 14
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.1 | 9 | 30.4406 | `8` / 86.19% | 0.2577 |
| `caramel-workshop` | 0.8 | 2 | 31.7332 | `8` / 82.32% | 0.3161 |
| `cracked-star-jar` | 0.7 | 3 | 33.7998 | `8` / 73.46% | 0.4093 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 9 (100.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 30.7999 | `opening_lt_60` | `player_health_depleted` | 2 | 36 | 120.19 |
| 62401 | 32.7665 | `opening_lt_60` | `player_health_depleted` | 2 | 32 | 120.3501 |
| 62402 | 27.9999 | `opening_lt_60` | `player_health_depleted` | 1 | 21 | 120.4801 |
| 62403 | 25.6666 | `opening_lt_60` | `player_health_depleted` | 2 | 23 | 120.34 |
| 62404 | 30.6665 | `opening_lt_60` | `player_health_depleted` | 2 | 30 | 119.9999 |
| 62405 | 34.7331 | `opening_lt_60` | `player_health_depleted` | 2 | 34 | 120.3799 |
| 62407 | 32.6332 | `opening_lt_60` | `player_health_depleted` | 2 | 31 | 120.0399 |
| 62408 | 27.5333 | `opening_lt_60` | `player_health_depleted` | 1 | 25 | 120.68 |
| 62409 | 31.1665 | `opening_lt_60` | `player_health_depleted` | 2 | 28 | 120.4667 |

### `caramel-workshop`

- `opening_lt_60`: 2 (100.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62402 | 32.0332 | `opening_lt_60` | `player_health_depleted` | 2 | 21 | 120.1334 |
| 62404 | 31.4332 | `opening_lt_60` | `player_health_depleted` | 1 | 18 | 120.0 |

### `cracked-star-jar`

- `opening_lt_60`: 3 (100.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62402 | 33.0998 | `opening_lt_60` | `player_health_depleted` | 2 | 26 | 120.4501 |
| 62405 | 37.2331 | `opening_lt_60` | `player_health_depleted` | 2 | 38 | 120.1134 |
| 62408 | 31.0665 | `opening_lt_60` | `player_health_depleted` | 2 | 33 | 120.2499 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
