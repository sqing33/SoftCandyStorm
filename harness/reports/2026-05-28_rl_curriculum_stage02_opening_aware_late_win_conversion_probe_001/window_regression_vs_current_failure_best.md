# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `8`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `0.0121` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `-14.4893` | `0.014` | `regression` |
| `180s` | `soda-creek` | `0.0` | `-20.6555` | `0.0646` | `regression` |
| `300s` | `caramel-workshop` | `0.0` | `-4.8233` | `-0.1294` | `regression` |
| `300s` | `cracked-star-jar` | `-0.3333` | `-34.4535` | `0.0478` | `regression` |
| `300s` | `soda-creek` | `0.0` | `-27.0569` | `0.0789` | `regression` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `-0.1032` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `-0.0596` | `pass` |
| `60s` | `soda-creek` | `-0.3333` | `-11.8554` | `0.0545` | `regression` |

## Blockers

- 180s/cracked-star-jar: average_survival_seconds dropped 14.4893s beyond allowed 0.0s
- 180s/soda-creek: average_survival_seconds dropped 20.6555s beyond allowed 0.0s
- 300s/caramel-workshop: average_survival_seconds dropped 4.8233s beyond allowed 0.0s
- 300s/cracked-star-jar: win_rate_delta -0.3333 below required 0.0
- 300s/cracked-star-jar: average_survival_seconds dropped 34.4535s beyond allowed 0.0s
- 300s/soda-creek: average_survival_seconds dropped 27.0569s beyond allowed 0.0s
- 60s/soda-creek: win_rate_delta -0.3333 below required 0.0
- 60s/soda-creek: average_survival_seconds dropped 11.8554s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
