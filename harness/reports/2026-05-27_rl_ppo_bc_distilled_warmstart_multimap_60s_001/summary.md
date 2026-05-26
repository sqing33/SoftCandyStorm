# RL PPO BC-Distilled Warm-Start High-Pressure 60s Comparison

- Model: `harness/reports/2026-05-27_rl_ppo_bc_distilled_warmstart_001/ppo_bc_distilled_warmstart.zip`
- Map preset: `high-pressure`
- Seeds: `48000` to `48004`
- Duration: `60` seconds
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`

## Results

| Map | Policy win rate | Avg survival | Normalized entropy | Dominant action ratio | Best rule Bot win rate |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 0.4 | 40.8131 | 0.1949 | 0.8468 | 1.0 |
| `caramel-workshop` | 0.8 | 55.6195 | 0.1359 | 0.9120 | 1.0 |
| `cracked-star-jar` | 0.8 | 56.7928 | 0.2134 | 0.8232 | 1.0 |

## Findings

- All three maps failed the per-map action distribution gate.
- `soda-creek` also underperformed the strongest compared rule Bot by more than half.

## Limitations

- This short-window result is not a balance, fun, release, or accepted-content gate.
