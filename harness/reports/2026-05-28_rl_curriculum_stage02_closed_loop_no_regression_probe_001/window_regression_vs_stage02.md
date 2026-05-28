# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `14`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `-0.3333` | `-50.6921` | `0.0366` | `regression` |
| `180s` | `cracked-star-jar` | `-0.3333` | `-22.5147` | `-0.0341` | `regression` |
| `180s` | `soda-creek` | `-0.3334` | `-71.0492` | `0.0092` | `regression` |
| `300s` | `caramel-workshop` | `0.0` | `-59.1161` | `0.0856` | `regression` |
| `300s` | `cracked-star-jar` | `-0.3333` | `-21.616` | `0.0667` | `regression` |
| `300s` | `soda-creek` | `0.0` | `-107.3215` | `-0.0291` | `regression` |
| `60s` | `caramel-workshop` | `-0.3333` | `-10.6999` | `0.1043` | `regression` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0908` | `pass` |
| `60s` | `soda-creek` | `-0.3333` | `-11.8554` | `-0.1295` | `regression` |

## Blockers

- 180s/caramel-workshop: win_rate_delta -0.3333 below required 0.0
- 180s/caramel-workshop: average_survival_seconds dropped 50.6921s beyond allowed 5.0s
- 180s/cracked-star-jar: win_rate_delta -0.3333 below required 0.0
- 180s/cracked-star-jar: average_survival_seconds dropped 22.5147s beyond allowed 5.0s
- 180s/soda-creek: win_rate_delta -0.3334 below required 0.0
- 180s/soda-creek: average_survival_seconds dropped 71.0492s beyond allowed 5.0s
- 300s/caramel-workshop: average_survival_seconds dropped 59.1161s beyond allowed 5.0s
- 300s/cracked-star-jar: win_rate_delta -0.3333 below required 0.0
- 300s/cracked-star-jar: average_survival_seconds dropped 21.616s beyond allowed 5.0s
- 300s/soda-creek: average_survival_seconds dropped 107.3215s beyond allowed 5.0s
- 60s/caramel-workshop: win_rate_delta -0.3333 below required 0.0
- 60s/caramel-workshop: average_survival_seconds dropped 10.6999s beyond allowed 5.0s
- 60s/soda-creek: win_rate_delta -0.3333 below required 0.0
- 60s/soda-creek: average_survival_seconds dropped 11.8554s beyond allowed 5.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
