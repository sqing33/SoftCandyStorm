# RL PPO Target-Entropy Warm-Start High-Pressure 60s Comparison

- Model: `harness/reports/2026-05-27_rl_ppo_target_entropy_warmstart_001/ppo_target_entropy_warmstart.zip`
- Map preset: `high-pressure`
- Seeds: `50000` to `50004`
- Duration: `60` seconds
- Gate decision: `multimap_comparison_recorded_not_balance_gate`

## Results

| Map | Policy win rate | Avg survival | Normalized entropy | Dominant action ratio | Best rule Bot win rate |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 0.8 | 55.7128 | 0.3189 | 0.5399 | 1.0 |
| `caramel-workshop` | 0.8 | 56.6861 | 0.3218 | 0.5976 | 1.0 |
| `cracked-star-jar` | 0.8 | 53.1662 | 0.3225 | 0.6247 | 1.0 |

## Findings

- The short-window comparison no longer triggers the compare script's action-bias repair.
- The policy still underperforms the strongest rule Bot on all three maps and remains below the RL acceptance entropy target.

## Limitations

- This short-window result is not a balance, fun, release, or accepted-content gate.
