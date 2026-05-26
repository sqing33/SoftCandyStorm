# RL PPO BC-Distilled Warm-Start Training

- Warm-start model: `harness/reports/2026-05-27_rl_sb3_bc_distillation_action_change_full_001/ppo_bc_distilled.zip`
- Output model: `harness/reports/2026-05-27_rl_ppo_bc_distilled_warmstart_001/ppo_bc_distilled_warmstart.zip`
- Training maps: `high-pressure`
- Training seconds: `300`
- Timesteps: `2048`
- Evaluation map: `soda-creek`
- Gate decision: `trained_needs_action_bias_repair`

## Result

- 60 second training report evaluation win rate: `0.0`
- Average survival: `31.0332`
- Normalized action entropy: `0.0042`
- Dominant action: `3` at `0.9989`

## Findings

- PPO warm-start training loaded the distilled `.zip` and completed environment optimization.
- The resulting policy collapsed almost entirely to action `3` in the built-in evaluation.
- This training report is `repair`, not an RL test Bot candidate.
