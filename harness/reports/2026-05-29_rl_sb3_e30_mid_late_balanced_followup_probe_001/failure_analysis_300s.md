# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-29_rl_sb3_e30_mid_late_balanced_followup_probe_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 158.6239 | `1` / 27.88% | 0.7988 |
| `caramel-workshop` | 0.0 | 3 | 153.2337 | `1` / 41.49% | 0.6454 |
| `cracked-star-jar` | 0.0 | 3 | 175.9474 | `5` / 31.72% | 0.7674 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 215.9172 | `late_180_to_300` | `player_health_depleted` | 8 | 526 | 120.2534 |
| 63101 | 24.4666 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.6299 |
| 63102 | 235.488 | `late_180_to_300` | `player_health_depleted` | 8 | 614 | 120.0203 |

### `caramel-workshop`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 212.1497 | `late_180_to_300` | `player_health_depleted` | 8 | 323 | 120.4071 |
| 63101 | 27.9333 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.5166 |
| 63102 | 219.618 | `late_180_to_300` | `player_health_depleted` | 6 | 337 | 121.2433 |

### `cracked-star-jar`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 56.8661 | `opening_lt_60` | `player_health_depleted` | 2 | 59 | 120.7099 |
| 63101 | 230.0202 | `late_180_to_300` | `player_health_depleted` | 8 | 498 | 120.6001 |
| 63102 | 240.9558 | `late_180_to_300` | `player_health_depleted` | 9 | 573 | 120.0163 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
