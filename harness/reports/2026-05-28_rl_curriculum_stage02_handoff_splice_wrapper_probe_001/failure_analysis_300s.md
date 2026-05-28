# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_handoff_splice_wrapper_probe_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 169.933 | `5` / 22.81% | 0.8398 |
| `caramel-workshop` | 0.0 | 3 | 154.1338 | `5` / 26.81% | 0.8049 |
| `cracked-star-jar` | 0.0 | 3 | 233.7305 | `5` / 32.83% | 0.7759 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 210.7827 | `late_180_to_300` | `player_health_depleted` | 8 | 498 | 120.1267 |
| 63101 | 83.0324 | `mid_60_to_180` | `player_health_depleted` | 2 | 83 | 120.0601 |
| 63102 | 215.9838 | `late_180_to_300` | `player_health_depleted` | 7 | 511 | 120.4735 |

### `caramel-workshop`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 221.0182 | `late_180_to_300` | `player_health_depleted` | 6 | 347 | 120.4 |
| 63101 | 27.9333 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.5166 |
| 63102 | 213.45 | `late_180_to_300` | `player_health_depleted` | 6 | 322 | 121.3067 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 266.5232 | `late_180_to_300` | `player_health_depleted` | 8 | 599 | 120.1366 |
| 63101 | 217.4842 | `late_180_to_300` | `player_health_depleted` | 6 | 480 | 120.0135 |
| 63102 | 217.1841 | `late_180_to_300` | `player_health_depleted` | 7 | 450 | 120.0367 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
