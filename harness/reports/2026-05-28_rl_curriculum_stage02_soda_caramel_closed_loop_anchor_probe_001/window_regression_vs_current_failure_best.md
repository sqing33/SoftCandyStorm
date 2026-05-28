# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `6`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180` | `caramel-workshop` | `0.0` | `0.0` | `0.1608` | `pass` |
| `180` | `cracked-star-jar` | `0.0` | `-4.8339` | `0.1697` | `regression` |
| `180` | `soda-creek` | `0.0` | `-26.4024` | `0.0181` | `regression` |
| `300` | `caramel-workshop` | `0.0` | `-6.8348` | `-0.0813` | `regression` |
| `300` | `cracked-star-jar` | `-0.3333` | `-25.5538` | `0.1948` | `regression` |
| `300` | `soda-creek` | `0.0` | `-33.7396` | `0.1597` | `regression` |
| `60` | `caramel-workshop` | `0.0` | `0.0` | `0.0` | `pass` |
| `60` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `pass` |
| `60` | `soda-creek` | `0.0` | `0.0` | `0.0` | `pass` |

## Blockers

- 180/cracked-star-jar: average_survival_seconds dropped 4.8339s beyond allowed 0.0s
- 180/soda-creek: average_survival_seconds dropped 26.4024s beyond allowed 0.0s
- 300/caramel-workshop: average_survival_seconds dropped 6.8348s beyond allowed 0.0s
- 300/cracked-star-jar: win_rate_delta -0.3333 below required 0.0
- 300/cracked-star-jar: average_survival_seconds dropped 25.5538s beyond allowed 0.0s
- 300/soda-creek: average_survival_seconds dropped 33.7396s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
