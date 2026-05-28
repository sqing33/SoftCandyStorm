# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `5`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180` | `caramel-workshop` | `0.0` | `0.0` | `0.2067` | `pass` |
| `180` | `cracked-star-jar` | `0.0` | `9.6554` | `0.176` | `pass` |
| `180` | `soda-creek` | `-0.3334` | `-12.0816` | `-0.1493` | `regression` |
| `300` | `caramel-workshop` | `0.0` | `1.0224` | `0.0252` | `pass` |
| `300` | `cracked-star-jar` | `-0.3333` | `-8.8419` | `0.1484` | `regression` |
| `300` | `soda-creek` | `0.0` | `-29.842` | `0.0502` | `regression` |
| `60` | `caramel-workshop` | `0.0` | `0.0` | `0.1032` | `pass` |
| `60` | `cracked-star-jar` | `0.0` | `0.0` | `0.0596` | `pass` |
| `60` | `soda-creek` | `0.3333` | `11.8554` | `-0.0545` | `pass` |

## Blockers

- 180/soda-creek: win_rate_delta -0.3334 below required 0.0
- 180/soda-creek: average_survival_seconds dropped 12.0816s beyond allowed 0.0s
- 300/cracked-star-jar: win_rate_delta -0.3333 below required 0.0
- 300/cracked-star-jar: average_survival_seconds dropped 8.8419s beyond allowed 0.0s
- 300/soda-creek: average_survival_seconds dropped 29.842s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
