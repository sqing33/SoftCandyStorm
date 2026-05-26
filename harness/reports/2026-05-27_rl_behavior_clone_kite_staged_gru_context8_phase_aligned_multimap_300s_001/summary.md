# RL Behavior Clone Phase-Aligned Staged GRU Context8 High-Pressure 300s Comparison

- Model: `harness/reports/2026-05-27_rl_behavior_clone_kite_staged_gru_context8_phase_aligned_smoke_001/staged.pt`
- Map preset: `high-pressure`
- Seeds: `47000` to `47002`
- Duration: `300` seconds
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`

## Results

| Map | Policy win rate | Avg survival | Normalized entropy | Dominant action ratio | Best rule Bot win rate |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 0.0 | 36.8442 | 0.2894 | 0.6921 | 0.667 |
| `caramel-workshop` | 0.0 | 163.7789 | 0.7146 | 0.3563 | 0.0 |
| `cracked-star-jar` | 0.3333 | 209.5998 | 0.8697 | 0.2265 | 1.0 |

## Findings

- `soda-creek`: policy recorded 0% win rate and must not be promoted as a multi-map RL test Bot.
- `caramel-workshop`: policy recorded 0% win rate in the long window.
- `cracked-star-jar`: policy win rate is less than half of the strongest compared rule Bot on this map.

## Limitations

- Correcting the phase-aligned data window did not fix movement-only imitation.
- This result is not a balance, fun, release, or accepted-content gate.
