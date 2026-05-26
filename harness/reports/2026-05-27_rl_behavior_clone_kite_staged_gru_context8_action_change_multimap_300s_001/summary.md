# RL Behavior Clone Action-Change Staged GRU Context8 High-Pressure 300s Comparison

- Model: `harness/reports/2026-05-27_rl_behavior_clone_kite_staged_gru_context8_action_change_smoke_001/staged.pt`
- Map preset: `high-pressure`
- Seeds: `47000` to `47002`
- Duration: `300` seconds
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`

## Results

| Map | Policy win rate | Avg survival | Normalized entropy | Dominant action ratio | Best rule Bot win rate |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 0.0 | 114.1384 | 0.6200 | 0.5507 | 0.667 |
| `caramel-workshop` | 0.0 | 214.3168 | 0.7715 | 0.3419 | 0.0 |
| `cracked-star-jar` | 0.0 | 104.8389 | 0.6370 | 0.3317 | 1.0 |

## Findings

- All three high-pressure maps recorded 0% policy win rate in the 300 second window.
- Action-change weighting improved action entropy but did not solve long-run survival or route planning.
- The policy remains `repair` and must not be promoted as a multi-map RL test Bot.

## Limitations

- This result is not a balance, fun, release, or accepted-content gate.
