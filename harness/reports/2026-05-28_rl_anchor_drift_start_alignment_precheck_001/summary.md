# RL Anchor Drift Start Alignment Precheck

- Decision: `anchor_drift_start_alignment_precheck_failed`
- Gate decision: `behavior_clone_anchor_alignment_failed`
- Candidate start model: `harness/reports/2026-05-28_rl_curriculum_stage02_anchor_regularized_smoke_001/ppo_anchor_regularized_smoke.zip`
- Anchor fallback model: `harness/reports/2026-05-28_rl_curriculum_stage02_current_failure_fallback_probe_001/fallback.pt`
- Anchor opening model: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip`
- Dataset: `harness/reports/2026-05-28_rl_curriculum_stage02_soda_caramel_closed_loop_anchor_probe_001/mid_anchor_drift_training_samples.jsonl`
- Failure case: `harness/failed_cases/fail_20260528_090_stage02_anchor_drift_start_alignment_precheck.json`

This precheck used `compare_sb3_to_behavior_clone_anchor.py --include-anchor-drift-samples` to compare the previous anchor-regularized PPO smoke checkpoint against the current-failure behavior-clone anchor on the top `200` mid-window drift rows. The dataset contains only `anchor_drift_sample` diagnostics with observations, so this report is a training preflight, not RL policy acceptance evidence.

The start model is not close enough to the selected drift rows. Overall mean KL is `2.26528` against a max threshold of `0.25`, and argmax agreement is `0.0` against a minimum threshold of `0.85`. Every map bucket also exceeds the `0.25` mean KL threshold: `caramel-workshop = 2.317458`, `cracked-star-jar = 2.318117`, and `soda-creek = 2.054458`.

This explains why the previous guarded PPO smoke immediately failed the anchor validation guard. Launching another guarded continuation from this same start model with only the top-200 drift rows would begin from a high-drift state rather than a repairable anchor neighborhood.

## Next

- Do not run longer PPO from this start model with only the top-200 mid drift rows.
- Mix the drift rows with broader opening / mid / late anchor data, or choose a closer start checkpoint before training.
- Keep the anchor validation guard enabled for future PPO continuation attempts.
- Any future checkpoint still needs full anchor alignment, deterministic high-pressure no-regression, repair-probe gate, failure-case review, and RL acceptance evidence.

## Files

- `anchor_drift_alignment_precheck.json`
