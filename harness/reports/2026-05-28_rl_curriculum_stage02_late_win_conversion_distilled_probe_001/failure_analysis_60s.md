# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_late_win_conversion_distilled_probe_001/comparison_60s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_watch`
- Duration: `60.0` seconds
- Total failures: 2
- Repair maps: `soda-creek`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.3333 | 2 | 36.3165 | `1` / 63.97% | 0.4111 |
| `caramel-workshop` | 1.0 | 0 | None | `1` / 57.21% | 0.5891 |
| `cracked-star-jar` | 1.0 | 0 | None | `1` / 56.38% | 0.5844 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 2 (100.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 42.833 | `opening_lt_60` | `player_health_depleted` | 2 | 46 | 120.21 |
| 63101 | 29.7999 | `opening_lt_60` | `player_health_depleted` | 1 | 24 | 120.3101 |

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
