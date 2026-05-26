# RL Behavior Clone Context5 Map Conditioned 60s Comparison

- Model: `python/train/models/behavior_clone_kite_high_pressure_context5_map_conditioned_smoke.pt`
- Map preset: `high-pressure`
- Seeds: `49000` to `49004`
- Duration: `60` seconds
- Gate decision: `multimap_comparison_recorded_not_balance_gate`

## Results

| Map | Policy win rate | Avg survival | Normalized entropy | Dominant action ratio | Best rule Bot win rate |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 1.0 | 60.0328 | 0.8893 | 0.2434 | 1.0 |
| `caramel-workshop` | 1.0 | 60.0328 | 0.8893 | 0.2420 | 1.0 |
| `cracked-star-jar` | 1.0 | 60.0328 | 0.8824 | 0.2403 | 1.0 |

## Findings

- None.

## Limitations

- This confirms short-window action distribution health only.
- The model still depends on 300-second high-pressure validation and RL acceptance review.

