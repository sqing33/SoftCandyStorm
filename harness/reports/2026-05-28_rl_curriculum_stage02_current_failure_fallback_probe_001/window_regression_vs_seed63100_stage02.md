# Policy Window Regression

- Decision: `policy_window_regression_passed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `0`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `-0.4738` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `7.8449` | `-0.1109` | `pass` |
| `180s` | `soda-creek` | `0.0` | `26.7024` | `-0.1025` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `7.735` | `-0.2077` | `pass` |
| `300s` | `cracked-star-jar` | `0.3333` | `20.1075` | `-0.0992` | `pass` |
| `300s` | `soda-creek` | `0.0` | `39.0285` | `-0.137` | `pass` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `0.0` | `pass` |

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
