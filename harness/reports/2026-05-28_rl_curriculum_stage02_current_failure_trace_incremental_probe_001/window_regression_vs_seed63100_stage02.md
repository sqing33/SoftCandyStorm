# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `1`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `-0.5301` | `pass` |
| `180s` | `cracked-star-jar` | `0.3333` | `22.5147` | `-0.0764` | `pass` |
| `180s` | `soda-creek` | `0.3334` | `31.9035` | `-0.1036` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `-0.4445` | `-0.3534` | `regression` |
| `300s` | `cracked-star-jar` | `0.0` | `47.6694` | `0.0414` | `pass` |
| `300s` | `soda-creek` | `0.3333` | `69.6839` | `-0.1262` | `pass` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `0.0` | `pass` |

## Blockers

- 300s/caramel-workshop: average_survival_seconds dropped 0.4445s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
