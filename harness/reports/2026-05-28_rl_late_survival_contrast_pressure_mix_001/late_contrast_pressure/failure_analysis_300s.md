# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_mix_001/late_contrast_pressure/high_pressure_300s_comparison.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 13
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 5 | 150.2383 | `1` / 51.43% | 0.6857 |
| `caramel-workshop` | 0.2 | 4 | 218.1093 | `1` / 33.03% | 0.7908 |
| `cracked-star-jar` | 0.2 | 4 | 178.064 | `1` / 49.89% | 0.6712 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 2 (40.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (60.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 217.2841 | `late_180_to_300` | `player_health_depleted` | 7 | 502 | 120.3836 |
| 62401 | 34.7998 | `opening_lt_60` | `player_health_depleted` | 2 | 30 | 120.3299 |
| 62402 | 252.5917 | `late_180_to_300` | `player_health_depleted` | 10 | 749 | 120.2702 |
| 62403 | 211.9496 | `late_180_to_300` | `player_health_depleted` | 8 | 491 | 120.4768 |
| 62404 | 34.5665 | `opening_lt_60` | `player_health_depleted` | 2 | 32 | 120.3901 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 4 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 214.3502 | `late_180_to_300` | `player_health_depleted` | 7 | 320 | 120.0301 |
| 62401 | 213.9501 | `late_180_to_300` | `player_health_depleted` | 7 | 326 | 120.38 |
| 62403 | 220.4515 | `late_180_to_300` | `player_health_depleted` | 8 | 341 | 120.46 |
| 62404 | 223.6855 | `late_180_to_300` | `player_health_depleted` | 7 | 344 | 121.2068 |

### `cracked-star-jar`

- `opening_lt_60`: 1 (25.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (75.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 231.1204 | `late_180_to_300` | `player_health_depleted` | 8 | 515 | 120.8302 |
| 62401 | 212.083 | `late_180_to_300` | `player_health_depleted` | 7 | 417 | 120.0733 |
| 62402 | 227.753 | `late_180_to_300` | `player_health_depleted` | 8 | 504 | 120.2236 |
| 62403 | 41.2997 | `opening_lt_60` | `player_health_depleted` | 2 | 39 | 120.59 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
