# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `1`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
|---|---|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.3333` | `50.6921` | `-0.3772` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `-4.8333` | `0.0129` | `pass` |
| `180s` | `soda-creek` | `0.3334` | `36.3257` | `-0.0035` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `64.7395` | `-0.1272` | `pass` |
| `300s` | `cracked-star-jar` | `0.0` | `-13.7463` | `0.0382` | `regression` |
| `300s` | `soda-creek` | `0.0` | `46.0163` | `0.0228` | `pass` |
| `60s` | `caramel-workshop` | `0.3333` | `10.6999` | `-0.3235` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0089` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0` | `-0.0481` | `pass` |

## Blockers

- 300s/cracked-star-jar: average_survival_seconds dropped 13.7463s beyond allowed 5.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
