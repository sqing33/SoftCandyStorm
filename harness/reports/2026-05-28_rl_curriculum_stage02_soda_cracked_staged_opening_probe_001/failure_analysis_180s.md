# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_soda_cracked_staged_opening_probe_001/comparison_180s.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_watch`
- Duration: `180.0` seconds
- Total failures: 4
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.3333 | 2 | 101.5994 | `7` / 40.23% | 0.5065 |
| `caramel-workshop` | 0.6667 | 1 | 27.9333 | `2` / 59.77% | 0.4908 |
| `cracked-star-jar` | 0.6667 | 1 | 127.6317 | `7` / 40.43% | 0.4936 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 2 (100.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63100 | 133.0661 | `mid_60_to_180` | `player_health_depleted` | 5 | 239 | 120.0067 |
| 63101 | 70.1326 | `mid_60_to_180` | `player_health_depleted` | 2 | 69 | 120.1001 |

### `caramel-workshop`

- `opening_lt_60`: 1 (100.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63101 | 27.9333 | `opening_lt_60` | `player_health_depleted` | 1 | 15 | 120.5166 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (100.00%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63101 | 127.6317 | `mid_60_to_180` | `player_health_depleted` | 5 | 199 | 120.0568 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
