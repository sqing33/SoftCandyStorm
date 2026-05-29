# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `7`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `-0.3334` | `-42.0811` | `0.115` | `regression` |
| `180s` | `cracked-star-jar` | `0.3333` | `41.0589` | `0.2068` | `regression` |
| `180s` | `soda-creek` | `0.0` | `-39.9354` | `0.1714` | `regression` |
| `300s` | `caramel-workshop` | `0.0` | `-59.4181` | `0.0451` | `regression` |
| `300s` | `cracked-star-jar` | `0.3333` | `95.3277` | `0.0408` | `pass` |
| `300s` | `soda-creek` | `0.0` | `-56.3611` | `0.0795` | `regression` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0232` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `-0.0891` | `pass` |
| `60s` | `soda-creek` | `-0.3334` | `-0.8` | `-0.0674` | `regression` |

## Blockers

- 180s/caramel-workshop: win_rate_delta -0.3334 below required 0.0
- 180s/caramel-workshop: average_survival_seconds dropped 42.0811s beyond allowed 5.0s
- 180s/cracked-star-jar: dominant_action_ratio increased 0.2068 beyond allowed 0.2
- 180s/soda-creek: average_survival_seconds dropped 39.9354s beyond allowed 5.0s
- 300s/caramel-workshop: average_survival_seconds dropped 59.4181s beyond allowed 5.0s
- 300s/soda-creek: average_survival_seconds dropped 56.3611s beyond allowed 5.0s
- 60s/soda-creek: win_rate_delta -0.3334 below required 0.0

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
