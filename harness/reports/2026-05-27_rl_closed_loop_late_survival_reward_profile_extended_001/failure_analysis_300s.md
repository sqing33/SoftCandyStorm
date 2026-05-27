# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-27_rl_closed_loop_late_survival_reward_profile_extended_001/comparison_300s_3seed.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Duration: `300.0` seconds
- Total failures: 8
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 3 | 144.1839 | `4` / 46.69% | 0.453 |
| `caramel-workshop` | 0.0 | 3 | 217.0507 | `4` / 51.65% | 0.521 |
| `cracked-star-jar` | 0.3333 | 2 | 187.6278 | `4` / 55.35% | 0.4227 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 2 (66.67%)
- `late_180_to_300`: 1 (33.33%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62300 | 210.5494 | `late_180_to_300` | `player_health_depleted` | 8 | 476 | 120.6903 |
| 62301 | 71.6659 | `mid_60_to_180` | `player_health_depleted` | 2 | 75 | 120.8798 |
| 62302 | 150.3365 | `mid_60_to_180` | `player_health_depleted` | 6 | 259 | 120.0872 |

### `caramel-workshop`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 3 (100.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62300 | 219.818 | `late_180_to_300` | `player_health_depleted` | 7 | 343 | 120.4234 |
| 62301 | 216.5173 | `late_180_to_300` | `player_health_depleted` | 7 | 331 | 120.3901 |
| 62302 | 214.8169 | `late_180_to_300` | `player_health_depleted` | 7 | 337 | 120.49 |

### `cracked-star-jar`

- `opening_lt_60`: 0 (0.00%)
- `mid_60_to_180`: 1 (50.00%)
- `late_180_to_300`: 1 (50.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62300 | 225.0191 | `late_180_to_300` | `player_health_depleted` | 9 | 521 | 120.8603 |
| 62301 | 150.2365 | `mid_60_to_180` | `player_health_depleted` | 6 | 277 | 120.217 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
