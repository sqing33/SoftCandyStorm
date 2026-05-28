# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_late_mixed_repair_probe_001/comparison_60s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_watch`
- Duration: `60.0` seconds
- Total failures: 3
- Repair maps: `soda-creek`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.3333 | 2 | 35.1831 | `3` / 37.68% | 0.5717 |
| `caramel-workshop` | 1.0 | 0 | None | `3` / 50.10% | 0.5727 |
| `cracked-star-jar` | 0.6667 | 1 | 51.6662 | `3` / 41.28% | 0.5811 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 2 (100.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63000 | 28.3332 | `opening_lt_60` | `player_health_depleted` | 2 | 27 | 120.4067 |
| 63002 | 42.033 | `opening_lt_60` | `player_health_depleted` | 2 | 32 | 120.4932 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

### `cracked-star-jar`

- `opening_lt_60`: 1 (100.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63001 | 51.6662 | `opening_lt_60` | `player_health_depleted` | 2 | 55 | 120.2866 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
