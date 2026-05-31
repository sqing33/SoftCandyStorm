# RL Repair Probe Gate

- Decision: `rl_repair_probe_gate_failed`
- Errors: `0`
- Blockers: `6`
- Warnings: `1`

## Inputs

- Training report: `harness/reports/2026-05-31_rl_opening_mid_boundary_retention_seed63405_probe_001/ppo_training_report.json`
- Window regression (required, `parent`): `harness/reports/2026-05-31_rl_opening_mid_boundary_retention_seed63405_probe_001/window_regression_high_pressure_vs_parent.json`
- Window regression (required, `caramel10`): `harness/reports/2026-05-31_rl_opening_mid_boundary_retention_seed63405_probe_001/window_regression_caramel_300s_10seed.json`
- Target seed preflight (required, `retention63405`): `harness/reports/2026-05-31_rl_opening_mid_boundary_retention_seed63405_probe_001/target_seed_preflight_seed63405_retention.json`
- Window target preflight (required, `short60`): `harness/reports/2026-05-31_rl_opening_mid_boundary_retention_seed63405_probe_001/window_target_preflight_60s_caramel.json`
- Failure analysis: `harness/reports/2026-05-31_rl_opening_mid_boundary_retention_seed63405_probe_001/failure_analysis_caramel_300s_10seed.json`

## Blockers

- parent/window_regression_high_pressure_vs_parent: 180s/cracked-star-jar: action_distribution_l1_delta 0.7526 beyond allowed 0.45
- parent/window_regression_high_pressure_vs_parent: 300s/caramel-workshop: action_distribution_l1_delta 0.6056 beyond allowed 0.45
- parent/window_regression_high_pressure_vs_parent: 60s/caramel-workshop: win_rate_delta -0.3334 below required 0.0
- retention63405/target_seed_preflight_seed63405_retention: caramel-workshop:63405: terminal_kind is `defeat`
- short60/window_target_preflight_60s_caramel: 60s-caramel-short-window/caramel-workshop: win_rate 0.3333 below required 0.6667
- short60/window_target_preflight_60s_caramel: 60s-caramel-short-window/caramel-workshop: average_survival_seconds 49.2774 below required 55.0000

## Warnings

- failure_analysis: remaining failures mean this can only be limited repair evidence

## Limitations

- This gate is for RL repair probes only; it is not policy acceptance.
- Passing means a limited follow-up run may be considered, not that the policy is a candidate.
- Release, playtest, and RL acceptance require their separate manifests and manual gates.
