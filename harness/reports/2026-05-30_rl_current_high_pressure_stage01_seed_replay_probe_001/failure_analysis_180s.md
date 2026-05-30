# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-30_rl_current_high_pressure_stage01_seed_replay_probe_001/comparison_180s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_watch`
- Duration: `180.0` seconds
- Total failures: 2
- Repair maps: `soda-creek`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.3333 | 2 | 91.6509 | `5` / 27.98% | 0.8372 |
| `caramel-workshop` | 1.0 | 0 | None | `5` / 41.25% | 0.7555 |
| `cracked-star-jar` | 1.0 | 0 | None | `7` / 27.13% | 0.8109 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 1 (50.00%)
- `mid_60_to_180`: 1 (50.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63401 | 145.7688 | `mid_60_to_180` | `player_health_depleted` | 5 | 277 | 120.1336 |
| 63402 | 37.5331 | `opening_lt_60` | `player_health_depleted` | 1 | 34 | 120.5832 |

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
