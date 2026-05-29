# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `9`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Action L1 Δ | Max Action Ratio Δ | Entropy Δ | Status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `-0.0225` | `None` | `None` | `None` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `-3.1111` | `-0.0123` | `None` | `None` | `None` | `regression` |
| `180s` | `soda-creek` | `0.0` | `-32.7355` | `-0.0885` | `None` | `None` | `None` | `regression` |
| `300s` | `caramel-workshop` | `0.0` | `-6.5347` | `0.1946` | `None` | `None` | `None` | `regression` |
| `300s` | `cracked-star-jar` | `0.0` | `-4.6225` | `0.13` | `None` | `None` | `None` | `regression` |
| `300s` | `soda-creek` | `0.0` | `-2.9339` | `-0.1056` | `None` | `None` | `None` | `regression` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `-0.0009` | `None` | `None` | `None` | `pass` |
| `60s` | `cracked-star-jar` | `-0.3333` | `-4.1778` | `0.0028` | `None` | `None` | `None` | `regression` |
| `60s` | `soda-creek` | `-0.3334` | `-8.2888` | `0.088` | `None` | `None` | `None` | `regression` |

## Blockers

- 180s/cracked-star-jar: average_survival_seconds dropped 3.1111s beyond allowed 0.0s
- 180s/soda-creek: average_survival_seconds dropped 32.7355s beyond allowed 0.0s
- 300s/caramel-workshop: average_survival_seconds dropped 6.5347s beyond allowed 0.0s
- 300s/cracked-star-jar: average_survival_seconds dropped 4.6225s beyond allowed 0.0s
- 300s/soda-creek: average_survival_seconds dropped 2.9339s beyond allowed 0.0s
- 60s/cracked-star-jar: win_rate_delta -0.3333 below required 0.0
- 60s/cracked-star-jar: average_survival_seconds dropped 4.1778s beyond allowed 0.0s
- 60s/soda-creek: win_rate_delta -0.3334 below required 0.0
- 60s/soda-creek: average_survival_seconds dropped 8.2888s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
