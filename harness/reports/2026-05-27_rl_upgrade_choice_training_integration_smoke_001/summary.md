# Upgrade Choice Training Integration Smoke

## 结论

`train_sb3.py --upgrade-choice-model` 现在可在真实 PPO 训练路径中加载升级选择 ranker，并把同一 ranker 传入训练后的 Gym evaluation。该 smoke 证明 closed-loop training 不再只能使用 bridge 默认第一个升级选项；但它仍是管线证据，不是升级策略质量、长局修复或 RL acceptance。

- Gate: `upgrade_choice_training_integration_smoke_not_policy_gate`
- Model: `harness/reports/2026-05-27_rl_upgrade_choice_training_integration_smoke_001/ppo_upgrade_choice_training_integration_smoke.zip`
- Upgrade ranker: `harness/reports/2026-05-27_rl_upgrade_choice_multimap_ranker_smoke_001/upgrade_choice_multimap_smoke.pt`
- Warm start: `harness/reports/2026-05-27_rl_closed_loop_late_survival_reward_profile_smoke_001/ppo_late_survival_reward_profile_smoke.zip`
- Training: PPO `256` timesteps, high-pressure maps, 120-second episodes, seeds `62300-62305`, `learning_rate=0.0001`
- Reward profile: `late-survival`

## Smoke Result

The post-training `soda-creek` 120-second evaluation reached victory in 1 seed and recorded `3` upgrade-ranker decisions:

| Prompt | Choice | Options |
|---:|---|---|
| 1 | `star-sugar-ray` | `rainbow-candy-shot-level-2`, `star-sugar-ray`, `nonstick-apron` |
| 2 | `mint-cyclone` | `star-sugar-ray-level-2`, `mint-cyclone`, `star-spoon` |
| 3 | `cream-clockwork` | `mint-cyclone-level-2`, `popping-candy-mine`, `cream-clockwork` |

The training report records `training.upgrade_choice_model`, and the evaluation report records top-level `upgrade_policy`, per-episode `upgrade_policy_decisions`, and summary `upgrade_policy_decision_count`.

## Evidence

- Training report: `ppo_training_report.json`
- Evaluation report: `ppo_evaluation_report.json`
- Known exploit notes: `ppo_known_exploits.json`
- Model metadata: `ppo_upgrade_choice_training_integration_smoke_metadata.json`

## Next

Use this plumbing in the next real repair experiment, but do not scale upgrade ranker samples alone. The long-run blocker still requires movement recovery, route objectives, low-health escape, hazard + boss pressure handling, and deterministic high-pressure 60 / 180 / 300-second comparisons.
