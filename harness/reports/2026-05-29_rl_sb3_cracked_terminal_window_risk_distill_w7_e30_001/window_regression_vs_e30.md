# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `3`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `0.0358` | `pass` |
| `180s` | `cracked-star-jar` | `0.3333` | `44.17` | `0.0257` | `pass` |
| `180s` | `soda-creek` | `0.0` | `-9.4888` | `0.1496` | `regression` |
| `300s` | `caramel-workshop` | `0.0` | `4.112` | `-0.0723` | `pass` |
| `300s` | `cracked-star-jar` | `0.0` | `51.5938` | `0.0546` | `pass` |
| `300s` | `soda-creek` | `0.0` | `-56.3051` | `0.0548` | `regression` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.2081` | `regression` |
| `60s` | `cracked-star-jar` | `0.3333` | `4.1778` | `0.0049` | `pass` |
| `60s` | `soda-creek` | `0.3334` | `8.2888` | `-0.049` | `pass` |

## Blockers

- 180s/soda-creek: average_survival_seconds dropped 9.4888s beyond allowed 5.0s
- 300s/soda-creek: average_survival_seconds dropped 56.3051s beyond allowed 5.0s
- 60s/caramel-workshop: dominant_action_ratio increased 0.2081 beyond allowed 0.2

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
