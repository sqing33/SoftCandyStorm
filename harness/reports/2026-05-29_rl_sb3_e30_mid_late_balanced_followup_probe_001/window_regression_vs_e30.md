# Policy Window Regression

- Decision: `policy_window_regression_passed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `0`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `0.0396` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `3.1111` | `-0.0218` | `pass` |
| `180s` | `soda-creek` | `0.0` | `25.8785` | `0.1502` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `1.3447` | `-0.0246` | `pass` |
| `300s` | `cracked-star-jar` | `0.0` | `5.5227` | `-0.0582` | `pass` |
| `300s` | `soda-creek` | `0.0` | `9.2797` | `0.0302` | `pass` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.1117` | `pass` |
| `60s` | `cracked-star-jar` | `0.3333` | `4.1778` | `-0.0023` | `pass` |
| `60s` | `soda-creek` | `0.3334` | `8.2888` | `0.0229` | `pass` |

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
