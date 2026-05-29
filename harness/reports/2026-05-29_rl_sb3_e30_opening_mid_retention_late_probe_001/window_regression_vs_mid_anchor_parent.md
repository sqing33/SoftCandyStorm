# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `3`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `0.2413` | `regression` |
| `180s` | `cracked-star-jar` | `0.3333` | `41.0589` | `0.0016` | `pass` |
| `180s` | `soda-creek` | `0.3334` | `5.4679` | `-0.0174` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `-2.7672` | `0.1519` | `pass` |
| `300s` | `cracked-star-jar` | `0.6667` | `102.203` | `0.0106` | `pass` |
| `300s` | `soda-creek` | `0.0` | `-27.2947` | `-0.0229` | `regression` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0155` | `pass` |
| `60s` | `cracked-star-jar` | `-0.3333` | `-1.0667` | `-0.0122` | `regression` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `0.0007` | `pass` |

## Blockers

- 180s/caramel-workshop: dominant_action_ratio increased 0.2413 beyond allowed 0.2
- 300s/soda-creek: average_survival_seconds dropped 27.2947s beyond allowed 5.0s
- 60s/cracked-star-jar: win_rate_delta -0.3333 below required 0.0

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
