# Edge Recovery Sample Validation

- Decision: `edge_recovery_samples_valid`
- Source: `harness/reports/2026-05-31_rl_failure_lane_opening_branch_drift_diagnostic_001/branch_edge_samples.jsonl`
- Samples: `3`
- Maps: `caramel-workshop`
- Seeds: `63401, 63402`
- Time range: `6.6333` to `20.0` seconds

## Original Actions
- `2`: 1
- `5`: 2

## Target Actions
- `3`: 1
- `7`: 2

## Notes
- This validator checks sample structure and edge-action consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
