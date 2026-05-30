# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `1`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Action L1 Δ | Max Action Ratio Δ | Entropy Δ | Status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `4.9557` | `0.1039` | `None` | `None` | `None` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `0.0` | `-0.1034` | `None` | `None` | `None` | `pass` |
| `180s` | `soda-creek` | `0.0` | `-0.0445` | `-0.0168` | `None` | `None` | `None` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `35.8833` | `0.0688` | `None` | `None` | `None` | `pass` |
| `300s` | `cracked-star-jar` | `0.0` | `22.0229` | `0.2034` | `None` | `None` | `None` | `regression` |
| `300s` | `soda-creek` | `0.0` | `12.6916` | `-0.0956` | `None` | `None` | `None` | `pass` |
| `60s` | `caramel-workshop` | `0.3333` | `6.1999` | `-0.0198` | `None` | `None` | `None` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.003` | `None` | `None` | `None` | `pass` |
| `60s` | `soda-creek` | `0.0` | `-0.0667` | `0.0101` | `None` | `None` | `None` | `pass` |

## Blockers

- 300s/cracked-star-jar: dominant_action_ratio increased 0.2034 beyond allowed 0.2

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
