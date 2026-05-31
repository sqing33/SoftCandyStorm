# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `2`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Action L1 Δ | Max Action Ratio Δ | Entropy Δ | Status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.3333` | `46.6366` | `-0.0658` | `0.4813` | `0.127` | `-0.0135` | `regression` |
| `180s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `pass` |
| `180s` | `soda-creek` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `60.2395` | `0.1414` | `0.5787` | `0.194` | `-0.0926` | `regression` |
| `300s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `pass` |
| `300s` | `soda-creek` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `caramel-workshop` | `0.3334` | `6.6443` | `0.0768` | `0.2031` | `0.0768` | `-0.057` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `pass` |

## Blockers

- 180s/caramel-workshop: action_distribution_l1_delta 0.4813 beyond allowed 0.45
- 300s/caramel-workshop: action_distribution_l1_delta 0.5787 beyond allowed 0.45

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
