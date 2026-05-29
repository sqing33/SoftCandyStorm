# RL Repair Probe Gate

- Decision: `rl_repair_probe_gate_failed`
- Errors: `0`
- Blockers: `6`
- Warnings: `1`

## Inputs

- Training report: `harness/reports/2026-05-29_rl_sb3_cracked_terminal_window_risk_distill_w7_e30_001/distillation_report.json`
- Anchor alignment: `harness/reports/2026-05-29_rl_sb3_cracked_terminal_window_risk_distill_w7_e30_001/full_anchor_alignment.json`
- Window regression (required, `e30`): `harness/reports/2026-05-29_rl_sb3_cracked_terminal_window_risk_distill_w7_e30_001/window_regression_vs_e30.json`
- Window regression (required, `parent`): `harness/reports/2026-05-29_rl_sb3_cracked_terminal_window_risk_distill_w7_e30_001/window_regression_vs_parent.json`
- Failure analysis: `harness/reports/2026-05-29_rl_sb3_cracked_terminal_window_risk_distill_w7_e30_001/failure_analysis_300s.json`

## Blockers

- e30/window_regression_vs_e30: 180s/soda-creek: average_survival_seconds dropped 9.4888s beyond allowed 5.0s
- e30/window_regression_vs_e30: 300s/soda-creek: average_survival_seconds dropped 56.3051s beyond allowed 5.0s
- e30/window_regression_vs_e30: 60s/caramel-workshop: dominant_action_ratio increased 0.2081 beyond allowed 0.2
- parent/window_regression_vs_parent: 180s/soda-creek: average_survival_seconds dropped 42.2243s beyond allowed 5.0s
- parent/window_regression_vs_parent: 300s/soda-creek: average_survival_seconds dropped 59.239s beyond allowed 5.0s
- parent/window_regression_vs_parent: 60s/caramel-workshop: dominant_action_ratio increased 0.2072 beyond allowed 0.2

## Warnings

- failure_analysis: remaining failures mean this can only be limited repair evidence

## Limitations

- This gate is for RL repair probes only; it is not policy acceptance.
- Passing means a limited follow-up run may be considered, not that the policy is a candidate.
- Release, playtest, and RL acceptance require their separate manifests and manual gates.
