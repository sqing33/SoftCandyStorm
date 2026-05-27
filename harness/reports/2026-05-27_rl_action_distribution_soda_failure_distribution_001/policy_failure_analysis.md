# RL Policy Failure Analysis

- Source: `harness/reports/2026-05-27_rl_action_distribution_multiseed_midwindow_samples_001/soda_180s_trace_eval.json`
- Decision: `rl_policy_failure_analysis_recorded`
- Gate decision: `comparison_recorded_not_balance_gate`
- Duration: `180.0` seconds
- Total failures: 18
- Repair maps: `soda-creek`

## Map Summary

| Map | Win Rate | Failures | Avg Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.1 | 18 | 49.3054 | `3` / 50.03% | 0.6185 |

## Failure Buckets

### `soda-creek`

- `opening_lt_60`: 14 (77.78%)
- `mid_60_to_180`: 4 (22.22%)
- `late_180_to_300`: 0 (0.00%)
- `post_300`: 0 (0.00%)

| Seed | Time | Bucket | Reason | Level | Kills | Damage |
|---:|---:|---|---|---:|---:|---:|
| 62400 | 22.5 | `opening_lt_60` | `player_health_depleted` | 1 | 18 | 120.3699 |
| 62401 | 38.7664 | `opening_lt_60` | `player_health_depleted` | 2 | 37 | 120.0099 |
| 62402 | 42.8997 | `opening_lt_60` | `player_health_depleted` | 2 | 40 | 120.3998 |
| 62403 | 28.1666 | `opening_lt_60` | `player_health_depleted` | 2 | 25 | 120.86 |
| 62404 | 131.1657 | `mid_60_to_180` | `player_health_depleted` | 5 | 212 | 120.0238 |
| 62405 | 28.2666 | `opening_lt_60` | `player_health_depleted` | 1 | 23 | 120.3999 |
| 62406 | 119.9652 | `mid_60_to_180` | `player_health_depleted` | 3 | 177 | 120.1403 |
| 62408 | 30.0332 | `opening_lt_60` | `player_health_depleted` | 2 | 26 | 120.7 |
| 62409 | 31.4332 | `opening_lt_60` | `player_health_depleted` | 2 | 31 | 120.4798 |
| 62410 | 62.3327 | `mid_60_to_180` | `player_health_depleted` | 2 | 64 | 120.0633 |
| 62411 | 30.5332 | `opening_lt_60` | `player_health_depleted` | 1 | 26 | 120.4099 |
| 62412 | 29.2332 | `opening_lt_60` | `player_health_depleted` | 2 | 29 | 120.0499 |
| 62414 | 146.369 | `mid_60_to_180` | `player_health_depleted` | 5 | 252 | 120.1501 |
| 62415 | 25.1666 | `opening_lt_60` | `player_health_depleted` | 1 | 21 | 120.43 |
| 62416 | 24.6333 | `opening_lt_60` | `player_health_depleted` | 1 | 19 | 120.6566 |
| 62417 | 29.6332 | `opening_lt_60` | `player_health_depleted` | 2 | 30 | 120.1998 |
| 62418 | 34.3998 | `opening_lt_60` | `player_health_depleted` | 2 | 32 | 120.8666 |
| 62419 | 31.9999 | `opening_lt_60` | `player_health_depleted` | 2 | 29 | 120.03 |

## Limitations

- This report summarizes existing comparison output only.
- It does not replay episodes or prove a fix.
- Use it to choose the next curriculum, reward, or policy diagnostic target.
