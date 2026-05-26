# RL SB3 Action-Change Teacher Distillation

- Script: `python/train/distill_behavior_clone_to_sb3.py`
- Teacher model: `harness/reports/2026-05-27_rl_behavior_clone_kite_staged_gru_context8_action_change_smoke_001/staged.pt`
- Dataset: `harness/reports/2026-05-27_rl_rule_bot_trajectory_phase_aligned_001`
- Samples: `21726`
- Epochs: `5`
- Output model: `harness/reports/2026-05-27_rl_sb3_bc_distillation_action_change_full_001/ppo_bc_distilled.zip`
- Gate decision: `sb3_distillation_smoke_only_not_policy_gate`

## Distillation Result

- Target mode: `teacher_probs`
- Teacher argmax agreement with trajectory action: `0.8365`
- Target entropy: `0.759978`
- Validation argmax accuracy: `0.6916`
- Validation policy entropy: `1.850775`

## Limitations

- This only initializes an SB3 PPO `MlpPolicy`; it does not prove environment-optimized policy quality.
- The distilled model must still be fine-tuned and run through high-pressure comparison plus RL acceptance.
