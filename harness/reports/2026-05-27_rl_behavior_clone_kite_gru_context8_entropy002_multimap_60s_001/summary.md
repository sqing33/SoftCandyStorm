# RL Behavior Clone GRU Context8 Entropy002 High-Pressure 60s Comparison

- Model: `python/train/models/behavior_clone_kite_high_pressure_gru_context8_entropy002_smoke.pt`
- Map preset: `high-pressure`
- Seeds: `46000` to `46004`
- Duration: `60` seconds
- Gate decision: `multimap_comparison_recorded_not_balance_gate`

## Results

| Map | Policy win rate | Avg survival | Normalized entropy | Dominant action ratio | Best rule Bot win rate |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 0.8 | 56.0062 | 0.6950 | 0.4779 | 1.0 |
| `caramel-workshop` | 1.0 | 60.0328 | 0.8068 | 0.3100 | 1.0 |
| `cracked-star-jar` | 0.8 | 54.6662 | 0.7468 | 0.3677 | 1.0 |

## Findings

- None

## Limitations

- This short-window report is not a balance, fun, release, or accepted-content gate.
- The 60-second result is healthier than the first GRU 60-second run on `caramel-workshop`, but it still misses 100% policy win rate on `soda-creek` and `cracked-star-jar`.
