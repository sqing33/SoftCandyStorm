# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `1`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `0.265` | `regression` |
| `180s` | `cracked-star-jar` | `0.3333` | `44.17` | `0.0527` | `pass` |
| `180s` | `soda-creek` | `0.3334` | `38.2034` | `0.1631` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `4.3454` | `0.0562` | `pass` |
| `300s` | `cracked-star-jar` | `0.3333` | `90.0397` | `-0.079` | `pass` |
| `300s` | `soda-creek` | `0.0` | `8.1995` | `0.1991` | `pass` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0173` | `pass` |
| `60s` | `cracked-star-jar` | `0.3333` | `4.1778` | `-0.0804` | `pass` |
| `60s` | `soda-creek` | `0.3334` | `8.2888` | `0.0153` | `pass` |

## Blockers

- 180s/caramel-workshop: dominant_action_ratio increased 0.265 beyond allowed 0.2

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
