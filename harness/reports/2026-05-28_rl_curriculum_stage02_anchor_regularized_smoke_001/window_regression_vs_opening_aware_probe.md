# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `1`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `-0.058` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `0.0` | `-0.0203` | `pass` |
| `180s` | `soda-creek` | `0.3334` | `6.3347` | `0.1028` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `-3.0339` | `0.0229` | `regression` |
| `300s` | `cracked-star-jar` | `0.3333` | `17.7416` | `-0.0014` | `pass` |
| `300s` | `soda-creek` | `0.0` | `23.1593` | `0.0306` | `pass` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `0.0` | `pass` |

## Blockers

- 300s/caramel-workshop: average_survival_seconds dropped 3.0339s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
