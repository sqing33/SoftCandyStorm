# RL Behavior Clone Context3 High-Pressure 60s Alternate Window

- Model: `python/train/models/behavior_clone_kite_high_pressure_context3_danger_weighted_smoke.pt`
- Map preset: `high-pressure`
- Seeds: `44000` to `44004`
- Duration: `60` seconds
- Gate decision: `multimap_comparison_recorded_not_balance_gate`

## Results

| Map | Policy win rate | Avg survival | Normalized entropy | Dominant action ratio | Best rule Bot win rate |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 1.0 | 60.0328 | 0.8957 | 0.2768 | 1.0 |
| `caramel-workshop` | 1.0 | 60.0328 | 0.9255 | 0.2277 | 1.0 |
| `cracked-star-jar` | 0.8 | 55.0462 | 0.9059 | 0.2714 | 1.0 |

## Findings

- None

## Limitations

- This alternate seed window is useful as robustness evidence, but it is not the primary acceptance short-window report.
- It is not a balance, fun, release, or accepted-content gate.
