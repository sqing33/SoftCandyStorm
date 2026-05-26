# RL Behavior Clone Context3 High-Pressure 300s Comparison

- Model: `python/train/models/behavior_clone_kite_high_pressure_context3_danger_weighted_smoke.pt`
- Map preset: `high-pressure`
- Seeds: `43000` to `43002`
- Duration: `300` seconds
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`

## Results

| Map | Policy win rate | Avg survival | Normalized entropy | Dominant action ratio | Best rule Bot win rate |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 0.6667 | 280.9732 | 0.8976 | 0.2075 | 0.667 |
| `caramel-workshop` | 0.0 | 224.5857 | 0.8825 | 0.2222 | 1.0 |
| `cracked-star-jar` | 0.3333 | 256.3524 | 0.8644 | 0.2806 | 0.667 |

## Findings

- `caramel-workshop`: policy recorded 0% win rate and must not be promoted as a multi-map RL test Bot.
- `cracked-star-jar`: policy win rate is less than half of the strongest compared rule Bot on this map.

## Limitations

- This comparison records policy behavior against rule Bot baselines; it is not a balance or fun gate.
- The policy remains a repair target and must not be promoted to `rl_test_bot_candidate`.
