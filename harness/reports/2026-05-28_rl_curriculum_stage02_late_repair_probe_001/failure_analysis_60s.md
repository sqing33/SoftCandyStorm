# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_late_repair_probe_001/comparison_60s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_watch`
- Duration: `60.0` seconds
- Total failures: 3
- Repair maps: `soda-creek`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.3333 | 2 | 44.1663 | `3` / 47.97% | 0.6374 |
| `caramel-workshop` | 1.0 | 0 | None | `3` / 53.43% | 0.4861 |
| `cracked-star-jar` | 0.6667 | 1 | 40.6997 | `3` / 46.86% | 0.5933 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 2 (100.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62901 | 40.0331 | `opening_lt_60` | `player_health_depleted` | 2 | 34 | 120.45 |
| 62902 | 48.2996 | `opening_lt_60` | `player_health_depleted` | 2 | 47 | 120.7103 |

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
| 62901 | 40.6997 | `opening_lt_60` | `player_health_depleted` | 2 | 36 | 120.2334 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
