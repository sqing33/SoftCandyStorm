# RL SB3 Target-Entropy Distillation Smoke

- Script: `python/train/distill_behavior_clone_to_sb3.py`
- Teacher model: `harness/reports/2026-05-27_rl_behavior_clone_kite_staged_gru_context8_action_change_smoke_001/staged.pt`
- Dataset: `harness/reports/2026-05-27_rl_rule_bot_trajectory_phase_aligned_001`
- Samples: `128`
- Epochs: `1`
- Teacher temperature: `1.5`
- Uniform target mix: `0.05`
- Output model: `harness/reports/2026-05-27_rl_sb3_bc_distillation_target_entropy_smoke_001/ppo_bc_distilled_target_entropy_smoke.zip`
- Gate decision: `sb3_distillation_smoke_only_not_policy_gate`

## Distillation Result

- Target mode: `teacher_probs`
- Teacher argmax agreement with trajectory action: `0.8750`
- Target entropy: `1.347383`
- Validation argmax accuracy: `0.3077`
- Validation policy entropy: `2.197138`

## Load Smoke

- `train_sb3.py --evaluate-model` loaded the distilled `.zip` and ran a 10 second `soda-creek` smoke.
- Smoke win rate: `1.0`
- Normalized action entropy: `0.2375`
- Dominant movement remains action `3` at `0.7967`, so this is still only a plumbing and target-transform smoke.

## Limitations

- This does not prove policy quality, high-pressure generalization, balance, fun, or release readiness.
- Full target-entropy distillation must still be followed by PPO training, 60/300 second high-pressure comparison, failure-case review, and RL acceptance validation.
