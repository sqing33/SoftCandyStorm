# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `1`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Action L1 Δ | Max Action Ratio Δ | Entropy Δ | Status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `0.0` | `None` | `None` | `None` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `0.0` | `-0.1104` | `None` | `None` | `None` | `pass` |
| `180s` | `soda-creek` | `0.0` | `0.0` | `-0.0425` | `None` | `None` | `None` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `-0.1444` | `0.0005` | `None` | `None` | `None` | `regression` |
| `300s` | `cracked-star-jar` | `0.3333` | `22.6759` | `0.027` | `None` | `None` | `None` | `pass` |
| `300s` | `soda-creek` | `0.0` | `11.847` | `-0.0304` | `None` | `None` | `None` | `pass` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0002` | `None` | `None` | `None` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `None` | `None` | `None` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `0.0` | `None` | `None` | `None` | `pass` |

## Blockers

- 300s/caramel-workshop: average_survival_seconds dropped 0.1444s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
