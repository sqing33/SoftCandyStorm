# Edge Recovery Sample Validation

- Decision: `edge_recovery_samples_valid`
- Source: `harness/reports/2026-05-30_rl_late_recovery_map_scope_high_pressure_001/scoped_chain_edge_samples.jsonl`
- Samples: `8`
- Maps: `caramel-workshop, soda-creek`
- Seeds: `63400, 63402`
- Time range: `25.0333` to `31.2665` seconds

## Original Actions
- `5`: 8

## Target Actions
- `7`: 8

## Notes
- This validator checks sample structure and edge-action consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
