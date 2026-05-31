# RL Repair Probe Gate

- Decision: `rl_repair_probe_gate_failed`
- Errors: `0`
- Blockers: `2`
- Warnings: `0`

## Inputs

- Training report: `harness/reports/2026-05-30_rl_stage01_seed63402_guard_anchor_probe_001/ppo_training_report.json`
- Window regression (required, `parent`): `harness/reports/2026-05-30_rl_stage01_seed63402_guard_anchor_probe_001/window_regression_vs_parent.json`

## Blockers

- training_report anchor guard: validation_mean_kl 4.251955 exceeds max 0.25
- training_report anchor guard: validation_argmax_agreement 0.0 below min 0.85

## Limitations

- This gate is for RL repair probes only; it is not policy acceptance.
- Passing means a limited follow-up run may be considered, not that the policy is a candidate.
- Release, playtest, and RL acceptance require their separate manifests and manual gates.
