# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `5`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `-0.4736` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `-6.6444` | `0.0193` | `regression` |
| `180s` | `soda-creek` | `0.3334` | `12.3816` | `-0.088` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `-2.256` | `-0.183` | `regression` |
| `300s` | `cracked-star-jar` | `0.0` | `-5.6008` | `0.121` | `regression` |
| `300s` | `soda-creek` | `0.0` | `21.7515` | `0.0303` | `pass` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `-0.1032` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `-0.0596` | `pass` |
| `60s` | `soda-creek` | `-0.3333` | `-11.8554` | `0.066` | `regression` |

## Blockers

- 180s/cracked-star-jar: average_survival_seconds dropped 6.6444s beyond allowed 0.0s
- 300s/caramel-workshop: average_survival_seconds dropped 2.256s beyond allowed 0.0s
- 300s/cracked-star-jar: average_survival_seconds dropped 5.6008s beyond allowed 0.0s
- 60s/soda-creek: win_rate_delta -0.3333 below required 0.0
- 60s/soda-creek: average_survival_seconds dropped 11.8554s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
