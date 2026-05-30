# Edge Recovery Sample Validation

- Decision: `edge_recovery_samples_valid`
- Source: `harness/reports/2026-05-30_rl_per_map_edge_branch_late_all_high_pressure_001/per_map_chain_edge_samples.jsonl`
- Samples: `21`
- Maps: `caramel-workshop, soda-creek`
- Seeds: `63400, 63401, 63402`
- Time range: `7.0333` to `59.9994` seconds

## Original Actions
- `1`: 4
- `2`: 3
- `4`: 2
- `5`: 12

## Target Actions
- `3`: 7
- `5`: 2
- `7`: 12

## Notes
- This validator checks sample structure and edge-action consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
