# Long Run Retention Reward Profile Smoke

## 结论

`long-run-retention` closed-loop PPO smoke 没有解除 RL 多图长局 blocker，结论为 `repair`。它从 `late-survival` extended checkpoint warm start 后，动作熵略有改善，但 300 秒 high-pressure 三图全部 0%，并且 60 秒短窗相对上一轮出现回归。

- Gate: `multimap_comparison_recorded_needs_policy_repair`
- Model: `harness/reports/2026-05-27_rl_closed_loop_long_run_retention_reward_profile_smoke_001/ppo_long_run_retention_reward_profile_smoke.zip`
- Reward profile: `long-run-retention`
- Warm start: `harness/reports/2026-05-27_rl_closed_loop_late_survival_reward_profile_extended_001/ppo_late_survival_reward_profile_extended.zip`
- Training: PPO `2048` timesteps, high-pressure maps, 300-second episodes, seeds `62300-62320`, `learning_rate=0.0001`
- Limitation: repair experiment only; not Stage 03, not RL acceptance, not playtest or balance evidence

## Deterministic High-pressure Results

| Window | soda-creek | caramel-workshop | cracked-star-jar | Decision |
|---|---:|---:|---:|---|
| 60s / 3 seed | 66.67% | 66.67% | 100% | short-window regression |
| 180s / 3 seed | 33.33% | 66.67% | 100% | repair |
| 300s / 3 seed | 0% | 0% | 0% | repair |

Compared with the previous `late-survival` extended run, this smoke regressed 300-second `cracked-star-jar` from 33.33% back to 0% and did not recover `soda-creek` or `caramel-workshop`. The 300-second action entropy improved slightly on some maps, but action `4` remained dominant at roughly 51-53%, and every 300-second episode ended in `player_health_depleted`.

## Failure Analysis

- Total 300-second failures: `9 / 9`
- `soda-creek`: failures split across `opening_lt_60`, `mid_60_to_180`, and `late_180_to_300`
- `caramel-workshop`: one `opening_lt_60` failure and two `late_180_to_300` failures
- `cracked-star-jar`: three `late_180_to_300` failures
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Evidence

- Training report: `ppo_training_report.json`
- 60s comparison: `comparison_60s_3seed.json`
- 180s comparison: `comparison_180s_3seed.json`
- 300s comparison: `comparison_300s_3seed.json`
- Failure analysis: `failure_analysis_300s.md`
- Failed-only traces: `traces_300s/`
- Failure case: `harness/failed_cases/fail_20260527_037_long_run_retention_reward_profile_regression.json`

## Next

Do not continue by only increasing `long-run-retention` timesteps. The next repair should preserve opening retention, add explicit route / recovery objectives for 60-300 seconds, and include upgrade-choice interaction or staged curriculum evidence before another 300-second high-pressure comparison.
