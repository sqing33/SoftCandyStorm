# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `1`
- Candidate windows: `1`
- Blockers: `1`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Action L1 Δ | Max Action Ratio Δ | Entropy Δ | Status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `300s` | `caramel-workshop` | `0.0` | `-4.1909` | `0.0167` | `None` | `None` | `None` | `regression` |

## Blockers

- 300s/caramel-workshop: average_survival_seconds dropped 4.1909s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
