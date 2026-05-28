# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_opening_aware_late_win_conversion_probe_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 145.0766 | `7` / 30.45% | 0.7315 |
| `caramel-workshop` | 0.0 | 3 | 157.1234 | `2` / 27.74% | 0.7301 |
| `cracked-star-jar` | 0.0 | 3 | 183.9131 | `5` / 29.32% | 0.7632 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 183.777 | `late_180_to_300` | `player_health_depleted` | 7 | 415 | 120.1368 |
| 63101 | 24.4666 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.6299 |
| 63102 | 226.9862 | `late_180_to_300` | `player_health_depleted` | 7 | 578 | 120.1499 |

### `caramel-workshop`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 217.3508 | `late_180_to_300` | `player_health_depleted` | 6 | 335 | 121.0534 |
| 63101 | 27.9333 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.5166 |
| 63102 | 226.086 | `late_180_to_300` | `player_health_depleted` | 8 | 359 | 120.0566 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 230.4203 | `late_180_to_300` | `player_health_depleted` | 10 | 551 | 120.0167 |
| 63101 | 92.5323 | `mid_60_to_180` | `player_health_depleted` | 3 | 110 | 120.1102 |
| 63102 | 228.7866 | `late_180_to_300` | `player_health_depleted` | 7 | 498 | 120.0734 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
