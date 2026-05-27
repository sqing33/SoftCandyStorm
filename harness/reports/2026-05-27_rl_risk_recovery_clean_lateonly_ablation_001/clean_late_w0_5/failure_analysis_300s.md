# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-27_rl_risk_recovery_clean_lateonly_ablation_001/clean_late_w0_5/high_pressure_300s_comparison.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 15
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 5 | 149.0248 | `1` / 46.68% | 0.7268 |
| `caramel-workshop` | 0.0 | 5 | 223.1454 | `1` / 32.64% | 0.817 |
| `cracked-star-jar` | 0.0 | 5 | 197.4302 | `1` / 45.95% | 0.6682 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 2 (40.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (60.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 249.391 | `late_180_to_300` | `player_health_depleted` | 10 | 656 | 120.2836 |
| 62401 | 34.7998 | `opening_lt_60` | `player_health_depleted` | 2 | 30 | 120.3299 |
| 62402 | 211.3162 | `late_180_to_300` | `player_health_depleted` | 8 | 493 | 120.5367 |
| 62403 | 215.0503 | `late_180_to_300` | `player_health_depleted` | 9 | 513 | 120.1069 |
| 62404 | 34.5665 | `opening_lt_60` | `player_health_depleted` | 2 | 32 | 120.3901 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 5 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 221.5184 | `late_180_to_300` | `player_health_depleted` | 8 | 345 | 120.5332 |
| 62401 | 213.8501 | `late_180_to_300` | `player_health_depleted` | 7 | 322 | 120.1967 |
| 62402 | 222.9853 | `late_180_to_300` | `player_health_depleted` | 9 | 350 | 120.8032 |
| 62403 | 225.4525 | `late_180_to_300` | `player_health_depleted` | 10 | 351 | 120.1767 |
| 62404 | 231.9206 | `late_180_to_300` | `player_health_depleted` | 8 | 370 | 120.2132 |

### `cracked-star-jar`

- `opening_lt_60`: 1 (20.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 4 (80.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 210.7827 | `late_180_to_300` | `player_health_depleted` | 7 | 447 | 120.4969 |
| 62401 | 236.0548 | `late_180_to_300` | `player_health_depleted` | 8 | 505 | 121.0536 |
| 62402 | 239.8223 | `late_180_to_300` | `player_health_depleted` | 9 | 526 | 121.0202 |
| 62403 | 41.2997 | `opening_lt_60` | `player_health_depleted` | 2 | 39 | 120.59 |
| 62404 | 259.1916 | `late_180_to_300` | `player_health_depleted` | 8 | 556 | 121.2401 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
