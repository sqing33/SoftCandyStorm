# Policy Window Regression

- Decision: `policy_window_regression_passed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `0`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `-0.1979` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `5.0554` | `0.0138` | `pass` |
| `180s` | `soda-creek` | `0.0` | `11.9558` | `0.007` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `-1.0891` | `-0.0813` | `pass` |
| `300s` | `cracked-star-jar` | `0.3333` | `23.7861` | `0.0431` | `pass` |
| `300s` | `soda-creek` | `0.0` | `6.6225` | `0.0411` | `pass` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `0.0` | `pass` |

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
