# Policy Window Regression

- Decision: `policy_window_regression_failed`
- Baseline windows: `3`
- Candidate windows: `3`
- Blockers: `17`

## Window Results

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Action L1 Δ | Max Action Ratio Δ | Entropy Δ | Status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `0.088` | `0.7067` | `0.2137` | `-0.107` | `regression` |
| `180s` | `cracked-star-jar` | `0.3333` | `44.17` | `-0.0059` | `0.4741` | `0.1536` | `-0.0173` | `regression` |
| `180s` | `soda-creek` | `0.3334` | `38.2034` | `0.0643` | `0.4458` | `0.1377` | `-0.0696` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `9.991` | `-0.0721` | `0.5721` | `0.1847` | `0.0196` | `regression` |
| `300s` | `cracked-star-jar` | `0.0` | `56.0503` | `-0.1411` | `0.7` | `0.1596` | `0.074` | `regression` |
| `300s` | `soda-creek` | `0.0` | `5.8012` | `0.1869` | `0.7617` | `0.3047` | `-0.1548` | `regression` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.2268` | `0.7526` | `0.2421` | `-0.2752` | `regression` |
| `60s` | `cracked-star-jar` | `0.3333` | `4.1778` | `0.0042` | `0.7808` | `0.2588` | `-0.1575` | `regression` |
| `60s` | `soda-creek` | `0.3334` | `8.2888` | `-0.049` | `0.8214` | `0.3702` | `-0.0116` | `regression` |

## Blockers

- 180s/caramel-workshop: action 5 ratio increased 0.2137 beyond allowed 0.2
- 180s/caramel-workshop: action_distribution_l1_delta 0.7067 beyond allowed 0.45
- 180s/cracked-star-jar: action_distribution_l1_delta 0.4741 beyond allowed 0.45
- 300s/caramel-workshop: action_distribution_l1_delta 0.5721 beyond allowed 0.45
- 300s/cracked-star-jar: action_distribution_l1_delta 0.7 beyond allowed 0.45
- 300s/soda-creek: action 1 ratio increased 0.3047 beyond allowed 0.2
- 300s/soda-creek: action_distribution_l1_delta 0.7617 beyond allowed 0.45
- 300s/soda-creek: normalized_action_entropy dropped 0.1548 beyond allowed 0.15
- 60s/caramel-workshop: dominant_action_ratio increased 0.2268 beyond allowed 0.2
- 60s/caramel-workshop: action 7 ratio increased 0.2421 beyond allowed 0.2
- 60s/caramel-workshop: action_distribution_l1_delta 0.7526 beyond allowed 0.45
- 60s/caramel-workshop: normalized_action_entropy dropped 0.2752 beyond allowed 0.15
- 60s/cracked-star-jar: action 7 ratio increased 0.2588 beyond allowed 0.2
- 60s/cracked-star-jar: action_distribution_l1_delta 0.7808 beyond allowed 0.45
- 60s/cracked-star-jar: normalized_action_entropy dropped 0.1575 beyond allowed 0.15
- 60s/soda-creek: action 1 ratio increased 0.3702 beyond allowed 0.2
- 60s/soda-creek: action_distribution_l1_delta 0.8214 beyond allowed 0.45

## Limitations

- This validator checks no-regression against supplied comparison reports only.
- A passing no-regression result is repair evidence, not RL policy acceptance.
- Final policies still require deterministic high-pressure, failure-case, and acceptance manifest review.
