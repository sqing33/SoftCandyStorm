# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-29_rl_current_high_pressure_smoke_001/comparison_180s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_watch`
- Duration: `180.0` seconds
- Total failures: 3
- Repair maps: `soda-creek`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.3333 | 2 | 84.2324 | `5` / 39.39% | 0.7468 |
| `caramel-workshop` | 1.0 | 0 | None | `5` / 28.44% | 0.8126 |
| `cracked-star-jar` | 0.6667 | 1 | 77.3325 | `5` / 52.45% | 0.6834 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 1 (50.00%)
- `mid_60_to_180`: 1 (50.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63200 | 48.9996 | `opening_lt_60` | `player_health_depleted` | 1 | 41 | 120.1202 |
| 63202 | 119.4652 | `mid_60_to_180` | `player_health_depleted` | 3 | 181 | 120.1169 |

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
| 63200 | 77.3325 | `mid_60_to_180` | `player_health_depleted` | 2 | 75 | 120.2732 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
