# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_soda_cracked_staged_opening_probe_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 8
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 139.7275 | `7` / 40.37% | 0.5019 |
| `caramel-workshop` | 0.0 | 3 | 153.1225 | `2` / 53.32% | 0.4909 |
| `cracked-star-jar` | 0.3333 | 2 | 183.0602 | `4` / 38.77% | 0.5112 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 2 (66.67%)
- `late_180_to_300`: 1 (33.33%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 133.0995 | `mid_60_to_180` | `player_health_depleted` | 6 | 242 | 120.0734 |
| 63101 | 70.1326 | `mid_60_to_180` | `player_health_depleted` | 2 | 69 | 120.1001 |
| 63102 | 215.9505 | `late_180_to_300` | `player_health_depleted` | 8 | 477 | 120.5136 |

### `caramel-workshop`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 213.8501 | `late_180_to_300` | `player_health_depleted` | 8 | 324 | 120.5803 |
| 63101 | 27.9333 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.5166 |
| 63102 | 217.5842 | `late_180_to_300` | `player_health_depleted` | 8 | 349 | 120.7234 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (50.00%)
- `late_180_to_300`: 1 (50.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63101 | 127.6317 | `mid_60_to_180` | `player_health_depleted` | 5 | 199 | 120.0568 |
| 63102 | 238.4887 | `late_180_to_300` | `player_health_depleted` | 9 | 513 | 120.3571 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
