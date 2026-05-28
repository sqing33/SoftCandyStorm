# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `8`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `0.1278` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `-14.4893` | `0.0089` | `regression` |
| `180s` | `soda-creek` | `0.3334` | `-14.3208` | `0.1512` | `regression` |
| `300s` | `caramel-workshop` | `0.0` | `-7.2793` | `-0.0325` | `regression` |
| `300s` | `cracked-star-jar` | `-0.3333` | `-28.6526` | `0.1734` | `regression` |
| `300s` | `soda-creek` | `0.0` | `-22.7782` | `0.1492` | `regression` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `-0.1032` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `-0.0596` | `pass` |
| `60s` | `soda-creek` | `-0.3333` | `-11.8554` | `0.0545` | `regression` |

## Blockers

- 180s/cracked-star-jar: average_survival_seconds dropped 14.4893s beyond allowed 0.0s
- 180s/soda-creek: average_survival_seconds dropped 14.3208s beyond allowed 0.0s
- 300s/caramel-workshop: average_survival_seconds dropped 7.2793s beyond allowed 0.0s
- 300s/cracked-star-jar: win_rate_delta -0.3333 below required 0.0
- 300s/cracked-star-jar: average_survival_seconds dropped 28.6526s beyond allowed 0.0s
- 300s/soda-creek: average_survival_seconds dropped 22.7782s beyond allowed 0.0s
- 60s/soda-creek: win_rate_delta -0.3333 below required 0.0
- 60s/soda-creek: average_survival_seconds dropped 11.8554s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
