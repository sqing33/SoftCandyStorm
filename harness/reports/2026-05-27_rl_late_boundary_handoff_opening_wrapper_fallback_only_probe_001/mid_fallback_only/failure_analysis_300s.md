# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-27_rl_late_boundary_handoff_opening_wrapper_fallback_only_probe_001/mid_fallback_only/high_pressure_300s_wrapper_comparison.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 15
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 5 | 138.8802 | `7` / 38.02% | 0.7251 |
| `caramel-workshop` | 0.0 | 5 | 204.5947 | `7` / 36.58% | 0.7793 |
| `cracked-star-jar` | 0.0 | 5 | 124.1025 | `7` / 61.49% | 0.5071 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 3 (60.00%)
- `late_180_to_300`: 2 (40.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 70.7993 | `mid_60_to_180` | `player_health_depleted` | 2 | 81 | 120.4401 |
| 62401 | 71.2993 | `mid_60_to_180` | `player_health_depleted` | 3 | 66 | 120.7099 |
| 62402 | 228.4865 | `late_180_to_300` | `player_health_depleted` | 9 | 569 | 120.0632 |
| 62403 | 216.9174 | `late_180_to_300` | `player_health_depleted` | 7 | 531 | 120.3404 |
| 62404 | 106.8987 | `mid_60_to_180` | `player_health_depleted` | 4 | 130 | 120.0799 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (20.00%)
- `late_180_to_300`: 4 (80.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 218.5511 | `late_180_to_300` | `player_health_depleted` | 6 | 336 | 121.0267 |
| 62401 | 159.3384 | `mid_60_to_180` | `player_health_depleted` | 5 | 213 | 120.1206 |
| 62402 | 218.8511 | `late_180_to_300` | `player_health_depleted` | 4 | 332 | 120.3334 |
| 62403 | 213.8167 | `late_180_to_300` | `player_health_depleted` | 8 | 328 | 121.0501 |
| 62404 | 212.4164 | `late_180_to_300` | `player_health_depleted` | 8 | 323 | 120.7735 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 4 (80.00%)
- `late_180_to_300`: 1 (20.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 99.8655 | `mid_60_to_180` | `player_health_depleted` | 4 | 118 | 120.0102 |
| 62401 | 124.9984 | `mid_60_to_180` | `player_health_depleted` | 5 | 178 | 120.6167 |
| 62402 | 216.0172 | `late_180_to_300` | `player_health_depleted` | 5 | 451 | 120.1934 |
| 62403 | 107.5654 | `mid_60_to_180` | `player_health_depleted` | 3 | 135 | 120.6833 |
| 62404 | 72.0659 | `mid_60_to_180` | `player_health_depleted` | 3 | 68 | 120.0169 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
