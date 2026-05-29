# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-29_rl_terminal_conversion_branch_probe_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 149.3442 | `5` / 24.86% | 0.8128 |
| `caramel-workshop` | 0.0 | 3 | 151.8889 | `5` / 43.95% | 0.7323 |
| `cracked-star-jar` | 0.0 | 3 | 170.5025 | `5` / 37.66% | 0.7231 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 210.5827 | `late_180_to_300` | `player_health_depleted` | 6 | 494 | 120.02 |
| 63101 | 24.4666 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.6299 |
| 63102 | 212.9832 | `late_180_to_300` | `player_health_depleted` | 7 | 470 | 120.5504 |

### `caramel-workshop`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 214.6502 | `late_180_to_300` | `player_health_depleted` | 6 | 334 | 120.0402 |
| 63101 | 27.9333 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.5166 |
| 63102 | 213.0832 | `late_180_to_300` | `player_health_depleted` | 5 | 325 | 120.3835 |

### `cracked-star-jar`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 47.4996 | `opening_lt_60` | `player_health_depleted` | 2 | 51 | 120.4767 |
| 63101 | 224.9858 | `late_180_to_300` | `player_health_depleted` | 7 | 495 | 120.2903 |
| 63102 | 239.0221 | `late_180_to_300` | `player_health_depleted` | 8 | 573 | 120.0666 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
