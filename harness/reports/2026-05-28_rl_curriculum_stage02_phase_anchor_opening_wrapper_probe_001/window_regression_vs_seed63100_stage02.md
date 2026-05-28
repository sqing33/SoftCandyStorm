# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `2`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `-0.4231` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `16.4134` | `0.073` | `pass` |
| `180s` | `soda-creek` | `0.0` | `22.1135` | `0.0304` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `-0.6446` | `-0.2525` | `regression` |
| `300s` | `cracked-star-jar` | `0.0` | `-8.158` | `0.0236` | `regression` |
| `300s` | `soda-creek` | `0.0` | `20.7811` | `0.0011` | `pass` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `0.0` | `pass` |

## Blockers

- 300s/caramel-workshop: average_survival_seconds dropped 0.6446s beyond allowed 0.0s
- 300s/cracked-star-jar: average_survival_seconds dropped 8.158s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
