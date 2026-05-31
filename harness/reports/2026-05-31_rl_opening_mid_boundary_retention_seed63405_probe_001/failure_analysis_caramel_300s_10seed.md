# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-31_rl_opening_mid_boundary_retention_seed63405_probe_001/candidate_caramel_300s_10seed.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `comparison_recorded_not_balance_gate`
- Duration: `300.0` seconds
- Total failures: 9
- Repair maps: `caramel-workshop`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `caramel-workshop` | 0.1 | 9 | 197.0746 | `5` / 25.54% | 0.8435 |

## Failure Buckets

### `caramel-workshop`

- `opening_lt_60`: 1 (11.11%)
- `mid_60_to_180`: 0 (0.00%)
- `late_180_to_300`: 8 (88.89%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 63400 | 214.6502 | `late_180_to_300` | `player_health_depleted` | 7 | 331 | 120.2667 |
| 63401 | 212.3497 | `late_180_to_300` | `player_health_depleted` | 7 | 323 | 121.0237 |
| 63402 | 40.0997 | `opening_lt_60` | `player_health_depleted` | 1 | 25 | 120.4667 |
| 63403 | 213.8167 | `late_180_to_300` | `player_health_depleted` | 6 | 328 | 120.2801 |
| 63404 | 218.5511 | `late_180_to_300` | `player_health_depleted` | 7 | 349 | 121.0766 |
| 63405 | 220.6515 | `late_180_to_300` | `player_health_depleted` | 5 | 335 | 120.8466 |
| 63406 | 216.8507 | `late_180_to_300` | `player_health_depleted` | 7 | 335 | 120.1167 |
| 63408 | 225.8193 | `late_180_to_300` | `player_health_depleted` | 6 | 357 | 120.3032 |
| 63409 | 210.8827 | `late_180_to_300` | `player_health_depleted` | 6 | 323 | 120.08 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
