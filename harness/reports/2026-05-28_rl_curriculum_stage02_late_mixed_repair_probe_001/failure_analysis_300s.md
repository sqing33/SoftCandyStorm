# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_late_mixed_repair_probe_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 57.8772 | `3` / 30.64% | 0.6863 |
| `caramel-workshop` | 0.0 | 3 | 221.1183 | `1` / 37.82% | 0.7679 |
| `cracked-star-jar` | 0.0 | 3 | 139.0177 | `1` / 57.16% | 0.5801 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 2 (66.67%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63000 | 28.3332 | `opening_lt_60` | `player_health_depleted` | 2 | 27 | 120.4067 |
| 63001 | 103.2654 | `mid_60_to_180` | `player_health_depleted` | 4 | 148 | 120.4204 |
| 63002 | 42.033 | `opening_lt_60` | `player_health_depleted` | 2 | 32 | 120.3432 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63000 | 231.4872 | `late_180_to_300` | `player_health_depleted` | 7 | 363 | 120.2166 |
| 63001 | 216.2506 | `late_180_to_300` | `player_health_depleted` | 7 | 332 | 120.7969 |
| 63002 | 215.6171 | `late_180_to_300` | `player_health_depleted` | 7 | 334 | 120.3967 |

### `cracked-star-jar`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 1 (33.33%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63000 | 142.9349 | `mid_60_to_180` | `player_health_depleted` | 6 | 236 | 120.0336 |
| 63001 | 51.6662 | `opening_lt_60` | `player_health_depleted` | 2 | 55 | 120.2866 |
| 63002 | 222.4519 | `late_180_to_300` | `player_health_depleted` | 7 | 450 | 120.2066 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
