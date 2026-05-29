# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `1`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Action L1 Δ | Max Action Ratio Δ | Entropy Δ | Status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `0.0225` | `0.4112` | `0.1482` | `-0.0591` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `3.1111` | `0.0123` | `0.3602` | `0.0973` | `0.0305` | `pass` |
| `180s` | `soda-creek` | `0.0` | `32.7355` | `0.0885` | `0.2925` | `0.1062` | `-0.0699` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `6.5347` | `-0.1946` | `0.4944` | `0.1875` | `0.0478` | `pass` |
| `300s` | `cracked-star-jar` | `0.0` | `4.2335` | `-0.0828` | `0.4879` | `0.0924` | `0.091` | `pass` |
| `300s` | `soda-creek` | `0.0` | `6.1791` | `0.0982` | `0.5952` | `0.216` | `-0.0768` | `regression` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0009` | `0.3368` | `0.161` | `0.0091` | `pass` |
| `60s` | `cracked-star-jar` | `0.3333` | `4.1778` | `-0.0028` | `0.294` | `0.0739` | `-0.0138` | `pass` |
| `60s` | `soda-creek` | `0.3334` | `8.2888` | `-0.088` | `0.2861` | `0.1083` | `-0.0303` | `pass` |

## Blockers

- 300s/soda-creek: action 1 ratio increased 0.216 beyond allowed 0.2

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
