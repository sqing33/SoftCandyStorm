# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_map_specific_fallback_w025_probe_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 143.5856 | `8` / 32.72% | 0.7881 |
| `caramel-workshop` | 0.0 | 3 | 157.5346 | `3` / 48.26% | 0.6467 |
| `cracked-star-jar` | 0.0 | 3 | 178.8784 | `8` / 38.05% | 0.8073 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 2 (66.67%)
- `late_180_to_300`: 1 (33.33%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 103.6654 | `mid_60_to_180` | `player_health_depleted` | 4 | 169 | 120.0168 |
| 63101 | 69.3993 | `mid_60_to_180` | `player_health_depleted` | 2 | 62 | 120.1401 |
| 63102 | 257.692 | `late_180_to_300` | `player_health_depleted` | 9 | 798 | 120.5499 |

### `caramel-workshop`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 212.083 | `late_180_to_300` | `player_health_depleted` | 6 | 320 | 120.3834 |
| 63101 | 27.9333 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.5166 |
| 63102 | 232.5874 | `late_180_to_300` | `player_health_depleted` | 6 | 360 | 120.5099 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 229.42 | `late_180_to_300` | `player_health_depleted` | 10 | 553 | 120.3566 |
| 63101 | 95.0656 | `mid_60_to_180` | `player_health_depleted` | 4 | 117 | 120.0068 |
| 63102 | 212.1497 | `late_180_to_300` | `player_health_depleted` | 9 | 452 | 120.8604 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
