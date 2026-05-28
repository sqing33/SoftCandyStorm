# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `5`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180` | `caramel-workshop` | `0.0` | `0.0` | `0.023` | `pass` |
| `180` | `cracked-star-jar` | `0.0` | `-12.2893` | `0.1164` | `regression` |
| `180` | `soda-creek` | `0.3334` | `0.99` | `-0.0115` | `pass` |
| `300` | `caramel-workshop` | `0.0` | `-7.5238` | `-0.0653` | `regression` |
| `300` | `cracked-star-jar` | `-0.3333` | `-37.7769` | `-0.0167` | `regression` |
| `300` | `soda-creek` | `0.0` | `-2.6774` | `0.0154` | `regression` |
| `60` | `caramel-workshop` | `0.0` | `0.0` | `0.0` | `pass` |
| `60` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `pass` |
| `60` | `soda-creek` | `0.0` | `0.0` | `0.0` | `pass` |

## Blockers

- 180/cracked-star-jar: average_survival_seconds dropped 12.2893s beyond allowed 0.0s
- 300/caramel-workshop: average_survival_seconds dropped 7.5238s beyond allowed 0.0s
- 300/cracked-star-jar: win_rate_delta -0.3333 below required 0.0
- 300/cracked-star-jar: average_survival_seconds dropped 37.7769s beyond allowed 0.0s
- 300/soda-creek: average_survival_seconds dropped 2.6774s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
