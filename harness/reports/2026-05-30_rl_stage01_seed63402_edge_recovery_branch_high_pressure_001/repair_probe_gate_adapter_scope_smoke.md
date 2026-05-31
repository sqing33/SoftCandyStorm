# RL Repair Probe Gate

- Decision: `rl_repair_probe_gate_passed_for_limited_followup`
- Errors: `0`
- Blockers: `0`
- Warnings: `0`

## Inputs

- Training report: `harness/reports/2026-05-30_rl_stage01_seed63402_edge_recovery_supervised_dataset_actions_001/distillation_report.json`
- Window regression (required, `edge`): `harness/reports/2026-05-30_rl_stage01_seed63402_edge_recovery_branch_high_pressure_001/window_regression_60_180_300s.json`
- Policy adapter scope (required, `edge`): `harness/reports/2026-05-30_rl_stage01_seed63402_edge_recovery_branch_high_pressure_001/policy_adapter_scope.json`

## Limitations

- This gate is for RL repair probes only; it is not policy acceptance.
- Passing means a limited follow-up run may be considered, not that the policy is a candidate.
- Release, playtest, and RL acceptance require their separate manifests and manual gates.
