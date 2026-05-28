# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `2`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `-0.5315` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `-5.8` | `-0.0773` | `regression` |
| `180s` | `soda-creek` | `0.0` | `1.9111` | `-0.1524` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `3.3229` | `-0.1319` | `pass` |
| `300s` | `cracked-star-jar` | `0.0` | `-19.3806` | `0.0359` | `regression` |
| `300s` | `soda-creek` | `0.0` | `10.4806` | `-0.0354` | `pass` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `0.0` | `pass` |

## Blockers

- 180s/cracked-star-jar: average_survival_seconds dropped 5.8s beyond allowed 0.0s
- 300s/cracked-star-jar: average_survival_seconds dropped 19.3806s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
