# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `3`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Action L1 Δ | Max Action Ratio Δ | Entropy Δ | Status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.3334` | `20.7592` | `0.1005` | `0.201` | `0.1005` | `-0.0698` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `0.0` | `-0.0752` | `0.4646` | `0.1268` | `0.0332` | `regression` |
| `180s` | `soda-creek` | `0.0` | `0.0666` | `0.0318` | `0.2939` | `0.0893` | `0.0339` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `35.1165` | `-0.1542` | `0.5872` | `0.1192` | `0.1403` | `regression` |
| `300s` | `cracked-star-jar` | `0.0` | `0.3111` | `0.1035` | `0.4218` | `0.1964` | `-0.0379` | `pass` |
| `300s` | `soda-creek` | `0.0` | `0.9224` | `0.0393` | `0.1091` | `0.0393` | `-0.0281` | `pass` |
| `60s` | `caramel-workshop` | `-0.3334` | `-4.5555` | `0.0569` | `0.2361` | `0.0569` | `-0.1011` | `regression` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `-0.0003` | `0.1932` | `0.0957` | `-0.0933` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0333` | `0.0096` | `0.0263` | `0.0096` | `-0.0082` | `pass` |

## Blockers

- 180s/cracked-star-jar: action_distribution_l1_delta 0.4646 beyond allowed 0.45
- 300s/caramel-workshop: action_distribution_l1_delta 0.5872 beyond allowed 0.45
- 60s/caramel-workshop: win_rate_delta -0.3334 below required 0.0

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
