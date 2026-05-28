# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_soda_caramel_closed_loop_anchor_probe_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 138.3939 | `7` / 38.53% | 0.7125 |
| `caramel-workshop` | 0.0 | 3 | 155.1118 | `7` / 32.55% | 0.6105 |
| `cracked-star-jar` | 0.0 | 3 | 192.8127 | `7` / 44.02% | 0.6627 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 2 (66.67%)
- `late_180_to_300`: 1 (33.33%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 132.0993 | `mid_60_to_180` | `player_health_depleted` | 5 | 244 | 120.1367 |
| 63101 | 70.1326 | `mid_60_to_180` | `player_health_depleted` | 2 | 69 | 120.1001 |
| 63102 | 212.9499 | `late_180_to_300` | `player_health_depleted` | 8 | 464 | 120.3901 |

### `caramel-workshop`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 218.6177 | `late_180_to_300` | `player_health_depleted` | 6 | 342 | 120.8334 |
| 63101 | 27.9333 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.5166 |
| 63102 | 218.7844 | `late_180_to_300` | `player_health_depleted` | 7 | 353 | 120.5166 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 230.8537 | `late_180_to_300` | `player_health_depleted` | 9 | 525 | 120.9367 |
| 63101 | 121.4985 | `mid_60_to_180` | `player_health_depleted` | 4 | 183 | 120.1768 |
| 63102 | 226.086 | `late_180_to_300` | `player_health_depleted` | 7 | 493 | 120.0202 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
