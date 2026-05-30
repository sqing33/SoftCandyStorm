# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `2`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Action L1 Δ | Max Action Ratio Δ | Entropy Δ | Status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.6667` | `67.3958` | `0.036` | `None` | `None` | `None` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `0.0` | `-0.0467` | `None` | `None` | `None` | `pass` |
| `180s` | `soda-creek` | `-0.3334` | `-11.4358` | `-0.1463` | `None` | `None` | `None` | `regression` |
| `300s` | `caramel-workshop` | `0.0` | `37.2724` | `0.126` | `None` | `None` | `None` | `pass` |
| `300s` | `cracked-star-jar` | `0.0` | `1.7781` | `0.0702` | `None` | `None` | `None` | `pass` |
| `300s` | `soda-creek` | `0.0` | `28.8833` | `0.0106` | `None` | `None` | `None` | `pass` |
| `60s` | `caramel-workshop` | `0.3333` | `6.1999` | `0.0419` | `None` | `None` | `None` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0004` | `None` | `None` | `None` | `pass` |
| `60s` | `soda-creek` | `0.0` | `-0.0222` | `0.0001` | `None` | `None` | `None` | `pass` |

## Blockers

- 180s/soda-creek: win_rate_delta -0.3334 below required 0.0
- 180s/soda-creek: average_survival_seconds dropped 11.4358s beyond allowed 5.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
