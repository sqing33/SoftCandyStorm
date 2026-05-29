# RL Repair Probe Gate

- Decision: `rl_repair_probe_gate_failed`
- Errors: `0`
- Blockers: `2`
- Warnings: `1`

## Inputs

- Training report: `harness/reports/2026-05-29_rl_sb3_e30_mid_late_balanced_followup_probe_001/ppo_training_report.json`
- Anchor alignment: `harness/reports/2026-05-29_rl_sb3_e30_mid_late_balanced_followup_probe_001/full_anchor_alignment.json`
- Window regression: `harness/reports/2026-05-29_rl_sb3_e30_mid_late_balanced_followup_probe_001/window_regression_vs_e30.json`
- Window regression: `harness/reports/2026-05-29_rl_sb3_e30_mid_late_balanced_followup_probe_001/window_regression_vs_mid_anchor_parent.json`
- Failure analysis: `harness/reports/2026-05-29_rl_sb3_e30_mid_late_balanced_followup_probe_001/failure_analysis_300s.json`

## Blockers

- window_regression_vs_mid_anchor_parent: 180s/soda-creek: average_survival_seconds dropped 6.857s beyond allowed 5.0s
- window_regression_vs_mid_anchor_parent: 300s/caramel-workshop: average_survival_seconds dropped 5.19s beyond allowed 5.0s

## Warnings

- failure_analysis: remaining failures mean this can only be limited repair evidence

## Limitations

- This gate is for RL repair probes only; it is not policy acceptance.
- Passing means a limited follow-up run may be considered, not that the policy is a candidate.
- Release, playtest, and RL acceptance require their separate manifests and manual gates.
