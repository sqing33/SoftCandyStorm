# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `1`
- Candidate windows: `1`
- Blockers: `2`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Action L1 Δ | Max Action Ratio Δ | Entropy Δ | Status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.3333` | `46.1922` | `-0.0221` | `None` | `None` | `None` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `None` | `None` | `None` | `pass` |
| `180s` | `soda-creek` | `-0.3333` | `-47.4699` | `-0.0278` | `None` | `None` | `None` | `regression` |

## Blockers

- 180s/soda-creek: win_rate_delta -0.3333 below required 0.0
- 180s/soda-creek: average_survival_seconds dropped 47.4699s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
