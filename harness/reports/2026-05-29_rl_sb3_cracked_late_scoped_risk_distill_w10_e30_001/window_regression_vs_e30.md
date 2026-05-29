# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `2`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `0.0915` | `pass` |
| `180s` | `cracked-star-jar` | `0.3333` | `44.17` | `0.2149` | `regression` |
| `180s` | `soda-creek` | `0.0` | `-8.3443` | `0.0957` | `regression` |
| `300s` | `caramel-workshop` | `0.0` | `0.5112` | `-0.1441` | `pass` |
| `300s` | `cracked-star-jar` | `0.0` | `54.161` | `0.0757` | `pass` |
| `300s` | `soda-creek` | `0.0` | `2.5005` | `0.0432` | `pass` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0155` | `pass` |
| `60s` | `cracked-star-jar` | `0.3333` | `4.1778` | `-0.0345` | `pass` |
| `60s` | `soda-creek` | `0.0` | `1.7889` | `-0.0286` | `pass` |

## Blockers

- 180s/cracked-star-jar: dominant_action_ratio increased 0.2149 beyond allowed 0.2
- 180s/soda-creek: average_survival_seconds dropped 8.3443s beyond allowed 5.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
