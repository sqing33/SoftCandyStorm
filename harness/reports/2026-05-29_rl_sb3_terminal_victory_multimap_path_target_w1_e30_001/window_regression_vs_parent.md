# Policy Window Regression

- Decision: `policy_window_regression_passed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `0`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Action L1 Δ | Max Action Ratio Δ | Entropy Δ | Status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `pass` |
| `180s` | `soda-creek` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `pass` |
| `300s` | `cracked-star-jar` | `0.0` | `9.9003` | `0.0906` | `0.1811` | `0.0906` | `-0.0272` | `pass` |
| `300s` | `soda-creek` | `0.0` | `3.2452` | `-0.0074` | `0.0556` | `0.0278` | `-0.0072` | `pass` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `pass` |

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
