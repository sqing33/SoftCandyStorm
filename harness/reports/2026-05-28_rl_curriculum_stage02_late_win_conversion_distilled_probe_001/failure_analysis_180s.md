# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_late_win_conversion_distilled_probe_001/comparison_180s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `180.0` seconds
- Total failures: 3
- Repair maps: `soda-creek`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 69.222 | `1` / 58.06% | 0.5146 |
| `caramel-workshop` | 1.0 | 0 | None | `7` / 29.02% | 0.7471 |
| `cracked-star-jar` | 1.0 | 0 | None | `1` / 34.91% | 0.8118 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 2 (66.67%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 42.833 | `opening_lt_60` | `player_health_depleted` | 2 | 46 | 120.21 |
| 63101 | 29.7999 | `opening_lt_60` | `player_health_depleted` | 1 | 24 | 120.3101 |
| 63102 | 135.0332 | `mid_60_to_180` | `player_health_depleted` | 5 | 227 | 120.0334 |

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
