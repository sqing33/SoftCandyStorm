# Extended Late Survival Reward Profile Run

## 结论

扩展版 `late-survival` closed-loop PPO 训练出现一点 300 秒长窗信号，但整体仍为 repair，并且带来 180 秒中窗回归。

- Gate: `multimap_comparison_recorded_needs_policy_repair`
- Model: `harness/reports/2026-05-27_rl_closed_loop_late_survival_reward_profile_extended_001/ppo_late_survival_reward_profile_extended.zip`
- Reward profile: `late-survival`
- Warm start: `harness/reports/2026-05-27_rl_closed_loop_late_survival_reward_profile_smoke_001/ppo_late_survival_reward_profile_smoke.zip`
- Training: PPO `5120` timesteps, high-pressure maps, 300-second episodes, seeds `62300-62320`, `learning_rate=0.0001`
- Limitation: repair experiment only; not Stage 03, not RL acceptance, not playtest or balance evidence

## Deterministic High-pressure Results

| Window | soda-creek | caramel-workshop | cracked-star-jar | Decision |
|---|---:|---:|---:|---|
| 60s / 3 seed | 100% | 100% | 100% | short-window pass only |
| 180s / 3 seed | 33.33% | 100% | 66.67% | watch / mid-window regression |
| 300s / 3 seed | 0% | 0% | 33.33% | repair |

Compared with the 1024 timestep smoke, this run improved 300-second `cracked-star-jar` from 0% to 33.33%, but regressed 180-second average win rate from 88.89% to 66.67%. The policy also became more action-4 dominant in all three 300-second maps.

## Failure Analysis

- Total 300-second failures: `8 / 9`
- `soda-creek`: 2 failures moved into `mid_60_to_180`, 1 failure in `late_180_to_300`
- `caramel-workshop`: 3 failures in `late_180_to_300`
- `cracked-star-jar`: 1 failure in `mid_60_to_180`, 1 failure in `late_180_to_300`, 1 victory
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Evidence

- Training report: `ppo_training_report.json`
- 60s comparison: `comparison_60s_3seed.json`
- 180s comparison: `comparison_180s_3seed.json`
- 300s comparison: `comparison_300s_3seed.json`
- Failure analysis: `failure_analysis_300s.md`
- Failed-only traces: `traces_300s/`
- Failure case: `harness/failed_cases/fail_20260527_036_extended_late_survival_reward_profile_regression.json`

## Next

Do not continue by only increasing timesteps. The next repair should add explicit mid-window retention and action-diversity pressure while preserving the long-window reward profile, then re-run deterministic 60/180/300 high-pressure comparisons.
