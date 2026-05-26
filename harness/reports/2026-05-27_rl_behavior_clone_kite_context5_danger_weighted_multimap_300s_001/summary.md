# RL Behavior Clone Context5 High-Pressure 300s Comparison

- Model: `python/train/models/behavior_clone_kite_high_pressure_context5_danger_weighted_smoke.pt`
- Map preset: `high-pressure`
- Seeds: `45000` to `45002`
- Duration: `300` seconds
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`

## Results

| Map | Policy win rate | Avg survival | Normalized entropy | Dominant action ratio | Best rule Bot win rate |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 0.6667 | 280.5842 | 0.8244 | 0.3146 | 1.0 |
| `caramel-workshop` | 0.0 | 220.0625 | 0.7459 | 0.4359 | 0.0 |
| `cracked-star-jar` | 1.0 | 300.0150 | 0.8224 | 0.3702 | 1.0 |

## Findings

- `caramel-workshop`: policy recorded 0% win rate and must not be promoted as a multi-map RL test Bot.

## Limitations

- This comparison uses a different seed window from the context3 acceptance report, so it is useful as an exploratory check rather than the primary acceptance comparison.
- It is not a balance, fun, release, or accepted-content gate.
