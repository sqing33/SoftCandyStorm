# RL PPO Target-Entropy Entropy-Coefficient Warm-Start Training

- Warm-start model: `harness/reports/2026-05-27_rl_sb3_bc_distillation_target_entropy_full_001/ppo_bc_distilled_target_entropy.zip`
- Output model: `harness/reports/2026-05-27_rl_ppo_target_entropy_entcoef_warmstart_001/ppo_target_entropy_entcoef_warmstart.zip`
- Training maps: `high-pressure`
- Training seconds: `300`
- Timesteps: `2048`
- Entropy coefficient: `0.02`
- Evaluation map: `soda-creek`
- Gate decision: `trained_needs_rule_bot_comparison`

## Result

- 60 second training report evaluation win rate: `0.6`
- Average survival: `57.8061`
- Normalized action entropy: `0.4036`
- Dominant action: `6` at `0.5237`
- Algorithm parameter source: `warm_start_metadata_with_overrides`

## Findings

- Entropy coefficient override is applied and recorded in the training report.
- Built-in 60 second entropy improves over the target-entropy warm-start without entropy override, but remains below the RL acceptance target.
- This training report is not an RL test Bot candidate.
