# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `7`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `-0.3334` | `-42.0811` | `0.1375` | `regression` |
| `180s` | `cracked-star-jar` | `0.3333` | `44.17` | `0.2191` | `regression` |
| `180s` | `soda-creek` | `0.0` | `-7.1999` | `0.2599` | `regression` |
| `300s` | `caramel-workshop` | `0.0` | `-52.8834` | `-0.1495` | `regression` |
| `300s` | `cracked-star-jar` | `0.3333` | `100.028` | `-0.088` | `pass` |
| `300s` | `soda-creek` | `0.0` | `-53.4272` | `0.1851` | `regression` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0241` | `pass` |
| `60s` | `cracked-star-jar` | `0.3333` | `4.1778` | `-0.0919` | `pass` |
| `60s` | `soda-creek` | `0.0` | `7.4888` | `-0.1554` | `pass` |

## Blockers

- 180s/caramel-workshop: win_rate_delta -0.3334 below required 0.0
- 180s/caramel-workshop: average_survival_seconds dropped 42.0811s beyond allowed 5.0s
- 180s/cracked-star-jar: dominant_action_ratio increased 0.2191 beyond allowed 0.2
- 180s/soda-creek: average_survival_seconds dropped 7.1999s beyond allowed 5.0s
- 180s/soda-creek: dominant_action_ratio increased 0.2599 beyond allowed 0.2
- 300s/caramel-workshop: average_survival_seconds dropped 52.8834s beyond allowed 5.0s
- 300s/soda-creek: average_survival_seconds dropped 53.4272s beyond allowed 5.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
