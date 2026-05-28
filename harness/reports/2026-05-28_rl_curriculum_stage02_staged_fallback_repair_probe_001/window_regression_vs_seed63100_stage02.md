# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `2`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `-0.4153` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `-5.9777` | `-0.1224` | `regression` |
| `180s` | `soda-creek` | `0.0` | `6.4444` | `-0.1155` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `-2.156` | `-0.3337` | `pass` |
| `300s` | `cracked-star-jar` | `0.0` | `-16.491` | `0.026` | `regression` |
| `300s` | `soda-creek` | `0.0` | `2.078` | `-0.1083` | `pass` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `0.0` | `pass` |

## Blockers

- 180s/cracked-star-jar: average_survival_seconds dropped 5.9777s beyond allowed 5.0s
- 300s/cracked-star-jar: average_survival_seconds dropped 16.491s beyond allowed 5.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
