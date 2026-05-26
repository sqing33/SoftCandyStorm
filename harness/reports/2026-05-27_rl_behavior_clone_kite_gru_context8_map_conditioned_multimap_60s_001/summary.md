# RL Behavior Clone GRU Context8 High-Pressure 60s Comparison

- Model: `python/train/models/behavior_clone_kite_high_pressure_gru_context8_map_conditioned_smoke.pt`
- Map preset: `high-pressure`
- Seeds: `46000` to `46004`
- Duration: `60` seconds
- Gate decision: `multimap_comparison_recorded_not_balance_gate`

## Results

| Map | Policy win rate | Avg survival | Normalized entropy | Dominant action ratio | Best rule Bot win rate |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 0.8 | 57.5928 | 0.7556 | 0.4167 | 1.0 |
| `caramel-workshop` | 0.8 | 54.5862 | 0.7326 | 0.3319 | 1.0 |
| `cracked-star-jar` | 0.8 | 54.6662 | 0.8364 | 0.3170 | 1.0 |

## Findings

- None

## Limitations

- This short-window report is weaker than the previous MLP context3/context5 60-second results, which reached 100% on all three maps.
- It is not a balance, fun, release, or accepted-content gate.
