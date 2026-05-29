# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `2`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `0.1612` | `pass` |
| `180s` | `cracked-star-jar` | `0.3333` | `41.0589` | `0.0669` | `pass` |
| `180s` | `soda-creek` | `0.0` | `-14.2247` | `0.0162` | `regression` |
| `300s` | `caramel-workshop` | `0.0` | `-2.6561` | `0.0786` | `pass` |
| `300s` | `cracked-star-jar` | `0.0` | `42.537` | `0.1479` | `pass` |
| `300s` | `soda-creek` | `0.0` | `-29.9947` | `-0.0862` | `regression` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0509` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `-0.1651` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `0.1026` | `pass` |

## Blockers

- 180s/soda-creek: average_survival_seconds dropped 14.2247s beyond allowed 5.0s
- 300s/soda-creek: average_survival_seconds dropped 29.9947s beyond allowed 5.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
