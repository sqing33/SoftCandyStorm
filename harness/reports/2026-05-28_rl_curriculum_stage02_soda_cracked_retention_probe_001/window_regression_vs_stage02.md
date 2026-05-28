# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `6`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `-0.2252` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `0.0` | `-0.081` | `pass` |
| `180s` | `soda-creek` | `0.0` | `-36.7347` | `0.0037` | `regression` |
| `300s` | `caramel-workshop` | `0.0` | `7.0793` | `-0.1955` | `pass` |
| `300s` | `cracked-star-jar` | `-0.3333` | `-10.151` | `0.0426` | `regression` |
| `300s` | `soda-creek` | `0.0` | `-51.462` | `0.0018` | `regression` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `-0.2153` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `-0.1624` | `pass` |
| `60s` | `soda-creek` | `-0.3333` | `-5.8111` | `-0.2518` | `regression` |

## Blockers

- 180s/soda-creek: average_survival_seconds dropped 36.7347s beyond allowed 5.0s
- 300s/cracked-star-jar: win_rate_delta -0.3333 below required 0.0
- 300s/cracked-star-jar: average_survival_seconds dropped 10.151s beyond allowed 5.0s
- 300s/soda-creek: average_survival_seconds dropped 51.462s beyond allowed 5.0s
- 60s/soda-creek: win_rate_delta -0.3333 below required 0.0
- 60s/soda-creek: average_survival_seconds dropped 5.8111s beyond allowed 5.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
