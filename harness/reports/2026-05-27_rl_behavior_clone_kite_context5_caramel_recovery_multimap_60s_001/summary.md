# RL Behavior Clone Context5 Caramel Recovery 60s Comparison

- Model: `python/train/models/behavior_clone_kite_high_pressure_context5_caramel_recovery_smoke.pt`
- Map preset: `high-pressure`
- Seeds: `47000` to `47004`
- Duration: `60` seconds
- Gate decision: `multimap_comparison_recorded_not_balance_gate`

## Results

| Map | Policy win rate | Avg survival | Normalized entropy | Dominant action ratio | Best rule Bot win rate |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 1.0 | 60.0328 | 0.8556 | 0.2917 | 1.0 |
| `caramel-workshop` | 1.0 | 60.0328 | 0.9190 | 0.2117 | 1.0 |
| `cracked-star-jar` | 1.0 | 60.0328 | 0.8535 | 0.2866 | 1.0 |

## Findings

- None

## Limitations

- This is a short comparison only and does not prove 300-second robustness.
