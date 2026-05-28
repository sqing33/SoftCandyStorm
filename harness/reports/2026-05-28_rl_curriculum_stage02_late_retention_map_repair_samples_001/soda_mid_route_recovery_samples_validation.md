# Edge Recovery Sample Validation

- Decision: `edge_recovery_samples_valid`
- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_late_retention_map_repair_samples_001/soda_mid_route_recovery_samples.jsonl`
- Samples: `115`
- Maps: `soda-creek`
- Seeds: `63100, 63101, 63102`
- Time range: `73.9992` to `179.0093` seconds

## Original Actions
- `3`: 37
- `5`: 22
- `8`: 56

## Target Actions
- `1`: 16
- `4`: 47
- `5`: 14
- `6`: 7
- `7`: 9
- `8`: 22

## Notes
- This validator checks sample structure and edge-action consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
