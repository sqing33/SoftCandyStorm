# RL PPO Target-Entropy Entropy-Coefficient High-Pressure 300s Comparison

- Model: `harness/reports/2026-05-27_rl_ppo_target_entropy_entcoef_warmstart_001/ppo_target_entropy_entcoef_warmstart.zip`
- Map preset: `high-pressure`
- Seeds: `55000` to `55002`
- Duration: `300` seconds
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`

## Results

| Map | Policy win rate | Avg survival | Normalized entropy | Dominant action ratio | Best rule Bot win rate |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 0.0 | 67.7215 | 0.3079 | 0.5908 | 1.0 |
| `caramel-workshop` | 0.0 | 216.1172 | 0.4518 | 0.6338 | 0.333 |
| `cracked-star-jar` | 0.0 | 162.7221 | 0.5988 | 0.3636 | 0.333 |

## Findings

- All three high-pressure maps recorded 0% policy win rate in the 300 second window.
- Entropy coefficient improves short-window action diversity but does not solve long-run survival, route planning, or upgrade timing.

## Limitations

- This result is not a balance, fun, release, or accepted-content gate.
