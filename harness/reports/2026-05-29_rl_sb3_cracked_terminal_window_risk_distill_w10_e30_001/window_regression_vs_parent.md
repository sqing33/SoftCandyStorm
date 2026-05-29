# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `1`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `0.0655` | `pass` |
| `180s` | `cracked-star-jar` | `0.3333` | `41.0589` | `-0.0182` | `pass` |
| `180s` | `soda-creek` | `0.3334` | `5.4679` | `-0.0242` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `3.4563` | `0.1225` | `pass` |
| `300s` | `cracked-star-jar` | `0.0` | `51.35` | `-0.0123` | `pass` |
| `300s` | `soda-creek` | `0.0` | `2.8673` | `0.0813` | `pass` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.2259` | `regression` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.007` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `0.039` | `pass` |

## Blockers

- 60s/caramel-workshop: dominant_action_ratio increased 0.2259 beyond allowed 0.2

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
