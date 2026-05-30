# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `8`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Action L1 Δ | Max Action Ratio Δ | Entropy Δ | Status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.6667` | `67.3958` | `0.032` | `None` | `None` | `None` | `pass` |
| `180s` | `cracked-star-jar` | `-0.3333` | `-8.7352` | `0.338` | `None` | `None` | `None` | `regression` |
| `180s` | `soda-creek` | `-0.6667` | `-56.1942` | `0.0551` | `None` | `None` | `None` | `regression` |
| `300s` | `caramel-workshop` | `0.0` | `93.2778` | `0.1226` | `None` | `None` | `None` | `pass` |
| `300s` | `cracked-star-jar` | `0.0` | `-13.5474` | `0.3262` | `None` | `None` | `None` | `regression` |
| `300s` | `soda-creek` | `0.0` | `-83.3869` | `0.2475` | `None` | `None` | `None` | `regression` |
| `60s` | `caramel-workshop` | `0.3333` | `6.1999` | `-0.0781` | `None` | `None` | `None` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0711` | `None` | `None` | `None` | `pass` |
| `60s` | `soda-creek` | `-0.3334` | `-7.7221` | `-0.0491` | `None` | `None` | `None` | `regression` |

## Blockers

- 180s/cracked-star-jar: win_rate_delta -0.3333 below required 0.0
- 180s/cracked-star-jar: average_survival_seconds dropped 8.7352s beyond allowed 0.0s
- 180s/soda-creek: win_rate_delta -0.6667 below required 0.0
- 180s/soda-creek: average_survival_seconds dropped 56.1942s beyond allowed 0.0s
- 300s/cracked-star-jar: average_survival_seconds dropped 13.5474s beyond allowed 0.0s
- 300s/soda-creek: average_survival_seconds dropped 83.3869s beyond allowed 0.0s
- 60s/soda-creek: win_rate_delta -0.3334 below required 0.0
- 60s/soda-creek: average_survival_seconds dropped 7.7221s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
