# RL Behavior Clone Context5 High-Pressure 300s Comparison Seed 43000

- Model: `python/train/models/behavior_clone_kite_high_pressure_context5_danger_weighted_smoke.pt`
- Map preset: `high-pressure`
- Seeds: `43000` to `43002`
- Duration: `300` seconds
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`

## Results

| Map | Policy win rate | Avg survival | Normalized entropy | Dominant action ratio | Best rule Bot win rate |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 0.6667 | 270.7488 | 0.8578 | 0.2760 | 0.667 |
| `caramel-workshop` | 0.0 | 219.9180 | 0.8593 | 0.2851 | 1.0 |
| `cracked-star-jar` | 0.3333 | 243.5497 | 0.8602 | 0.3144 | 0.667 |

## Findings

- `caramel-workshop`: policy recorded 0% win rate and must not be promoted as a multi-map RL test Bot.
- `cracked-star-jar`: policy win rate is less than half of the strongest compared rule Bot on this map.

## Limitations

- This is the primary same-seed comparison against the context3 300-second report.
- It confirms that simply increasing MLP context from 3 to 5 frames does not clear the long-game repair gate.
