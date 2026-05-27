# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-27_rl_curriculum_stage02_low_lr_short_001/comparison_60s_10seed.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_not_balance_gate`
- Duration: `60.0` seconds
- Total failures: 2
- Repair maps: `soda-creek`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.8 | 2 | 37.3331 | `7` / 44.91% | 0.4691 |
| `caramel-workshop` | 1.0 | 0 | None | `2` / 47.07% | 0.5072 |
| `cracked-star-jar` | 1.0 | 0 | None | `2` / 49.38% | 0.4437 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 2 (100.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 24.5666 | `opening_lt_60` | `player_health_depleted` | 2 | 21 | 121.0533 |
| 62407 | 50.0996 | `opening_lt_60` | `player_health_depleted` | 2 | 50 | 120.4001 |

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
