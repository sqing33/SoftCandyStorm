# RL Behavior Clone Action-Change Staged GRU Context8 High-Pressure 60s Comparison

- Model: `harness/reports/2026-05-27_rl_behavior_clone_kite_staged_gru_context8_action_change_smoke_001/staged.pt`
- Map preset: `high-pressure`
- Seeds: `46000` to `46004`
- Duration: `60` seconds
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`

## Results

| Map | Policy win rate | Avg survival | Normalized entropy | Dominant action ratio | Best rule Bot win rate |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 0.4 | 41.8397 | 0.6104 | 0.5226 | 1.0 |
| `caramel-workshop` | 0.8 | 54.8262 | 0.5629 | 0.5128 | 1.0 |
| `cracked-star-jar` | 0.6 | 52.8262 | 0.6935 | 0.2639 | 1.0 |

## Findings

- Action-change weighting removed the 60 second `soda-creek` action-distribution repair seen in the phase-aligned staged policy.
- `soda-creek` still underperformed the strongest compared rule Bot by more than half.
- This short-window improvement is not enough to promote the model.

## Limitations

- This short-window result is not a balance, fun, release, or accepted-content gate.
