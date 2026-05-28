# Policy Window Regression

- Decision: `policy_window_regression_passed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `0`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `-0.4406` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `-3.5` | `-0.0999` | `pass` |
| `180s` | `soda-creek` | `0.0` | `6.4444` | `-0.1757` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `0.778` | `-0.1415` | `pass` |
| `300s` | `cracked-star-jar` | `0.3333` | `9.0849` | `0.065` | `pass` |
| `300s` | `soda-creek` | `0.0` | `1.7779` | `-0.1029` | `pass` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `0.0` | `pass` |

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
