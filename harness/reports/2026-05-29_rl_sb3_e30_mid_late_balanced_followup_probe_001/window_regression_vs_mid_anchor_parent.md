# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `2`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `0.0171` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `0.0` | `-0.0341` | `pass` |
| `180s` | `soda-creek` | `0.0` | `-6.857` | `0.0617` | `regression` |
| `300s` | `caramel-workshop` | `0.0` | `-5.19` | `0.17` | `regression` |
| `300s` | `cracked-star-jar` | `0.0` | `0.8224` | `0.0706` | `pass` |
| `300s` | `soda-creek` | `0.0` | `6.3458` | `-0.0754` | `pass` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.1108` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0005` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `0.1109` | `pass` |

## Blockers

- 180s/soda-creek: average_survival_seconds dropped 6.857s beyond allowed 5.0s
- 300s/caramel-workshop: average_survival_seconds dropped 5.19s beyond allowed 5.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
