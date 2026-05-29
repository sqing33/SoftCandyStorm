# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `6`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `0.069` | `pass` |
| `180s` | `cracked-star-jar` | `0.3333` | `41.0589` | `0.2026` | `regression` |
| `180s` | `soda-creek` | `0.0` | `-41.0798` | `0.0072` | `regression` |
| `300s` | `caramel-workshop` | `0.0` | `-6.0235` | `0.0505` | `regression` |
| `300s` | `cracked-star-jar` | `0.0` | `49.4607` | `0.2045` | `regression` |
| `300s` | `soda-creek` | `0.0` | `-0.4334` | `-0.0624` | `pass` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0146` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `-0.0317` | `pass` |
| `60s` | `soda-creek` | `-0.3334` | `-6.4999` | `0.0594` | `regression` |

## Blockers

- 180s/cracked-star-jar: dominant_action_ratio increased 0.2026 beyond allowed 0.2
- 180s/soda-creek: average_survival_seconds dropped 41.0798s beyond allowed 5.0s
- 300s/caramel-workshop: average_survival_seconds dropped 6.0235s beyond allowed 5.0s
- 300s/cracked-star-jar: dominant_action_ratio increased 0.2045 beyond allowed 0.2
- 60s/soda-creek: win_rate_delta -0.3334 below required 0.0
- 60s/soda-creek: average_survival_seconds dropped 6.4999s beyond allowed 5.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
