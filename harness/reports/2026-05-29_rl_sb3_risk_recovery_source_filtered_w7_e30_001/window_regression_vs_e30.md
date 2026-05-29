# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `1`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `0.1837` | `pass` |
| `180s` | `cracked-star-jar` | `0.3333` | `44.17` | `0.0792` | `pass` |
| `180s` | `soda-creek` | `0.0` | `18.5108` | `0.1047` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `3.8786` | `-0.116` | `pass` |
| `300s` | `cracked-star-jar` | `0.0` | `47.2373` | `0.0191` | `pass` |
| `300s` | `soda-creek` | `0.0` | `-27.0608` | `0.0194` | `regression` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0518` | `pass` |
| `60s` | `cracked-star-jar` | `0.3333` | `4.1778` | `-0.1679` | `pass` |
| `60s` | `soda-creek` | `0.3334` | `8.2888` | `0.0146` | `pass` |

## Blockers

- 300s/soda-creek: average_survival_seconds dropped 27.0608s beyond allowed 5.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
