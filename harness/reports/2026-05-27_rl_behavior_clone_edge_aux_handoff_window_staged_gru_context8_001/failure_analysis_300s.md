# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-27_rl_behavior_clone_edge_aux_handoff_window_staged_gru_context8_001/comparison_300s_3seed.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 8
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 237.2439 | `3` / 29.07% | 0.7972 |
| `caramel-workshop` | 0.0 | 3 | 220.2403 | `5` / 17.95% | 0.9252 |
| `cracked-star-jar` | 0.3333 | 2 | 207.0152 | `3` / 35.00% | 0.8025 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62300 | 251.2247 | `late_180_to_300` | `player_health_depleted` | 11 | 749 | 121.0767 |
| 62301 | 241.0892 | `late_180_to_300` | `player_health_depleted` | 9 | 645 | 120.0337 |
| 62302 | 219.4179 | `late_180_to_300` | `player_health_depleted` | 8 | 475 | 121.0701 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62300 | 220.5515 | `late_180_to_300` | `player_health_depleted` | 7 | 341 | 121.0466 |
| 62301 | 225.3525 | `late_180_to_300` | `player_health_depleted` | 7 | 355 | 120.0598 |
| 62302 | 214.8169 | `late_180_to_300` | `player_health_depleted` | 7 | 340 | 120.8503 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 2 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62300 | 194.946 | `late_180_to_300` | `player_health_depleted` | 8 | 411 | 120.1405 |
| 62301 | 219.0845 | `late_180_to_300` | `player_health_depleted` | 7 | 453 | 120.1272 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
