# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_staged_fallback_repair_probe_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 135.183 | `8` / 25.43% | 0.8035 |
| `caramel-workshop` | 0.0 | 3 | 152.0556 | `5` / 28.08% | 0.8189 |
| `cracked-star-jar` | 0.0 | 3 | 181.768 | `8` / 37.06% | 0.7484 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 2 (66.67%)
- `late_180_to_300`: 1 (33.33%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 103.6654 | `mid_60_to_180` | `player_health_depleted` | 4 | 169 | 120.0168 |
| 63101 | 82.9991 | `mid_60_to_180` | `player_health_depleted` | 2 | 81 | 120.0801 |
| 63102 | 218.8845 | `late_180_to_300` | `player_health_depleted` | 8 | 511 | 121.2701 |

### `caramel-workshop`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 214.8169 | `late_180_to_300` | `player_health_depleted` | 8 | 329 | 120.3669 |
| 63101 | 27.9333 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.5166 |
| 63102 | 213.4166 | `late_180_to_300` | `player_health_depleted` | 9 | 355 | 121.0369 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 223.052 | `late_180_to_300` | `player_health_depleted` | 8 | 462 | 120.3731 |
| 63101 | 94.5322 | `mid_60_to_180` | `player_health_depleted` | 4 | 115 | 120.0968 |
| 63102 | 227.7197 | `late_180_to_300` | `player_health_depleted` | 9 | 507 | 120.2103 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
