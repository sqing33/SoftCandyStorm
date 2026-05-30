# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `1`
- Candidate windows: `1`
- Blockers: `2`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Action L1 Δ | Max Action Ratio Δ | Entropy Δ | Status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `60s` | `caramel-workshop` | `0.3333` | `6.1999` | `0.0767` | `None` | `None` | `None` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `None` | `None` | `None` | `pass` |
| `60s` | `soda-creek` | `-0.3333` | `-7.5666` | `-0.0143` | `None` | `None` | `None` | `regression` |

## Blockers

- 60s/soda-creek: win_rate_delta -0.3333 below required 0.0
- 60s/soda-creek: average_survival_seconds dropped 7.5666s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
