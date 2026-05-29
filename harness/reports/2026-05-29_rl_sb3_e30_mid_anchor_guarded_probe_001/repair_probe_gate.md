# RL Repair Probe Gate

- Decision: `rl_repair_probe_gate_passed_for_limited_followup`
- Errors: `0`
- Blockers: `0`
- Warnings: `1`

## Inputs

- Training report: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_training_report.json`
- Anchor alignment: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/full_anchor_alignment.json`
- Window regression: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/window_regression_vs_e30.json`
- Failure analysis: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/failure_analysis_300s.json`

## Warnings

- failure_analysis: remaining failures mean this can only be limited repair evidence

## Limitations

- This gate is for RL repair probes only; it is not policy acceptance.
- Passing means a limited follow-up run may be considered, not that the policy is a candidate.
- Release, playtest, and RL acceptance require their separate manifests and manual gates.
