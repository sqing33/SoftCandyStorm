# Edge Recovery Sample Validation

- Decision: `edge_recovery_samples_valid`
- Source: `harness/reports/2026-05-30_rl_stage01_seed63402_edge_recovery_branch_high_pressure_001/branch_samples_60s_soda-creek.jsonl`
- Samples: `4`
- Maps: `soda-creek`
- Seeds: `63401, 63402`
- Time range: `7.0333` to `59.9994` seconds

## Original Actions
- `1`: 1
- `2`: 1
- `5`: 2

## Target Actions
- `3`: 2
- `7`: 2

## Notes
- This validator checks sample structure and edge-action consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
