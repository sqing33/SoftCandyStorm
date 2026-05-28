# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_anchor_map_bucket_full_smoke_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 149.3553 | `5` / 37.48% | 0.7388 |
| `caramel-workshop` | 0.0 | 3 | 154.6673 | `7` / 37.43% | 0.7506 |
| `cracked-star-jar` | 0.0 | 3 | 189.7139 | `7` / 41.88% | 0.7118 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 210.1159 | `late_180_to_300` | `player_health_depleted` | 7 | 491 | 120.3201 |
| 63101 | 24.4666 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.6299 |
| 63102 | 213.4833 | `late_180_to_300` | `player_health_depleted` | 7 | 480 | 120.5101 |

### `caramel-workshop`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 215.8171 | `late_180_to_300` | `player_health_depleted` | 8 | 332 | 120.2236 |
| 63101 | 27.9333 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.5166 |
| 63102 | 220.2514 | `late_180_to_300` | `player_health_depleted` | 7 | 338 | 120.1433 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 258.6251 | `late_180_to_300` | `player_health_depleted` | 10 | 598 | 120.1437 |
| 63101 | 92.5323 | `mid_60_to_180` | `player_health_depleted` | 3 | 110 | 120.1102 |
| 63102 | 217.9843 | `late_180_to_300` | `player_health_depleted` | 7 | 456 | 120.9271 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
