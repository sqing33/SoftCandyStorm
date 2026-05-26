# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-27_rl_curriculum_time_bucket_stage01_retry_20k_001/comparison_60s_10seed.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_not_balance_gate`
- Duration: `60.0` seconds
- Total failures: 2
- Repair maps: `soda-creek`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.8 | 2 | 37.5164 | `7` / 41.23% | 0.5027 |
| `caramel-workshop` | 1.0 | 0 | None | `7` / 43.40% | 0.5096 |
| `cracked-star-jar` | 1.0 | 0 | None | `7` / 46.41% | 0.5134 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 2 (100.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62406 | 46.1996 | `opening_lt_60` | `player_health_depleted` | 1 | 38 | 120.26 |
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
