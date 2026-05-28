# Stage 02 Mid Anchor Guard Smoke

- Decision: `mid_anchor_guard_smoke_rejected_anchor_guard`
- Gate decision: `trained_anchor_validation_guard_failed_not_policy_gate`
- Start model: `harness/reports/2026-05-28_rl_curriculum_stage02_anchor_regularized_smoke_001/ppo_anchor_regularized_smoke.zip`
- Model: `ppo_mid_anchor_guard_smoke.zip`
- Failure case: `harness/failed_cases/fail_20260528_089_stage02_mid_anchor_guard_smoke_anchor_guard.json`

This smoke used the new anchor validation guard before attempting a longer mid-window repair. It started from the previous anchor-regularized smoke checkpoint, trained only on `soda-creek` / `caramel-workshop` with `late-route-recovery`, and used the top `200` `mid_60_to_180` drift rows from `mid_anchor_drift_training_samples.jsonl` as the offline anchor dataset.

The guard did its job and stopped the run early. The command requested `512` timesteps, but the report records `actual_timesteps = 256` because the first chunk failed the anchor validation thresholds: validation mean KL was `2.310775` against a max of `0.25`, and validation argmax agreement was `0.0` against a minimum of `0.85`.

Because the training guard failed, this branch did not proceed to fixed-window `60s` / `180s` / `300s` no-regression comparisons. It is a rejected repair smoke, not a policy gate, playtest candidate, or RL acceptance artifact.

## Next

- Do not continue this exact branch by raising timesteps.
- Pre-check the start model against the drift rows before training.
- Mix the top drift rows with broader anchor datasets, or lower the PPO update size, while keeping this guard enabled.
- Any future checkpoint still needs anchor alignment, fixed-window high-pressure no-regression, repair-probe gate, and failure-case review.

## Files

- `train_cli_report.json`
- `ppo_training_report.json`
- `ppo_evaluation_report.json`
- `ppo_known_exploits.json`
- `ppo_mid_anchor_guard_smoke_metadata.json`
- `ppo_mid_anchor_guard_smoke.zip`
