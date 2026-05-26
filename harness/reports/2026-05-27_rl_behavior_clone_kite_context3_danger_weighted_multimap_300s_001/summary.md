# RL Behavior Clone Context3 High-Pressure 300s Alternate Window

- Model: `python/train/models/behavior_clone_kite_high_pressure_context3_danger_weighted_smoke.pt`
- Map preset: `high-pressure`
- Seeds: `45000` to `45002`
- Duration: `300` seconds
- Gate decision: `multimap_comparison_recorded_watch`

## Results

| Map | Policy win rate | Avg survival | Normalized entropy | Dominant action ratio | Best rule Bot win rate |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 0.3333 | 244.8388 | 0.8748 | 0.2400 | 1.0 |
| `caramel-workshop` | 1.0 | 300.0150 | 0.8743 | 0.2420 | 0.0 |
| `cracked-star-jar` | 0.3333 | 254.5409 | 0.8739 | 0.2271 | 1.0 |

## Findings

- `soda-creek`: policy win rate is less than half of the strongest compared rule Bot on this map.
- `cracked-star-jar`: policy win rate is less than half of the strongest compared rule Bot on this map.

## Limitations

- This alternate seed window is exploratory evidence; the primary acceptance long-window report remains the `seed-start 43000` repair result.
- It is not a balance, fun, release, or accepted-content gate.
