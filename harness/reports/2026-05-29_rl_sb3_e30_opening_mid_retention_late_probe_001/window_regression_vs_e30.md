# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `2`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `0.2638` | `regression` |
| `180s` | `cracked-star-jar` | `0.3333` | `44.17` | `0.0139` | `pass` |
| `180s` | `soda-creek` | `0.3334` | `38.2034` | `0.0711` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `3.7675` | `-0.0427` | `pass` |
| `300s` | `cracked-star-jar` | `0.6667` | `106.9033` | `-0.1182` | `pass` |
| `300s` | `soda-creek` | `0.0` | `-24.3608` | `0.0827` | `regression` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0164` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `3.1111` | `-0.015` | `pass` |
| `60s` | `soda-creek` | `0.3334` | `8.2888` | `-0.0873` | `pass` |

## Blockers

- 180s/caramel-workshop: dominant_action_ratio increased 0.2638 beyond allowed 0.2
- 300s/soda-creek: average_survival_seconds dropped 24.3608s beyond allowed 5.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
