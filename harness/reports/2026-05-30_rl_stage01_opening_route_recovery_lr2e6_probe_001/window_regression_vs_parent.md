# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `2`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Action L1 Δ | Max Action Ratio Δ | Entropy Δ | Status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `-0.0444` | `0.0002` | `None` | `None` | `None` | `regression` |
| `180s` | `cracked-star-jar` | `0.0` | `0.0` | `-0.0457` | `None` | `None` | `None` | `pass` |
| `180s` | `soda-creek` | `0.0` | `0.0111` | `-0.065` | `None` | `None` | `None` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `-0.1444` | `0.0005` | `None` | `None` | `None` | `regression` |
| `300s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `None` | `None` | `None` | `pass` |
| `300s` | `soda-creek` | `0.0` | `11.5247` | `-0.0358` | `None` | `None` | `None` | `pass` |
| `60s` | `caramel-workshop` | `0.3333` | `6.1999` | `-0.0085` | `None` | `None` | `None` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.1557` | `None` | `None` | `None` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `0.0` | `None` | `None` | `None` | `pass` |

## Blockers

- 180s/caramel-workshop: average_survival_seconds dropped 0.0444s beyond allowed 0.0s
- 300s/caramel-workshop: average_survival_seconds dropped 0.1444s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
