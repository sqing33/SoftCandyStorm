# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `2`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180` | `caramel-workshop` | `0.0` | `0.0` | `-0.4508` | `pass` |
| `180` | `cracked-star-jar` | `0.0` | `-4.4444` | `0.0055` | `regression` |
| `180` | `soda-creek` | `0.3334` | `27.6924` | `-0.114` | `pass` |
| `300` | `caramel-workshop` | `0.0` | `0.2112` | `-0.273` | `pass` |
| `300` | `cracked-star-jar` | `0.0` | `-17.6694` | `-0.1159` | `regression` |
| `300` | `soda-creek` | `0.0` | `36.3511` | `-0.1216` | `pass` |
| `60` | `caramel-workshop` | `0.0` | `0.0` | `0.0` | `pass` |
| `60` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `pass` |
| `60` | `soda-creek` | `0.0` | `0.0` | `0.0` | `pass` |

## Blockers

- 180/cracked-star-jar: average_survival_seconds dropped 4.4444s beyond allowed 0.0s
- 300/cracked-star-jar: average_survival_seconds dropped 17.6694s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
