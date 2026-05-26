# RL Behavior Clone GRU Context8 Time-Phase High-Pressure 60s Comparison

- Model: `python/train/models/behavior_clone_kite_high_pressure_gru_context8_time_phase_smoke.pt`
- Map preset: `high-pressure`
- Seeds: `46000` to `46004`
- Duration: `60` seconds
- Gate decision: `multimap_comparison_recorded_not_balance_gate`

## Results

| Map | Policy win rate | Avg survival | Normalized entropy | Dominant action ratio | Best rule Bot win rate |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 1.0 | 60.0328 | 0.8977 | 0.2038 | 1.0 |
| `caramel-workshop` | 0.8 | 57.0061 | 0.8405 | 0.2572 | 1.0 |
| `cracked-star-jar` | 1.0 | 60.0328 | 0.8348 | 0.3411 | 1.0 |

## Findings

- None

## Limitations

- The 60-second window improved over entropy002 on `soda-creek` and `cracked-star-jar`, but `caramel-workshop` still missed 100% win rate.
- This short-window result is not a balance, fun, release, or accepted-content gate.
