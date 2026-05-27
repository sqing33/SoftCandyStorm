# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-27_rl_behavior_clone_edge_aux_staged_opening_handoff_probe_001/comparison_180s_3seed.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_not_balance_gate`
- Duration: `180.0` seconds
- Total failures: 2
- Repair maps: `soda-creek`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.6667 | 1 | 171.2743 | `3` / 35.95% | 0.6922 |
| `caramel-workshop` | 1.0 | 0 | None | `3` / 34.82% | 0.7831 |
| `cracked-star-jar` | 0.6667 | 1 | 157.338 | `7` / 37.48% | 0.7789 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (100.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62201 | 171.2743 | `mid_60_to_180` | `player_health_depleted` | 6 | 347 | 120.0703 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (100.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62201 | 157.338 | `mid_60_to_180` | `player_health_depleted` | 6 | 266 | 120.2638 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
