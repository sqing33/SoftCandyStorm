# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-31_rl_opening_mid_boundary_retention_seed63405_probe_001/candidate_high_pressure_300s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 144.6755 | `5` / 40.43% | 0.7627 |
| `caramel-workshop` | 0.0 | 3 | 155.6999 | `8` / 18.18% | 0.8985 |
| `cracked-star-jar` | 0.0 | 3 | 221.0849 | `1` / 31.68% | 0.8139 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 1 (33.33%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63400 | 218.4177 | `late_180_to_300` | `player_health_depleted` | 7 | 515 | 121.2467 |
| 63401 | 177.709 | `mid_60_to_180` | `player_health_depleted` | 6 | 363 | 120.1136 |
| 63402 | 37.8998 | `opening_lt_60` | `player_health_depleted` | 1 | 34 | 121.0666 |

### `caramel-workshop`

- `opening_lt_60`: 1 (33.33%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (66.67%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63400 | 214.6502 | `late_180_to_300` | `player_health_depleted` | 7 | 331 | 120.2667 |
| 63401 | 212.3497 | `late_180_to_300` | `player_health_depleted` | 7 | 323 | 121.0237 |
| 63402 | 40.0997 | `opening_lt_60` | `player_health_depleted` | 1 | 25 | 120.4667 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63400 | 211.2828 | `late_180_to_300` | `player_health_depleted` | 7 | 444 | 120.2837 |
| 63401 | 224.2856 | `late_180_to_300` | `player_health_depleted` | 6 | 482 | 121.38 |
| 63402 | 227.6863 | `late_180_to_300` | `player_health_depleted` | 7 | 477 | 120.0005 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
