# RL SB3 Target-Entropy Full Distillation

- Script: `python/train/distill_behavior_clone_to_sb3.py`
- Teacher model: `harness/reports/2026-05-27_rl_behavior_clone_kite_staged_gru_context8_action_change_smoke_001/staged.pt`
- Dataset: `harness/reports/2026-05-27_rl_rule_bot_trajectory_phase_aligned_001`
- Samples: `21726`
- Epochs: `5`
- Teacher temperature: `1.5`
- Uniform target mix: `0.05`
- Output model: `harness/reports/2026-05-27_rl_sb3_bc_distillation_target_entropy_full_001/ppo_bc_distilled_target_entropy.zip`
- Gate decision: `sb3_distillation_smoke_only_not_policy_gate`

## Distillation Result

- Target mode: `teacher_probs`
- Teacher argmax agreement with trajectory action: `0.8365`
- Target entropy: `1.186717`
- Validation argmax accuracy: `0.7199`
- Validation policy entropy: `1.854044`

## Limitations

- This only initializes an SB3 PPO `MlpPolicy`; it does not prove environment-optimized policy quality.
- The distilled model must still be fine-tuned and run through high-pressure comparison plus RL acceptance.
