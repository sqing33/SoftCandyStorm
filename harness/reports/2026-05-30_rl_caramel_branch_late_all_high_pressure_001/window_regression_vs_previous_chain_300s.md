# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `1`
- Candidate windows: `1`
- Blockers: `2`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Action L1 Δ | Max Action Ratio Δ | Entropy Δ | Status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `300s` | `caramel-workshop` | `0.0` | `67.9857` | `-0.0039` | `None` | `None` | `None` | `pass` |
| `300s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `None` | `None` | `None` | `pass` |
| `300s` | `soda-creek` | `-0.6667` | `-92.0373` | `-0.0503` | `None` | `None` | `None` | `regression` |

## Blockers

- 300s/soda-creek: win_rate_delta -0.6667 below required 0.0
- 300s/soda-creek: average_survival_seconds dropped 92.0373s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
