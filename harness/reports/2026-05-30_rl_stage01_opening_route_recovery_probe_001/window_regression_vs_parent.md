# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `5`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Action L1 Δ | Max Action Ratio Δ | Entropy Δ | Status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.3334` | `21.0592` | `0.046` | `None` | `None` | `None` | `pass` |
| `180s` | `cracked-star-jar` | `-0.3333` | `-31.0702` | `-0.0438` | `None` | `None` | `None` | `regression` |
| `180s` | `soda-creek` | `0.0` | `-0.0445` | `-0.0367` | `None` | `None` | `None` | `regression` |
| `300s` | `caramel-workshop` | `0.0` | `4.2106` | `0.0286` | `None` | `None` | `None` | `pass` |
| `300s` | `cracked-star-jar` | `0.0` | `22.8242` | `0.1135` | `None` | `None` | `None` | `pass` |
| `300s` | `soda-creek` | `0.0` | `13.5584` | `0.0132` | `None` | `None` | `None` | `pass` |
| `60s` | `caramel-workshop` | `0.0` | `-0.5667` | `-0.0071` | `None` | `None` | `None` | `regression` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0004` | `None` | `None` | `None` | `pass` |
| `60s` | `soda-creek` | `0.0` | `-0.0667` | `0.0005` | `None` | `None` | `None` | `regression` |

## Blockers

- 180s/cracked-star-jar: win_rate_delta -0.3333 below required 0.0
- 180s/cracked-star-jar: average_survival_seconds dropped 31.0702s beyond allowed 0.0s
- 180s/soda-creek: average_survival_seconds dropped 0.0445s beyond allowed 0.0s
- 60s/caramel-workshop: average_survival_seconds dropped 0.5667s beyond allowed 0.0s
- 60s/soda-creek: average_survival_seconds dropped 0.0667s beyond allowed 0.0s

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
