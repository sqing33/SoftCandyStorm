# RL Repair Probe Gate

- Decision: `rl_repair_probe_gate_failed`
- Errors: `0`
- Blockers: `9`
- Warnings: `0`

## Inputs

- Training report: `harness/reports/2026-05-31_rl_mid_path_retention_seed63407_closed_loop_probe_001/ppo_training_report.json`
- Window regression (required, `parent`): `harness/reports/2026-05-31_rl_mid_path_retention_seed63407_closed_loop_probe_001/window_regression_high_pressure_vs_parent.json`
- Target seed preflight (required, `target63407`): `harness/reports/2026-05-31_rl_mid_path_retention_seed63407_closed_loop_probe_001/target_seed_preflight_seed63407.json`
- Target seed preflight (required, `opening63402`): `harness/reports/2026-05-31_rl_mid_path_retention_seed63407_closed_loop_probe_001/target_seed_preflight_seed63402_opening.json`
- Target seed preflight (required, `retention63405`): `harness/reports/2026-05-31_rl_mid_path_retention_seed63407_closed_loop_probe_001/target_seed_preflight_seed63405_retention.json`
- Window target preflight (required, `short60`): `harness/reports/2026-05-31_rl_mid_path_retention_seed63407_closed_loop_probe_001/window_target_preflight_60s_caramel.json`

## Blockers

- parent/window_regression_high_pressure_vs_parent: 180s/cracked-star-jar: action_distribution_l1_delta 0.4646 beyond allowed 0.45
- parent/window_regression_high_pressure_vs_parent: 300s/caramel-workshop: action_distribution_l1_delta 0.5872 beyond allowed 0.45
- parent/window_regression_high_pressure_vs_parent: 60s/caramel-workshop: win_rate_delta -0.3334 below required 0.0
- opening63402/target_seed_preflight_seed63402_opening: caramel-workshop:63402: time_seconds 40.0997 below required 60.0000
- opening63402/target_seed_preflight_seed63402_opening: caramel-workshop:63402: terminal_kind is `defeat`
- retention63405/target_seed_preflight_seed63405_retention: caramel-workshop:63405: time_seconds 138.6673 below required 180.0000
- retention63405/target_seed_preflight_seed63405_retention: caramel-workshop:63405: terminal_kind is `defeat`
- short60/window_target_preflight_60s_caramel: 60s-caramel-short-window/caramel-workshop: win_rate 0.3333 below required 0.6667
- short60/window_target_preflight_60s_caramel: 60s-caramel-short-window/caramel-workshop: average_survival_seconds 49.2774 below required 55.0000

## Limitations

- This gate is for RL repair probes only; it is not policy acceptance.
- Passing means a limited follow-up run may be considered, not that the policy is a candidate.
- Release, playtest, and RL acceptance require their separate manifests and manual gates.
