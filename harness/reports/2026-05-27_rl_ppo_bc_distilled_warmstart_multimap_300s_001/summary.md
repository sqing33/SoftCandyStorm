# RL PPO BC-Distilled Warm-Start High-Pressure 300s Comparison

- Model: `harness/reports/2026-05-27_rl_ppo_bc_distilled_warmstart_001/ppo_bc_distilled_warmstart.zip`
- Map preset: `high-pressure`
- Seeds: `49000` to `49002`
- Duration: `300` seconds
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`

## Results

| Map | Policy win rate | Avg survival | Normalized entropy | Dominant action ratio | Best rule Bot win rate |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 0.0 | 77.6462 | 0.2439 | 0.7728 | 0.333 |
| `caramel-workshop` | 0.0 | 197.9022 | 0.3003 | 0.7631 | 0.333 |
| `cracked-star-jar` | 0.0 | 151.1557 | 0.1928 | 0.8494 | 0.667 |

## Findings

- All three high-pressure maps recorded 0% policy win rate in the 300 second window.
- All three maps also failed the per-map action distribution gate.
- PPO warm-start did not remove the action 3 bias inherited from the supervised initialization / early optimization.

## Limitations

- This result is not a balance, fun, release, or accepted-content gate.
