# RL Behavior Clone Context5 Map Conditioned 300s Comparison Seed 43000

- Model: `python/train/models/behavior_clone_kite_high_pressure_context5_map_conditioned_smoke.pt`
- Map preset: `high-pressure`
- Seeds: `43000` to `43002`
- Duration: `300` seconds
- Gate decision: `multimap_comparison_recorded_watch`

## Results

| Map | Policy win rate | Avg survival | Normalized entropy | Dominant action ratio | Best rule Bot win rate |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 0.6667 | 272.4158 | 0.8287 | 0.3207 | 0.667 |
| `caramel-workshop` | 0.3333 | 243.7720 | 0.8264 | 0.3677 | 1.0 |
| `cracked-star-jar` | 0.3333 | 250.1511 | 0.8626 | 0.3053 | 0.667 |

## Findings

- `caramel-workshop`: policy win rate is less than half of the strongest compared rule Bot.
- `cracked-star-jar`: policy win rate is less than half of the strongest compared rule Bot.

## Limitations

- Map conditioning removes the previous 0% long-run win-rate collapse, but the policy still underperforms rule Bot baselines on two high-pressure maps.
- This model remains `watch` and must not be promoted to `rl_test_bot_candidate`.

