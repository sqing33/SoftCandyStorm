# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `6`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `-0.022` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `-1.8782` | `-0.0069` | `regression` |
| `180s` | `soda-creek` | `0.0` | `-20.258` | `-0.0453` | `regression` |
| `300s` | `caramel-workshop` | `0.0` | `-7.246` | `-0.027` | `regression` |
| `300s` | `cracked-star-jar` | `-0.3333` | `-7.3324` | `0.1243` | `regression` |
| `300s` | `soda-creek` | `0.0` | `-18.2827` | `0.1682` | `regression` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `0.0` | `pass` |

## Blockers

- 180s/cracked-star-jar: average_survival_seconds dropped 1.8782s beyond allowed 0.0s
- 180s/soda-creek: average_survival_seconds dropped 20.258s beyond allowed 0.0s
- 300s/caramel-workshop: average_survival_seconds dropped 7.246s beyond allowed 0.0s
- 300s/cracked-star-jar: win_rate_delta -0.3333 below required 0.0
- 300s/cracked-star-jar: average_survival_seconds dropped 7.3324s beyond allowed 0.0s
- 300s/soda-creek: average_survival_seconds dropped 18.2827s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
