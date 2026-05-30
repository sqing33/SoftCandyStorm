# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `1`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Action L1 Δ | Max Action Ratio Δ | Entropy Δ | Status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `5.6003` | `0.0297` | `None` | `None` | `None` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `0.0` | `-0.0827` | `None` | `None` | `None` | `pass` |
| `180s` | `soda-creek` | `0.0` | `0.0222` | `0.0696` | `None` | `None` | `None` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `1.9004` | `-0.0785` | `None` | `None` | `None` | `pass` |
| `300s` | `cracked-star-jar` | `0.0` | `-1.956` | `0.0399` | `None` | `None` | `None` | `regression` |
| `300s` | `soda-creek` | `0.0` | `18.3595` | `0.1078` | `None` | `None` | `None` | `pass` |
| `60s` | `caramel-workshop` | `0.0` | `0.0222` | `-0.0002` | `None` | `None` | `None` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `None` | `None` | `None` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0111` | `-0.0001` | `None` | `None` | `None` | `pass` |

## Blockers

- 300s/cracked-star-jar: average_survival_seconds dropped 1.956s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
