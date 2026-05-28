# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `6`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `-0.1828` | `pass` |
| `180s` | `cracked-star-jar` | `-0.3333` | `-27.348` | `-0.106` | `regression` |
| `180s` | `soda-creek` | `0.0` | `-18.8349` | `0.016` | `regression` |
| `300s` | `caramel-workshop` | `0.0` | `6.6236` | `-0.0996` | `pass` |
| `300s` | `cracked-star-jar` | `-0.3333` | `-63.1601` | `-0.012` | `regression` |
| `300s` | `soda-creek` | `0.0` | `-51.1301` | `-0.0385` | `regression` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `-0.2403` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `-0.0378` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `-0.2321` | `pass` |

## Blockers

- 180s/cracked-star-jar: win_rate_delta -0.3333 below required 0.0
- 180s/cracked-star-jar: average_survival_seconds dropped 27.348s beyond allowed 5.0s
- 180s/soda-creek: average_survival_seconds dropped 18.8349s beyond allowed 5.0s
- 300s/cracked-star-jar: win_rate_delta -0.3333 below required 0.0
- 300s/cracked-star-jar: average_survival_seconds dropped 63.1601s beyond allowed 5.0s
- 300s/soda-creek: average_survival_seconds dropped 51.1301s beyond allowed 5.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
