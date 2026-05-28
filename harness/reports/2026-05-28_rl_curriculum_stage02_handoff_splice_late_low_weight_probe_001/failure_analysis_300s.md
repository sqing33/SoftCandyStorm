# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_handoff_splice_late_low_weight_probe_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 169.4561 | `3` / 24.10% | 0.8706 |
| `caramel-workshop` | 0.0 | 3 | 154.4228 | `5` / 34.15% | 0.778 |
| `cracked-star-jar` | 0.0 | 3 | 180.5896 | `5` / 22.87% | 0.8554 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 212.5164 | `late_180_to_300` | `player_health_depleted` | 7 | 507 | 120.29 |
| 63101 | 70.3993 | `mid_60_to_180` | `player_health_depleted` | 2 | 69 | 120.1201 |
| 63102 | 225.4525 | `late_180_to_300` | `player_health_depleted` | 8 | 549 | 120.5499 |

### `caramel-workshop`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 219.818 | `late_180_to_300` | `player_health_depleted` | 7 | 344 | 121.9067 |
| 63101 | 27.9333 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.5166 |
| 63102 | 215.5171 | `late_180_to_300` | `player_health_depleted` | 8 | 331 | 121.26 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 223.4521 | `late_180_to_300` | `player_health_depleted` | 9 | 489 | 120.8398 |
| 63101 | 99.1322 | `mid_60_to_180` | `player_health_depleted` | 4 | 126 | 120.1102 |
| 63102 | 219.1845 | `late_180_to_300` | `player_health_depleted` | 9 | 470 | 120.0471 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
