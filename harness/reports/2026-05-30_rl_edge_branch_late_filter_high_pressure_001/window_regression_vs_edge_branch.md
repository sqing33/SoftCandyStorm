# Policy Window Regression

- Decision: `policy_window_regression_passed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `0`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Action L1 Δ | Max Action Ratio Δ | Entropy Δ | Status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `180` | `caramel-workshop` | `0.3334` | `21.2036` | `-0.0536` | `0.182` | `0.0507` | `0.0391` | `pass` |
| `180` | `cracked-star-jar` | `0.0` | `0.0` | `-0.0308` | `0.4871` | `0.0888` | `-0.0102` | `pass` |
| `180` | `soda-creek` | `0.0` | `0.0` | `-0.0682` | `0.4447` | `0.0845` | `0.0097` | `pass` |
| `300` | `caramel-workshop` | `0.0` | `43.107` | `-0.1042` | `0.5857` | `0.1001` | `0.0862` | `pass` |
| `300` | `cracked-star-jar` | `0.3333` | `68.7881` | `0.0108` | `0.2346` | `0.0449` | `0.0343` | `pass` |
| `300` | `soda-creek` | `1.0` | `78.2077` | `-0.0326` | `0.3601` | `0.1083` | `0.0463` | `pass` |
| `60` | `caramel-workshop` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `pass` |
| `60` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `pass` |
| `60` | `soda-creek` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `pass` |

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
