# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `2`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.3333` | `50.6921` | `-0.4196` | `pass` |
| `180s` | `cracked-star-jar` | `0.3333` | `22.5147` | `0.0379` | `pass` |
| `180s` | `soda-creek` | `0.3334` | `18.4259` | `-0.0158` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `65.1952` | `-0.2231` | `pass` |
| `300s` | `cracked-star-jar` | `0.0` | `39.2628` | `0.0928` | `pass` |
| `300s` | `soda-creek` | `0.0` | `45.6844` | `0.0631` | `pass` |
| `60s` | `caramel-workshop` | `0.3333` | `10.6999` | `-0.2985` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `-0.1157` | `pass` |
| `60s` | `soda-creek` | `-0.3333` | `-5.8111` | `-0.0678` | `regression` |

## Blockers

- 60s/soda-creek: win_rate_delta -0.3333 below required 0.0
- 60s/soda-creek: average_survival_seconds dropped 5.8111s beyond allowed 5.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
