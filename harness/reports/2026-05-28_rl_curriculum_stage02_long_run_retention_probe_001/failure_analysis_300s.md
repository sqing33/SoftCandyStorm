# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_long_run_retention_probe_001/comparison_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 179.1213 | `4` / 38.54% | 0.5111 |
| `caramel-workshop` | 0.0 | 3 | 218.9511 | `7` / 48.73% | 0.5055 |
| `cracked-star-jar` | 0.0 | 3 | 184.5128 | `7` / 38.28% | 0.5308 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 116.0986 | `mid_60_to_180` | `player_health_depleted` | 5 | 199 | 120.0301 |
| 63101 | 211.0161 | `late_180_to_300` | `player_health_depleted` | 8 | 498 | 120.4502 |
| 63102 | 210.2493 | `late_180_to_300` | `player_health_depleted` | 8 | 473 | 120.0236 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 214.6502 | `late_180_to_300` | `player_health_depleted` | 9 | 344 | 120.4869 |
| 63101 | 215.417 | `late_180_to_300` | `player_health_depleted` | 4 | 329 | 120.3067 |
| 63102 | 226.7861 | `late_180_to_300` | `player_health_depleted` | 9 | 368 | 120.3065 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 221.8518 | `late_180_to_300` | `player_health_depleted` | 9 | 491 | 120.5802 |
| 63101 | 97.9655 | `mid_60_to_180` | `player_health_depleted` | 3 | 117 | 120.0532 |
| 63102 | 233.721 | `late_180_to_300` | `player_health_depleted` | 9 | 499 | 120.1038 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
