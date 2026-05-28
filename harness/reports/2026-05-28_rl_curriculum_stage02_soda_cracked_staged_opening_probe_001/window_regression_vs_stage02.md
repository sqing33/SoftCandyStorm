# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `11`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `-0.3333` | `-50.6921` | `-0.0035` | `regression` |
| `180s` | `cracked-star-jar` | `-0.3333` | `-17.4593` | `-0.1051` | `regression` |
| `180s` | `soda-creek` | `-0.3334` | `-43.2048` | `0.0265` | `regression` |
| `300s` | `caramel-workshop` | `0.0` | `-59.205` | `-0.0537` | `regression` |
| `300s` | `cracked-star-jar` | `0.0` | `-25.6277` | `-0.0071` | `regression` |
| `300s` | `soda-creek` | `0.0` | `-90.5239` | `-0.0202` | `regression` |
| `60s` | `caramel-workshop` | `-0.3333` | `-10.6999` | `0.0832` | `regression` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `-0.0467` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `-0.184` | `pass` |

## Blockers

- 180s/caramel-workshop: win_rate_delta -0.3333 below required 0.0
- 180s/caramel-workshop: average_survival_seconds dropped 50.6921s beyond allowed 5.0s
- 180s/cracked-star-jar: win_rate_delta -0.3333 below required 0.0
- 180s/cracked-star-jar: average_survival_seconds dropped 17.4593s beyond allowed 5.0s
- 180s/soda-creek: win_rate_delta -0.3334 below required 0.0
- 180s/soda-creek: average_survival_seconds dropped 43.2048s beyond allowed 5.0s
- 300s/caramel-workshop: average_survival_seconds dropped 59.205s beyond allowed 5.0s
- 300s/cracked-star-jar: average_survival_seconds dropped 25.6277s beyond allowed 5.0s
- 300s/soda-creek: average_survival_seconds dropped 90.5239s beyond allowed 5.0s
- 60s/caramel-workshop: win_rate_delta -0.3333 below required 0.0
- 60s/caramel-workshop: average_survival_seconds dropped 10.6999s beyond allowed 5.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
