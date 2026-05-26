# RL Behavior Clone Phase-Aligned Staged GRU Context8 High-Pressure 60s Comparison

- Model: `harness/reports/2026-05-27_rl_behavior_clone_kite_staged_gru_context8_phase_aligned_smoke_001/staged.pt`
- Map preset: `high-pressure`
- Seeds: `46000` to `46004`
- Duration: `60` seconds
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`

## Results

| Map | Policy win rate | Avg survival | Normalized entropy | Dominant action ratio | Best rule Bot win rate |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 0.0 | 32.5465 | 0.2356 | 0.7911 | 1.0 |
| `caramel-workshop` | 0.8 | 54.8262 | 0.6081 | 0.5359 | 1.0 |
| `cracked-star-jar` | 0.8 | 53.6595 | 0.5195 | 0.5669 | 1.0 |

## Findings

- `soda-creek`: policy action distribution failed the per-map comparison gate.
- `soda-creek`: policy recorded 0% win rate and must not be promoted as a multi-map RL test Bot.

## Limitations

- Phase-aligned opening data did not repair the short-window staged policy collapse.
- This short-window result is not a balance, fun, release, or accepted-content gate.
