# SB3 Distillation From Time-Phase Balance Teacher

## 结论

阶段平衡 GRU teacher 可以被 `distill_behavior_clone_to_sb3.py` 蒸馏为 SB3 PPO zip，但 deterministic 在线评估仍出现 action collapse。本次结论为 `sb3_distillation_smoke_only_not_policy_gate`，不能推进为 RL 测试 Bot 或 warm-start 成功证据。

对应 failure case：`harness/failed_cases/fail_20260527_016_time_phase_balance_distillation_action_collapse.json`。

## Distillation

- Dataset: `harness/reports/2026-05-27_rl_rule_bot_trajectory_phase_aligned_001`
- Teacher: `harness/reports/2026-05-27_rl_behavior_clone_time_phase_balance_curriculum_full_001/time_phase_balance_curriculum_full.pt`
- Model: `ppo_time_phase_balance_distilled.zip`
- Metadata: `ppo_time_phase_balance_distilled_metadata.json`
- Epochs: `5`
- Teacher temperature: `1.5`
- Uniform target mix: `0.05`
- Teacher argmax agreement: `0.8898`
- Target entropy: `0.903933`
- Final validation argmax accuracy: `0.8069`
- Final validation policy entropy: `1.295753`

## Loading Smoke

`evaluation_soda_creek_10s.json` loaded the distilled zip through `train_sb3.py --evaluate-model`, but deterministic action selection collapsed:

- Map: `soda-creek`
- Duration: `10` seconds
- Episodes: `1`
- Win rate: `1.0`
- Normalized action entropy: `0.0`
- Dominant action: `3` / `100%`

This means the supervised zip is only a serialization and initialization artifact. Any next attempt must use PPO environment optimization, stronger target entropy, or stochastic diagnostics before running long high-pressure comparisons.
