# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `1`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180` | `caramel-workshop` | `0.0` | `0.0` | `-0.313` | `pass` |
| `180` | `cracked-star-jar` | `0.0` | `3.011` | `0.0588` | `pass` |
| `180` | `soda-creek` | `0.0` | `0.3` | `-0.0844` | `pass` |
| `300` | `caramel-workshop` | `0.0` | `0.9002` | `-0.289` | `pass` |
| `300` | `cracked-star-jar` | `0.0` | `-5.4463` | `0.0956` | `regression` |
| `300` | `soda-creek` | `0.0` | `5.2889` | `0.0227` | `pass` |
| `60` | `caramel-workshop` | `0.0` | `0.0` | `0.0` | `pass` |
| `60` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `pass` |
| `60` | `soda-creek` | `0.0` | `0.0` | `0.0` | `pass` |

## Blockers

- 300/cracked-star-jar: average_survival_seconds dropped 5.4463s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
