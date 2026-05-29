# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `3`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `0.0935` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `13.4109` | `0.0892` | `pass` |
| `180s` | `soda-creek` | `0.0` | `-36.391` | `0.0026` | `regression` |
| `300s` | `caramel-workshop` | `0.0` | `-2.7005` | `0.094` | `pass` |
| `300s` | `cracked-star-jar` | `0.0` | `10.4873` | `0.2153` | `regression` |
| `300s` | `soda-creek` | `0.0` | `-23.5161` | `-0.0423` | `regression` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.1588` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `-0.0195` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `-0.0593` | `pass` |

## Blockers

- 180s/soda-creek: average_survival_seconds dropped 36.391s beyond allowed 5.0s
- 300s/cracked-star-jar: dominant_action_ratio increased 0.2153 beyond allowed 0.2
- 300s/soda-creek: average_survival_seconds dropped 23.5161s beyond allowed 5.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
