# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_phase_specific_anchor_smoke_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 154.8565 | `5` / 39.29% | 0.7009 |
| `caramel-workshop` | 0.0 | 3 | 151.9556 | `7` / 43.15% | 0.5671 |
| `cracked-star-jar` | 0.0 | 3 | 192.6582 | `7` / 46.56% | 0.6719 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 212.1164 | `late_180_to_300` | `player_health_depleted` | 6 | 514 | 120.2901 |
| 63101 | 24.4666 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.6299 |
| 63102 | 227.9864 | `late_180_to_300` | `player_health_depleted` | 8 | 558 | 120.4435 |

### `caramel-workshop`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 213.8167 | `late_180_to_300` | `player_health_depleted` | 8 | 323 | 120.8069 |
| 63101 | 27.9333 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.5166 |
| 63102 | 214.1168 | `late_180_to_300` | `player_health_depleted` | 7 | 323 | 121.42 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 263.6572 | `late_180_to_300` | `player_health_depleted` | 8 | 617 | 120.3299 |
| 63101 | 92.5323 | `mid_60_to_180` | `player_health_depleted` | 3 | 110 | 120.1102 |
| 63102 | 221.7851 | `late_180_to_300` | `player_health_depleted` | 7 | 465 | 120.0571 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
