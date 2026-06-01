# Policy Window Regression

- Decision: `policy_window_regression_passed`
- Baseline windows: `1`
- Candidate windows: `1`
- Blockers: `0`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Action L1 Δ | Max Action Ratio Δ | Entropy Δ | Status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `300s` | `caramel-workshop` | `0.0` | `17.195` | `-0.0046` | `0.037` | `0.0118` | `0.0012` | `pass` |

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
