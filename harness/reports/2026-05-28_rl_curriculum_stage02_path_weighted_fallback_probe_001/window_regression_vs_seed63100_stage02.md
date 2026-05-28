# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `2`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `-0.4666` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `-9.1443` | `-0.0576` | `regression` |
| `180s` | `soda-creek` | `0.0` | `1.9111` | `-0.1195` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `6.4236` | `-0.0186` | `pass` |
| `300s` | `cracked-star-jar` | `0.3333` | `1.5179` | `-0.0024` | `pass` |
| `300s` | `soda-creek` | `0.0` | `-2.2886` | `-0.066` | `regression` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `0.0` | `pass` |

## Blockers

- 180s/cracked-star-jar: average_survival_seconds dropped 9.1443s beyond allowed 0.0s
- 300s/soda-creek: average_survival_seconds dropped 2.2886s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
