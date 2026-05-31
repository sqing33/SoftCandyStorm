# RL Repair Probe Gate

- Decision: `rl_repair_probe_gate_failed`
- Errors: `0`
- Blockers: `1`
- Warnings: `1`

## Inputs

- Training report: `harness/reports/2026-05-31_rl_caramel_selective_ranked_victory_terminal_branch_w05_001/distillation_report.json`
- Window regression (required, `per_map_chain`): `harness/reports/2026-05-31_rl_caramel_selective_ranked_victory_terminal_branch_w05_001/window_regression_vs_per_map_chain.json`
- Failure analysis: `harness/reports/2026-05-31_rl_caramel_selective_ranked_victory_terminal_branch_w05_001/failure_analysis_300s.json`

## Blockers

- per_map_chain/window_regression_vs_per_map_chain: 300s/caramel-workshop: average_survival_seconds dropped 0.4223s beyond allowed 0.0s

## Warnings

- failure_analysis: remaining failures mean this can only be limited repair evidence

## Limitations

- This gate is for RL repair probes only; it is not policy acceptance.
- Passing means a limited follow-up run may be considered, not that the policy is a candidate.
- Release, playtest, and RL acceptance require their separate manifests and manual gates.
