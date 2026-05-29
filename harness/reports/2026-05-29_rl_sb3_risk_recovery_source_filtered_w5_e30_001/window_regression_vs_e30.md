# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `1`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `0.116` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `16.522` | `0.1015` | `pass` |
| `180s` | `soda-creek` | `0.0` | `-3.6555` | `0.0911` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `3.8342` | `-0.1006` | `pass` |
| `300s` | `cracked-star-jar` | `0.0` | `15.1876` | `0.0865` | `pass` |
| `300s` | `soda-creek` | `0.0` | `-20.5822` | `0.0633` | `regression` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.1597` | `pass` |
| `60s` | `cracked-star-jar` | `0.3333` | `4.1778` | `-0.0223` | `pass` |
| `60s` | `soda-creek` | `0.3334` | `8.2888` | `-0.1473` | `pass` |

## Blockers

- 300s/soda-creek: average_survival_seconds dropped 20.5822s beyond allowed 5.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
