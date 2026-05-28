# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `10`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `-0.1974` | `pass` |
| `180s` | `cracked-star-jar` | `-0.6667` | `-55.1393` | `-0.0844` | `regression` |
| `180s` | `soda-creek` | `-0.6667` | `-104.6304` | `0.1234` | `regression` |
| `300s` | `caramel-workshop` | `0.0` | `8.7908` | `-0.2087` | `pass` |
| `300s` | `cracked-star-jar` | `-0.3333` | `-108.6551` | `0.1768` | `regression` |
| `300s` | `soda-creek` | `0.0` | `-172.3742` | `-0.1175` | `regression` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `-0.1048` | `pass` |
| `60s` | `cracked-star-jar` | `-0.3333` | `-2.7889` | `-0.1038` | `regression` |
| `60s` | `soda-creek` | `-0.6667` | `-16.5665` | `-0.2299` | `regression` |

## Blockers

- 180s/cracked-star-jar: win_rate_delta -0.6667 below required 0.0
- 180s/cracked-star-jar: average_survival_seconds dropped 55.1393s beyond allowed 5.0s
- 180s/soda-creek: win_rate_delta -0.6667 below required 0.0
- 180s/soda-creek: average_survival_seconds dropped 104.6304s beyond allowed 5.0s
- 300s/cracked-star-jar: win_rate_delta -0.3333 below required 0.0
- 300s/cracked-star-jar: average_survival_seconds dropped 108.6551s beyond allowed 5.0s
- 300s/soda-creek: average_survival_seconds dropped 172.3742s beyond allowed 5.0s
- 60s/cracked-star-jar: win_rate_delta -0.3333 below required 0.0
- 60s/soda-creek: win_rate_delta -0.6667 below required 0.0
- 60s/soda-creek: average_survival_seconds dropped 16.5665s beyond allowed 5.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
