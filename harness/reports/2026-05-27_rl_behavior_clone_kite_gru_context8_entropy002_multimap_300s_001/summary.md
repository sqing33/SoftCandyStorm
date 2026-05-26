# RL Behavior Clone GRU Context8 Entropy002 High-Pressure 300s Comparison

- Model: `python/train/models/behavior_clone_kite_high_pressure_gru_context8_entropy002_smoke.pt`
- Map preset: `high-pressure`
- Seeds: `47000` to `47002`
- Duration: `300` seconds
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`

## Results

| Map | Policy win rate | Avg survival | Normalized entropy | Dominant action ratio | Best rule Bot win rate |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 0.0 | 249.9656 | 0.8100 | 0.3458 | 0.667 |
| `caramel-workshop` | 0.3333 | 247.1060 | 0.7768 | 0.4360 | 0.0 |
| `cracked-star-jar` | 0.0 | 222.6964 | 0.7980 | 0.3802 | 1.0 |

## Findings

- `soda-creek`: policy recorded 0% win rate and must not be promoted as a multi-map RL test Bot.
- `cracked-star-jar`: policy recorded 0% win rate and must not be promoted as a multi-map RL test Bot.

## Limitations

- Entropy regularization improved action spread, but it did not solve 300-second high-pressure survival or rule Bot parity.
- This result is not a balance, fun, release, or accepted-content gate.
