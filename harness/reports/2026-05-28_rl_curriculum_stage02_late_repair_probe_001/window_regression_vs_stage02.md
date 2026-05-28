# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `11`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `-0.1554` | `pass` |
| `180s` | `cracked-star-jar` | `-0.3333` | `-46.4366` | `-0.1341` | `regression` |
| `180s` | `soda-creek` | `-0.3334` | `-81.4046` | `-0.0052` | `regression` |
| `300s` | `caramel-workshop` | `0.0` | `9.2798` | `-0.0563` | `pass` |
| `300s` | `cracked-star-jar` | `-0.3333` | `-83.26` | `-0.0002` | `regression` |
| `300s` | `soda-creek` | `0.0` | `-128.4458` | `-0.0801` | `regression` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `-0.0715` | `pass` |
| `60s` | `cracked-star-jar` | `-0.3333` | `-6.4444` | `-0.048` | `regression` |
| `60s` | `soda-creek` | `-0.6667` | `-10.5777` | `-0.127` | `regression` |

## Blockers

- 180s/cracked-star-jar: win_rate_delta -0.3333 below required 0.0
- 180s/cracked-star-jar: average_survival_seconds dropped 46.4366s beyond allowed 5.0s
- 180s/soda-creek: win_rate_delta -0.3334 below required 0.0
- 180s/soda-creek: average_survival_seconds dropped 81.4046s beyond allowed 5.0s
- 300s/cracked-star-jar: win_rate_delta -0.3333 below required 0.0
- 300s/cracked-star-jar: average_survival_seconds dropped 83.26s beyond allowed 5.0s
- 300s/soda-creek: average_survival_seconds dropped 128.4458s beyond allowed 5.0s
- 60s/cracked-star-jar: win_rate_delta -0.3333 below required 0.0
- 60s/cracked-star-jar: average_survival_seconds dropped 6.4444s beyond allowed 5.0s
- 60s/soda-creek: win_rate_delta -0.6667 below required 0.0
- 60s/soda-creek: average_survival_seconds dropped 10.5777s beyond allowed 5.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
