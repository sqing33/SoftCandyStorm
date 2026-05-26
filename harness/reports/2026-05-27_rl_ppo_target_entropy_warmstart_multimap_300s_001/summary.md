# RL PPO Target-Entropy Warm-Start High-Pressure 300s Comparison

- Model: `harness/reports/2026-05-27_rl_ppo_target_entropy_warmstart_001/ppo_target_entropy_warmstart.zip`
- Map preset: `high-pressure`
- Seeds: `51000` to `51002`
- Duration: `300` seconds
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`

## Results

| Map | Policy win rate | Avg survival | Normalized entropy | Dominant action ratio | Best rule Bot win rate |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 0.0 | 56.8328 | 0.2993 | 0.6481 | 0.667 |
| `caramel-workshop` | 0.0 | 184.7216 | 0.2276 | 0.8237 | 0.333 |
| `cracked-star-jar` | 0.0 | 193.5457 | 0.2900 | 0.8119 | 0.667 |

## Findings

- All three high-pressure maps recorded 0% policy win rate in the 300 second window.
- Target-entropy distillation improved the short-window surface but did not solve long-run planning or action-bias repair.
- The failure mode shifted from action 3 dominance to action 6 dominance in longer runs.

## Limitations

- This result is not a balance, fun, release, or accepted-content gate.
