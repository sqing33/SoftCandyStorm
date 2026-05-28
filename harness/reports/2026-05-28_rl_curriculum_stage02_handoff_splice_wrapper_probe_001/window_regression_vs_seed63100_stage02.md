# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `1`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `-0.5196` | `pass` |
| `180s` | `cracked-star-jar` | `0.3333` | `22.5147` | `-0.0555` | `pass` |
| `180s` | `soda-creek` | `0.0` | `20.4233` | `-0.1773` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `-0.0778` | `-0.3464` | `regression` |
| `300s` | `cracked-star-jar` | `0.0` | `35.4715` | `-0.0163` | `pass` |
| `300s` | `soda-creek` | `0.0` | `36.828` | `-0.1345` | `pass` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `0.0` | `pass` |

## Blockers

- 300s/caramel-workshop: average_survival_seconds dropped 0.0778s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
