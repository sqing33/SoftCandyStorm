# RL Behavior Clone Context3 High-Pressure 60s Comparison

- Model: `python/train/models/behavior_clone_kite_high_pressure_context3_danger_weighted_smoke.pt`
- Map preset: `high-pressure`
- Seeds: `42000` to `42004`
- Duration: `60` seconds
- Gate decision: `multimap_comparison_recorded_not_balance_gate`

## Results

| Map | Policy win rate | Avg survival | Normalized entropy | Dominant action ratio | Best rule Bot win rate |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 1.0 | 60.0328 | 0.8740 | 0.2919 | 1.0 |
| `caramel-workshop` | 1.0 | 60.0328 | 0.9206 | 0.2299 | 1.0 |
| `cracked-star-jar` | 1.0 | 60.0328 | 0.9074 | 0.2386 | 1.0 |

## Findings

- None

## Limitations

- This is a short comparison only; it does not prove 300-second high-pressure survival.
- It is not a balance, fun, release, or accepted-content gate.
