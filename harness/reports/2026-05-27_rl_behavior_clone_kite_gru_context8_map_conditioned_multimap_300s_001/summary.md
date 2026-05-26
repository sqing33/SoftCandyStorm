# RL Behavior Clone GRU Context8 High-Pressure 300s Comparison

- Model: `python/train/models/behavior_clone_kite_high_pressure_gru_context8_map_conditioned_smoke.pt`
- Map preset: `high-pressure`
- Seeds: `47000` to `47002`
- Duration: `300` seconds
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`

## Results

| Map | Policy win rate | Avg survival | Normalized entropy | Dominant action ratio | Best rule Bot win rate |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 0.0 | 132.8960 | 0.6121 | 0.5899 | 0.667 |
| `caramel-workshop` | 0.0 | 196.6911 | 0.7484 | 0.3474 | 0.667 |
| `cracked-star-jar` | 0.0 | 200.7250 | 0.8189 | 0.2421 | 1.0 |

## Findings

- `soda-creek`: policy recorded 0% win rate and must not be promoted as a multi-map RL test Bot.
- `caramel-workshop`: policy recorded 0% win rate and must not be promoted as a multi-map RL test Bot.
- `cracked-star-jar`: policy recorded 0% win rate and must not be promoted as a multi-map RL test Bot.

## Limitations

- This result proves the GRU support path can be evaluated, but the first context8 map-conditioned checkpoint is worse than the previous map-conditioned MLP watch result.
- It is not a balance, fun, release, or accepted-content gate.
