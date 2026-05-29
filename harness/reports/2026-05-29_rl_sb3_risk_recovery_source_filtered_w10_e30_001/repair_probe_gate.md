# RL Repair Probe Gate

- Decision: `rl_repair_probe_gate_failed`
- Errors: `0`
- Blockers: `14`
- Warnings: `1`

## Inputs

- Training report: `harness/reports/2026-05-29_rl_sb3_risk_recovery_source_filtered_w10_e30_001/distillation_report.json`
- Anchor alignment: `harness/reports/2026-05-29_rl_sb3_risk_recovery_source_filtered_w10_e30_001/full_anchor_alignment.json`
- Window regression (required, `e30`): `harness/reports/2026-05-29_rl_sb3_risk_recovery_source_filtered_w10_e30_001/window_regression_vs_e30.json`
- Window regression (required, `parent`): `harness/reports/2026-05-29_rl_sb3_risk_recovery_source_filtered_w10_e30_001/window_regression_vs_parent.json`
- Failure analysis: `harness/reports/2026-05-29_rl_sb3_risk_recovery_source_filtered_w10_e30_001/failure_analysis_300s.json`

## Blockers

- e30/window_regression_vs_e30: 180s/caramel-workshop: win_rate_delta -0.3334 below required 0.0
- e30/window_regression_vs_e30: 180s/caramel-workshop: average_survival_seconds dropped 42.0811s beyond allowed 5.0s
- e30/window_regression_vs_e30: 180s/cracked-star-jar: dominant_action_ratio increased 0.2191 beyond allowed 0.2
- e30/window_regression_vs_e30: 180s/soda-creek: average_survival_seconds dropped 7.1999s beyond allowed 5.0s
- e30/window_regression_vs_e30: 180s/soda-creek: dominant_action_ratio increased 0.2599 beyond allowed 0.2
- e30/window_regression_vs_e30: 300s/caramel-workshop: average_survival_seconds dropped 52.8834s beyond allowed 5.0s
- e30/window_regression_vs_e30: 300s/soda-creek: average_survival_seconds dropped 53.4272s beyond allowed 5.0s
- parent/window_regression_vs_parent: 180s/caramel-workshop: win_rate_delta -0.3334 below required 0.0
- parent/window_regression_vs_parent: 180s/caramel-workshop: average_survival_seconds dropped 42.0811s beyond allowed 5.0s
- parent/window_regression_vs_parent: 180s/cracked-star-jar: dominant_action_ratio increased 0.2068 beyond allowed 0.2
- parent/window_regression_vs_parent: 180s/soda-creek: average_survival_seconds dropped 39.9354s beyond allowed 5.0s
- parent/window_regression_vs_parent: 300s/caramel-workshop: average_survival_seconds dropped 59.4181s beyond allowed 5.0s
- parent/window_regression_vs_parent: 300s/soda-creek: average_survival_seconds dropped 56.3611s beyond allowed 5.0s
- parent/window_regression_vs_parent: 60s/soda-creek: win_rate_delta -0.3334 below required 0.0

## Warnings

- failure_analysis: remaining failures mean this can only be limited repair evidence

## Limitations

- This gate is for RL repair probes only; it is not policy acceptance.
- Passing means a limited follow-up run may be considered, not that the policy is a candidate.
- Release, playtest, and RL acceptance require their separate manifests and manual gates.
