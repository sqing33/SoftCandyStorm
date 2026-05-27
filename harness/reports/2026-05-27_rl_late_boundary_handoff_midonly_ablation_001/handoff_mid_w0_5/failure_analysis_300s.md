# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-27_rl_late_boundary_handoff_midonly_ablation_001/handoff_mid_w0_5/high_pressure_300s_comparison.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 13
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 5 | 143.5903 | `3` / 38.21% | 0.7164 |
| `caramel-workshop` | 0.0 | 5 | 220.9716 | `3` / 35.87% | 0.7161 |
| `cracked-star-jar` | 0.4 | 3 | 165.2796 | `3` / 33.08% | 0.7655 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 2 (40.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (60.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 210.316 | `late_180_to_300` | `player_health_depleted` | 8 | 468 | 120.1069 |
| 62401 | 34.7998 | `opening_lt_60` | `player_health_depleted` | 2 | 30 | 120.3299 |
| 62402 | 225.5859 | `late_180_to_300` | `player_health_depleted` | 9 | 549 | 120.1702 |
| 62403 | 212.6831 | `late_180_to_300` | `player_health_depleted` | 8 | 497 | 120.4636 |
| 62404 | 34.5665 | `opening_lt_60` | `player_health_depleted` | 2 | 32 | 120.3901 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 5 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 220.1514 | `late_180_to_300` | `player_health_depleted` | 8 | 336 | 120.3866 |
| 62401 | 225.2192 | `late_180_to_300` | `player_health_depleted` | 8 | 345 | 120.19 |
| 62402 | 213.1832 | `late_180_to_300` | `player_health_depleted` | 8 | 324 | 120.5302 |
| 62403 | 219.9513 | `late_180_to_300` | `player_health_depleted` | 8 | 351 | 120.9368 |
| 62404 | 226.3527 | `late_180_to_300` | `player_health_depleted` | 4 | 343 | 120.9032 |

### `cracked-star-jar`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 237.1217 | `late_180_to_300` | `player_health_depleted` | 8 | 521 | 120.2101 |
| 62401 | 217.4175 | `late_180_to_300` | `player_health_depleted` | 9 | 430 | 120.34 |
| 62403 | 41.2997 | `opening_lt_60` | `player_health_depleted` | 2 | 39 | 120.59 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
