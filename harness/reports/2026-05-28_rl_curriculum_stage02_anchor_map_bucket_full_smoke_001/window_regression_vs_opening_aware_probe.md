# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `1`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `0.1157` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `0.0` | `-0.0051` | `pass` |
| `180s` | `soda-creek` | `0.3334` | `6.3347` | `0.0866` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `-2.456` | `0.0969` | `regression` |
| `300s` | `cracked-star-jar` | `0.0` | `5.8009` | `0.1256` | `pass` |
| `300s` | `soda-creek` | `0.0` | `4.2787` | `0.0703` | `pass` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `0.0` | `pass` |

## Blockers

- 300s/caramel-workshop: average_survival_seconds dropped 2.456s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
