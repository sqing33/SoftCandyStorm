# RL Repair Probe Gate

- Decision: `rl_repair_probe_gate_failed`
- Errors: `0`
- Blockers: `5`
- Warnings: `1`

## Inputs

- Training report: `harness/reports/2026-05-29_rl_sb3_e30_opening_mid_retention_late_probe_001/ppo_training_report.json`
- Anchor alignment: `harness/reports/2026-05-29_rl_sb3_e30_opening_mid_retention_late_probe_001/full_anchor_alignment.json`
- Window regression (required, `e30`): `harness/reports/2026-05-29_rl_sb3_e30_opening_mid_retention_late_probe_001/window_regression_vs_e30.json`
- Window regression (required, `parent`): `harness/reports/2026-05-29_rl_sb3_e30_opening_mid_retention_late_probe_001/window_regression_vs_mid_anchor_parent.json`
- Failure analysis: `harness/reports/2026-05-29_rl_sb3_e30_opening_mid_retention_late_probe_001/failure_analysis_300s.json`

## Blockers

- e30/window_regression_vs_e30: 180s/caramel-workshop: dominant_action_ratio increased 0.2638 beyond allowed 0.2
- e30/window_regression_vs_e30: 300s/soda-creek: average_survival_seconds dropped 24.3608s beyond allowed 5.0s
- parent/window_regression_vs_mid_anchor_parent: 180s/caramel-workshop: dominant_action_ratio increased 0.2413 beyond allowed 0.2
- parent/window_regression_vs_mid_anchor_parent: 300s/soda-creek: average_survival_seconds dropped 27.2947s beyond allowed 5.0s
- parent/window_regression_vs_mid_anchor_parent: 60s/cracked-star-jar: win_rate_delta -0.3333 below required 0.0

## Warnings

- failure_analysis: remaining failures mean this can only be limited repair evidence

## Limitations

- This gate is for RL repair probes only; it is not policy acceptance.
- Passing means a limited follow-up run may be considered, not that the policy is a candidate.
- Release, playtest, and RL acceptance require their separate manifests and manual gates.
