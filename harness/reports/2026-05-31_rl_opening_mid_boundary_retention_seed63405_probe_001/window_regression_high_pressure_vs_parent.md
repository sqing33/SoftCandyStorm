# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `3`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Action L1 Δ | Max Action Ratio Δ | Entropy Δ | Status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.3334` | `20.7592` | `0.1005` | `0.201` | `0.1005` | `-0.0698` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `0.0` | `-0.0114` | `0.7526` | `0.1841` | `-0.0441` | `regression` |
| `180s` | `soda-creek` | `0.0` | `0.0666` | `0.032` | `0.1578` | `0.0349` | `0.0059` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `35.5055` | `-0.2089` | `0.6056` | `0.1687` | `0.1575` | `regression` |
| `300s` | `cracked-star-jar` | `0.0` | `0.1333` | `0.1064` | `0.4257` | `0.1993` | `-0.0397` | `pass` |
| `300s` | `soda-creek` | `0.0` | `1.5781` | `0.0361` | `0.1013` | `0.0361` | `-0.0264` | `pass` |
| `60s` | `caramel-workshop` | `-0.3334` | `-4.5555` | `0.0569` | `0.2357` | `0.0569` | `-0.1009` | `regression` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `-0.0003` | `0.1936` | `0.0957` | `-0.0933` | `pass` |
| `60s` | `soda-creek` | `0.0` | `0.0111` | `0.0094` | `0.0259` | `0.0094` | `-0.008` | `pass` |

## Blockers

- 180s/cracked-star-jar: action_distribution_l1_delta 0.7526 beyond allowed 0.45
- 300s/caramel-workshop: action_distribution_l1_delta 0.6056 beyond allowed 0.45
- 60s/caramel-workshop: win_rate_delta -0.3334 below required 0.0

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
