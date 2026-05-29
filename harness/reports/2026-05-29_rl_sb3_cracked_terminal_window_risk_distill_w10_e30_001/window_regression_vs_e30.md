# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `1`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `0.088` | `pass` |
| `180s` | `cracked-star-jar` | `0.3333` | `44.17` | `-0.0059` | `pass` |
| `180s` | `soda-creek` | `0.3334` | `38.2034` | `0.0643` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `9.991` | `-0.0721` | `pass` |
| `300s` | `cracked-star-jar` | `0.0` | `56.0503` | `-0.1411` | `pass` |
| `300s` | `soda-creek` | `0.0` | `5.8012` | `0.1869` | `pass` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.2268` | `regression` |
| `60s` | `cracked-star-jar` | `0.3333` | `4.1778` | `0.0042` | `pass` |
| `60s` | `soda-creek` | `0.3334` | `8.2888` | `-0.049` | `pass` |

## Blockers

- 60s/caramel-workshop: dominant_action_ratio increased 0.2268 beyond allowed 0.2

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
