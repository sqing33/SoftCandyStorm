# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `2`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Action L1 Δ | Max Action Ratio Δ | Entropy Δ | Status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `0.0016` | `None` | `None` | `None` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `0.0` | `-0.0209` | `None` | `None` | `None` | `pass` |
| `180s` | `soda-creek` | `0.0` | `0.0` | `-0.0173` | `None` | `None` | `None` | `pass` |
| `300s` | `caramel-workshop` | `0.3333` | `17.0636` | `0.028` | `None` | `None` | `None` | `pass` |
| `300s` | `cracked-star-jar` | `0.6667` | `10.2753` | `-0.0186` | `None` | `None` | `None` | `pass` |
| `300s` | `soda-creek` | `0.0` | `0.0` | `-0.0194` | `None` | `None` | `None` | `pass` |
| `60s` | `caramel-workshop` | `-0.3333` | `-4.1111` | `0.0407` | `None` | `None` | `None` | `regression` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `None` | `None` | `None` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `0.0` | `None` | `None` | `None` | `pass` |

## Blockers

- 60s/caramel-workshop: win_rate_delta -0.3333 below required 0.0
- 60s/caramel-workshop: average_survival_seconds dropped 4.1111s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
