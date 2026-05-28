# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `1`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `-0.0119` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `0.0` | `0.1162` | `pass` |
| `180s` | `soda-creek` | `0.3334` | `6.3347` | `-0.0501` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `-5.1677` | `0.1541` | `regression` |
| `300s` | `cracked-star-jar` | `0.0` | `8.7452` | `0.1724` | `pass` |
| `300s` | `soda-creek` | `0.0` | `9.7799` | `0.0884` | `pass` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `0.0115` | `pass` |

## Blockers

- 300s/caramel-workshop: average_survival_seconds dropped 5.1677s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
