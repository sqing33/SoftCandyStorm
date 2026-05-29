# RL Repair Probe Gate

- Decision: `rl_repair_probe_gate_failed`
- Errors: `0`
- Blockers: `1`
- Warnings: `1`

## Inputs

- Training report: `harness/reports/2026-05-29_rl_sb3_cracked_terminal_window_risk_distill_w10_e30_001/distillation_report.json`
- Anchor alignment: `harness/reports/2026-05-29_rl_sb3_cracked_terminal_window_risk_distill_w10_e30_001/full_anchor_alignment.json`
- Window regression (required, `e30`): `harness/reports/2026-05-29_rl_terminal_conversion_parent_branch_probe_001/window_regression_vs_e30.json`
- Window regression (required, `parent`): `harness/reports/2026-05-29_rl_terminal_conversion_parent_branch_probe_001/window_regression_vs_parent.json`
- Failure analysis: `harness/reports/2026-05-29_rl_terminal_conversion_parent_branch_probe_001/failure_analysis_300s.json`

## Blockers

- parent/window_regression_vs_parent: 300s/cracked-star-jar: average_survival_seconds dropped 0.4779s beyond allowed 0.0s

## Warnings

- failure_analysis: remaining failures mean this can only be limited repair evidence

## Limitations

- This gate is for RL repair probes only; it is not policy acceptance.
- Passing means a limited follow-up run may be considered, not that the policy is a candidate.
- Release, playtest, and RL acceptance require their separate manifests and manual gates.
