# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-27_rl_behavior_clone_late_survival_clean_teacher_no_phase_staged_gru_context8_001/comparison_300s_3seed.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 162.8904 | `3` / 31.65% | 0.7933 |
| `caramel-workshop` | 0.0 | 3 | 218.0843 | `3` / 31.34% | 0.8218 |
| `cracked-star-jar` | 0.0 | 3 | 129.9734 | `8` / 25.11% | 0.8267 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62300 | 233.7543 | `late_180_to_300` | `player_health_depleted` | 7 | 581 | 120.0134 |
| 62301 | 39.0997 | `opening_lt_60` | `player_health_depleted` | 2 | 40 | 120.5599 |
| 62302 | 215.8171 | `late_180_to_300` | `player_health_depleted` | 8 | 467 | 121.0402 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62300 | 219.4179 | `late_180_to_300` | `player_health_depleted` | 6 | 339 | 120.0467 |
| 62301 | 214.2501 | `late_180_to_300` | `player_health_depleted` | 7 | 324 | 120.0968 |
| 62302 | 220.5848 | `late_180_to_300` | `player_health_depleted` | 8 | 342 | 120.6134 |

### `cracked-star-jar`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 1 (33.33%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62300 | 133.6329 | `mid_60_to_180` | `player_health_depleted` | 6 | 244 | 120.1005 |
| 62301 | 23.9 | `opening_lt_60` | `player_health_depleted` | 1 | 19 | 120.6065 |
| 62302 | 232.3873 | `late_180_to_300` | `player_health_depleted` | 9 | 517 | 120.2331 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
