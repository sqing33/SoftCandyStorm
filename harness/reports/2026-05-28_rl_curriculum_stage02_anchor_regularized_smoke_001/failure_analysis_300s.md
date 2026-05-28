# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_anchor_regularized_smoke_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 8
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 168.2359 | `7` / 33.51% | 0.6392 |
| `caramel-workshop` | 0.0 | 3 | 154.0894 | `3` / 30.03% | 0.7058 |
| `cracked-star-jar` | 0.3333 | 2 | 152.4744 | `3` / 29.18% | 0.7582 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 216.3173 | `late_180_to_300` | `player_health_depleted` | 9 | 534 | 120.2501 |
| 63101 | 24.4666 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.6299 |
| 63102 | 263.9238 | `late_180_to_300` | `player_health_depleted` | 9 | 785 | 120.1068 |

### `caramel-workshop`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 213.0832 | `late_180_to_300` | `player_health_depleted` | 7 | 337 | 120.977 |
| 63101 | 27.9333 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.5166 |
| 63102 | 221.2516 | `late_180_to_300` | `player_health_depleted` | 6 | 348 | 120.3798 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (50.00%)
- `late_180_to_300`: 1 (50.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 212.4164 | `late_180_to_300` | `player_health_depleted` | 7 | 448 | 120.5801 |
| 63101 | 92.5323 | `mid_60_to_180` | `player_health_depleted` | 3 | 110 | 120.1102 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
