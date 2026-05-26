# RL SB3 Behavior Clone Distillation Smoke

- Script: `python/train/distill_behavior_clone_to_sb3.py`
- Teacher model: `harness/reports/2026-05-27_rl_behavior_clone_kite_staged_gru_context8_action_change_smoke_001/staged.pt`
- Dataset: `harness/reports/2026-05-27_rl_rule_bot_trajectory_phase_aligned_001`
- Limit samples: `256`
- Epochs: `1`
- Output model: `harness/reports/2026-05-27_rl_sb3_bc_distillation_smoke_001/ppo_bc_distilled_smoke.zip`
- Gate decision: `sb3_distillation_smoke_only_not_policy_gate`

## Distillation Result

- Status: `trained`
- Target mode: `teacher_probs`
- Teacher argmax agreement with trajectory action: `0.8633`
- Target entropy: `0.841871`
- Validation argmax accuracy: `0.3922`
- Validation policy entropy: `2.197070`

## Load / Evaluation Smoke

- Existing `train_sb3.py --evaluate-model` path loaded the distilled `.zip`.
- 10 second `soda-creek` smoke completed with action score diagnostics available.
- The deterministic smoke selected action `3` for all 300 steps; this is expected for a 1 epoch / 256 sample plumbing test and is not policy-quality evidence.

## Limitations

- This smoke proves only that BC teacher probabilities can initialize an SB3 PPO `MlpPolicy` and be loaded by the existing evaluator.
- It does not run PPO environment optimization, high-pressure comparison, RL policy acceptance, balance, fun, or release gates.
