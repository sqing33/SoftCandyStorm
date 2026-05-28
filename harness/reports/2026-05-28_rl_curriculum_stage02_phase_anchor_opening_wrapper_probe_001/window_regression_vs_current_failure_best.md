# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `5`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `0.0507` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `8.5685` | `0.1839` | `pass` |
| `180s` | `soda-creek` | `0.0` | `-4.5889` | `0.1329` | `regression` |
| `300s` | `caramel-workshop` | `0.0` | `-8.3796` | `-0.0448` | `regression` |
| `300s` | `cracked-star-jar` | `-0.3333` | `-28.2655` | `0.1228` | `regression` |
| `300s` | `soda-creek` | `0.0` | `-18.2474` | `0.1381` | `regression` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `0.0` | `pass` |

## Blockers

- 180s/soda-creek: average_survival_seconds dropped 4.5889s beyond allowed 0.0s
- 300s/caramel-workshop: average_survival_seconds dropped 8.3796s beyond allowed 0.0s
- 300s/cracked-star-jar: win_rate_delta -0.3333 below required 0.0
- 300s/cracked-star-jar: average_survival_seconds dropped 28.2655s beyond allowed 0.0s
- 300s/soda-creek: average_survival_seconds dropped 18.2474s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
