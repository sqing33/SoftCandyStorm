# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `4`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `-0.346` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `-6.6444` | `-0.102` | `regression` |
| `180s` | `soda-creek` | `0.3334` | `12.3816` | `0.0487` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `0.4557` | `-0.2402` | `pass` |
| `300s` | `cracked-star-jar` | `0.0` | `-8.5451` | `0.0742` | `regression` |
| `300s` | `soda-creek` | `0.0` | `16.2503` | `0.0122` | `pass` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `-0.1032` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `-0.0596` | `pass` |
| `60s` | `soda-creek` | `-0.3333` | `-11.8554` | `0.0545` | `regression` |

## Blockers

- 180s/cracked-star-jar: average_survival_seconds dropped 6.6444s beyond allowed 0.0s
- 300s/cracked-star-jar: average_survival_seconds dropped 8.5451s beyond allowed 0.0s
- 60s/soda-creek: win_rate_delta -0.3333 below required 0.0
- 60s/soda-creek: average_survival_seconds dropped 11.8554s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
