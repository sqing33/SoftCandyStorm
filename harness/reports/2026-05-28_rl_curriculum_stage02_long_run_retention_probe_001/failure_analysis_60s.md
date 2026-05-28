# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_long_run_retention_probe_001/comparison_60s.json`
- Decision: `rl_policy_failure_analysis_no_failures`
- Gate decision: `multimap_comparison_recorded_not_balance_gate`
- Duration: `60.0` seconds
- Total failures: 0
- Repair maps: None

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 1.0 | 0 | None | `7` / 37.46% | 0.4971 |
| `caramel-workshop` | 1.0 | 0 | None | `2` / 36.55% | 0.5205 |
| `cracked-star-jar` | 1.0 | 0 | None | `7` / 47.88% | 0.4733 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

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
