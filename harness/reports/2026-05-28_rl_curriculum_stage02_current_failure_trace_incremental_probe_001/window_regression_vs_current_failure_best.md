# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `2`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `-0.0563` | `pass` |
| `180s` | `cracked-star-jar` | `0.3333` | `14.6698` | `0.0345` | `pass` |
| `180s` | `soda-creek` | `0.3334` | `5.2011` | `-0.0011` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `-8.1795` | `-0.1457` | `regression` |
| `300s` | `cracked-star-jar` | `-0.3333` | `27.5619` | `0.1406` | `regression` |
| `300s` | `soda-creek` | `0.3333` | `30.6554` | `0.0108` | `pass` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `0.0` | `pass` |

## Blockers

- 300s/caramel-workshop: average_survival_seconds dropped 8.1795s beyond allowed 0.0s
- 300s/cracked-star-jar: win_rate_delta -0.3333 below required 0.0

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
