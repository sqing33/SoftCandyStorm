# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_late_mixed_repair_probe_001/comparison_180s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `180.0` seconds
- Total failures: 5
- Repair maps: `soda-creek`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 66.3105 | `1` / 49.92% | 0.6177 |
| `caramel-workshop` | 1.0 | 0 | None | `1` / 40.38% | 0.7352 |
| `cracked-star-jar` | 0.3333 | 2 | 97.3006 | `1` / 42.50% | 0.7067 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 2 (66.67%)
- `mid_60_to_180`: 1 (33.33%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63000 | 28.3332 | `opening_lt_60` | `player_health_depleted` | 2 | 27 | 120.4067 |
| 63001 | 128.5652 | `mid_60_to_180` | `player_health_depleted` | 5 | 224 | 120.0371 |
| 63002 | 42.033 | `opening_lt_60` | `player_health_depleted` | 2 | 32 | 120.3432 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

### `cracked-star-jar`

- `opening_lt_60`: 1 (50.00%)
- `mid_60_to_180`: 1 (50.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63000 | 142.9349 | `mid_60_to_180` | `player_health_depleted` | 6 | 236 | 120.0336 |
| 63001 | 51.6662 | `opening_lt_60` | `player_health_depleted` | 2 | 55 | 120.2866 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
