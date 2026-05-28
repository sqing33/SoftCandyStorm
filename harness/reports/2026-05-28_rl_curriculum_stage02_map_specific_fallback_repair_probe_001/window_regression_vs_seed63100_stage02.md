# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `1`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `-0.2491` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `15.8355` | `-0.0266` | `pass` |
| `180s` | `soda-creek` | `0.0` | `5.3444` | `-0.1323` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `5.6346` | `-0.1158` | `pass` |
| `300s` | `cracked-star-jar` | `0.6667` | `55.0749` | `0.1377` | `pass` |
| `300s` | `soda-creek` | `0.0` | `-0.0111` | `-0.1168` | `regression` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `0.0` | `pass` |

## Blockers

- 300s/soda-creek: average_survival_seconds dropped 0.0111s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
