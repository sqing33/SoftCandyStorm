# RL Behavior Clone Legacy Compatibility Smoke

- Model: `python/train/models/behavior_clone_kite_high_pressure_context5_danger_weighted_smoke.pt`
- Map preset: `high-pressure`
- Seeds: `1`
- Duration: `5` seconds
- Gate decision: `multimap_comparison_recorded_not_balance_gate`

## Results

| Map | Policy win rate | Avg survival | Normalized entropy | Dominant action ratio |
|---|---:|---:|---:|---:|
| `soda-creek` | 1.0 | 5.0333 | 0.4457 | 0.5828 |
| `caramel-workshop` | 1.0 | 5.0333 | 0.4513 | 0.5762 |
| `cracked-star-jar` | 1.0 | 5.0333 | 0.3347 | 0.5894 |

## Notes

- This smoke confirms older behavior clone checkpoints still load after adding map-conditioning support.
- The 5-second run is a compatibility check only and must not be interpreted as policy acceptance.

