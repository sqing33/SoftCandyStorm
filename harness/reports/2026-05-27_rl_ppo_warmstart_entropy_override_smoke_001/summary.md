# RL PPO Warm-Start Entropy Override Smoke

- Script: `python/train/train_sb3.py`
- Warm-start model: `harness/reports/2026-05-27_rl_sb3_bc_distillation_target_entropy_full_001/ppo_bc_distilled_target_entropy.zip`
- Output model: `harness/reports/2026-05-27_rl_ppo_warmstart_entropy_override_smoke_001/ppo_entropy_override_smoke.zip`
- Timesteps: `256`
- Training maps: `high-pressure`
- Entropy coefficient override: `0.02`
- Algorithm parameter source: `warm_start_metadata_with_overrides`
- Gate decision: `trained_needs_action_bias_repair`

## Result

- The CLI accepted `--model-in` and `--ent-coef` together.
- The training report recorded `ent_coef: 0.02` and `algorithm_parameters_source: warm_start_metadata_with_overrides`.
- The 10 second deterministic smoke still collapsed to action `3` at `1.0`, so this smoke proves plumbing only, not policy quality.

## Limitations

- This is not an RL test Bot candidate, balance gate, fun gate, or release gate.
- Full entropy/curriculum experiments still need high-pressure 60/300 second comparison and RL acceptance validation.
