# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_01_opening_lt_60/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 213.7723 | `7` / 56.89% | 0.4703 |
| `caramel-workshop` | 0.0 | 3 | 215.8505 | `7` / 38.57% | 0.6019 |
| `cracked-star-jar` | 0.0 | 3 | 235.5752 | `7` / 46.22% | 0.4869 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62700 | 238.5887 | `late_180_to_300` | `player_health_depleted` | 9 | 638 | 121.1499 |
| 62701 | 152.1702 | `mid_60_to_180` | `player_health_depleted` | 5 | 283 | 120.1338 |
| 62702 | 250.5579 | `late_180_to_300` | `player_health_depleted` | 10 | 733 | 120.4736 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62700 | 218.2843 | `late_180_to_300` | `player_health_depleted` | 6 | 334 | 121.1467 |
| 62701 | 217.4842 | `late_180_to_300` | `player_health_depleted` | 7 | 331 | 120.8433 |
| 62702 | 211.7829 | `late_180_to_300` | `player_health_depleted` | 6 | 316 | 120.1502 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62700 | 227.2529 | `late_180_to_300` | `player_health_depleted` | 8 | 491 | 120.4365 |
| 62701 | 267.0897 | `late_180_to_300` | `player_health_depleted` | 9 | 619 | 120.8937 |
| 62702 | 212.3831 | `late_180_to_300` | `player_health_depleted` | 8 | 432 | 120.6498 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
