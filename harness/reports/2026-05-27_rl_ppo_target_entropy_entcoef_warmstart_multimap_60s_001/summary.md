# RL PPO Target-Entropy Entropy-Coefficient High-Pressure 60s Comparison

- Model: `harness/reports/2026-05-27_rl_ppo_target_entropy_entcoef_warmstart_001/ppo_target_entropy_entcoef_warmstart.zip`
- Map preset: `high-pressure`
- Seeds: `54000` to `54004`
- Duration: `60` seconds
- Gate decision: `multimap_comparison_recorded_not_balance_gate`

## Results

| Map | Policy win rate | Avg survival | Normalized entropy | Dominant action ratio | Best rule Bot win rate |
|---|---:|---:|---:|---:|---:|
| `soda-creek` | 0.8 | 53.4929 | 0.5801 | 0.3993 | 1.0 |
| `caramel-workshop` | 0.6 | 49.7862 | 0.5823 | 0.4431 | 1.0 |
| `cracked-star-jar` | 0.8 | 53.7929 | 0.5307 | 0.4257 | 1.0 |

## Findings

- All three maps clear the short-window entropy threshold used by RL acceptance.
- The policy still underperforms the strongest rule Bot on all three maps, so it cannot advance.

## Limitations

- This short-window result is not a balance, fun, release, or accepted-content gate.
