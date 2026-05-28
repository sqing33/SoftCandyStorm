# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `4`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `-0.0458` | `pass` |
| `180s` | `cracked-star-jar` | `0.3333` | `14.6698` | `0.0554` | `pass` |
| `180s` | `soda-creek` | `0.0` | `-6.2791` | `-0.0748` | `regression` |
| `300s` | `caramel-workshop` | `0.0` | `-7.8128` | `-0.1387` | `regression` |
| `300s` | `cracked-star-jar` | `-0.3333` | `15.364` | `0.0829` | `regression` |
| `300s` | `soda-creek` | `0.0` | `-2.2005` | `0.0025` | `regression` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `0.0` | `pass` |

## Blockers

- 180s/soda-creek: average_survival_seconds dropped 6.2791s beyond allowed 0.0s
- 300s/caramel-workshop: average_survival_seconds dropped 7.8128s beyond allowed 0.0s
- 300s/cracked-star-jar: win_rate_delta -0.3333 below required 0.0
- 300s/soda-creek: average_survival_seconds dropped 2.2005s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
