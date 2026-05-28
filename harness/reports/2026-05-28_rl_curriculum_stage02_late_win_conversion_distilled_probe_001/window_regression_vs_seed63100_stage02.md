# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `5`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.3333` | `50.6921` | `-0.5054` | `pass` |
| `180s` | `cracked-star-jar` | `0.3333` | `22.5147` | `-0.0414` | `pass` |
| `180s` | `soda-creek` | `-0.3333` | `-46.5583` | `0.1853` | `regression` |
| `300s` | `caramel-workshop` | `0.0` | `60.6164` | `-0.1741` | `pass` |
| `300s` | `cracked-star-jar` | `0.3333` | `40.6119` | `-0.018` | `pass` |
| `300s` | `soda-creek` | `0.0` | `-63.883` | `0.218` | `regression` |
| `60s` | `caramel-workshop` | `0.3333` | `10.6999` | `-0.1169` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0939` | `pass` |
| `60s` | `soda-creek` | `-0.6667` | `-15.8109` | `0.217` | `regression` |

## Blockers

- 180s/soda-creek: win_rate_delta -0.3333 below required 0.0
- 180s/soda-creek: average_survival_seconds dropped 46.5583s beyond allowed 0.0s
- 300s/soda-creek: average_survival_seconds dropped 63.883s beyond allowed 0.0s
- 60s/soda-creek: win_rate_delta -0.6667 below required 0.0
- 60s/soda-creek: average_survival_seconds dropped 15.8109s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
