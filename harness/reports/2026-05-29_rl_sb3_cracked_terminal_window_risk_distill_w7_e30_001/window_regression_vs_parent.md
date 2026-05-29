# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `3`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `0.0133` | `pass` |
| `180s` | `cracked-star-jar` | `0.3333` | `41.0589` | `0.0134` | `pass` |
| `180s` | `soda-creek` | `0.0` | `-42.2243` | `0.0611` | `regression` |
| `300s` | `caramel-workshop` | `0.0` | `-2.4227` | `0.1223` | `pass` |
| `300s` | `cracked-star-jar` | `0.0` | `46.8935` | `0.1834` | `pass` |
| `300s` | `soda-creek` | `0.0` | `-59.239` | `-0.0508` | `regression` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.2072` | `regression` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0077` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `0.039` | `pass` |

## Blockers

- 180s/soda-creek: average_survival_seconds dropped 42.2243s beyond allowed 5.0s
- 300s/soda-creek: average_survival_seconds dropped 59.239s beyond allowed 5.0s
- 60s/caramel-workshop: dominant_action_ratio increased 0.2072 beyond allowed 0.2

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
