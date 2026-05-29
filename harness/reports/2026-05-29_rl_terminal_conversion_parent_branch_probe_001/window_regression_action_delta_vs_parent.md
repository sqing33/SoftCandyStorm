# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `1`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Action L1 Δ | Max Action Ratio Δ | Entropy Δ | Status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `pass` |
| `180s` | `soda-creek` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `pass` |
| `300s` | `cracked-star-jar` | `0.0` | `-0.4779` | `0.044` | `0.0947` | `0.044` | `-0.0075` | `regression` |
| `300s` | `soda-creek` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `pass` |

## Blockers

- 300s/cracked-star-jar: average_survival_seconds dropped 0.4779s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
