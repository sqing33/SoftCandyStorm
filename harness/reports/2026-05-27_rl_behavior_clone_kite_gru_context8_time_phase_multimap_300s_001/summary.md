# RL Behavior Clone GRU Context8 Time-Phase High-Pressure 300s Comparison

- Model: `python/train/models/behavior_clone_kite_high_pressure_gru_context8_time_phase_smoke.pt`
- Map preset: `high-pressure`
- Seeds: `47000` to `47002`
- Duration: `300` seconds
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`

## Results

| Map | Policy win rate | Avg survival | Normalized entropy | Dominant action ratio | Best rule Bot win rate |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 0.0 | 219.0067 | 0.7460 | 0.3255 | 0.667 |
| `caramel-workshop` | 0.0 | 156.6331 | 0.6689 | 0.3894 | 0.0 |
| `cracked-star-jar` | 0.3333 | 212.4663 | 0.7925 | 0.3815 | 1.0 |

## Findings

- `soda-creek`: policy recorded 0% win rate and must not be promoted as a multi-map RL test Bot.
- `caramel-workshop`: policy recorded 0% win rate and must not be promoted as a multi-map RL test Bot.
- `cracked-star-jar`: policy win rate is less than half of the strongest compared rule Bot on this map.

## Limitations

- Time-phase conditioning improved short-window action distribution but did not solve 300-second high-pressure survival.
- This result is not a balance, fun, release, or accepted-content gate.
