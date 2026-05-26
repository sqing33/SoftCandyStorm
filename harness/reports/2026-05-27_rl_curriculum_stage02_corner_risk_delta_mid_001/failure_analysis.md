# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-27_rl_curriculum_stage02_corner_risk_delta_mid_001/comparison_180s_3seed.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `180.0` seconds
- Total failures: 2
- Repair maps: `soda-creek`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.3333 | 2 | 114.9375 | `7` / 55.25% | 0.3134 |
| `caramel-workshop` | 1.0 | 0 | None | `2` / 77.81% | 0.2502 |
| `cracked-star-jar` | 1.0 | 0 | None | `7` / 51.05% | 0.4198 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 1 (50.00%)
- `mid_60_to_180`: 1 (50.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62201 | 177.0755 | `mid_60_to_180` | `player_health_depleted` | 7 | 374 | 120.097 |
| 62202 | 52.7995 | `opening_lt_60` | `player_health_depleted` | 2 | 54 | 120.2401 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
