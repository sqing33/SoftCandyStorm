# Policy Window Regression

- Decision: `policy_window_regression_passed`
- Baseline windows: `1`
- Candidate windows: `1`
- Blockers: `0`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Action L1 Δ | Max Action Ratio Δ | Entropy Δ | Status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `60s` | `caramel-workshop` | `0.3333` | `6.1999` | `0.0767` | `None` | `None` | `None` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `None` | `None` | `None` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `0.0544` | `None` | `None` | `None` | `pass` |

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
