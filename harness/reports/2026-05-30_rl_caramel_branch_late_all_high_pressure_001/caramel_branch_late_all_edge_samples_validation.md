# Edge Recovery Sample Validation

- Decision: `edge_recovery_samples_valid`
- Source: `harness/reports/2026-05-30_rl_caramel_branch_late_all_high_pressure_001/caramel_branch_late_all_edge_samples.jsonl`
- Samples: `3`
- Maps: `caramel-workshop`
- Seeds: `63402`
- Time range: `31.2665` to `31.2665` seconds

## Original Actions
- `5`: 3

## Target Actions
- `7`: 3

## Notes
- This validator checks sample structure and edge-action consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
