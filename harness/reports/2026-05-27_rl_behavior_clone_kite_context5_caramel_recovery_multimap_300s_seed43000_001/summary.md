# RL Behavior Clone Context5 Caramel Recovery 300s Comparison Seed 43000

- Model: `python/train/models/behavior_clone_kite_high_pressure_context5_caramel_recovery_smoke.pt`
- Map preset: `high-pressure`
- Seeds: `43000` to `43002`
- Duration: `300` seconds
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`

## Results

| Map | Policy win rate | Avg survival | Normalized entropy | Dominant action ratio | Best rule Bot win rate |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 0.3333 | 248.2285 | 0.8562 | 0.2738 | 0.667 |
| `caramel-workshop` | 0.6667 | 273.1048 | 0.8634 | 0.3023 | 1.0 |
| `cracked-star-jar` | 0.0 | 221.4850 | 0.8702 | 0.2622 | 0.667 |

## Findings

- `soda-creek`: policy win rate is less than half of the strongest compared rule Bot.
- `cracked-star-jar`: policy recorded 0% win rate and must not be promoted as a multi-map RL test Bot.

## Limitations

- The targeted recovery data improved caramel-workshop but moved the failure surface to other high-pressure maps.
- This model remains `repair` and must not be promoted to `rl_test_bot_candidate`.
