# RL PPO Target-Entropy Warm-Start Training

- Warm-start model: `harness/reports/2026-05-27_rl_sb3_bc_distillation_target_entropy_full_001/ppo_bc_distilled_target_entropy.zip`
- Output model: `harness/reports/2026-05-27_rl_ppo_target_entropy_warmstart_001/ppo_target_entropy_warmstart.zip`
- Training maps: `high-pressure`
- Training seconds: `300`
- Timesteps: `2048`
- Evaluation map: `soda-creek`
- Gate decision: `trained_needs_rule_bot_comparison`

## Result

- 60 second training report evaluation win rate: `0.6`
- Average survival: `51.3529`
- Normalized action entropy: `0.3186`
- Dominant action: `6` at `0.5730`

## Findings

- Target-entropy distillation removed the previous near-total action 3 collapse in the built-in evaluation.
- The policy still has low action entropy and must pass high-pressure comparison before it can be considered useful.
- This training report is `repair/watch`, not an RL test Bot candidate.
