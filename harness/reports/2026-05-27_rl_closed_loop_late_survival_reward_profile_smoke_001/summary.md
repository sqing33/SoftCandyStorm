# Closed-loop Late Survival Reward Profile Smoke

## 结论

`late-survival` reward profile 的真实 closed-loop PPO 训练链路已跑通，但没有解除 300 秒 high-pressure 多图 blocker。

- Gate: `multimap_comparison_recorded_needs_policy_repair`
- Model: `harness/reports/2026-05-27_rl_closed_loop_late_survival_reward_profile_smoke_001/ppo_late_survival_reward_profile_smoke.zip`
- Reward profile: `late-survival`
- Warm start: `harness/reports/2026-05-27_rl_curriculum_stage01_corner_risk_delta_smoke_001/stage01_corner_risk_delta_smoke.zip`
- Training: PPO `1024` timesteps, high-pressure maps, 300-second episodes, seeds `62300-62308`
- Limitation: smoke-scale training only; not Stage 03, not RL acceptance, not playtest or balance evidence

## Deterministic High-pressure Results

| Window | soda-creek | caramel-workshop | cracked-star-jar | Decision |
|---|---:|---:|---:|---|
| 60s / 3 seed | 100% | 100% | 100% | short-window pass only |
| 180s / 3 seed | 66.67% | 100% | 100% | watch / not enough for long-run |
| 300s / 3 seed | 0% | 0% | 0% | repair |

300-second failure analysis:

- Total failures: `9 / 9`
- `soda-creek`: one opening failure at `39.6997s`, two late failures at `211.4162s` and `216.584s`
- `caramel-workshop`: three failures in `late_180_to_300`
- `cracked-star-jar`: three failures in `late_180_to_300`
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`

## Evidence

- Training report: `ppo_training_report.json`
- 60s comparison: `comparison_60s_3seed.json`
- 180s comparison: `comparison_180s_3seed.json`
- 300s comparison: `comparison_300s_3seed.json`
- Failure analysis: `failure_analysis_300s.md`
- Failed-only traces: `traces_300s/`
- Failure case: `harness/failed_cases/fail_20260527_035_closed_loop_late_survival_reward_profile_gap.json`

## Next

The next repair should keep the real closed-loop path, but target the 180-300 second window more directly: longer late-survival training on the observed failure seeds, explicit low-health recovery, hazard + boss pressure route objectives, and opening retention checks. Do not promote this model to Stage 03 or `rl_test_bot_candidate`.
