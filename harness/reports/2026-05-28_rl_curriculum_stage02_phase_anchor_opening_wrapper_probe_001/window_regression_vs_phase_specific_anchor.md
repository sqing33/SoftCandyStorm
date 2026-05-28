# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `3`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `0.0505` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `23.0578` | `0.0537` | `pass` |
| `180s` | `soda-creek` | `-0.3334` | `9.7319` | `0.1184` | `regression` |
| `300s` | `caramel-workshop` | `0.0` | `1.6114` | `-0.0695` | `pass` |
| `300s` | `cracked-star-jar` | `0.0` | `-2.5572` | `-0.0974` | `regression` |
| `300s` | `soda-creek` | `0.0` | `-0.9704` | `-0.0292` | `regression` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.1032` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0596` | `pass` |
| `60s` | `soda-creek` | `0.3333` | `11.8554` | `-0.066` | `pass` |

## Blockers

- 180s/soda-creek: win_rate_delta -0.3334 below required 0.0
- 300s/cracked-star-jar: average_survival_seconds dropped 2.5572s beyond allowed 0.0s
- 300s/soda-creek: average_survival_seconds dropped 0.9704s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
