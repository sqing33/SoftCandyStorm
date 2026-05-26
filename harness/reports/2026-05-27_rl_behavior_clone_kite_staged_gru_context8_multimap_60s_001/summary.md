# RL Behavior Clone Staged GRU Context8 High-Pressure 60s Comparison

- Model: `harness/reports/2026-05-27_rl_behavior_clone_kite_staged_gru_context8_smoke_001/staged.pt`
- Map preset: `high-pressure`
- Seeds: `46000` to `46004`
- Duration: `60` seconds
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`

## Results

| Map | Policy win rate | Avg survival | Normalized entropy | Dominant action ratio | Best rule Bot win rate |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 0.2 | 38.7398 | 0.3163 | 0.7672 | 1.0 |
| `caramel-workshop` | 0.8 | 54.8262 | 0.4368 | 0.5686 | 1.0 |
| `cracked-star-jar` | 0.8 | 53.6595 | 0.5365 | 0.5229 | 1.0 |

## Findings

- `soda-creek`: policy action distribution failed the per-map comparison gate.
- `soda-creek`: policy win rate is less than half of the strongest compared rule Bot.

## Limitations

- The staged policy did not pass the short-window action distribution check.
- This short-window result is not a balance, fun, release, or accepted-content gate.
