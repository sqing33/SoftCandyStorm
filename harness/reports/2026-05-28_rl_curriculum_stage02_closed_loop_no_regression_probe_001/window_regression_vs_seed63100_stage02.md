# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `4`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `-0.1578` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0848` | `pass` |
| `180s` | `soda-creek` | `0.0` | `-15.8886` | `-0.0103` | `regression` |
| `300s` | `caramel-workshop` | `0.0` | `-1.0002` | `0.058` | `pass` |
| `300s` | `cracked-star-jar` | `0.0` | `27.7978` | `0.1169` | `pass` |
| `300s` | `soda-creek` | `0.0` | `-10.1751` | `0.0322` | `regression` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0211` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.1375` | `pass` |
| `60s` | `soda-creek` | `-0.3333` | `-11.8554` | `0.0545` | `regression` |

## Blockers

- 180s/soda-creek: average_survival_seconds dropped 15.8886s beyond allowed 5.0s
- 300s/soda-creek: average_survival_seconds dropped 10.1751s beyond allowed 5.0s
- 60s/soda-creek: win_rate_delta -0.3333 below required 0.0
- 60s/soda-creek: average_survival_seconds dropped 11.8554s beyond allowed 5.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
