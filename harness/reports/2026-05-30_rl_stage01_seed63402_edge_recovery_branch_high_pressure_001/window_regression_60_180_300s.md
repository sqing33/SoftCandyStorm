# Policy Window Regression

- Decision: `policy_window_regression_passed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `0`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Action L1 Δ | Max Action Ratio Δ | Entropy Δ | Status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `pass` |
| `180s` | `soda-creek` | `0.3333` | `47.4699` | `-0.092` | `0.5937` | `0.138` | `0.0806` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `pass` |
| `300s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `pass` |
| `300s` | `soda-creek` | `0.0` | `78.7099` | `-0.0907` | `0.6546` | `0.2334` | `0.0111` | `pass` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `cracked-star-jar` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` | `pass` |
| `60s` | `soda-creek` | `0.3333` | `7.5666` | `0.0143` | `0.2956` | `0.1334` | `0.0672` | `pass` |

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
