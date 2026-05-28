# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `5`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.3333` | `50.6921` | `-0.0316` | `pass` |
| `180s` | `cracked-star-jar` | `0.3333` | `14.6698` | `0.0695` | `pass` |
| `180s` | `soda-creek` | `-0.3333` | `-73.2607` | `0.2878` | `regression` |
| `300s` | `caramel-workshop` | `0.0` | `52.8814` | `0.0336` | `pass` |
| `300s` | `cracked-star-jar` | `0.0` | `20.5044` | `0.0812` | `pass` |
| `300s` | `soda-creek` | `0.0` | `-102.9115` | `0.355` | `regression` |
| `60s` | `caramel-workshop` | `0.3333` | `10.6999` | `-0.1169` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0939` | `pass` |
| `60s` | `soda-creek` | `-0.6667` | `-15.8109` | `0.217` | `regression` |

## Blockers

- 180s/soda-creek: win_rate_delta -0.3333 below required 0.0
- 180s/soda-creek: average_survival_seconds dropped 73.2607s beyond allowed 0.0s
- 300s/soda-creek: average_survival_seconds dropped 102.9115s beyond allowed 0.0s
- 60s/soda-creek: win_rate_delta -0.6667 below required 0.0
- 60s/soda-creek: average_survival_seconds dropped 15.8109s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
