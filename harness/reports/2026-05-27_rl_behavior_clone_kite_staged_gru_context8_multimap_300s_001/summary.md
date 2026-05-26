# RL Behavior Clone Staged GRU Context8 High-Pressure 300s Comparison

- Model: `harness/reports/2026-05-27_rl_behavior_clone_kite_staged_gru_context8_smoke_001/staged.pt`
- Map preset: `high-pressure`
- Seeds: `47000` to `47002`
- Duration: `300` seconds
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`

## Results

| Map | Policy win rate | Avg survival | Normalized entropy | Dominant action ratio | Best rule Bot win rate |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 0.0 | 175.9025 | 0.4893 | 0.5317 | 0.667 |
| `caramel-workshop` | 0.3333 | 247.5061 | 0.6129 | 0.4784 | 0.0 |
| `cracked-star-jar` | 0.3333 | 196.6791 | 0.5904 | 0.4615 | 1.0 |

## Findings

- `soda-creek`: policy recorded 0% win rate and must not be promoted as a multi-map RL test Bot.
- `cracked-star-jar`: policy win rate is less than half of the strongest compared rule Bot on this map.

## Limitations

- Staging separate opening/mid/late clones improved neither the short-window gate nor long-window rule Bot parity.
- This result is not a balance, fun, release, or accepted-content gate.
