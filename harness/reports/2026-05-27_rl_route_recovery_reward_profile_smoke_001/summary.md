# Route Recovery Reward Profile Smoke

## 结论

`route_recovery` action-aware reward 已接入 `long-run-retention` closed-loop PPO smoke，并同时使用升级选择 ranker；结论为 `repair`。该信号能在 reward breakdown 中稳定记录 policy 继续朝边界、敌压、危险区或 Boss 压力移动的负反馈，但 2048 timestep continuation 没有把负反馈转化为可通过 high-pressure gate 的恢复路线。

- Gate: `multimap_comparison_recorded_needs_policy_repair`
- Model: `harness/reports/2026-05-27_rl_route_recovery_reward_profile_smoke_001/ppo_route_recovery_reward_profile_smoke.zip`
- Reward profile: `long-run-retention` with `route_recovery`
- Upgrade ranker: `harness/reports/2026-05-27_rl_upgrade_choice_multimap_ranker_smoke_001/upgrade_choice_multimap_smoke.pt`
- Warm start: `harness/reports/2026-05-27_rl_closed_loop_late_survival_reward_profile_extended_001/ppo_late_survival_reward_profile_extended.zip`
- Training: PPO `2048` timesteps, high-pressure maps, 300-second episodes, seeds `62300-62320`, `learning_rate=0.0001`, `ent_coef=0.02`
- Limitation: repair experiment only; not Stage 03, not RL acceptance, not playtest or balance evidence

## Deterministic High-pressure Results

| Window | soda-creek | caramel-workshop | cracked-star-jar | Decision |
|---|---:|---:|---:|---|
| 60s / 3 seed | 33.33% | 100% | 100% | opening regression on `soda-creek` |
| 180s / 3 seed | 33.33% | 0% | 33.33% | repair |
| 300s / 3 seed | 0% | 0% | 0% | repair |

Compared with the previous `long-run-retention` smoke, the 300-second blocker is unchanged and the 180-second window regressed on `caramel-workshop` and `cracked-star-jar`. The 60-second `soda-creek` result also fell from 66.67% to 33.33%, so this checkpoint must not be promoted.

## Route Recovery Signal

Average `route_recovery` stayed negative in every deterministic comparison:

| Window | soda-creek | caramel-workshop | cracked-star-jar |
|---|---:|---:|---:|
| 60s | -1.2984 | -1.9921 | -1.5745 |
| 180s | -6.5148 | -3.8890 | -9.3872 |
| 300s | -8.5833 | -3.8837 | -9.0086 |

The signal is therefore detecting unsafe movement, but the current short continuation still leaves action `4` dominant in the 300-second reports and does not learn a reliable recovery policy.

## Failure Analysis

- Total 300-second failures: `9 / 9`
- `soda-creek`: 2 opening failures and 1 late-window failure
- `caramel-workshop`: 3 mid-window failures
- `cracked-star-jar`: 2 mid-window failures and 1 late-window failure
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Evidence

- Training report: `ppo_training_report.json`
- Training evaluation: `ppo_evaluation_report.json`
- 60s comparison: `comparison_60s_3seed.json`
- 180s comparison: `comparison_180s_3seed.json`
- 300s comparison: `comparison_300s_3seed.json`
- Failure analysis: `failure_analysis_300s.md`
- Failed-only traces: `traces_60s/`, `traces_180s/`, `traces_300s/`
- Failure case: `harness/failed_cases/fail_20260527_038_route_recovery_reward_profile_regression.json`

## Next

Do not continue by simply increasing `route_recovery` weight or timesteps. The next repair should first inspect failed-only traces where `route_recovery` is most negative, then choose between lower-weight shaping, supervised recovery samples, staged opening/mid/late policies, or a curriculum that preserves the last known healthy opening gate before adding long-run route objectives.
