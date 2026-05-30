# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-30_rl_current_high_pressure_stage01_seed_replay_probe_001/comparison_60s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_not_balance_gate`
- Duration: `60.0` seconds
- Total failures: 1
- Repair maps: `soda-creek`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.6667 | 1 | 37.2664 | `7` / 43.83% | 0.6176 |
| `caramel-workshop` | 1.0 | 0 | None | `7` / 53.25% | 0.634 |
| `cracked-star-jar` | 1.0 | 0 | None | `7` / 38.46% | 0.6845 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 1 (100.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63402 | 37.2664 | `opening_lt_60` | `player_health_depleted` | 1 | 33 | 120.5999 |

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
